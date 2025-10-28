import frappe

@frappe.whitelist(allow_guest=False)
def create_waitlist(patient, preferred_doctor, preferred_date, notes=None, contact_email=None, priority="Medium"):
    """Add a new patient to the waitlist"""
    doc = frappe.get_doc({
        "doctype": "Waitlist",
        "patient": patient,
        "preferred_doctor": preferred_doctor,
        "preferred_date": preferred_date,
        "notes": notes,
        "contact_email": contact_email,
        "priority": priority,
        "status": "Waiting"
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"message": "Added to waitlist successfully", "waitlist_id": doc.name}


@frappe.whitelist(allow_guest=False)
def get_waitlist(name=None):
    """Fetch specific or all waitlist entries"""
    if name:
        doc = frappe.get_doc("Waitlist", name)
        return doc.as_dict()
    else:
        data = frappe.get_all("Waitlist", fields=["name", "patient", "preferred_doctor", "preferred_date", "status", "priority"])
        return {"waitlist": data}


@frappe.whitelist(allow_guest=False)
def update_waitlist(name, **kwargs):
    """Update waitlist entry"""
    doc = frappe.get_doc("Waitlist", name)
    for key, value in kwargs.items():
        if key in doc.as_dict():
            doc.set(key, value)
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"message": "Waitlist updated successfully"}


@frappe.whitelist(allow_guest=False)
def remove_waitlist(name):
    """Remove patient from waitlist"""
    frappe.delete_doc("Waitlist", name, ignore_permissions=True)
    frappe.db.commit()
    return {"message": "Waitlist entry removed successfully"}
