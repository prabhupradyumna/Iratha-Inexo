/** @odoo-module **/
import { rpc } from "@web/core/network/rpc";

let selected_date = $('.custom-calendar').val();
function getDayName(dateString) {
    const days = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"];
    const date = new Date(dateString);
    return days[date.getUTCDay()];
}

function renderTimeSlots(selected_date, selectedUserId, appointmentId) {
    console.log("hiiiiiiiiiii111======1111111=====")
    if (selected_date) {
        var selected_day = getDayName(selected_date);
        rpc("/fetch_date", {
            'selected_date': selected_date,
            'selected_day': selected_day,
            'selected_user_id': selectedUserId,
            'appointment_id': appointmentId,
        }).then(function (res) {
            const columns = $(".time-column");
            const numColumns = columns.length;
            let slotsAvailable = false;

            // Clear previous time slots and messages
            $(".time-column").empty();
            $(".no-slots-message").remove();

            if (res && res.length > 0) {
                res.forEach((item, index) => {
                    const colIndex = index % numColumns;
                    const column = $(columns[colIndex]);

                    const isBooked = item.is_booked;
                    const cardClass = isBooked ? "time-slot booked" : "time-slot available";
                    const bookedColor = "background-color: #ffcccc; color: #b71c1c; border: 1px solid #ef9a9a;";
                    const availableColor = "background-color: #e6ffe6; color: #2e7d32; border: 1px solid #81c784;";
                    const cardStyle = isBooked ? bookedColor : availableColor;

                    const card = `
                        <div class="${cardClass}" data-slot-id="${item.id}" style="${cardStyle}" title="${isBooked ? 'Already Booked' : 'Click to select'}">
                            <div class="card-body">
                                ${item.name}
                            </div>
                        </div>
                    `;

                    if (!isBooked) {
                        slotsAvailable = true;
                    }

                    column.append(card);
                });
            }

            if (!slotsAvailable) {
                const noSlotsMessage = $('<div class="no-slots-message">No available slots for this date.</div>').css({
                    'color': 'red',
                    'font-weight': 'bold',
                    'text-align': 'center',
                    'margin-top': '20px'
                });
                $(".table-container").append(noSlotsMessage);
            }
        });
    }
}

// Get today's date in YYYY-MM-DD format
const today = new Date();
const today_date = today.toISOString().split('T')[0];
console.log("hiiiiiiiiiii111===========")
// Set default value to calendar input
$('.custom-calendar').val(today_date);

// Document ready handler
$(document).ready(function () {
    // Get initial selected user id on page load
    const selectedUserId = $('#user_id').val();
    const appointmentId = window.appointmentData?.id;
    renderTimeSlots(today_date, selectedUserId, appointmentId);
});
$('#user_id').on('change', function () {
    const selectedUserId = $(this).val();
    const selectedUserName = $("#user_id option:selected").text();

    if (selectedUserId) {
        $('#selected_user_info').text("Selected User: " + selectedUserName);

        // Fetch and display timezone
        rpc("/get_user_timezone", {
            user_id: selectedUserId
        }).then(function (result) {
            const timezone = result.timezone;
            $('#selected_user_timezone').text("Timezone: " + timezone);
        });
    } else {
        // Do nothing if user is not selected
        $('#selected_user_info').text("");
        // Keep the timezone display as it is
    }

    if (selected_date) {
        renderTimeSlots(selected_date, selectedUserId, window.appointmentData?.id);
    }
});


// When calendar changes
$(".custom-calendar").on('change', function () {
    selected_date = $(this).val();  // update global variable correctly
    var selectedUserId = $('#user_id').val();
    var appointmentId = window.appointmentData?.id;
    $('input[name="request_date"]').val(selected_date);
    renderTimeSlots(selected_date, selectedUserId, appointmentId);
});

    $(document).on('click', '.time-slot', function () {
          if ($(this).hasClass('booked')) {
            event.preventDefault(); // ✅ FIXED: use the event object
            return false;
        }
	console.log("heloooo========")
        var slotId = $(this).data('slot-id');
        var EmpId = $(this).data('emp_id');
        var empName = $(this).data('emp-name');
        var slotName = $(this).find('.card-body').text();

        var apptId = window.appointmentData?.id; // ✅ pulled from global JS var
        var apptName = window.appointmentData?.name;
        var apptLocation = window.appointmentData?.location;
        var apptImg = window.appointmentData?.image_1920;
        var apptFees = window.appointmentData?.fees;
//        var apptServiceTime = window.appointmentData?.service_time;
        var apptAppointmentType = window.appointmentData?.appointment_type;


        $('#selected_slot_id').val(slotId);
        console.log("slotId====88888888888=====",$('#selected_slot_id').val());
//        console.log(ddddd)
        $('#time_slot_name').val(slotName);
        $('#emp_id').val(EmpId);
        $('#emp_name').val(empName);
        $('#appointment_id').val(apptId);
        $('#appointment_name').val(apptName);
        $('#appointment_location').val(apptLocation);
        $('#appointment_img').val(apptImg);
        $('#appointment_fees').val(apptFees);
//        $('#appointment_service_time').val(apptServiceTime);
        $('#appointment_type').val(apptAppointmentType);
        $('#form2').submit();
    });
    
//});

$(document).on('click', 'form button.time-slot', function(event) {
    event.preventDefault();
    const apptId = $(this).data('appointment-id');

    $('#appointment_id_hidden').val(apptId);
    $('#appointmentForm').submit();
});
