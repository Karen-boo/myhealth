// Global object to hold patient page logic and state
let myHealthPatientPortal = {};

frappe.pages['new_patient'].on_page_load = function(wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Patient Health Portal',
        single_column: true
    });

    const container = $(page.main);
    myHealthPatientPortal.container = container;
    myHealthPatientPortal.page = page;

    myHealthPatientPortal.goHome = function() {
        this.page.set_title("Patient Health Portal");
        this.welcomeView();
    };

    // --- CRUCIAL: Function to securely get the Patient DocType ID (PAT-xxxx) ---
    myHealthPatientPortal.getPatientId = function(callback) {
        if (myHealthPatientPortal.patient_id) {
            callback(myHealthPatientPortal.patient_id);
            return;
        }

        frappe.call({
            method: "myhealth.myhealth.api.appointment_api.get_patient_id_for_user",
            callback: function(r) {
                if (r.message) {
                    myHealthPatientPortal.patient_id = r.message;
                    callback(r.message);
                } else {
                    frappe.throw("Could not find Patient record for the logged-in user. Please contact support.");
                }
            },
            error: function() {
                 frappe.throw("Error fetching Patient ID. Please check API logs.");
            }
        });
    };

    // Initialize the view only after attempting to fetch Patient ID
    myHealthPatientPortal.getPatientId(() => {
        myHealthPatientPortal.welcomeView();
    });
};

// --- STYLE BLOCK ---
myHealthPatientPortal.styles = `
/* --- Professional Dashboard Styling --- */
.dashboard-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px 0;
}
.app-card {
    background: #ffffff;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    margin-bottom: 20px;
    padding: 20px;
    border: 1px solid #f0f0f0;
}
.card-header-main {
    font-size: 1.5em;
    font-weight: 600;
    color: #007bff; /* Primary Brand Color */
    margin-bottom: 15px;
}
.appointment-detail {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-left: 3px solid #007bff;
    padding: 10px 15px 10px 15px;
    margin-bottom: 10px;
    transition: background-color 0.2s;
}
.appointment-detail:hover {
    background-color: #f8f9fa;
}
.appt-date {
    font-size: 1.1em;
    font-weight: 600;
    color: #333;
}
.appt-doctor {
    font-size: 0.9em;
    color: #6c757d;
}
.status-indicator {
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 0.8em;
    font-weight: 700;
    color: white;
}
.status-Pending { background-color: #ffc107; } /* Yellow/Amber */
.status-Completed { background-color: #28a745; } /* Green */
.status-Cancelled { background-color: #dc3545; } /* Red */
.btn-back {
    color: #6c757d;
    font-weight: 600;
    transition: color 0.2s;
}
.btn-back:hover {
    color: #007bff;
}
`;
// --- END STYLE BLOCK ---


// --- HELPER FUNCTIONS ---

// Helper function to load summary data for the Welcome view
myHealthPatientPortal.loadQuickSummary = function(element) {
    frappe.call({
        method: "myhealth.myhealth.api.appointment_api.get_appointment_summary",
        callback: function(r) {
            if(r.message) {
                const s = r.message.summary;
                element.innerHTML = `
                    <div class="row text-center">
                        <div class="col">
                            <h4 class="text-primary">${s.total_appointments}</h4>
                            <p class="text-muted">Total</p>
                        </div>
                        <div class="col">
                            <h4 class="text-warning">${s.pending}</h4>
                            <p class="text-muted">Pending</p>
                        </div>
                        <div class="col">
                            <h4 class="text-success">${s.completed}</h4>
                            <p class="text-muted">Completed</p>
                        </div>
                    </div>
                `;
            }
        }
    });
};

// Helper function to render a single appointment item
myHealthPatientPortal.renderAppointmentItem = function(appt) {
    const statusClass = 'status-' + appt.status;
    // Format time and date nicely
    const timeDisplay = frappe.datetime.str_to_user(appt.start_time).substring(0, 5);
    const dateDisplay = frappe.datetime.str_to_user(appt.appointment_date);

    return `
        <div class="appointment-detail">
            <div>
                <div class="appt-date">🗓️ ${dateDisplay} at ${timeDisplay}</div>
                <div class="appt-doctor">👨‍⚕️ ${appt.service} with Dr. ${appt.doctor_name}</div>
            </div>
            <span class="status-indicator ${statusClass}">${appt.status}</span>
        </div>
    `;
};


