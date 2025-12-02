frappe.pages['doctor-dashboard'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Doctor Dashboard 🩺',
        single_column: true
    });

    // HTML structure
    const html = `
        <div class="doctor-dashboard p-4">
            <div class="text-center mb-4">
                <h2 class="fw-bold">Doctor Dashboard</h2>
                <p class="text-muted">View your appointments, availability, and leave days</p>
            </div>

            <div class="legend mb-3 d-flex justify-content-center gap-2">
                <span class="badge" style="background:#4B9CD3;">🩺 Appointments</span>
                <span class="badge" style="background:#81C784;">✅ Availability</span>
                <span class="badge" style="background:#E57373;">🏖️ Leave</span>
            </div>

            <div class="filters mb-3 text-center">
                <button class="btn btn-outline-primary btn-sm navigate-appointments">🩺 Appointments</button>
                <button class="btn btn-outline-success btn-sm navigate-availability">✅ Availability</button>
                <button class="btn btn-outline-danger btn-sm navigate-leave">🏖️ Leave</button>
                <button class="btn btn-primary btn-sm refresh-calendar">🔄 Refresh</button>
            </div>

            <div id="calendar" class="card shadow-sm p-3" style="border-radius:12px;"></div>
        </div>
    `;

    $(wrapper).find('.layout-main-section').html(html);

    // --- FULLCALENDAR INIT ---
    $('#calendar').fullCalendar({
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,agendaWeek,agendaDay'
        },
        height: 700,
        weekends: true,
        events: function(start, end, timezone, callback) {
            frappe.call({
                method: "myhealth.myhealth.api.appointment_api.get_calendar_events",
                args: {},
                callback: function(r) {
                    if (!r.message) {
                        callback([]);
                        return;
                    }

                    let events = r.message.map(e => {
                        // Color based on status
                        let color = "#4B9CD3"; // default: appointment
                        if (e.status === "Completed") color = "#81C784";
                        else if (e.status === "Cancelled") color = "#E57373";

                        return {
                            title: e.title,
                            start: e.start,
                            end: e.end,
                            color: color,
                            url: `/app/Appointment/${e.name}`
                        };
                    });

                    callback(events);
                }
            });
        },
        eventClick: function(event) {
            if (event.url) {
                frappe.set_route(event.url.replace('/app/', ''));
                return false;
            }
        },
        dayRender: function(date, cell) {
            // Highlight today
            const today = moment().format('YYYY-MM-DD');
            if (date.format('YYYY-MM-DD') === today) {
                cell.css('background-color', '#FFF3E0');
            }
            // Highlight weekends
            if (date.day() === 0 || date.day() === 6) {
                cell.css('background-color', '#F0F0F0');
            }
        }
    });

    // --- BUTTON NAVIGATION ---
    $(wrapper).on('click', '.navigate-appointments', function() {
        frappe.set_route('List', 'Appointment', { doctor: frappe.session.user });
    });
    $(wrapper).on('click', '.navigate-availability', function() {
        frappe.set_route('List', 'Doctor Availability', { doctor: frappe.session.user });
    });
    $(wrapper).on('click', '.navigate-leave', function() {
        frappe.set_route('List', 'Doctor Leave', { doctor: frappe.session.user });
    });
    $(wrapper).on('click', '.refresh-calendar', function() {
        $('#calendar').fullCalendar('refetchEvents');
        frappe.show_alert("🔄 Calendar refreshed");
    });
};

