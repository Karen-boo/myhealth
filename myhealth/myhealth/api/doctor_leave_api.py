import frappe
from datetime import datetime

@frappe.whitelist(allow_guest=False)
def apply_leave(doctor, leave_start, leave_end, leave_reason=None):
    """Doctor applies for leave - creates a new Doctor Leave record"""
    if not frappe.db.exists("Doctor", doctor):
        frappe.throw("Doctor not found")

    # Check if doctor already has overlapping approved leave
    existing = frappe.get_all(
        "Doctor Leave",
        filters={
            "doctor": doctor,
            "status": "Approved",
            "leave_end": (">=", leave_start),
            "leave_start": ("<=", leave_end),
        },
        fields=["name"]
    )

    if existing:
        frappe.throw("Doctor already has approved leave during this period.")

    leave_doc = frappe.get_doc({
        "doctype": "Doctor Leave",
        "doctor": doctor,
        "leave_start": leave_start,
        "leave_end": leave_end,
        "leave_reason": leave_reason,
        "status": "Pending"
    })
    leave_doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "message": "Leave request submitted successfully and pending approval.",
        "leave_id": leave_doc.name
    }


@frappe.whitelist(allow_guest=False)
def approve_leave(leave_id, approved_by=None):
    """Approve a doctor leave and update doctor's status"""
    doc = frappe.get_doc("Doctor Leave", leave_id)
    if doc.status == "Approved":
        frappe.throw("This leave is already approved.")
    
    doc.status = "Approved"
    doc.approved_by = approved_by or frappe.session.user
    doc.save(ignore_permissions=True)

    # Update doctor availability
    doctor = frappe.get_doc("Doctor", doc.doctor)
    doctor.availability_status = "Unavailable"
    doctor.save(ignore_permissions=True)

    frappe.db.commit()
    return {"message": f"Leave approved for {doctor.full_name} from {doc.leave_start} to {doc.leave_end}"}


@frappe.whitelist(allow_guest=False)
def end_leave(leave_id):
    """End leave manually or automatically after leave_end"""
    doc = frappe.get_doc("Doctor Leave", leave_id)
    if doc.status != "Approved":
        frappe.throw("Only approved leaves can be ended.")

    doc.status = "Completed"
    doc.save(ignore_permissions=True)

    doctor = frappe.get_doc("Doctor", doc.doctor)
    doctor.availability_status = "Available"
    doctor.save(ignore_permissions=True)

    frappe.db.commit()
    return {"message": f"{doctor.full_name}'s leave has ended and status is now available."}

def auto_end_expired_leaves():
    today = datetime.now().date()
    expired_leaves = frappe.get_all("Doctor Leave", filters={
        "status": "Approved",
        "leave_end": ("<", today)
    })

    for leave in expired_leaves:
        end_leave(leave.name)