frappe.pages['doctor-leave'].on_page_load = function (wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: '🏖️ Doctor Leave',
    single_column: true
  });

  $(page.body).html(frappe.render_template("doctor_leave", {}));

  let calendar; // FullCalendar instance

  // --- Initialize Calendar ---
  function render_calendar(events) {
    const calendarEl = document.getElementById('leave-calendar');
    if (!calendarEl) return;

    if (calendar) {
      calendar.destroy(); // re-render safely
    }

    calendar = new FullCalendar.Calendar(calendarEl, {
      initialView: 'dayGridMonth',
      height: 500,
      headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: ''
      },
      events: events,
    });

    calendar.render();
  }

  // --- Load Leave History ---
  function load_leave_history() {
    frappe.call({
      method: "myhealth.myhealth.api.doctor_leave_api.get_doctor_leaves",
      args: { doctor: frappe.session.user },
      callback: function (r) {
        const body = $("#leave-history-body");
        body.empty();

        let approved_events = [];

        if (r.message && r.message.length > 0) {
          r.message.forEach(leave => {
            const statusBadge = {
              "Pending": "warning",
              "Approved": "success",
              "Rejected": "danger"
            }[leave.status] || "secondary";

            body.append(`
              <tr>
                <td>${leave.from_date}</td>
                <td>${leave.to_date}</td>
                <td>${leave.reason || "-"}</td>
                <td><span class="badge bg-${statusBadge}">${leave.status}</span></td>
              </tr>
            `);

            // Only approved leaves go to calendar
            if (leave.status === "Approved") {
              approved_events.push({
                title: `Leave (${leave.reason || 'No reason'})`,
                start: leave.from_date,
                end: leave.to_date,
                color: "#81C784"
              });
            }
          });
        } else {
          body.append(`<tr><td colspan="4" class="text-center text-muted py-3">No leave records found</td></tr>`);
        }

        // Render approved leaves calendar
        render_calendar(approved_events);
      }
    });
  }

  // --- Apply Leave ---
  page.body.on("click", "#apply-leave-btn", function () {
    const from_date = $("#from_date").val();
    const to_date = $("#to_date").val();
    const reason = $("#reason").val();

    if (!from_date || !to_date || !reason) {
      frappe.msgprint("Please fill all fields before applying for leave.");
      return;
    }

    frappe.call({
      method: "myhealth.myhealth.api.doctor_leave_api.apply_leave",
      args: {
        doctor: frappe.session.user,
        from_date,
        to_date,
        reason
      },
      callback: function (r) {
        if (!r.exc) {
          frappe.msgprint("Leave application submitted successfully!");
          $("#leave-form")[0].reset();
          load_leave_history();
        }
      }
    });
  });

  // --- Initialize ---
  load_leave_history();
};
