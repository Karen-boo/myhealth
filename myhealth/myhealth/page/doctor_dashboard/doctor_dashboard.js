frappe.pages['doctor-dashboard'].on_page_load = function(wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Doctor Dashboard',
        single_column: true
    });

    // --- FILTER STATE ---
    let showAppointments = true;
    let showAvailability = true;
    let showLeave = true;

    // --- LEGEND ---
    const legend = `
        <div style="margin-bottom: 10px;">
            <span style="background:#4B9CD3; color:white; padding:4px 8px; border-radius:4px;">🩺 Appointments</span>
            <span style="background:#81C784; color:white; padding:4px 8px; border-radius:4px;">✅ Availability</span>
            <span style="background:#E57373; color:white; padding:4px 8px; border-radius:4px;">🏖️ Leave</span>
        </div>
    `;

    // --- FILTER BUTTONS ---
    const filterBar = `
        <div class="flex gap-2 mb-2">
            <button class="btn btn-default btn-sm toggle-appointments">🩺 Appointments</button>
            <button class="btn btn-default btn-sm toggle-availability">✅ Availability</button>
            <button class="btn btn-default btn-sm toggle-leave">🏖️ Leave</button>
            <button class="btn btn-primary btn-sm refresh-calendar">🔄 Refresh</button>
        </div>
    `;

    $(wrapper).find('.layout-main-section').append(legend + filterBar + '<div id="calendar"></div>');

    // --- CALENDAR INITIALIZATION ---
    $('#calendar').fullCalendar({
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,agendaWeek,agendaDay'
        },
        height: 700,
        events: function(start, end, timezone, callback) {
            frappe.call({
                method: "myhealth.myhealth.api.doctor_api.get_doctor_schedule",
                args: { doctor: frappe.session.user },
                callback: function(r) {
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
        eventClick: function(event) {
            if (event.url) {
                frappe.set_route(event.url.replace('/app/', ''));
                return false;
            }
        }
    });

    // --- BUTTON EVENT LISTENERS ---
    $(wrapper).on('click', '.toggle-appointments', function() {
        showAppointments = !showAppointments;
        $('#calendar').fullCalendar('refetchEvents');
        frappe.show_alert(`Appointments ${showAppointments ? 'shown' : 'hidden'}`);
    });

    $(wrapper).on('click', '.toggle-availability', function() {
        showAvailability = !showAvailability;
        $('#calendar').fullCalendar('refetchEvents');
        frappe.show_alert(`Availability ${showAvailability ? 'shown' : 'hidden'}`);
    });

    $(wrapper).on('click', '.toggle-leave', function() {
        showLeave = !showLeave;
        $('#calendar').fullCalendar('refetchEvents');
        frappe.show_alert(`Leave ${showLeave ? 'shown' : 'hidden'}`);
    });

    $(wrapper).on('click', '.refresh-calendar', function() {
        $('#calendar').fullCalendar('refetchEvents');
        frappe.show_alert("Calendar refreshed 🔄");
    });
};

