# Copyright (c) 2025, Karen and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days, nowdate


class Appointment(Document):
    def validate(self):
        """Prevent double booking for the same doctor/time slot"""
        conflict = frappe.db.exists(
            "Appointment",
            {
                "doctor": self.doctor,
                "appointment_date": self.appointment_date,
                "start_time": self.start_time,
                "end_time": self.end_time,
                "status": ["!=", "Cancelled"],
                "name": ["!=", self.name],
            },
        )

        if conflict:
            frappe.throw(
                f"Doctor {self.doctor} already has another appointment at this time."
            )

    def on_submit(self):
        """Send confirmation email after appointment submission"""
        if not getattr(self, "confirmation_sent", 0):
            frappe.sendmail(
                recipients=self.patient_email,
                subject=f"Appointment Confirmation with Dr. {self.doctor_name}",
                message=f"Your appointment on {self.appointment_date} at {self.start_time} has been confirmed.",
            )
            self.confirmation_sent = 1
            self.db_set("confirmation_sent", 1)

    def on_cancel(self):
        """When appointment is cancelled, check for waitlisted patients"""
        waitlisted = frappe.get_all(
            "Waitlist",
            filters={
                "preferred_doctor": self.doctor,
                "preferred_date": self.appointment_date,
                "status": "Waiting",
            },
            fields=["name", "patient", "contact_email"],
        )

        if waitlisted:
            next_patient = waitlisted[0]
            frappe.sendmail(
                recipients=next_patient.contact_email,
                subject=f"Appointment Slot Available for Dr. {self.doctor}",
                message=f"Hi, a slot just opened for your preferred date with Dr. {self.doctor}. Please confirm your booking soon.",
            )
            frappe.db.set_value("Waitlist", next_patient.name, "status", "Converted")


def send_appointment_reminders():
    """Send reminders for tomorrow's appointments"""
    tomorrow = add_days(nowdate(), 1)
    appointments = frappe.get_all(
        "Appointment",
        filters={"appointment_date": tomorrow, "reminder_sent": 0, "status": "Scheduled"},
        fields=[
            "name",
            "patient_email",
            "doctor_name",
            "appointment_date",
            "start_time",
            "end_time",
        ],
    )

    for appt in appointments:
        frappe.sendmail(
            recipients=appt.patient_email,
            subject=f"Reminder: Appointment with Dr. {appt.doctor_name} Tomorrow",
            message=f"Reminder: You have an appointment on {appt.appointment_date} at {appt.start_time}.",
        )
        frappe.db.set_value("Appointment", appt.name, "reminder_sent", 1)


def create_recurring_appointments():
    """Auto-create next occurrence for recurring appointments"""
    rec = frappe.get_all("Appointment", filters={"is_recurring": 1}, fields=["*"])
    for r in rec:
        new_date = add_days(r.appointment_date, int(r.recurrence_interval))
        frappe.get_doc({
            "doctype": "Appointment",
            "patient": r.patient,
            "doctor": r.doctor,
            "appointment_date": new_date,
            "start_time": r.start_time,
            "end_time": r.end_time,
            "service": r.service,
            "status": "Scheduled",
        }).insert(ignore_permissions=True)
