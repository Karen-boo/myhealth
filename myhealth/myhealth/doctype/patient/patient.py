import frappe
from frappe.model.document import Document
from datetime import datetime, date   

class Patient(Document):
    
    def validate(self):
        # --- Date of Birth & Age ---
        if self.date_of_birth:
            dob = self._parse_date(self.date_of_birth)

            # Check if DOB is in the future
            if dob > date.today():
                frappe.throw("Date of Birth cannot be in the future")

            # Calculate age
            self.age = self.calculate_age(dob)

        # --- Full Name ---
        if self.first_name and self.last_name:
            self.full_name = f"{self.first_name} {self.last_name}"
        elif self.first_name:
            self.full_name = self.first_name
        else:
            self.full_name = "Unknown"

    def calculate_age(self, dob):
        """Return age in years and months."""
        today = date.today()
        years = today.year - dob.year
        months = today.month - dob.month
        days = today.day - dob.day

        if days < 0:
            months -= 1
            days += 30
        if months < 0:
            years -= 1
            months += 12

        return f"{years} years, {months} months"

    def _parse_date(self, dob):
        """Ensure dob is always a datetime.date object."""
        if isinstance(dob, str):
            return datetime.strptime(dob, "%Y-%m-%d").date()
        return dob
