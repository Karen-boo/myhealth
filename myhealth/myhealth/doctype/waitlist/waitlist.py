# Copyright (c) 2025, Karen and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Waitlist(Document):
    def validate(self):
        # Automatically mark as Waiting when created
        if not self.status:
            self.status = "Waiting"

