frappe.pages['patient-portal'].on_page_load = function(wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: '👩‍⚕️ Patient Portal',
        single_column: true
    });

    $(frappe.render_template("patient_portal", {}), page.body);

    // Load doctors dynamically
    function load_doctors() {
        frappe.call({
            method: "myhealth.myhealth.api.patient_api.get_doctors",
            callback: function(r) {
                if (r.message && Array.isArray(r.message)) {
                    let doctorSelect = $("#doctor");
                    doctorSelect.empty();
                    doctorSelect.append('<option value="">--Select--</option>');
                    r.message.forEach(doc => {
                        doctorSelect.append(
                            `<option value="${doc.name}">${doc.doctor_name || doc.name}</option>`
                        );
                    });
                }
            }
        });
    }

    // Event: Book New Appointment
    page.body.on('click', '#book-appointment-btn', function() {
        const doctor = $("#doctor").val();
        const date = $("#appointment_date").val();
        const time = $("#appointment_time").val();
        const service = $("#service").val();

        if (!doctor || !date || !time || !service) {
            frappe.msgprint("Please fill all fields before booking.");
            return;
        }

        frappe.call({
            method: "myhealth.myhealth.api.patient_api.book_appointment",
            args: { patient: frappe.session.user, doctor, appointment_date: date, appointment_time: time, service },
            callback: function(r) {
                if (!r.exc) {
                    frappe.msgprint("Appointment booked successfully!");
                    load_appointments();
                }
            }
        });
    });

    // Load existing appointments
    function load_appointments() {
        frappe.call({
            method: "myhealth.myhealth.api.patient_api.get_patient_appointments",
            args: { patient: frappe.session.user },
            callback: function(r) {
                const body = $("#appointments-body");
                body.empty();

                if (r.message && r.message.length > 0) {
                    r.message.forEach(app => {
                        body.append(`
                            <tr>
                                <td>${app.appointment_date}</td>
                                <td>${app.appointment_time}</td>
                                <td>${app.doctor}</td>
                                <td>${app.status}</td>
                            </tr>
                        `);
                    });
                } else {
                    body.append(`<tr><td colspan="4" class="text-center text-muted">No appointments found</td></tr>`);
                }
            }
        });
    }

    load_doctors();
    load_appointments();
};
