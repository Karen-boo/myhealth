import frappe
from frappe.model.document import Document
from datetime import datetime
from frappe.utils import add_days, nowdate

# In myhealth/myhealth/api/appointment_api.py

@frappe.whitelist(allow_guest=False)
def create_appointment(patient, doctor, service, appointment_date, start_time, end_time, notes=None):
    """Create a new appointment (with double-booking prevention)"""
    
    # --- CRITICAL FIX START ---
    # The 'patient' argument is now the correct Patient ID (e.g., PAT012)
    # because the frontend uses the result of get_patient_id_for_user.
    patient_id = patient 
    
    # Validation: Ensure the Patient ID actually exists before proceeding.
    if not frappe.db.exists("Patient", patient_id):
         frappe.throw(f"Patient ID {patient_id} does not exist. Please check the Patient DocType.")
    # --- CRITICAL FIX END ---
    
    # Check if doctor is already booked at that date and time
    existing = frappe.get_all(
        "Appointment",
        filters={
            "doctor": doctor,
            "appointment_date": appointment_date,
            "start_time": start_time,
            "end_time": end_time,
            "service_status": ["!=", "Cancelled"]
        },
        fields=["name", "service_status"]
    )

    if existing:
        frappe.throw(f"Doctor already has an appointment at {appointment_date} {start_time} {end_time}")

    # Otherwise, create new appointment
    doc = frappe.get_doc({
        "doctype": "Appointment",
        "patient": patient_id, # Use the directly provided Patient ID
        "doctor": doctor,
        "service": service,
        "service_status": "Pending",
        "appointment_date": appointment_date,
        "start_time": start_time,
        "end_time": end_time,
        "notes": notes
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "message": "Appointment created successfully",
        "appointment_id": doc.name
    }

# FETCH Appointments (optionally filter by patient)
@frappe.whitelist(allow_guest=False)
def get_appointments(patient_id=None, service_status=None, doctor=None,
                     date=None, start_date=None, end_date=None, search=None):
    """Fetch appointments with advanced filters + patient search"""
    filters = {}

    # Basic filters
    if patient_id:
        filters["patient"] = patient_id
    if service_status:
        filters["service_status"] = service_status
    if doctor:
        filters["doctor"] = doctor
    if date:
        filters["appointment_date"] = date
    if start_date and end_date:
        filters["appointment_date"] = ["between", [start_date, end_date]]

    # Get appointments that match the base filters
    appointments = frappe.get_all(
        "Appointment",
        filters=filters,
        fields=["name", "patient", "doctor", "service", "service_status",
                "appointment_date", "start_time", "end_time", "notes"]
    )

    results = []
    for a in appointments:
        patient = frappe.get_doc("Patient", a.get("patient"))

        # Attach patient info
        a["patient_info"] = {
            "first_name": patient.get("first_name"),
            "last_name": patient.get("last_name"),
            "age": patient.get("age"),
            "gender": patient.get("gender"),
            "email": patient.get("email")
        }

        # Search filter
        if search:
            search_lower = search.lower()
            if (
                search_lower in str(patient.first_name).lower()
                or search_lower in str(patient.last_name).lower()
                or search_lower in str(patient.email).lower()
            ):
                results.append(a)
        else:
            results.append(a)

    return {"appointments": results}

# UPDATE Appointment
@frappe.whitelist(allow_guest=False)
def update_appointment(name, **kwargs):
    doc = frappe.get_doc("Appointment", name)
    for key, value in kwargs.items():
        if key in doc.as_dict():
            doc.set(key, value)
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"message": "Appointment updated successfully"}


# CANCEL Appointment
@frappe.whitelist(allow_guest=False)
def cancel_appointment(name):
    doc = frappe.get_doc("Appointment", name)
    doc.service_status = "Cancelled"
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"message": f"Appointment {name} marked as Cancelled"}

@frappe.whitelist(allow_guest=False)
def get_appointment_summary():
    """Return summary statistics for appointments"""
    summary = {
        "total_appointments": 0,
        "pending": 0,
        "completed": 0,
        "cancelled": 0
    }

    # Get all appointments
    all_appointments = frappe.get_all("Appointment", fields=["service_status"])
    summary["total_appointments"] = len(all_appointments)

    # Count by status
    for appt in all_appointments:
        status = appt.get("service_status", "").lower()
        if status == "pending":
            summary["pending"] += 1
        elif status == "completed":
            summary["completed"] += 1
        elif status == "cancelled":
            summary["cancelled"] += 1

    return {"summary": summary}

