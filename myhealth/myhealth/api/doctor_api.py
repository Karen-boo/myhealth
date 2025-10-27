import frappe

@frappe.whitelist(allow_guest=False)
def create_doctor(first_name, last_name, specialization, email, phone_number, years_of_experience=0, bio="", availability_status="Available"):
    doc = frappe.get_doc({
        "doctype": "Doctor",
        "first_name": first_name,
        "last_name": last_name,
        "specialization": specialization,
        "email": email,
        "phone_number": phone_number,
        "years_of_experience": years_of_experience,
        "bio": bio,
        "availability_status": availability_status
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"message": "Doctor created successfully", "doctor_id": doc.name}


@frappe.whitelist(allow_guest=False)
def get_doctors(specialization=None, availability_status=None):
    filters = {}
    if specialization:
        filters["specialization"] = specialization
    if availability_status:
        filters["availability_status"] = availability_status

    doctors = frappe.get_all(
        "Doctor",
        filters=filters,
        fields=["name", "first_name", "last_name", "specialization", "availability_status", "email", "phone_number"]
    )
    return {"doctors": doctors}


@frappe.whitelist(allow_guest=False)
def update_doctor(name, **kwargs):
    doc = frappe.get_doc("Doctor", name)
    for key, value in kwargs.items():
        if key in doc.as_dict():
            doc.set(key, value)
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"message": "Doctor updated successfully"}


@frappe.whitelist(allow_guest=False)
def deactivate_doctor(name):
    doc = frappe.get_doc("Doctor", name)
    doc.availability_status = "On Leave"
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"message": f"Doctor {name} marked as On Leave"}


@frappe.whitelist(allow_guest=False)
def get_doctor_patients(doctor):
    """Fetch all unique patients associated with a specific doctor"""
    appointments = frappe.get_all(
        "Appointment",
        filters={"doctor": doctor},
        fields=["patient"],
        distinct=True
    )
    patients = []
    for appt in appointments:
        patient = frappe.get_doc("Patient", appt.patient)
        patients.append({
            "patient_id": patient.name,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "gender": patient.gender,
            "age": patient.age,
            "email": patient.email
        })

    return {"doctor": doctor, "patients": patients}
