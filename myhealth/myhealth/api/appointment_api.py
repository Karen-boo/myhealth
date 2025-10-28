import frappe
from frappe.model.document import Document
from datetime import datetime
from frappe.utils import add_days, nowdate

# CREATE Appointment
@frappe.whitelist(allow_guest=False)
def create_appointment(patient, doctor, service, appointment_date, appointment_time, notes=None):
    """Create a new appointment (with double-booking prevention)"""
    
    # Check if doctor is already booked at that date and time
    existing = frappe.get_all(
        "Appointment",
        filters={
            "doctor": doctor,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "service_status": ["!=", "Cancelled"]
        },
        fields=["name", "service_status"]
    )

    if existing:
        frappe.throw(f"Doctor already has an appointment at {appointment_date} {appointment_time}")

    # Otherwise, create new appointment
    doc = frappe.get_doc({
        "doctype": "Appointment",
        "patient": patient,
        "doctor": doctor,
        "service": service,
        "service_status": "Pending",
        "appointment_date": appointment_date,
        "appointment_time": appointment_time,
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
                "appointment_date", "appointment_time", "notes"]
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
def get_calendar_events(start, end):
    """
    Fetch appointments between start and end date.
    If the logged-in user is a Doctor, show only their appointments.
    """
    user = frappe.session.user

    # Check if the user is linked to a Doctor profile
    doctor = frappe.db.get_value("Doctor", {"user_id": user}, "name")

    filters = {"appointment_date": ["between", [start, end]]}

    # If the user is a doctor, filter by their name
    if doctor:
        filters["doctor_name"] = doctor

    appointments = frappe.get_all(
        "Appointment",
        filters=filters,
        fields=[
            "name",
            "patient",
            "doctor_name",
            "service",
            "service_status",
            "appointment_date",
            "appointment_time"
        ]
    )

    events = []
    for a in appointments:
        events.append({
            "name": a.name,
            "title": f"{a.patient} - {a.service}",
            "start": f"{a.appointment_date}T{a.appointment_time}",
            "doc": a
        })

    return events

@frappe.whitelist(allow_guest=False)
def check_availability(doctor, appointment_date, appointment_time):
    """Check if a doctor is available at the given time"""
    existing = frappe.db.exists(
        "Appointment",
        {
            "doctor": doctor,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "status": ["!=", "Cancelled"]
        }
    )
    if existing:
        return {"available": False, "message": "Doctor is already booked at that time."}
    return {"available": True, "message": "Doctor is available."}

