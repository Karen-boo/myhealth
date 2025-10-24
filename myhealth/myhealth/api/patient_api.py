import frappe

@frappe.whitelist(allow_guest=True)
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


@frappe.whitelist(allow_guest=True)
def get_patient(name):
    frappe.set_user('Administrator')
    doc = frappe.get_doc("Patient", name)
    return doc.as_dict()


@frappe.whitelist(allow_guest=True)
def update_patient(name, **kwargs):
    frappe.set_user('Administrator')
    doc = frappe.get_doc("Patient", name)
    for key, value in kwargs.items():
        if key in doc.as_dict():
            doc.set(key, value)
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"message": "Patient updated successfully"}


@frappe.whitelist(allow_guest=True)
def delete_patient(name):
    frappe.set_user('Administrator')
    frappe.delete_doc("Patient", name, ignore_permissions=True)
    frappe.db.commit()
    return {"message": "Patient deleted successfully"}

@frappe.whitelist(allow_guest=True)
def list_patients():
    frappe.set_user('Administrator')
    patients = frappe.get_all("Patient", fields=["name", "first_name", "last_name", "age", "gender", "email"])
    return {"patients": patients}
