import frappe

@frappe.whitelist()
def get_patient_info():
    user = frappe.session.user
    patient_name = frappe.get_value("Patient", {"user_id": user}, "name")
    if not patient_name:
        return {"error": "No patient found"}
    doc = frappe.get_doc("Patient", patient_name)
    return {"name": doc.patient_name, "email": doc.email, "phone": doc.mobile_no}

