import frappe

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
