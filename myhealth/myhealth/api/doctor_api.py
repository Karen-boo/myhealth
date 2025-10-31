import frappe
from frappe.utils import getdate

# ✅ Create a new doctor
@frappe.whitelist(allow_guest=False)
def create_doctor(first_name, last_name, email, specialization=None, qualifications=None, department=None,
                  years_experience=0, phone_number=None, bio=None, availability_status="Available"):
    """Create a new doctor profile"""
    
    if frappe.db.exists("Doctor", {"email": email}):
        frappe.throw(f"Doctor with email {email} already exists")

    doc = frappe.get_doc({
        "doctype": "Doctor",
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "specialization": specialization,
        "qualifications": qualifications,
        "department": department,
        "years_experience": years_experience,
        "phone_number": phone_number,
        "bio": bio,
        "availability_status": availability_status
    })

    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "message": "Doctor created successfully",
        "doctor_id": doc.name
    }


# ✅ Fetch a specific doctor
@frappe.whitelist(allow_guest=False)
def get_doctor(name):
    """Fetch a doctor record by ID"""
    if not frappe.db.exists("Doctor", name):
        frappe.throw(f"Doctor {name} not found")

    doc = frappe.get_doc("Doctor", name)
    return {"doctor": doc.as_dict()}


# ✅ List or search doctors
@frappe.whitelist(allow_guest=False)
def list_doctors(search=None, specialization=None, department=None, availability_status=None):
    """List all doctors, with optional filters"""
    filters = {}

    if search:
        filters["full_name"] = ["like", f"%{search}%"]
    if specialization:
        filters["specialization"] = specialization
    if department:
        filters["department"] = department
    if availability_status:
        filters["availability_status"] = availability_status

    doctors = frappe.get_all(
        "Doctor",
        filters=filters,
        fields=[
            "name", "full_name", "specialization", "department",
            "email", "phone_number", "availability_status",
            "years_experience", "appointments_completed", "average_rating"
        ],
        order_by="full_name asc"
    )

    return {"doctors": doctors}


# ✅ Update a doctor
@frappe.whitelist(allow_guest=False)
def update_doctor(name, **kwargs):
    """Update doctor details dynamically"""
    if not frappe.db.exists("Doctor", name):
        frappe.throw(f"Doctor {name} not found")

    doc = frappe.get_doc("Doctor", name)
    allowed_fields = [
        "first_name", "last_name", "specialization", "qualifications",
        "department", "years_experience", "phone_number", "bio",
        "availability_status", "is_active"
    ]

    for key, value in kwargs.items():
        if key in allowed_fields:
            doc.set(key, value)

    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {"message": "Doctor updated successfully"}


# ✅ Soft-delete (Deactivate doctor)
@frappe.whitelist(allow_guest=False)
def deactivate_doctor(name):
    """Deactivate a doctor (instead of deleting permanently)"""
    if not frappe.db.exists("Doctor", name):
        frappe.throw(f"Doctor {name} not found")

    doc = frappe.get_doc("Doctor", name)
    doc.is_active = 0
    doc.availability_status = "Unavailable"
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {"message": f"Doctor {doc.full_name} has been deactivated"}


# ✅ Reactivate doctor
@frappe.whitelist(allow_guest=False)
def activate_doctor(name):
    """Reactivate a doctor profile"""
    if not frappe.db.exists("Doctor", name):
        frappe.throw(f"Doctor {name} not found")

    doc = frappe.get_doc("Doctor", name)
    doc.is_active = 1
    doc.availability_status = "Available"
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {"message": f"Doctor {doc.full_name} has been reactivated"}


# ✅ Delete permanently (only for admins)
@frappe.whitelist(allow_guest=False)
def delete_doctor(name):
    """Delete doctor permanently (admin only)"""
    if not frappe.has_permission("Doctor", "delete"):
        frappe.throw("You are not allowed to delete doctors")

    if not frappe.db.exists("Doctor", name):
        frappe.throw(f"Doctor {name} not found")

    frappe.delete_doc("Doctor", name, ignore_permissions=True)
    frappe.db.commit()

    return {"message": "Doctor deleted successfully"}

@frappe.whitelist(allow_guest=False)
def get_doctor_schedule(doctor=None):
    """
    Returns combined calendar events (availability, appointments, leave)
    for the doctor dashboard.
    """
    if not doctor:
        doctor = frappe.session.user

    events = []

    # --- 1️⃣ Appointments ---
    appointments = frappe.get_all(
        "Appointment",
        filters={"doctor": doctor},
        fields=["name", "patient", "appointment_date", "status"]
    )

    for a in appointments:
        events.append({
            "title": f"🩺 Appointment: {a.patient}",
            "start": a.appointment_date,
            "color": "#4B9CD3" if a.status == "Confirmed" else "#F9A825",
            "url": f"/app/appointment/{a.name}"
        })

    # --- 2️⃣ Doctor Leave ---
    leaves = frappe.get_all(
        "Doctor Leave",
        filters={"doctor": doctor, "status": "Approved"},
        fields=["leave_start", "leave_end", "reason", "name"]
    )

    for l in leaves:
        events.append({
            "title": f"🏖️ Leave: {l.reason or 'On Leave'}",
            "start": l.leave_start,
            "end": l.leave_end,
            "color": "#E57373",
            "url": f"/app/doctor-leave/{l.name}"
        })

    # --- 3️⃣ Doctor Availability ---
    availabilities = frappe.get_all(
        "Doctor Availability",
        filters={"doctor": doctor},
        fields=["start_time", "end_time", "date", "doctor"]
    )

    for av in availabilities:
        events.append({
            "title": f"✅ Available ({av.day_of_week})",
            "start": av.available_from,
            "end": av.available_to,
            "color": "#81C784",
            "url": f"/app/doctor-availability/{av.name}"
        })

    return events

@frappe.whitelist(allow_guest=False)
def get_doctor_stats(doctor):
    total_appointments = frappe.db.count("Appointment", {"doctor_name": doctor})
    upcoming = frappe.db.count("Appointment", {"doctor_name": doctor, "service_status": "Pending"})
    active_leaves = frappe.db.count("Doctor Leave", {"doctor": doctor, "status": "Approved"})
    patients_seen = frappe.db.count("Appointment", {"doctor_name": doctor, "service_status": "Completed"})

    return {
        "total_appointments": total_appointments,
        "upcoming": upcoming,
        "active_leaves": active_leaves,
        "patients_seen": patients_seen
    }

@frappe.whitelist(allow_guest=True)
def get_doctor(name):
    doctor = frappe.get_doc("Doctor", name)
    return {
        "name": doctor.name,
        "full_name": doctor.full_name,
        "category": doctor.doctor_category,
        "description": doctor.category_description,
        "status": doctor.status
    }