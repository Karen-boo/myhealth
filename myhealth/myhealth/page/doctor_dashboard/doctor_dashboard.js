frappe.pages['doctor-dashboard'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Doctor Dashboard 🩺',
        single_column: true
    });

    // --- DASHBOARD HEADER ---
    const header = `
        <div class="flex justify-between items-center mb-4">
            <div>
                <h2 class="text-xl font-semibold">Welcome, Dr. ${frappe.session.user_fullname}</h2>
                <p class="text-sm text-gray-600">Your current overview and schedule</p>
            </div>
            <button class="btn btn-primary refresh-btn">🔄 Refresh</button>
        </div>
    `;

    // --- STATS CARDS ---
    const statsCards = `
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div class="card shadow p-4 bg-blue-100">
                <h4 class="font-bold text-blue-800">Total Appointments</h4>
                <p class="text-2xl" id="total_appointments">0</p>
            </div>
            <div class="card shadow p-4 bg-green-100">
                <h4 class="font-bold text-green-800">Upcoming</h4>
                <p class="text-2xl" id="upcoming_appointments">0</p>
            </div>
            <div class="card shadow p-4 bg-yellow-100">
                <h4 class="font-bold text-yellow-800">Active Leaves</h4>
                <p class="text-2xl" id="active_leaves">0</p>
            </div>
            <div class="card shadow p-4 bg-purple-100">
                <h4 class="font-bold text-purple-800">Patients Seen</h4>
                <p class="text-2xl" id="patients_seen">0</p>
            </div>
        </div>
    `;

    // --- CALENDAR ---
    const calendarContainer = `<div id="calendar"></div>`;

    $(wrapper).find('.layout-main-section').html(header + statsCards + calendarContainer);

    // --- CALENDAR SETUP ---
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
                        callback(r.message);
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

    // --- LOAD STATS FUNCTION ---
    function load_stats() {
        frappe.call({
            method: "myhealth.myhealth.api.doctor_api.get_doctor_stats",
            args: { doctor: frappe.session.user },
            callback: function(r) {
                if (r.message) {
                    $("#total_appointments").text(r.message.total_appointments);
                    $("#upcoming_appointments").text(r.message.upcoming);
                    $("#active_leaves").text(r.message.active_leaves);
                    $("#patients_seen").text(r.message.patients_seen);
                }
            }
        });
    }

    // --- REFRESH EVENTS ---
    $('.refresh-btn').on('click', function() {
        $('#calendar').fullCalendar('refetchEvents');
        load_stats();
        frappe.show_alert("Dashboard refreshed 🔄");
    });

    // Auto-refresh every 60 seconds
    setInterval(() => {
        $('#calendar').fullCalendar('refetchEvents');
        load_stats();
    }, 60000);

    // Initial load
    load_stats();
};

