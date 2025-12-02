frappe.provide('frappe.pages.patient_portal');

frappe.pages.patient_portal.on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Patient Portal 🩺',
        single_column: true
    });

    // Inject HTML
    $(wrapper).find('.layout-main-section').html(frappe.render_template('patient_portal', {}));

    // Load patient info
    load_patient_info();

    // Setup button click
    $('#load-appointments').on('click', function() {
        load_appointments();
    });
};

function load_patient_info() {
    frappe.call({
        method: "myhealth.myhealth.page.patient_portal.patient_portal.get_patient_info",
        callback: function(r) {
            if (r.message && !r.message.error) {
                $('#patient-info').html(
                    `<strong>${r.message.name}</strong> - ${r.message.email} - ${r.message.phone}`
                );
            } else {
                $('#patient-info').html('Patient info not found');
            }
        }
    });
}

function load_appointments() {
    $('#appointments').html('Loading appointments…');
    frappe.call({
        method: "myhealth.myhealth.api.appointment_api.get_patient_appointments",
        callback: function(r) {
            if (!r.message || r.message.length === 0) {
                $('#appointments').html('<div>No appointments found</div>');
                return;
            }

            const html = r.message.map(a => {
                let status_class = '';
                if (a.status === 'Cancelled') status_class = 'cancelled';
                if (a.status === 'Completed') status_class = 'completed';

                return `
                    <div class="appointment-card ${status_class}">
                        <strong>${a.service}</strong> with <em>${a.doctor_name}</em><br>
                        Date: ${a.appointment_date} | ${a.start_time} - ${a.end_time}<br>
                        Status: ${a.status}
                    </div>
                `;
            }).join('');

            $('#appointments').html(html);
        }
    });
}


