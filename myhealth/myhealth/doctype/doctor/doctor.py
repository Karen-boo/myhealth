import frappe
from frappe.model.document import Document


class Doctor(Document):
    def validate(self):
        """
        Keep full_name synced with first_name + last_name
        """
        if self.first_name and self.last_name:
            self.full_name = f"{self.first_name} {self.last_name}"
        elif self.first_name:
            self.full_name = f"{self.first_name}"
        else:
            self.full_name = "Unknown"

