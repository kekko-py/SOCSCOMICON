let timerIntervalCouple = null;
let startTimeCouple = null;
let isGameActiveCouple = false;

let timerIntervalSingle = null;
let startTimeSingle = null;
let isGameActiveSingle = false;

function updateNextPlayer() {
    fetch('/simulate')
        .then(response => response.json())
        .then(data => {
            // Aggiorna il prossimo giocatore condiviso
            if (data.next_player_alfa_bravo_id) {
                $('#next-player').text(data.next_player_alfa_bravo_id);
                $('#next-player-btn').prop('disabled', false);
            } else {
                $('#next-player').text('-');
                $('#next-player-btn').prop('disabled', true);
            }

            // Aggiorna giocatori correnti
            if (data.current_player_bravo) {
                $('#current-player-couple').text(data.current_player_bravo.id);
            } else if (data.current_player_alfa && data.current_player_alfa.id && data.current_player_alfa.id.startsWith("GIALLO")) {
                $('#current-player-couple').text(data.current_player_alfa.id);
            } else {
                $('#current-player-couple').text('-');
            }
            
            if (data.current_player_alfa && data.current_player_alfa.id && data.current_player_alfa.id.startsWith("BLU")) {
                $('#current-player-single').text(data.current_player_alfa.id);
            } else {
                $('#current-player-single').text('-');
            }
        })
        .catch(error => {
            console.error('Error fetching player data:', error);
        });
}

function updateAvailability() {
    $.get('/check_availability', function(data) {
        // Coppia
        $('#start-btn-couple').prop('disabled', !data.can_start_couple);
        $('#status-couple').text(`ALFA: ${data.alfa_status} - BRAVO: ${data.bravo_status}`);
        
        if (!data.can_start_couple) {
            $('#start-btn-couple').attr('title', 'Attendere che entrambe le piste siano libere');
        } else {
            $('#start-btn-couple').attr('title', '');
        }
        
        // Singolo
        $('#start-btn-single').prop('disabled', !data.can_start_single);
        $('#status-single').text(`ALFA: ${data.alfa_status}`);
        
        if (!data.can_start_single) {
            $('#start-btn-single').attr('title', 'Attendere che la pista ALFA sia libera');
        } else {
            $('#start-btn-single').attr('title', '');
        }
    }).fail(function(jqXHR, textStatus, errorThrown) {
        console.error('Error checking availability:', textStatus, errorThrown);
    });
}

function updateTimer(type) {
    const now = new Date();
    let diff, minutes, seconds;
    
    if (type === 'couple' && startTimeCouple) {
        diff = Math.floor((now - startTimeCouple) / 1000);
        minutes = Math.floor(diff / 60).toString().padStart(2, '0');
        seconds = (diff % 60).toString().padStart(2, '0');
        $('#timer-couple').text(`${minutes}:${seconds}`);
    } else if (type === 'single' && startTimeSingle) {
        diff = Math.floor((now - startTimeSingle) / 1000);
        minutes = Math.floor(diff / 60).toString().padStart(2, '0');
        seconds = (diff % 60).toString().padStart(2, '0');
        $('#timer-single').text(`${minutes}:${seconds}`);
    }
}

function activateNextPlayer() {
    $('#next-player-btn').prop('disabled', true);
    updateAvailability();
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

            if (button === 'first_start' && type === 'couple') {
                startTimeCouple = new Date();
                isGameActiveCouple = true;
                clearInterval(timerIntervalCouple);
                timerIntervalCouple = setInterval(() => updateTimer('couple'), 1000);
                $('#start-btn-couple').prop('disabled', true);
                $('#stop-btn-couple').prop('disabled', false);
                
                const player = response.current_player_bravo || response.current_player_alfa;
                if (player && player.id) {
                    $('#current-player-couple').text(player.id);
                }
            } 
            else if (button === 'second_start' && type === 'single') {
                startTimeSingle = new Date();
                isGameActiveSingle = true;
                clearInterval(timerIntervalSingle);
                timerIntervalSingle = setInterval(() => updateTimer('single'), 1000);
                $('#start-btn-single').prop('disabled', true);
                $('#stop-btn-single').prop('disabled', false);
                
                if (response.current_player_alfa && response.current_player_alfa.id) {
                    $('#current-player-single').text(response.current_player_alfa.id);
                }
            }
            else if (button === 'first_stop' && type === 'couple' && isGameActiveCouple) {
                isGameActiveCouple = false;
                clearInterval(timerIntervalCouple);
                $('#start-btn-couple').prop('disabled', true);
                $('#stop-btn-couple').prop('disabled', true);
                $('#current-player-couple').text('-');
            }
            else if (button === 'second_stop' && type === 'single' && isGameActiveSingle) {
                isGameActiveSingle = false;
                clearInterval(timerIntervalSingle);
                $('#start-btn-single').prop('disabled', true);
                $('#stop-btn-single').prop('disabled', true);
                $('#current-player-single').text('-');
            }

            updateNextPlayer();
            updateAvailability();
        },
        error: function(xhr, status, error) {
            console.error('Error pressing button:', error);
            alert("Si è verificato un errore durante l'operazione");
        }
    });
}

// Aggiornamento periodico
setInterval(() => {
    updateAvailability();
    updateNextPlayer();
}, 1000);

$(document).ready(function() {
    updateAvailability();
    updateNextPlayer();
});