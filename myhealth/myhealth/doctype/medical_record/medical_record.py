import frappe
from frappe.model.document import Document

class MedicalRecord(Document):
    def before_insert(self):
        # Auto-assign version number
        self.version = 1

    def before_save(self):
        # Versioning logic
        if not self.is_new():
            current_version = frappe.db.get_value("Medical Record", self.name, "version")
            self.version = (current_version or 1) + 1

    def validate(self):
        if self.confidential and not frappe.session.user == self.doctor:
            frappe.msgprint("⚠️ Confidential record: Access restricted to assigned doctor only.")
