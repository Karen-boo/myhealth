frappe.pages["patient-portal"].on_page_load = function (wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: "👩‍⚕️ Patient Portal",
    single_column: true,
  });

  $(page.body).html(frappe.render_template("patient_portal", {}));

  // Set footer year
  document.getElementById("footer-year").textContent = new Date().getFullYear();

  // Load doctors
  function load_doctors() {
    frappe.call({
      method: "myhealth.myhealth.api.patient_api.get_doctors",
      callback: function (r) {
        const doctorSelect = $("#doctor");
        doctorSelect.empty().append('<option value="">-- Select Doctor --</option>');
        (r.message || []).forEach((doc) => {
          doctorSelect.append(
            `<option value="${doc.name}">${doc.doctor_name || doc.name}</option>`
          );
        });
      },
    });
  }

  // Load appointments
  function load_appointments() {
    frappe.call({
      method: "myhealth.myhealth.api.patient_api.get_patient_appointments",
      args: { patient: frappe.session.user },
      callback: function (r) {
        const body = $("#appointments-body");
        body.empty();

        if (r.message && r.message.length > 0) {
          r.message.forEach((app) => {
            const statusColor =
              app.status === "Confirmed"
                ? "text-success"
                : app.status === "Pending"
                ? "text-warning"
                : "text-danger";

            body.append(`
              <tr>
                <td>${app.appointment_date}</td>
                <td>${app.appointment_time}</td>
                <td>${app.doctor}</td>
                <td class="${statusColor} fw-bold">${app.status}</td>
              </tr>
            `);
          });
        } else {
          body.append(
            `<tr><td colspan="4" class="text-center text-muted py-3">No appointments found</td></tr>`
          );
        }
      },
    });
  }

  // Book appointment
  page.body.on("click", "#book-appointment-btn", function () {
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
      args: {
        patient: frappe.session.user,
        doctor,
        appointment_date: date,
        appointment_time: time,
        service,
      },
      callback: function (r) {
        if (!r.exc) {
          frappe.msgprint("✅ Appointment booked successfully!");
          $("#appointment-form")[0].reset();
          load_appointments();
        }
      },
    });
  });

  // Initialize
  load_doctors();
  load_appointments();
};
