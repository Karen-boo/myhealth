frappe.pages['doctor-dashboard'].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Doctor Dashboard 🩺',
        single_column: true
    });

    // State toggles
    let showAppointments = true;
    let showAvailability = true;
    let showLeave = true;

    // --- STRUCTURE ---
    const html = `
        <div class="doctor-dashboard p-4">
            <div class="text-center mb-4">
                <h2 class="fw-bold">Doctor Dashboard</h2>
                <p class="text-muted">View your schedule, availability, and leave days</p>
            </div>

            <div class="legend mb-3 d-flex justify-content-center flex-wrap gap-2">
                <span class="badge" style="background:#4B9CD3;">🩺 Appointments</span>
                <span class="badge" style="background:#81C784;">✅ Availability</span>
                <span class="badge" style="background:#E57373;">🏖️ Leave</span>
            </div>

            <div class="filters mb-4 text-center">
                <button class="btn btn-outline-primary btn-sm toggle-appointments">🩺 Appointments</button>
                <button class="btn btn-outline-success btn-sm toggle-availability">✅ Availability</button>
                <button class="btn btn-outline-danger btn-sm toggle-leave">🏖️ Leave</button>
                <button class="btn btn-primary btn-sm refresh-calendar">🔄 Refresh</button>
            </div>

            <div id="calendar" class="card shadow-sm p-3" style="border-radius: 12px;"></div>
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
        events: function (start, end, timezone, callback) {
            frappe.call({
                method: "myhealth.myhealth.api.doctor_api.get_doctor_schedule",
                args: { doctor: frappe.session.user },
                callback: function (r) {
                    if (r.message) {
                        let events = r.message.filter(e => {
                            if (e.title.includes('Appointment') && !showAppointments) return false;
                            if (e.title.includes('Available') && !showAvailability) return false;
                            if (e.title.includes('Leave') && !showLeave) return false;
                            return true;
                        });
                        callback(events);
                    }
                }
            });
        },
        eventClick: function (event) {
            if (event.url) {
                frappe.set_route(event.url.replace('/app/', ''));
                return false;
            }
        }
    });

    // --- FILTER ACTIONS ---
    $(wrapper).on('click', '.toggle-appointments', function () {
        showAppointments = !showAppointments;
        $('#calendar').fullCalendar('refetchEvents');
        frappe.show_alert(`🩺 Appointments ${showAppointments ? 'shown' : 'hidden'}`);
    });

    $(wrapper).on('click', '.toggle-availability', function () {
        showAvailability = !showAvailability;
        $('#calendar').fullCalendar('refetchEvents');
        frappe.show_alert(`✅ Availability ${showAvailability ? 'shown' : 'hidden'}`);
    });

    $(wrapper).on('click', '.toggle-leave', function () {
        showLeave = !showLeave;
        $('#calendar').fullCalendar('refetchEvents');
        frappe.show_alert(`🏖️ Leave ${showLeave ? 'shown' : 'hidden'}`);
    });

    $(wrapper).on('click', '.refresh-calendar', function () {
        $('#calendar').fullCalendar('refetchEvents');
        frappe.show_alert("🔄 Calendar refreshed");
    });
};
