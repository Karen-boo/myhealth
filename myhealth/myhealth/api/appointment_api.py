import frappe
from frappe import _

# ✅ Create Appointment
@frappe.whitelist(allow_guest=False)
def create_appointment(patient, doctor_name, service, appointment_date, appointment_time, notes=None):
    try:
        doc = frappe.get_doc({
            "doctype": "Appointment",
            "patient": patient,
            "doctor_name": doctor_name,
            "service": service,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "service_status": "Pending",
            "notes": notes
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return {"message": "Appointment created successfully", "appointment_id": doc.name}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create Appointment Error")
        frappe.throw(_("Failed to create appointment: {0}").format(str(e)))


# ✅ Fetch Appointments
@frappe.whitelist(allow_guest=False)
def get_appointments(patient=None):
    filters = {}
    if patient:
        filters["patient"] = patient

    appointments = frappe.get_all(
        "Appointment",
        filters=filters,
        fields=[
            "name", "patient", "doctor_name", "service",
            "service_status", "appointment_date", "appointment_time", "notes"
        ]
    )
    return {"appointments": appointments}


# ✅ Update Appointment
@frappe.whitelist(allow_guest=False)
def update_appointment(name, service_status=None, notes=None):
    try:
        doc = frappe.get_doc("Appointment", name)
        if service_status:
            doc.service_status = service_status
        if notes:
            doc.notes = notes
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        return {"message": "Appointment updated successfully"}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Update Appointment Error")
        frappe.throw(_("Failed to update appointment: {0}").format(str(e)))
