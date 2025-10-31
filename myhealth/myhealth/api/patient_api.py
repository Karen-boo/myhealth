import frappe
from frappe.utils import now_datetime

@frappe.whitelist(allow_guest=False)
def create_patient(first_name, last_name, age, gender, email):
    # temporarily disable permission check
    frappe.set_user('Administrator')
    doc = frappe.get_doc({
        "doctype": "Patient",
        "first_name": first_name,
        "last_name": last_name,
        "age": age,
        "gender": gender,
        "email": email
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"message": "Patient created successfully", "patient_name": doc.name}


@frappe.whitelist(allow_guest=False)
def get_patient(name):
    frappe.set_user('Administrator')
    doc = frappe.get_doc("Patient", name)
    return doc.as_dict()


@frappe.whitelist(allow_guest=False)
def update_patient(name, **kwargs):
    frappe.set_user('Administrator')
    doc = frappe.get_doc("Patient", name)
    for key, value in kwargs.items():
        if key in doc.as_dict():
            doc.set(key, value)
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"message": "Patient updated successfully"}


@frappe.whitelist(allow_guest=False)
def delete_patient(name):
    frappe.set_user('Administrator')
    frappe.delete_doc("Patient", name, ignore_permissions=True)
    frappe.db.commit()
    return {"message": "Patient deleted successfully"}

@frappe.whitelist(allow_guest=False)
def list_patients():
    frappe.set_user('Administrator')
    patients = frappe.get_all("Patient", fields=["name", "first_name", "last_name", "age", "gender", "email"])
    return {"patients": patients}

@frappe.whitelist(allow_guest=False)
def upload_patient_files(patient, id_document=None, insurance_card=None):
    """Attach ID and Insurance files to patient"""
    doc = frappe.get_doc("Patient", patient)

    if id_document:
        doc.id_document = id_document
    if insurance_card:
        doc.insurance_card = insurance_card

    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {"message": "Files uploaded successfully"}

@frappe.whitelist(allow_guest=False)
def get_patient_history(patient):
    """Return a patient's appointments and related info"""
    appointments = frappe.get_all(
        "Appointment",
        filters={"patient": patient},
        fields=[
            "name", "doctor", "service", "appointment_date", "service_status", "notes"
        ]
    )
    return {"patient": patient, "appointments": appointments}


@frappe.whitelist(allow_guest=False)
def get_patient_doctors(patient):
    """Fetch all doctors a patient has had appointments with"""
    appointments = frappe.get_all(
        "Appointment",
        filters={"patient": patient},
        fields=["doctor"],
        distinct=True
    )

    doctors = []
    for appt in appointments:
        doctor = frappe.get_doc("Doctor", appt.doctor)
        doctors.append({
            "doctor_id": doctor.name,
            "first_name": doctor.first_name,
            "last_name": doctor.last_name,
            "specialization": doctor.specialization,
            "availability_status": doctor.availability_status,
            "email": doctor.email
        })

    return {"patient": patient, "doctors": doctors}

@frappe.whitelist()
def get_patient_appointments(patient=None):
    """Return list of appointments for a given patient or logged-in user"""
    user = frappe.session.user
    if not patient:
        patient = frappe.db.get_value("Patient", {"user": user}, "name")
        if not patient:
            frappe.throw(f"No Patient profile found for user: {user}")

    appointments = frappe.get_all(
        "Appointment",
        filters={"patient": patient},
        fields=[
            "name",
            "appointment_date",
            "appointment_time",
            "doctor",
            "service",
            "status"
        ],
        order_by="appointment_date desc"
    )
    return appointments

@frappe.whitelist()
def cancel_appointment(appointment_id):
    """Cancel appointment by ID"""
    if not frappe.has_permission("Appointment", "cancel"):
        frappe.throw("Not permitted to cancel this appointment.")

    appt = frappe.get_doc("Appointment", appointment_id)
    appt.status = "Cancelled"
    appt.save(ignore_permissions=True)
    frappe.db.commit()

    return {"message": f"Appointment {appointment_id} has been cancelled."}

@frappe.whitelist()
def book_appointment(patient, doctor, appointment_date, appointment_time, service=None):
    """Book a new appointment"""
    appt = frappe.get_doc({
        "doctype": "Appointment",
        "patient": patient,
        "doctor": doctor,
        "appointment_date": appointment_date,
        "appointment_time": appointment_time,
        "service": service,
        "status": "Scheduled"
    })
    appt.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"message": "Appointment booked successfully!"}

@frappe.whitelist(allow_guest=False)
def book_appointment(patient=None, doctor=None, appointment_date=None, appointment_time=None, service=None):
    """Book a new appointment for the logged-in user"""

    if not (patient and doctor and appointment_date and appointment_time and service):
        frappe.throw("All fields are required to book an appointment.")

    # Get Patient linked to user (if exists)
    patient_doc = frappe.db.get_value("Patient", {"user": patient}, "name")
    if not patient_doc:
        frappe.throw("No Patient profile found for this user. Please create one first.")

    # Create appointment document
    appointment = frappe.get_doc({
        "doctype": "Appointment",
        "patient": patient_doc,
        "doctor": doctor,
        "appointment_date": appointment_date,
        "appointment_time": appointment_time,
        "service": service,
        "status": "Scheduled",
        "creation": now_datetime(),
    })
    appointment.insert(ignore_permissions=True)
    frappe.db.commit()

    return {"message": "Appointment booked successfully", "appointment_id": appointment.name}

def create_patient_on_user_signup(doc, method):
    """Automatically create a Patient record when a new User is added."""
    # Avoid duplicates
    if frappe.db.exists("Patient", {"user": doc.name}):
        return

    # Create new Patient
    patient = frappe.get_doc({
        "doctype": "Patient",
        "first_name": doc.first_name or doc.full_name or doc.name,
        "email": doc.email,
        "user": doc.name
    })
    patient.insert(ignore_permissions=True)
    frappe.db.commit()
    frappe.logger().info(f"✅ Auto-created Patient for user: {doc.name}")


@frappe.whitelist()
def get_doctors():
    """Return a list of all doctors"""
    doctors = frappe.get_all("Doctor", fields=["name", "full_name"])
    return doctors
