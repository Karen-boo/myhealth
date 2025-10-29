import frappe

@frappe.whitelist(allow_guest=False)
def create_medical_record(patient, appointment, doctor, record_type, summary, record_details=None, confidential=False):
    """Create new medical record"""
    record = frappe.get_doc({
        "doctype": "Medical Record",
        "patient": patient,
        "appointment": appointment,
        "doctor": doctor,
        "record_type": record_type,
        "summary": summary,
        "confidential": confidential,
        "status": "Active"
    })

    if record_details:
        for detail in record_details:
            record.append("record_details", {
                "parameter": detail.get("parameter"),
                "value": detail.get("value"),
                "unit": detail.get("unit"),
                "notes": detail.get("notes"),
                "added_by": frappe.session.user
            })

    record.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"message": "Medical record created", "record_id": record.name}


@frappe.whitelist(allow_guest=False)
def get_medical_records(patient=None, doctor=None):
    """Retrieve all records for a given patient or doctor"""
    filters = {}
    if patient:
        filters["patient"] = patient
    if doctor:
        filters["doctor"] = doctor

    data = frappe.get_all("Medical Record", filters=filters,
                          fields=["name", "patient", "doctor", "record_type", "record_date", "version", "status"])
    return {"records": data}


@frappe.whitelist(allow_guest=False)
def get_medical_record_details(record_id):
    """Get detailed record info"""
    record = frappe.get_doc("Medical Record", record_id)
    return record.as_dict()
