import frappe

@frappe.whitelist()
def get_np_info():
    user = frappe.session.user
    patient = frappe.get_value("Patient", {"user": user}, "name")
    if not patient:
        return {"error": "Patient not found"}

    doc = frappe.get_doc("Patient", patient)
    return {
        "name": doc.full_name,
        "email": doc.email,
        "phone": doc.phone_number
    }