class Appointment(Document):
    def validate(self):
        self.validate_doctor_availability()

    def validate_doctor_availability(self):
        """
        Prevent appointment booking if doctor is on approved leave
        """
        if not self.doctor or not self.appointment_date:
            return

        # Convert string to date if needed
        appointment_date = self.appointment_date
        if isinstance(appointment_date, str):
            appointment_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()

        # Get approved leaves that overlap with this date
        overlapping_leave = frappe.get_all(
            "Doctor Leave",
            filters={
                "doctor": self.doctor,
                "status": "Approved",
                "leave_start": ("<=", appointment_date),
                "leave_end": (">=", appointment_date)
            },
            fields=["name", "leave_start", "leave_end"]
        )

        if overlapping_leave:
            leave = overlapping_leave[0]
            frappe.throw(
                f"❌ Doctor {self.doctor} is on approved leave "
                f"from {leave.leave_start} to {leave.leave_end}. "
                f"Please select another date or doctor."
            )

@frappe.whitelist(allow_guest=False)
def get_doctors():
    """Fetch all available doctors"""
    doctors = frappe.get_all("Doctor", fields=["name", "full_name", "specialization"])
    return doctors

@frappe.whitelist(allow_guest=False)
def get_patient_appointments(patient=None):
    if not patient:
        patient = frappe.session.user

    appointments = frappe.get_all(
        "Appointment",
        filters={"patient": patient},
        fields=["name", "doctor", "service", "service_status", "appointment_date", "start_time", "end_time"]
    )

    results = []
    for a in appointments:
        doctor_name = frappe.db.get_value("Doctor", a.get("doctor"), "full_name") or a.get("doctor")
        results.append({
            "name": a.get("name"),
            "doctor": a.get("doctor"),
            "doctor_name": doctor_name,
            "service": a.get("service"),
            "status": a.get("service_status"),
            "appointment_date": a.get("appointment_date"),
            "start_time": a.get("start_time"),
            "end_time": a.get("end_time")
        })
    return results

@frappe.whitelist(allow_guest=False)
def get_calendar_events():
    """
    Fetch appointments for the logged-in doctor only,
    including start_time and end_time.
    """
    user = frappe.session.user

    # First try match by email
    doctor = frappe.db.get_value("Doctor", {"email": user}, "name")

    # If no match, try full_name
    if not doctor:
        full_name = frappe.db.get_value("User", user, "full_name")
        doctor = frappe.db.get_value("Doctor", {"full_name": full_name}, "name")

    if not doctor:
        return []

    appointments = frappe.get_all(
        "Appointment",
        filters={"doctor": doctor},
        fields=["name", "patient", "service", "appointment_date", "start_time", "end_time", "status"]
    )

    events = []
    for a in appointments:
        start = f"{a.appointment_date}T{a.start_time}"
        end = f"{a.appointment_date}T{a.end_time}"

        color = "#4B9CD3"  # default
        if a.status == "Completed":
            color = "#81C784"
        elif a.status == "Cancelled":
            color = "#E57373"

        events.append({
            "name": a.name,
            "title": f"{a.patient} - {a.service}",
            "start": start,
            "end": end,
            "color": color
        })

    return events

@frappe.whitelist(allow_guest=False)
def check_availability(doctor, appointment_date, start_time, end_time):
    """Check if a doctor is available at the given time"""
    existing = frappe.db.exists(
        "Appointment",
        {
            "doctor": doctor,
            "appointment_date": appointment_date,
            "start_time": start_time,
            "end_time": end_time,
            "status": ["!=", "Cancelled"]
        }
    )
    if existing:
        return {"available": False, "message": "Doctor is already booked at that time."}
    return {"available": True, "message": "Doctor is available."}

@frappe.whitelist(allow_guest=False)
def get_patient_id_for_user():
    """Maps the logged-in User ID (email/username) to the Patient DocType Name."""
    user_id = frappe.session.user
    
    # 1. Try matching the Patient DocType by the 'Email' field
    # (Since your User ID is likely the email, this is the most reliable link)
    patient_doc_name = frappe.db.get_value("Patient", {"email": user_id}, "name")
    
    # 2. Fallback: Try matching by the 'User' Link field
    if not patient_doc_name and frappe.db.exists("User", user_id):
        patient_doc_name = frappe.db.get_value("Patient", {"user": user_id}, "name")
         
    if not patient_doc_name:
        # Frappe will display this message to the user if no patient record is found
        frappe.throw(f"No Patient record found for the user: {user_id}. Please ensure your Patient DocType's 'Email' field matches your login email.")
        
    return patient_doc_name