// --- VIEW FUNCTIONS ---

// 1. Welcome / Landing Page View
myHealthPatientPortal.welcomeView = function() {
    const patientFullName = frappe.session.user_fullname || frappe.session.user;

    this.container.html(`
        <style>${myHealthPatientPortal.styles}</style>
        <div class="dashboard-container text-center py-5">
            <h1 class="text-primary mb-2">Welcome, ${patientFullName} 👋</h1>
            <p class="text-muted mb-5">Your secure dashboard for managing health appointments.</p>
            
            <div class="row justify-content-center">
                <div class="col-md-6 mb-3">
                    <button type="button" class="btn btn-primary btn-lg w-100 py-3" id="go-book-appointment">
                        <i class="fa fa-calendar-plus-o mr-2"></i> Book New Appointment
                    </button>
                </div>
                <div class="col-md-6 mb-3">
                    <button type="button" class="btn btn-outline-primary btn-lg w-100 py-3" id="go-view-appointments">
                        <i class="fa fa-list-alt mr-2"></i> View My Appointments
                    </button>
                </div>
            </div>
            
            <div class="app-card mt-5 text-left">
                <div class="card-header-main">Quick Health Snapshot</div>
                <div id="quick-summary-placeholder">
                    <p class="text-muted">Loading...</p>
                </div>
            </div>
        </div>
    `);
    
    // Attach event listeners
    this.container.find("#go-book-appointment").on('click', () => {
        this.page.set_title("New Appointment Booking");
        this.bookAppointmentView();
    });

    this.container.find("#go-view-appointments").on('click', () => {
        this.page.set_title("Your Appointments");
        this.viewAppointmentsView();
    });
    
    this.loadQuickSummary(this.container.find("#quick-summary-placeholder")[0]);
};


// 2. Book Appointment Page View
myHealthPatientPortal.bookAppointmentView = function() {
    this.container.html(`
        <style>${myHealthPatientPortal.styles}</style>
        <div class="dashboard-container">
            <button class="btn btn-link btn-back mb-4" id="go-home"><i class="fa fa-arrow-left mr-1"></i> Back to Dashboard</button>

            <div class="app-card col-md-8 mx-auto">
                <div class="card-header-main"><i class="fa fa-stethoscope mr-2"></i> Schedule Appointment</div>
                
                <div class="form-group mb-3">
                    <label for="doctor-dropdown">Doctor</label>
                    <select id="doctor-dropdown" class="form-control"></select>
                </div>

                <div class="form-group mb-3">
                    <label for="service-dropdown">Reason / Service</label>
                    <select id="service-dropdown" class="form-control">
                        <option value="Follow-up">Follow-up</option>
                        <option value="Treatment">Treatment</option>
                        <option value="Emergency">Emergency</option>
                        <option value="Consultation">Consultation</option>
                    </select>
                </div>

                <div class="row">
                    <div class="col-12 form-group">
                        <label for="appointment-date">Date</label>
                        <input type="date" id="appointment-date" class="form-control">
                    </div>
                    <div class="col-6 form-group">
                        <label for="start-time">Start Time</label>
                        <input type="time" id="start-time" class="form-control">
                    </div>
                    <div class="col-6 form-group">
                        <label for="end-time">End Time</label>
                        <input type="time" id="end-time" class="form-control">
                    </div>
                </div>
                
                <div class="form-group mb-4">
                    <label for="notes">Notes</label>
                    <textarea id="notes" class="form-control" rows="3" placeholder="Symptoms, requests, or special notes for your doctor"></textarea>
                </div>

                <button class="btn btn-primary btn-block btn-lg" id="book-btn">Confirm Booking</button>
            </div>
        </div>
    `);

    this.container.find("#go-home").on('click', () => this.goHome());
    const doctorDropdown = this.container.find("#doctor-dropdown")[0];
    const bookBtn = this.container.find("#book-btn")[0];

    // Load available doctors
    frappe.call({
        method: "myhealth.myhealth.api.appointment_api.get_doctors",
        callback: function(r) {
            if(r.message) {
                if (doctorDropdown) {
                    r.message.forEach(doc => {
                        const opt = document.createElement("option");
                        opt.value = doc.name;
                        opt.text = `${doc.full_name} (${doc.specialization})`;
                        doctorDropdown.add(opt); 
                    });
                }
            }
        }
    });

    // Book new appointment handler
    bookBtn.addEventListener("click", () => {
        const date = myHealthPatientPortal.container.find("#appointment-date").val();
        const start_time = myHealthPatientPortal.container.find("#start-time").val();
        const end_time = myHealthPatientPortal.container.find("#end-time").val();
        const notes = myHealthPatientPortal.container.find("#notes").val();
        const doctor = doctorDropdown.value;
        const service = myHealthPatientPortal.container.find("#service-dropdown").val();
        
        if (!doctor || !date || !start_time || !end_time) {
            frappe.throw("Please fill in all required fields.");
            return;
        }

        frappe.call({
            method: "myhealth.myhealth.api.appointment_api.create_appointment",
            args: {
                patient: myHealthPatientPortal.patient_id, 
                doctor: doctor,
                service: service,
                appointment_date: date,
                start_time: start_time,
                end_time: end_time,
                notes: notes
            },
            callback: function(r) {
                if(r.message) {
                    frappe.msgprint("Appointment booked successfully!", "Success");
                    myHealthPatientPortal.page.set_title("Your Appointments");
                    myHealthPatientPortal.viewAppointmentsView();
                }
            },
            error: function(err) {
                frappe.msgprint(err.responseJSON?.message || "Error booking appointment", "Error");
            }
        });
    });
};


