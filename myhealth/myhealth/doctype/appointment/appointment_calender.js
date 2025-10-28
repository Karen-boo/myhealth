frappe.views.calendar["Appointment"] = {
    field_map: {
        start: "appointment_date",
        end: "appointment_date",
        title: "patient",
        allDay: 1,
        status: "service_status",
    },
    order_by: "appointment_date",
    get_events_method: "myhealth.myhealth.api.appointment_api.get_calendar_events",

    // Optional: Color-code appointments by status
    get_event_color: function(event) {
        if (event.doc.service_status === "Pending") return "orange";
        if (event.doc.service_status === "Completed") return "green";
        if (event.doc.service_status === "Cancelled") return "red";
        return "gray";
    },
};
