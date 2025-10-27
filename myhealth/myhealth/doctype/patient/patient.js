frappe.ui.form.on('Patient', {
    validate: function(frm) {
        if (frm.doc.age && frm.doc.age <= 0) {
            frappe.throw(__('Age must be greater than zero'));
        }

        if (frm.doc.phone_number && !/^\+?\d{10,15}$/.test(frm.doc.phone_number)) {
            frappe.throw(__('Please enter a valid phone number'));
        }

        if (!frm.doc.first_name || !frm.doc.last_name) {
            frappe.throw(__('First and last name are required'));
        }
    }
});