// 3. View Appointments Page View (Separated Upcoming and Past)
myHealthPatientPortal.viewAppointmentsView = function() {
    this.container.html(`
        <style>${myHealthPatientPortal.styles}</style>
        <div class="dashboard-container">
            <button class="btn btn-link btn-back mb-4" id="go-home"><i class="fa fa-arrow-left mr-1"></i> Back to Dashboard</button>

            <div class="row">
                <div class="col-md-6">
                    <div class="app-card">
                        <div class="card-header-main text-primary">
                            <i class="fa fa-clock-o mr-2"></i> Upcoming Appointments
                        </div>
                        <div id="upcoming-list-container">
                            <p class="text-muted text-center">Loading appointments...</p>
                        </div>
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="app-card">
                        <div class="card-header-main text-secondary">
                            <i class="fa fa-history mr-2"></i> Past Appointments
                        </div>
                        <div id="past-list-container">
                            <p class="text-muted text-center">Loading appointments...</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `);

    this.container.find("#go-home").on('click', () => this.goHome());

    const upcomingContainer = this.container.find("#upcoming-list-container")[0];
    const pastContainer = this.container.find("#past-list-container")[0];

    // Load and sort appointments
    function loadAppointments() {
        if (!myHealthPatientPortal.patient_id) {
            upcomingContainer.innerHTML = '<p class="text-danger text-center mt-3">Error: Patient ID not found. Cannot load appointments.</p>';
            pastContainer.innerHTML = '';
            return;
        }

        frappe.call({
            method: "myhealth.myhealth.api.appointment_api.get_patient_appointments",
            args: { patient: myHealthPatientPortal.patient_id }, 
            callback: function(r) {
                const appointments = r.message || [];
                const now = new Date();
                
                let upcomingHtml = '';
                let pastHtml = '';
                
                // Sort by date (oldest first for past, soonest first for upcoming)
                appointments.sort((a, b) => new Date(a.appointment_date) - new Date(b.appointment_date));

                if (appointments.length === 0) {
                    upcomingHtml = '<p class="text-muted text-center mt-3">You have no upcoming appointments.</p>';
                    pastHtml = '<p class="text-muted text-center mt-3">No past appointment history found.</p>';
                } else {
                    appointments.forEach(appt => {
                        const apptDateTime = new Date(`${appt.appointment_date}T${appt.start_time}`);
                        const html = myHealthPatientPortal.renderAppointmentItem(appt);
                        
                        // Categorize based on status and time
                        if (appt.status === 'Completed' || appt.status === 'Cancelled' || apptDateTime < now) {
                            pastHtml += html;
                        } else {
                            upcomingHtml += html;
                        }
                    });
                }
                
                upcomingContainer.innerHTML = upcomingHtml || '<p class="text-muted text-center mt-3">No appointments scheduled.</p>';
                pastContainer.innerHTML = pastHtml || '<p class="text-muted text-center mt-3">No past history to display.</p>';
            }
        });
    }

    loadAppointments();
};
