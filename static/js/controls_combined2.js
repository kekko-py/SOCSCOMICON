let timerIntervalCouple2 = null;
let startTimeCouple2 = null;
let isGameActiveCouple2 = false;

let timerIntervalSingle2 = null;
let startTimeSingle2 = null;
let isGameActiveSingle2 = false;

function updateNextPlayer2() {
    fetch('/simulate')
        .then(response => response.json())
        .then(data => {
            // Aggiorna il prossimo giocatore condiviso per le piste 2
            if (data.next_player_alfa_bravo_id2) {
                $('#next-player2').text(data.next_player_alfa_bravo_id2);
                $('#next-player-btn2').prop('disabled', false);
            } else {
                $('#next-player2').text('-');
                $('#next-player-btn2').prop('disabled', true);
            }

            // Aggiorna giocatori correnti per piste 2
            if (data.current_player_bravo2) {
                $('#current-player-couple2').text(data.current_player_bravo2.id);
            } else if (data.current_player_alfa2 && data.current_player_alfa2.id && data.current_player_alfa2.id.startsWith("GIALLO")) {
                $('#current-player-couple2').text(data.current_player_alfa2.id);
            } else {
                $('#current-player-couple2').text('-');
            }
            
            if (data.current_player_alfa2 && data.current_player_alfa2.id && data.current_player_alfa2.id.startsWith("BLU")) {
                $('#current-player-single2').text(data.current_player_alfa2.id);
            } else {
                $('#current-player-single2').text('-');
            }
        })
        .catch(error => {
            console.error('Error fetching player data:', error);
        });
}

function updateAvailability2() {
    $.get('/check_availability2', function(data) {
        // Coppia 2
        $('#start-btn-couple2').prop('disabled', !data.can_start_couple2);
        $('#status-couple2').text(`ALFA2: ${data.alfa2_status} - BRAVO2: ${data.bravo2_status}`);
        
        if (!data.can_start_couple2) {
            $('#start-btn-couple2').attr('title', 'Attendere che entrambe le piste siano libere');
        } else {
            $('#start-btn-couple2').attr('title', '');
        }
        
        // Singolo 2
        $('#start-btn-single2').prop('disabled', !data.can_start_single2);
        $('#status-single2').text(`ALFA2: ${data.alfa2_status}`);
        
        if (!data.can_start_single2) {
            $('#start-btn-single2').attr('title', 'Attendere che la pista ALFA2 sia libera');
        } else {
            $('#start-btn-single2').attr('title', '');
        }
    }).fail(function(jqXHR, textStatus, errorThrown) {
        console.error('Error checking availability:', textStatus, errorThrown);
    });
}

function updateTimer2(type) {
    const now = new Date();
    let diff, minutes, seconds;
    
    if (type === 'couple2' && startTimeCouple2) {
        diff = Math.floor((now - startTimeCouple2) / 1000);
        minutes = Math.floor(diff / 60).toString().padStart(2, '0');
        seconds = (diff % 60).toString().padStart(2, '0');
        $('#timer-couple2').text(`${minutes}:${seconds}`);
    } else if (type === 'single2' && startTimeSingle2) {
        diff = Math.floor((now - startTimeSingle2) / 1000);
        minutes = Math.floor(diff / 60).toString().padStart(2, '0');
        seconds = (diff % 60).toString().padStart(2, '0');
        $('#timer-single2').text(`${minutes}:${seconds}`);
    }
}

function activateNextPlayer2() {
    $('#next-player-btn2').prop('disabled', true);
    updateAvailability2();
}

function pressButton(button, type) {
    $.ajax({
        url: '/button_press',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ button: button }),
        success: function(response) {
            if (!response.success) {
                alert(response.error);
                return;
            }

            if (button === 'first_start2' && type === 'couple2') {
                startTimeCouple2 = new Date();
                isGameActiveCouple2 = true;
                clearInterval(timerIntervalCouple2);
                timerIntervalCouple2 = setInterval(() => updateTimer2('couple2'), 1000);
                $('#start-btn-couple2').prop('disabled', true);
                $('#stop-btn-couple2').prop('disabled', false);
                
                const player = response.current_player_bravo2 || response.current_player_alfa2;
                if (player && player.id) {
                    $('#current-player-couple2').text(player.id);
                }
            } 
            else if (button === 'second_start2' && type === 'single2') {
                startTimeSingle2 = new Date();
                isGameActiveSingle2 = true;
                clearInterval(timerIntervalSingle2);
                timerIntervalSingle2 = setInterval(() => updateTimer2('single2'), 1000);
                $('#start-btn-single2').prop('disabled', true);
                $('#stop-btn-single2').prop('disabled', false);
                
                if (response.current_player_alfa2 && response.current_player_alfa2.id) {
                    $('#current-player-single2').text(response.current_player_alfa2.id);
                }
            }
            else if (button === 'first_stop2' && type === 'couple2' && isGameActiveCouple2) {
                isGameActiveCouple2 = false;
                clearInterval(timerIntervalCouple2);
                $('#start-btn-couple2').prop('disabled', true);
                $('#stop-btn-couple2').prop('disabled', true);
                $('#current-player-couple2').text('-');
            }
            else if (button === 'second_stop2' && type === 'single2' && isGameActiveSingle2) {
                isGameActiveSingle2 = false;
                clearInterval(timerIntervalSingle2);
                $('#start-btn-single2').prop('disabled', true);
                $('#stop-btn-single2').prop('disabled', true);
                $('#current-player-single2').text('-');
            }

            updateNextPlayer2();
            updateAvailability2();
        },
        error: function(xhr, status, error) {
            console.error('Error pressing button:', error);
            alert("Si è verificato un errore durante l'operazione");
        }
    });
}

// Aggiornamento periodico
setInterval(() => {
    updateAvailability2();
    updateNextPlayer2();
}, 1000);

$(document).ready(function() {
    updateAvailability2();
    updateNextPlayer2();
});