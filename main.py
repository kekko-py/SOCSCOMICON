import datetime
from copy import deepcopy
import pytz
from typing import List, Dict, TypedDict, Tuple, Optional, Union

class Player(TypedDict):
    id: str
    name: str

class Queue(TypedDict, total=False):
    id: str
    arrival: datetime.datetime
    name: str   # aggiunto come chiave opzionale

class GameBackend:
    def __init__(self) -> None:
        # Code: ogni elemento è un dizionario con "id" e "arrival" (orario d'arrivo)
        self.queue_couples: List[Queue] = []  # Es. [{'id': 'GIALLO-01', 'arrival': datetime}, ...]
        self.queue_singles: List[Queue] = []  # Es. [{'id': 'BLU-01', 'arrival': datetime}, ...]
        self.queue_couples2: List[Queue] = []  # Es. [{'id': 'VIOLA-01', 'arrival': datetime}, ...]
        self.queue_singles2: List[Queue] = []  # Es. [{'id': 'ARANCIO-01', 'arrival': datetime}, ...]
        self.queue_charlie: List[Queue] = []  # Es. [{'id': 'VERDE-01', 'arrival': datetime}, ...]
        self.queue_statico: List[Queue] = []

        self.couples= []
        # Storico dei tempi (in minuti) registrati per aggiornamento dinamico
        self.couple_history_mid: List[float] = []    # Tempo dal Pulsante 1 al Pulsante 3 (liberazione di ALFA)
        self.couple_history_total: List[float] = []  # Tempo totale per il game coppia (fino alla liberazione di BRAVO)
        self.single_history: List[float] = []        # Tempo totale per il game singolo (durata in cui ALFA è occupata)
        self.couple_history_mid2: List[float] = []    # Tempo dal Pulsante 1 al Pulsante 3 (liberazione di ALFA)
        self.couple_history_total2: List[float] = []  # Tempo totale per il game coppia2 (fino alla liberazione di BRAVO)
        self.single_history2: List[float] = []        # Tempo totale per il game singolo2 (durata in cui ALFA è occupata)
        self.charlie_history: List[float] = []       # Tempo totale per il game charlie
        self.statico_history: List[float] = []

        # Valori indicativi (default) iniziali (in minuti)
        self.default_T_mid = 2.0
        self.default_T_total = 5.0
        self.default_T_single = 2.0
        self.default_T_charlie = 3.0
        self.default_T_statico = 5.0

        # Tempi attuali: partono dai valori indicativi e verranno aggiornati
        self.T_mid = self.default_T_mid
        self.T_total = self.default_T_total
        self.T_single = self.default_T_single
        self.T_charlie = self.default_T_charlie
        self.T_statico = self.default_T_statico

        # Giocatori attuali in pista
        self.current_player_alfa: Optional[Queue] = None
        self.current_player_bravo: Optional[Queue] = None
        self.current_player_alfa2: Optional[Queue] = None
        self.current_player_bravo2: Optional[Queue] = None
        self.current_player_charlie: Optional[Queue] = None
        self.current_player_delta: Optional[Queue] = None
        self.current_player_echo: Optional[Queue] = None

        # Stato iniziale delle piste: disponibilità immediata
        self.rome_tz = pytz.timezone('Europe/Rome')
        now = self.get_current_time()
        self.ALFA_next_available = now
        self.BRAVO_next_available = now
        self.ALFA_next_available2 = now
        self.BRAVO_next_available2 = now
        self.CHARLIE_next_available = now
        self.DELTA_next_available = now
        self.ECHO_next_available = now

        # Variabili per la gestione dei giocatori
        self.next_player_alfa_bravo_id: Optional[str] = None
        self.next_player_alfa_bravo_locked: bool = False
        self.next_player_alfa_bravo_name: Optional[str] = None
        self.next_player_alfa_bravo_id2: Optional[str] = None
        self.next_player_alfa_bravo_locked2: bool = False
        self.next_player_alfa_bravo_name2: Optional[str] = None
        self.next_player_charlie_id: Optional[str] = None
        self.next_player_charlie_locked: bool = False
        self.next_player_charlie_name: Optional[str] = None
        self.current_player_couple: Optional[Queue] = None
        self.current_player_couple2: Optional[Queue] = None
        self.player_in_charlie: bool = False
        self.next_player_statico_id: Optional[str] = None
        self.next_player_statico_locked: bool = False
        self.next_player_statico_name: Optional[str] = None

        # Flag per tracciare lo stato delle piste
        self.couple_in_bravo = False
        self.couple_in_alfa = False
        self.single_in_alfa = False
        self.third_button_pressed = False
        self.couple_in_bravo2 = False
        self.couple_in_alfa2 = False
        self.single_in_alfa2 = False
        self.third_button_pressed2 = False
        self.statico_in_delta = False
        self.statico_in_echo = False

        # Liste per i giocatori skippati
        self.skipped_couples: List[Queue] = []
        self.skipped_singles: List[Queue] = []
        self.skipped_couples2: List[Queue] = []
        self.skipped_singles2: List[Queue] = []
        self.skipped_charlie: List[Queue] = []
        self.skipped_statico: List[Queue] = []

        # Dizionario per memorizzare i nomi dei giocatori
        self.player_names: Dict[str, str] = {}

        # Inizializza le code con i nuovi formati ID
        # for i in range(1, 11):
        #     couple_id = f"GIALLO-{i:02d}"
        #     single_id = f"BLU-{i:02d}"
        #     charlie_id = f"VERDE-{i:02d}"
            
        #     self.add_couple(couple_id)
        #     self.add_single(single_id)
        #     self.add_charlie_player(charlie_id)

        self.player_start_times: Dict[str, datetime.datetime] = {}
        self.player_durations: Dict[str, float] = {}

    def add_couple(self, couple_id, name) -> None:
        self.queue_couples.append({'id': couple_id, 'arrival': self.get_current_time()})
        self.player_names[couple_id] = name

    def add_single(self, single_id, name) -> None:
        self.queue_singles.append({'id': single_id, 'arrival': self.get_current_time()})
        self.player_names[single_id] = name

    def add_couple2(self, couple_id, name) -> None:
        self.queue_couples2.append({'id': couple_id, 'arrival': self.get_current_time()})
        self.player_names[couple_id] = name

    def add_single2(self, single_id, name) -> None:
        self.queue_singles2.append({'id': single_id, 'arrival': self.get_current_time()})
        self.player_names[single_id] = name 

    def add_charlie_player(self, player_id, name) -> None:
        """Aggiunge un giocatore alla coda Charlie"""
        if not any(p['id'] == player_id for p in self.queue_charlie):
            self.queue_charlie.append({
                'id': player_id,
                'arrival': self.get_current_time(),
                'name': name
            })
            self.player_names[player_id] = name
            if not self.next_player_charlie_id and not self.next_player_charlie_locked:
                self.next_player_charlie_id = player_id
                self.next_player_charlie_name = name
                self.next_player_charlie_locked = True

    def add_statico_player(self, player_id: str, name: str) -> None:
        """Aggiunge un giocatore alla coda Statico"""
        if not any(p['id'] == player_id for p in self.queue_statico):
            self.queue_statico.append({
                'id': player_id,
                'arrival': self.get_current_time(),
                'name': name
            })
            self.player_names[player_id] = name
            if not self.next_player_statico_id and not self.next_player_statico_locked:
                self.next_player_statico_id = player_id
                self.next_player_statico_name = name
                self.next_player_statico_locked = True

    def record_couple_game(self, mid_time: float, total_time: float) -> None:
        """
        Registra i tempi (in minuti) relativi a un game coppia:
          - mid_time: tempo dal Pulsante 1 all'attivazione del Pulsante 3
          - total_time: tempo totale dal Pulsante 1 (avvio) allo stop (liberazione di BRAVO)
        Dopo la registrazione, aggiorna i tempi medi.
        """
        self.couple_history_mid.append(mid_time)
        self.couple_history_total.append(total_time)
        # Mantiene la pista BRAVO occupata fino alla fine del game di coppia
        self.current_player_bravo = None  
        self.couple_in_alfa = False
        self.couple_in_bravo = False
        self.update_averages()
        self.update_next_player()
        # Record the duration
        player_id = self.current_player_couple['id']
        start_time = self.player_start_times.pop(player_id, None)
        if start_time:
            duration = (self.get_current_time() - start_time).total_seconds() / 60
            self.player_durations[player_id] = duration

    def record_single_game(self, game_time: float) -> None:
        """
        Registra il tempo (in minuti) relativo a un game singolo (durata in cui ALFA è occupata).
        Dopo la registrazione, aggiorna i tempi medi.
        """
        if self.current_player_alfa:
            player_id = self.current_player_alfa['id']
            self.single_history.append(game_time)
            self.update_averages()
            self.current_player_alfa = None
            if self.couple_in_bravo and self.queue_singles:
                self.next_player_alfa_bravo_id = self.queue_singles[0]['id']
                self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id)
                self.next_player_alfa_bravo_locked = True
            else:
                self.update_next_player()
            # Record the duration
            start_time = self.player_start_times.pop(player_id, None)
            if start_time:
                duration = (self.get_current_time() - start_time).total_seconds() / 60
                self.player_durations[player_id] = duration

    def record_couple2_game(self, mid_time: float, total_time: float) -> None:
        """
        Registra i tempi per un game coppia 2 (Viola).
        Il tempo totale viene aggiunto alla storia comune per la classifica.
        """
        if self.current_player_couple2: # Controllo di sicurezza
            player_id = self.current_player_couple2['id']

            # Aggiungi mid_time alla storia specifica di mid2 (se vuoi medie separate)
            self.couple_history_mid2.append(mid_time)
            # Aggiungi total_time alla storia COMUNE per la classifica
            self.couple_history_total.append(total_time)

            # Memorizza la durata specifica del giocatore
            start_time = self.player_start_times.pop(player_id, None)
            if start_time:
                duration = (self.get_current_time() - start_time).total_seconds() / 60
                self.player_durations[player_id] = duration
            else:
                # Se non troviamo start_time, usiamo total_time come fallback per player_durations
                self.player_durations[player_id] = total_time

            # Resetta lo stato per il set 2
            self.current_player_bravo2 = None # Libera Bravo 2
            # Nota: current_player_alfa2 dovrebbe essere già None se è stato premuto third2
            self.couple_in_bravo2 = False
            self.third_button_pressed2 = False # Resetta il flag di metà percorso 2

            self.update_averages() # Aggiorna le medie (che ora considerano i tempi combinati)
            self.update_next_player2() # Aggiorna il prossimo giocatore per il set 2

            # Rimuovi current_player_couple2 alla fine
            self.current_player_couple2 = None


    def record_single2_game(self, game_time: float) -> None:
        """
        Registra il tempo per un game singolo 2 (Arancio).
        Il tempo viene aggiunto alla storia comune per la classifica.
        """
        if self.current_player_alfa2: # Controllo di sicurezza
            player_id = self.current_player_alfa2['id']

            # Aggiungi game_time alla storia COMUNE per la classifica
            self.single_history.append(game_time)

            # Memorizza la durata specifica del giocatore
            start_time = self.player_start_times.pop(player_id, None)
            if start_time:
                duration = (self.get_current_time() - start_time).total_seconds() / 60
                self.player_durations[player_id] = duration
            else:
                self.player_durations[player_id] = game_time # Fallback

            # Resetta lo stato per il set 2
            self.current_player_alfa2 = None # Libera Alfa 2
            self.single_in_alfa2 = False

            self.update_averages() # Aggiorna le medie
            self.update_next_player2() # Aggiorna il prossimo giocatore per il set 2
        
                

    def record_charlie_game(self, game_time: float) -> None:
        """Registra il tempo (in minuti) relativo a un game charlie"""
        if self.current_player_charlie:
            player_id = self.current_player_charlie['id']
            self.charlie_history.append(game_time)
            self.update_averages()
            self.current_player_charlie = None
            self.player_in_charlie = False
            # Record the duration
            start_time = self.player_start_times.pop(player_id, None)
            if start_time:
                duration = (self.get_current_time() - start_time).total_seconds() / 60
                self.player_durations[player_id] = duration

    def format_time(self, time_in_minutes: float) -> str:
        """Formatta il tempo in minuti e secondi"""
        minutes = int(time_in_minutes)
        seconds = int((time_in_minutes - minutes) * 60)
        return f"{minutes}m {seconds}s"
    
    def get_leaderboard(self) -> Dict[str, List[Tuple[str, str]]]:
        """
        Restituisce la classifica dei giocatori in base ai tempi medi di gioco.
        """
        couple_avg_times = [(f"COMPLETATO-{i+1}", self.format_time(time)) for i, time in enumerate(self.couple_history_total)]
        single_avg_times = [(f"COMPLETATO-{i+1}", self.format_time(time)) for i, time in enumerate(self.single_history)]
        charlie_avg_times = [(f"COMPLETATO-{i+1}", self.format_time(time)) for i, time in enumerate(self.charlie_history)]
        statico_avg_times = [(f"COMPLETATO-{i+1}", self.format_time(time)) for i, time in enumerate(self.statico_history)]

        return {
            'couples': couple_avg_times,
            'singles': single_avg_times,
            'charlie': charlie_avg_times,
            'statico': statico_avg_times
        }

    def get_current_time(self) -> datetime.datetime:
        """Ottiene l'ora corrente nel fuso orario di Roma"""
        return datetime.datetime.now(self.rome_tz)

    def localize_time(self, dt):
        """Assicura che un datetime abbia il fuso orario di Roma"""
        if dt.tzinfo is None:
            return self.rome_tz.localize(dt)
        return dt
    
    

    # Dentro la classe GameBackend in main.py

    def update_averages(self) -> None:
        """
        Aggiorna i tempi medi. T_total e T_single usano storie combinate.
        T_mid e T_mid2 sono calcolate separatamente.
        """
        min_games_for_avg = 5 # Numero minimo di game per calcolare la media

        # Media T_mid (Set 1)
        if len(self.couple_history_mid) >= min_games_for_avg:
            self.T_mid = sum(self.couple_history_mid) / len(self.couple_history_mid)
        else:
            self.T_mid = self.default_T_mid

        # Media T_mid2 (Set 2) - NUOVO attributo T_mid2
        if len(self.couple_history_mid2) >= min_games_for_avg:
            self.T_mid2 = sum(self.couple_history_mid2) / len(self.couple_history_mid2)
        else:
            # Potresti voler un default diverso per T_mid2 se necessario
            self.T_mid2 = self.default_T_mid # Usiamo lo stesso default per ora

        # Media T_total (Combinata) - MODIFICATA
        # Ora self.couple_history_total contiene i tempi di entrambi i set
        if len(self.couple_history_total) >= min_games_for_avg:
            self.T_total = sum(self.couple_history_total) / len(self.couple_history_total)
        else:
            self.T_total = self.default_T_total

        # Media T_single (Combinata) - MODIFICATA
        # Ora self.single_history contiene i tempi di entrambi i set
        if len(self.single_history) >= min_games_for_avg:
            self.T_single = sum(self.single_history) / len(self.single_history)
        else:
            self.T_single = self.default_T_single

        # Media T_charlie (invariata)
        if len(self.charlie_history) >= min_games_for_avg:
            self.T_charlie = sum(self.charlie_history) / len(self.charlie_history)
        else:
            self.T_charlie = self.default_T_charlie

        # Media T_statico (invariata)
        if len(self.statico_history) >= min_games_for_avg:
            self.T_statico = sum(self.statico_history) / len(self.statico_history)
        else:
            self.T_statico = self.default_T_statico    

    def get_player_name(self, player_id: Optional[str]) -> str:
        if player_id is None:
            return "N/D"
        return self.player_names.get(player_id, player_id)

    def update_next_player(self) -> None:
        """
        Aggiorna next_player_alfa_bravo_id e next_player_alfa_bravo_name in base alla disponibilità in coda,
        considerando l'orario di entrata (campo 'arrival') oppure la priorità,
        in modo che il prossimo giocatore da entrare venga mostrato nella finestra "Prossimo ingresso".
        """
        if self.current_player_alfa is None and self.current_player_bravo is None:
            if self.queue_couples:
                self.next_player_alfa_bravo_id = self.queue_couples[0]['id']
                assert self.next_player_alfa_bravo_id is not None
                self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id)
                self.next_player_alfa_bravo_locked = True
            elif self.queue_singles:
                self.next_player_alfa_bravo_id = self.queue_singles[0]['id']
                assert self.next_player_alfa_bravo_id is not None
                self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id)
                self.next_player_alfa_bravo_locked = True
            else:
                self.next_player_alfa_bravo_id = None
                self.next_player_alfa_bravo_name = None
                self.next_player_alfa_bravo_locked = False
        elif self.current_player_alfa is None and self.current_player_bravo is not None:
            if self.queue_couples:
                self.next_player_alfa_bravo_id = self.queue_couples[0]['id']
                assert self.next_player_alfa_bravo_id is not None
                self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id)
                self.next_player_alfa_bravo_locked = True
            elif self.queue_singles:
                self.next_player_alfa_bravo_id = self.queue_singles[0]['id']
                assert self.next_player_alfa_bravo_id is not None
                self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id)
                self.next_player_alfa_bravo_locked = True
            else:
                self.next_player_alfa_bravo_id = None
                self.next_player_alfa_bravo_name = None
                self.next_player_alfa_bravo_locked = False
        else:
            if self.queue_couples and self.current_player_alfa and self.current_player_alfa["id"].startswith("BLU") and self.current_player_bravo is None:
                self.next_player_alfa_bravo_id = self.queue_couples[0]['id']
                assert self.next_player_alfa_bravo_id is not None
                self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id)
                self.next_player_alfa_bravo_locked = True
            elif self.queue_couples:
                self.next_player_alfa_bravo_id = self.queue_couples[0]['id']
                assert self.next_player_alfa_bravo_id is not None
                self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id)
                self.next_player_alfa_bravo_locked = True
            elif self.queue_singles:
                self.next_player_alfa_bravo_id = self.queue_singles[0]['id']
                assert self.next_player_alfa_bravo_id is not None
                self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id)
                self.next_player_alfa_bravo_locked = True
            else:
                self.next_player_alfa_bravo_id = None
                self.next_player_alfa_bravo_name = None
                self.next_player_alfa_bravo_locked = False

    def update_next_player2(self) -> None:
        """
        Aggiorna next_player_alfa_bravo_id e next_player_alfa_bravo_name in base alla disponibilità in coda,
        considerando l'orario di entrata (campo 'arrival') oppure la priorità,
        in modo che il prossimo giocatore da entrare venga mostrato nella finestra "Prossimo ingresso".
        """ 
        if self.current_player_alfa2 is None and self.current_player_bravo2 is None:
            if self.queue_couples2:
                self.next_player_alfa_bravo_id2 = self.queue_couples2[0]['id']
                assert self.next_player_alfa_bravo_id2 is not None
                self.next_player_alfa_bravo_name2 = self.get_player_name(self.next_player_alfa_bravo_id2)
                self.next_player_alfa_bravo_locked2 = True
            elif self.queue_singles2:
                self.next_player_alfa_bravo_id2 = self.queue_singles2[0]['id']
                assert self.next_player_alfa_bravo_id2 is not None
                self.next_player_alfa_bravo_name2 = self.get_player_name(self.next_player_alfa_bravo_id2)
                self.next_player_alfa_bravo_locked2 = True
            else:
                self.next_player_alfa_bravo_id2 = None
                self.next_player_alfa_bravo_name2 = None
                self.next_player_alfa_bravo_locked2 = False
        elif self.current_player_alfa2 is None and self.current_player_bravo2 is not None:
            if self.queue_couples2:
                self.next_player_alfa_bravo_id2 = self.queue_couples2[0]['id']
                assert self.next_player_alfa_bravo_id2 is not None
                self.next_player_alfa_bravo_name2 = self.get_player_name(self.next_player_alfa_bravo_id2)
                self.next_player_alfa_bravo_locked2 = True
            elif self.queue_singles2:
                self.next_player_alfa_bravo_id2 = self.queue_singles2[0]['id']  
                assert self.next_player_alfa_bravo_id2 is not None
                self.next_player_alfa_bravo_name2 = self.get_player_name(self.next_player_alfa_bravo_id2)
                self.next_player_alfa_bravo_locked2 = True
            else:
                self.next_player_alfa_bravo_id2 = None
                self.next_player_alfa_bravo_name2 = None
                self.next_player_alfa_bravo_locked2 = False 
        else:
            if self.queue_couples2 and self.current_player_alfa2 and self.current_player_alfa2["id"].startswith("BLU") and self.current_player_bravo2 is None:
                self.next_player_alfa_bravo_id2 = self.queue_couples2[0]['id']
                assert self.next_player_alfa_bravo_id2 is not None
                self.next_player_alfa_bravo_name2 = self.get_player_name(self.next_player_alfa_bravo_id2)
                self.next_player_alfa_bravo_locked2 = True      
            elif self.queue_couples2:
                self.next_player_alfa_bravo_id2 = self.queue_couples2[0]['id']
                assert self.next_player_alfa_bravo_id2 is not None
                self.next_player_alfa_bravo_name2 = self.get_player_name(self.next_player_alfa_bravo_id2)
                self.next_player_alfa_bravo_locked2 = True      
            elif self.queue_singles2:
                self.next_player_alfa_bravo_id2 = self.queue_singles2[0]['id']
                assert self.next_player_alfa_bravo_id2 is not None
                self.next_player_alfa_bravo_name2 = self.get_player_name(self.next_player_alfa_bravo_id2)
                self.next_player_alfa_bravo_locked2 = True
            else:
                self.next_player_alfa_bravo_id2 = None
                self.next_player_alfa_bravo_name2 = None
                self.next_player_alfa_bravo_locked2 = False                

    def start_game(self, is_couple: bool) -> None:
        now = self.get_current_time()
        if is_couple:
            if self.queue_couples:
                self.current_player_couple = self.queue_couples.pop(0)
                self.ALFA_next_available = now + datetime.timedelta(minutes=self.T_mid)
                self.BRAVO_next_available = now + datetime.timedelta(minutes=self.T_total)
                self.current_player_alfa = self.current_player_couple
                self.current_player_bravo = self.current_player_couple
                self.couple_in_alfa = True
                self.couple_in_bravo = True
                self.player_start_times[self.current_player_couple['id']] = now
                if self.queue_singles:
                    self.next_player_alfa_bravo_id = self.queue_singles[0]['id']
                    self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id)
                    self.next_player_alfa_bravo_locked = True
                else:
                    self.next_player_alfa_bravo_id = self.queue_couples[0]['id'] if self.queue_couples else None
                    self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id) if self.next_player_alfa_bravo_id else None
                    self.next_player_alfa_bravo_locked = True if self.next_player_alfa_bravo_id else False
            else:
                raise ValueError("No couples in queue to start the game.")
        else:
            if self.queue_singles:
                self.current_player_alfa = self.queue_singles.pop(0)
                self.single_in_alfa = True
                self.ALFA_next_available = now + datetime.timedelta(minutes=self.T_single)
                self.player_start_times[self.current_player_alfa['id']] = now
                if self.queue_couples:
                    self.next_player_alfa_bravo_id = self.queue_couples[0]['id']
                    self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id)
                    self.next_player_alfa_bravo_locked = True
                else:
                    self.next_player_alfa_bravo_id = self.queue_singles[0]['id'] if self.queue_singles else None
                    self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id) if self.next_player_alfa_bravo_id else None
                    self.next_player_alfa_bravo_locked = True if self.next_player_alfa_bravo_id else False
            else:
                raise ValueError("No singles in queue to start the game.")
            
    def start_game2(self, is_couple: bool) -> None:
        now = self.get_current_time()
        if is_couple:
            if self.queue_couples2:
                self.current_player_couple2 = self.queue_couples2.pop(0)
                self.ALFA_next_available2 = now + datetime.timedelta(minutes=self.T_mid)   
                self.BRAVO_next_available2 = now + datetime.timedelta(minutes=self.T_total)
                self.current_player_alfa2 = self.current_player_couple2
                self.current_player_bravo2 = self.current_player_couple2
                self.couple_in_alfa2 = True
                self.couple_in_bravo2 = True
                self.player_start_times[self.current_player_couple2['id']] = now    
                if self.queue_singles2:
                    self.next_player_alfa_bravo_id2 = self.queue_singles2[0]['id']
                    self.next_player_alfa_bravo_name2 = self.get_player_name(self.next_player_alfa_bravo_id2)
                    self.next_player_alfa_bravo_locked2 = True
                else:   
                    self.next_player_alfa_bravo_id2 = self.queue_couples2[0]['id'] if self.queue_couples2 else None
                    self.next_player_alfa_bravo_name2 = self.get_player_name(self.next_player_alfa_bravo_id2) if self.next_player_alfa_bravo_id2 else None
                    self.next_player_alfa_bravo_locked2 = True if self.next_player_alfa_bravo_id2 else False
            else:
                raise ValueError("No couples in queue to start the game.")
        else:   
            if self.queue_singles2:
                self.current_player_alfa2 = self.queue_singles2.pop(0)
                self.single_in_alfa2 = True
                self.ALFA_next_available2 = now + datetime.timedelta(minutes=self.T_single)
                self.player_start_times[self.current_player_alfa2['id']] = now
                if self.queue_couples2:
                    self.next_player_alfa_bravo_id2 = self.queue_couples2[0]['id']
                    self.next_player_alfa_bravo_name2 = self.get_player_name(self.next_player_alfa_bravo_id2)
                    self.next_player_alfa_bravo_locked2 = True
                else:
                    self.next_player_alfa_bravo_id2 = self.queue_singles2[0]['id'] if self.queue_singles2 else None
                    self.next_player_alfa_bravo_name2 = self.get_player_name(self.next_player_alfa_bravo_id2) if self.next_player_alfa_bravo_id2 else None
                    self.next_player_alfa_bravo_locked2 = True if self.next_player_alfa_bravo_id2 else False
            else:
                raise ValueError("No singles in queue to start the game.")  
                

    def start_statico_game(self, pista: str) -> None:
        """Avvia un gioco sulla pista Statico specificata"""
        if not self.queue_statico:
            raise ValueError("Nessun giocatore in coda per Statico")
        
        if pista == 'delta' and not self.current_player_delta:
            self.current_player_delta = {
                'id': self.queue_statico[0]['id'],
                'arrival': self.get_current_time()
            }
            self.DELTA_next_available = self.get_current_time() + datetime.timedelta(minutes=self.T_statico)
            self.player_start_times[self.current_player_delta['id']] = self.get_current_time()
            # Rimuovi il giocatore dalla coda
            self.queue_statico.pop(0)
            
        elif pista == 'echo' and not self.current_player_echo:
            self.current_player_echo = {
                'id': self.queue_statico[0]['id'],
                'arrival': self.get_current_time()
            }
            self.ECHO_next_available = self.get_current_time() + datetime.timedelta(minutes=self.T_statico)
            self.player_start_times[self.current_player_echo['id']] = self.get_current_time()
            # Rimuovi il giocatore dalla coda
            self.queue_statico.pop(0)
        
        # Aggiorna il prossimo giocatore
        if self.queue_statico:
            self.next_player_statico_id = self.queue_statico[0]['id']
            self.next_player_statico_name = self.get_player_name(self.next_player_statico_id)
            self.next_player_statico_locked = True
        else:
            self.next_player_statico_id = None
            self.next_player_statico_name = None
            self.next_player_statico_locked = False

    def record_statico_game(self, game_time: float, pista: str) -> None:
        """Registra il tempo di gioco per la pista Statico specificata"""
        if pista == 'delta' and self.current_player_delta:
            player_id = self.current_player_delta['id']
            self.statico_history.append(game_time)
            self.update_averages()
            self.player_start_times.pop(player_id, None)
            self.current_player_delta = None
            
        elif pista == 'echo' and self.current_player_echo:
            player_id = self.current_player_echo['id']
            self.statico_history.append(game_time)
            self.update_averages()
            self.player_start_times.pop(player_id, None)
            self.current_player_echo = None

    def simulate_schedule(self) -> Dict[str, datetime.datetime]:
        """
        Simula la pianificazione degli ingressi a partire dallo stato attuale, considerando:
          - Un game (coppia o singolo) parte sempre da ALFA.
          - Se ALFA e BRAVO sono libere (ossia, BRAVO è libera al momento in cui ALFA diventa disponibile),
            il prossimo ingresso deve essere una coppia (se in coda).
          - Se ALFA è libera ma BRAVO non lo è, solo i singoli possono iniziare.
          - Notare che il tempo di un game singolo (T_single) potrebbe essere maggiore della finestra
            di tempo compresa tra il liberamento di ALFA (da un game coppia) e la fine dello stesso game coppia.
            Questo verrà preso in considerazione aggiornando l'orario in cui ALFA diventa disponibile.
          
        La funzione restituisce un dizionario in cui, per ogni elemento in coda (id),
        viene associato l'orario stimato d'ingresso.
        """
        now = self.get_current_time()
        # Il tempo di partenza della simulazione è il momento in cui ALFA è (o diventerà) disponibile
        self.ALFA_next_available = self.localize_time(self.ALFA_next_available)
        sim_time = max(now, self.ALFA_next_available)
        
        # Assicurati che BRAVO_next_available abbia il fuso orario
        self.BRAVO_next_available = self.localize_time(self.BRAVO_next_available)
        BRAVO_avail = self.BRAVO_next_available if self.BRAVO_next_available > sim_time else sim_time

        # Creiamo dei timedelta dai tempi medi (in minuti)
        dt_mid = datetime.timedelta(minutes=self.T_mid)
        dt_total = datetime.timedelta(minutes=self.T_total)
        dt_single = datetime.timedelta(minutes=self.T_single)

        # Facciamo una copia delle code in modo da non modificare lo stato reale
        couples = deepcopy(self.queue_couples)
        singles = deepcopy(self.queue_singles)

        estimated_times = {}  # key: id, value: orario stimato (datetime)

        # Simulazione: continuiamo finché rimane almeno un elemento in una delle code
        while couples or singles:
            # Se non ci sono coppie in coda, ma ci sono singoli, serviamo un singolo
            if not couples and singles:
                item = singles.pop(0)
                start_time = sim_time
                estimated_times[item['id']] = start_time
                sim_time = start_time + dt_single
                continue

            # Se, al momento in cui ALFA è libera, anche BRAVO lo è (o è già stata liberata),
            # allora possiamo avviare un game coppia se in coda.
            if BRAVO_avail <= sim_time:
                if couples:
                    item = couples.pop(0)
                    start_time = sim_time
                    estimated_times[item['id']] = start_time
                    # Quando parte un game coppia:
                    # - ALFA è occupata fino a T_mid (dopo di che si libera)
                    # - BRAVO resta occupata fino a T_total
                    sim_time = start_time + dt_mid
                    BRAVO_avail = start_time + dt_total
                    continue
                else:
                    # Se non ci sono coppie in coda, ma ci sono singoli, serviamo un singolo
                    if singles:
                        item = singles.pop(0)
                        start_time = sim_time
                        estimated_times[item['id']] = start_time
                        # Nota: il game singolo occupa ALFA per T_single, 
                        # che potrebbe essere maggiore della finestra tra liberazione di ALFA e fine di un game coppia.
                        sim_time = start_time + dt_single
                        # BRAVO non viene modificata in questo caso
                        continue
                    else:
                        break  # Non ci sono altri elementi in coda
            else:
                # Se ALFA è libera ma BRAVO è ancora occupata, solo i singoli possono iniziare
                if singles:
                    item = singles.pop(0)
                    start_time = sim_time
                    estimated_times[item['id']] = start_time
                    sim_time = start_time + dt_single
                    continue
                else:
                    # Se non ci sono singoli, dobbiamo attendere che BRAVO diventi libera
                    sim_time = BRAVO_avail
                    continue

        return estimated_times

    def simulate_schedule2(self) -> Dict[str, datetime.datetime]:
        now = self.get_current_time()
        sim_time = max(now, self.ALFA_next_available2)

        self.ALFA_next_available2 = self.localize_time(self.ALFA_next_available2)
        BRAVO_avail2 = self.BRAVO_next_available2 if self.BRAVO_next_available2 > sim_time else sim_time
        
        dt_mid2 = datetime.timedelta(minutes=self.T_mid)
        dt_total2 = datetime.timedelta(minutes=self.T_total)
        dt_single2 = datetime.timedelta(minutes=self.T_single)
        
        couples = deepcopy(self.queue_couples2)
        singles = deepcopy(self.queue_singles2) 

        estimated_times2 = {}

        while couples or singles:
            if not couples and singles:
                item = singles.pop(0)   
                start_time = sim_time
                estimated_times2[item['id']] = start_time
                sim_time = start_time + dt_single2
                continue
            
            if BRAVO_avail2 <= sim_time:
                if couples: 
                    item = couples.pop(0)
                    start_time = sim_time
                    estimated_times2[item['id']] = start_time
                    sim_time = start_time + dt_mid2
                    BRAVO_avail2 = start_time + dt_total2
                    continue
                else:
                    if singles:
                        item = singles.pop(0)
                        start_time = sim_time
                        estimated_times2[item['id']] = start_time
                        sim_time = start_time + dt_single2
                        continue
                    else:
                        break
            else:
                if singles:
                    item = singles.pop(0)
                    start_time = sim_time
                    estimated_times2[item['id']] = start_time
                    sim_time = start_time + dt_single2
                    continue    
                else:
                    sim_time = BRAVO_avail2
                    continue

        return estimated_times2
    

    def get_waiting_board(self) -> Tuple[
        List[Tuple[int, str, Union[datetime.datetime, str]]],
        List[Tuple[int, str, Union[datetime.datetime, str]]],
        List[Tuple[int, str, Union[datetime.datetime, str]]],
        List[Tuple[int, str, Union[datetime.datetime, str]]],
        List[Tuple[int, str, Union[datetime.datetime, str]]],
        List[Tuple[int, str, Union[datetime.datetime, str]]]  # Aggiungiamo la board statico
    ]:
        now = self.get_current_time()
        # Calcola i tempi stimati di ingresso
        est1 = self.simulate_schedule()
        est2 = self.simulate_schedule2()
        # --- Logica per next_player_alfa_bravo_id (usa est1) ---
        if not self.next_player_alfa_bravo_locked:
            # ... (logica esistente per next_player_alfa_bravo_id usando est1) ...
            # Caso speciale: se c'è una coppia in BRAVO e un singolo in ALFA, prioritizza le coppie
            if self.couple_in_bravo and self.single_in_alfa and self.queue_couples:
                self.next_player_alfa_bravo_id = self.queue_couples[0]['id']
                self.next_player_alfa_bravo_locked = True
            else:
                # Altrimenti, controlla il tempo stimato per ogni giocatore in coda
                next_player_found = False
                for queue_item in self.queue_couples + self.queue_singles:
                    estimated_time = est1.get(queue_item['id'])
                    if estimated_time:
                        minutes_to_entry = (estimated_time - now).total_seconds() / 60
                        # Imposta come prossimo se l'ingresso è imminente o è il primo della coda simulata
                        if minutes_to_entry <= 2 or not next_player_found:
                            self.next_player_alfa_bravo_id = queue_item['id']
                            self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id) # Aggiorna anche il nome
                            self.next_player_alfa_bravo_locked = True
                            next_player_found = True
                            # Se l'ingresso è imminente, blocca la scelta
                            if minutes_to_entry <= 2:
                                break # Esci dal ciclo una volta trovato un giocatore imminente


        # --- Logica per next_player_alfa_bravo_id2 (usa est2) --- (NUOVA)
        if not self.next_player_alfa_bravo_locked2:
            if self.couple_in_bravo2 and self.single_in_alfa2 and self.queue_couples2:
                self.next_player_alfa_bravo_id2 = self.queue_couples2[0]['id']
                self.next_player_alfa_bravo_name2 = self.get_player_name(self.next_player_alfa_bravo_id2) # Aggiorna anche il nome
                self.next_player_alfa_bravo_locked2 = True
            else:
                next_player_found2 = False
                for queue_item in self.queue_couples2 + self.queue_singles2:
                    estimated_time = est2.get(queue_item['id']) # Usa est2
                    if estimated_time:
                        minutes_to_entry = (estimated_time - now).total_seconds() / 60
                        if minutes_to_entry <= 2 or not next_player_found2:
                            self.next_player_alfa_bravo_id2 = queue_item['id']
                            self.next_player_alfa_bravo_name2 = self.get_player_name(self.next_player_alfa_bravo_id2) # Aggiorna anche il nome
                            self.next_player_alfa_bravo_locked2 = True
                            next_player_found2 = True
                            if minutes_to_entry <= 2:
                                break

            # --- Costruzione board ALFA/BRAVO 1 (usa est1) ---
        couples_board: List[Tuple[int, str, Union[datetime.datetime, str]]] = []
        for idx, item in enumerate(self.queue_couples):
            estimated = est1.get(item['id'], "N/D") # Default a "N/D" se non trovato
            display_time = "PROSSIMO INGRESSO" if item['id'] == self.next_player_alfa_bravo_id else estimated
            couples_board.append((idx + 1, item['id'], display_time))

        singles_board: List[Tuple[int, str, Union[datetime.datetime, str]]] = []
        for idx, item in enumerate(self.queue_singles):
            estimated = est1.get(item['id'], "N/D") # Default a "N/D"
            display_time = "PROSSIMO INGRESSO" if item['id'] == self.next_player_alfa_bravo_id else estimated
            singles_board.append((idx + 1, item['id'], display_time))

        # --- Costruzione board ALFA/BRAVO 2 (usa est2) --- (MODIFICATA)
        couples_board2: List[Tuple[int, str, Union[datetime.datetime, str]]] = []
        for idx, item in enumerate(self.queue_couples2):
            estimated = est2.get(item['id'], "N/D") # Usa est2, Default a "N/D"
            display_time = "PROSSIMO INGRESSO" if item['id'] == self.next_player_alfa_bravo_id2 else estimated
            couples_board2.append((idx + 1, item['id'], display_time))

        singles_board2: List[Tuple[int, str, Union[datetime.datetime, str]]] = []
        for idx, item in enumerate(self.queue_singles2):
            estimated = est2.get(item['id'], "N/D") # Usa est2, Default a "N/D"
            display_time = "PROSSIMO INGRESSO" if item['id'] == self.next_player_alfa_bravo_id2 else estimated
            singles_board2.append((idx + 1, item['id'], display_time))

            charlie_board: List[Tuple[int, str, Union[datetime.datetime, str]]] = []
            for idx, item in enumerate(self.queue_charlie):
                if item['id'] == self.next_player_charlie_id:
                    charlie_board.append((idx + 1, item['id'], "PROSSIMO INGRESSO"))
                else:
                    players_ahead = idx
                    estimated_time = now + datetime.timedelta(minutes=self.T_charlie * players_ahead)
                    charlie_board.append((idx + 1, item['id'], estimated_time))

        # Costruzione della board statico (nuova)
        statico_board: List[Tuple[int, str, Union[datetime.datetime, str]]] = []
        for idx, item in enumerate(self.queue_statico):
            if item['id'] == self.next_player_statico_id:
                statico_board.append((idx + 1, item['id'], "PROSSIMO INGRESSO"))
            else:
                # Per statico usiamo una logica simile a Charlie
                players_ahead = idx
                # Consideriamo che ci sono 2 piste (DELTA e ECHO) quindi il tempo si dimezza
                estimated_time = now + datetime.timedelta(minutes=(self.T_statico * players_ahead) / 2)
                statico_board.append((idx + 1, item['id'], estimated_time))

            # Esempio ricalcolo Charlie
        charlie_board: List[Tuple[int, str, Union[datetime.datetime, str]]] = []
        charlie_sim_time = max(now, self.localize_time(self.CHARLIE_next_available))
        for idx, item in enumerate(self.queue_charlie):
            start_time = charlie_sim_time
            if item['id'] == self.next_player_charlie_id:
                display_time = "PROSSIMO INGRESSO"
            else:
                display_time = start_time

            charlie_board.append((idx + 1, item['id'], display_time))
            # Il prossimo può iniziare solo dopo che questo finisce
            charlie_sim_time = start_time + datetime.timedelta(minutes=self.T_charlie)


        # Esempio ricalcolo Statico
        statico_board: List[Tuple[int, str, Union[datetime.datetime, str]]] = []
        delta_avail = self.localize_time(self.DELTA_next_available)
        echo_avail = self.localize_time(self.ECHO_next_available)
        for idx, item in enumerate(self.queue_statico):
            # Trova la prossima pista disponibile da ora in poi
            next_avail_time = min(max(now, delta_avail), max(now, echo_avail))
            start_time = next_avail_time

            if item['id'] == self.next_player_statico_id:
                display_time = "PROSSIMO INGRESSO"
            else:
                display_time = start_time

            statico_board.append((idx + 1, item['id'], display_time))

            # Aggiorna la disponibilità della pista usata
            if max(now, delta_avail) <= max(now, echo_avail):
                delta_avail = start_time + datetime.timedelta(minutes=self.T_statico)
            else:
                echo_avail = start_time + datetime.timedelta(minutes=self.T_statico)
            

        return couples_board, singles_board, couples_board2, singles_board2, charlie_board, statico_board

    def button_third_pressed(self) -> None:
        """Gestisce la pressione del pulsante metà percorso e libera la Pista ALPHA solo se c'era una coppia"""
        if self.current_player_alfa and self.current_player_alfa["id"].startswith("GIALLO"):
            self.third_button_pressed = True
            self.couple_in_alfa = False
            self.current_player_alfa = None    # Libera la pista ALPHA
            self.next_player_alfa_bravo_id = None         # Correzione: resettiamo next_player_alfa_bravo_id
        else:
            raise ValueError("Non c'è una coppia in ALFA.")

    def button_third_pressed2(self) -> None:
        """Gestisce la pressione del pulsante metà percorso 2 e libera ALFA 2 solo se c'era una coppia VIOLA"""
        if self.current_player_alfa2 and self.current_player_alfa2.get("id", "").startswith("VIOLA"):
            now = self.get_current_time()
            self.third_button_pressed2 = True
            self.couple_in_alfa2 = False
            self.current_player_alfa2 = None # Libera la pista
            self.ALFA_next_available2 = now # Rende ALFA 2 disponibile
        else:
            current_player_id = self.current_player_alfa2.get("id", "Nessuno") if self.current_player_alfa2 else "Nessuno"
            raise ValueError("Non c'è una Coppia 2 (Viola) in ALFA 2.")


    def can_stop_couple(self) -> bool:
        "Verifica se una coppia può fermarsi"
        return self.third_button_pressed
    
    def can_stop_couple2(self) -> bool:
        return self.third_button_pressed2 and self.current_player_bravo2 and self.current_player_bravo2.get("id", "").startswith("VIOLA")


    def skip_player(self, player_id: str) -> None:
        """Sposta un giocatore nella lista degli skippati (Alfa/Bravo)"""
        player = next((c for c in self.queue_couples if c['id'] == player_id), None)
        if player:
            self.queue_couples.remove(player)
            self.skipped_couples.append(player)
            # Set the next player to the next couple in the queue
            if self.queue_couples:
                self.next_player_alfa_bravo_id = self.queue_couples[0]['id']
                self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id)
                self.next_player_alfa_bravo_locked = True
            else:
                self.next_player_alfa_bravo_id = None
                self.next_player_alfa_bravo_name = None
                self.next_player_alfa_bravo_locked = False
        else:
            player = next((s for s in self.queue_singles if s['id'] == player_id), None)
            if player:
                self.queue_singles.remove(player)
                self.skipped_singles.append(player)
                # Set the next player to the next single in the queue
                if self.queue_singles:
                    self.next_player_alfa_bravo_id = self.queue_singles[0]['id']
                    self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id)
                    self.next_player_alfa_bravo_locked = True
                elif self.queue_couples:
                    self.next_player_alfa_bravo_id = self.queue_couples[0]['id']
                    self.next_player_alfa_bravo_name = self.get_player_name(self.next_player_alfa_bravo_id)
                    self.next_player_alfa_bravo_locked = True
                else:
                    self.next_player_alfa_bravo_id = None
                    self.next_player_alfa_bravo_name = None
                    self.next_player_alfa_bravo_locked = False

    def skip_player2(self, player_id: str) -> None:
        """Sposta un giocatore nella lista degli skippati (Alfa/Bravo)"""
        player = next((c for c in self.queue_couples2 if c['id'] == player_id), None)
        if player:
            self.queue_couples2.remove(player)
            self.skipped_couples2.append(player)    
            if self.queue_couples2:
                self.next_player_alfa_bravo_id2 = self.queue_couples2[0]['id']
                self.next_player_alfa_bravo_name2 = self.get_player_name(self.next_player_alfa_bravo_id2)
                self.next_player_alfa_bravo_locked2 = True
            else:
                self.next_player_alfa_bravo_id2 = None  
                self.next_player_alfa_bravo_name2 = None
                self.next_player_alfa_bravo_locked2 = False 
        else:
            player = next((s for s in self.queue_singles2 if s['id'] == player_id), None)
            if player:
                self.queue_singles2.remove(player)
                self.skipped_singles2.append(player)    
                if self.queue_singles2:
                    self.next_player_alfa_bravo_id2 = self.queue_singles2[0]['id']
                    self.next_player_alfa_bravo_name2 = self.get_player_name(self.next_player_alfa_bravo_id2)
                    self.next_player_alfa_bravo_locked2 = True
                elif self.queue_couples2:
                    self.next_player_alfa_bravo_id2 = self.queue_couples2[0]['id']
                    self.next_player_alfa_bravo_name2 = self.get_player_name(self.next_player_alfa_bravo_id2)
                    self.next_player_alfa_bravo_locked2 = True
                else:   
                    self.next_player_alfa_bravo_id2 = None
                    self.next_player_alfa_bravo_name2 = None
                    self.next_player_alfa_bravo_locked2 = False

    def skip_charlie_player(self, player_id: str) -> None:
        """Sposta un giocatore nella lista degli skippati (Charlie)"""
        player = next((p for p in self.queue_charlie if p['id'] == player_id), None)
        if player:
            self.queue_charlie.remove(player)
            self.skipped_charlie.append(player)
            # Set the next player to the next Charlie in the queue
            if self.queue_charlie:
                self.next_player_charlie_id = self.queue_charlie[0]['id']
                self.next_player_charlie_name = self.get_player_name(self.next_player_charlie_id)
                self.next_player_charlie_locked = True
            else:
                self.next_player_charlie_id = None
                self.next_player_charlie_name = None
                self.next_player_charlie_locked = False

    def skip_statico_player(self, player_id: str) -> None:
        """Sposta un giocatore nella lista degli skippati (Statico)"""
        player = next((p for p in self.queue_statico if p['id'] == player_id), None)
        if player:
            self.queue_statico.remove(player)
            self.skipped_statico.append(player)
            # Set the next player to the next Statico in the queue
            if self.queue_statico:
                self.next_player_statico_id = self.queue_statico[0]['id']
                self.next_player_statico_name = self.get_player_name(self.next_player_statico_id)
                self.next_player_statico_locked = True
            else:
                self.next_player_statico_id = None
                self.next_player_statico_name = None
                self.next_player_statico_locked = False            

    def restore_skipped(self, player_id: str) -> None:
        """Ripristina un giocatore skippato in coda come priorità"""
        player = next((c for c in self.skipped_couples if c['id'] == player_id), None)
        if player:
            self.skipped_couples.remove(player)
            self.queue_couples.insert(0, player)
        else:
            player = next((s for s in self.skipped_singles if s['id'] == player_id), None)
            if player:
                self.skipped_singles.remove(player)
                self.queue_singles.insert(0, player)
            else:
                player = next((p for p in self.skipped_charlie if p['id'] == player_id), None)
                if player:
                    self.skipped_charlie.remove(player)
                    self.queue_charlie.insert(0, player)
                

    def restore_skipped_as_next(self, player_id: str) -> None:
        """Ripristina un giocatore skippato come prossimo nella coda"""
        # Cerca in tutte le liste di skippati
        player = next((c for c in self.skipped_couples if c['id'] == player_id), None)
        if player:
            self.skipped_couples.remove(player)
            self.queue_couples.insert(0, player)
            self.next_player_alfa_bravo_id = player_id
            self.next_player_alfa_bravo_locked = True
            return

        player = next((s for s in self.skipped_singles if s['id'] == player_id), None)
        if player:
            self.skipped_singles.remove(player)
            self.queue_singles.insert(0, player)
            self.next_player_alfa_bravo_id = player_id
            self.next_player_alfa_bravo_locked = True
            return
        
        player = next((p for p in self.skipped_couples2 if p['id'] == player_id), None)
        if player:
            self.skipped_couples2.remove(player)
            self.queue_couples2.insert(0, player)
            self.next_player_alfa_bravo_id2 = player_id
            self.next_player_alfa_bravo_locked2 = True
            return  
        
        player = next((s for s in self.skipped_singles2 if s['id'] == player_id), None) 
        if player:
            self.skipped_singles2.remove(player)
            self.queue_singles2.insert(0, player)
            self.next_player_alfa_bravo_id2 = player_id
            self.next_player_alfa_bravo_locked2 = True
            return  
        
        player = next((p for p in self.skipped_charlie if p['id'] == player_id), None)
        if player:
            self.skipped_charlie.remove(player)
            self.queue_charlie.insert(0, player)
            self.next_player_charlie_id = player_id
            self.next_player_charlie_name = self.get_player_name(player_id)
            self.next_player_charlie_locked = True
            return
        
        # Aggiungi questo blocco per gestire gli skippati statico
        player = next((p for p in self.skipped_statico if p['id'] == player_id), None)
        if player:
            self.skipped_statico.remove(player)
            self.queue_statico.insert(0, player)
            self.next_player_statico_id = player_id
            self.next_player_statico_name = self.get_player_name(player_id)
            self.next_player_statico_locked = True
            return
        
        raise ValueError(f"Player {player_id} not found in any skipped list")

    def start_charlie_game(self) -> None:
        """Avvia un gioco sulla pista Charlie"""
        if self.next_player_charlie_id:
            self.current_player_charlie = {'id': self.next_player_charlie_id, 'arrival': self.get_current_time()}
            self.CHARLIE_next_available = self.get_current_time() + datetime.timedelta(minutes=self.T_charlie)
            self.player_start_times[self.current_player_charlie['id']] = self.get_current_time()
            self.player_in_charlie = True
            # Rimuovi il giocatore dalla coda
            self.queue_charlie = [p for p in self.queue_charlie if p['id'] != self.next_player_charlie_id]
            # Imposta il prossimo giocatore
            if self.queue_charlie:
                self.next_player_charlie_id = self.queue_charlie[0]['id']
                self.next_player_charlie_name = self.get_player_name(self.next_player_charlie_id)
                self.next_player_charlie_locked = True
            else:
                self.next_player_charlie_id = None
                self.next_player_charlie_name = None
                self.next_player_charlie_locked = False

    def get_durations(self) -> Dict[str, str]:
        """Restituisce le durate dei giocatori attuali in pista formattate in minuti:secondi"""
        durations = {}
        now = self.get_current_time()
        if self.current_player_alfa:
            player_id = self.current_player_alfa['id']
            start_time = self.player_start_times.get(player_id)
            if start_time:
                duration_seconds = (now - start_time).total_seconds()
                minutes = int(duration_seconds // 60)
                seconds = int(duration_seconds % 60)
                durations['alfa'] = f"{minutes:02}:{seconds:02}"
        if self.current_player_bravo:
            player_id = self.current_player_bravo['id']
            start_time = self.player_start_times.get(player_id)
            if start_time:
                duration_seconds = (now - start_time).total_seconds()
                minutes = int(duration_seconds // 60)
                seconds = int(duration_seconds % 60)
                durations['bravo'] = f"{minutes:02}:{seconds:02}"

        if self.current_player_alfa2:
            player_id = self.current_player_alfa2['id']
            start_time = self.player_start_times.get(player_id)
            if start_time:
                duration_seconds = (now - start_time).total_seconds()
                minutes = int(duration_seconds // 60)
                seconds = int(duration_seconds % 60)
                durations['alfa2'] = f"{minutes:02}:{seconds:02}"   

        if self.current_player_bravo2:
            player_id = self.current_player_bravo2['id']
            start_time = self.player_start_times.get(player_id)
            if start_time:
                duration_seconds = (now - start_time).total_seconds()
                minutes = int(duration_seconds // 60)
                seconds = int(duration_seconds % 60)
                durations['bravo2'] = f"{minutes:02}:{seconds:02}"  

        if self.current_player_charlie:
            player_id = self.current_player_charlie['id']
            start_time = self.player_start_times.get(player_id)
            if start_time:
                duration_seconds = (now - start_time).total_seconds()
                minutes = int(duration_seconds // 60)
                seconds = int(duration_seconds % 60)
                durations['charlie'] = f"{minutes:02}:{seconds:02}"
        if self.current_player_delta:
            player_id = self.current_player_delta['id']
            start_time = self.player_start_times.get(player_id)
            if start_time:
                duration_seconds = (now - start_time).total_seconds()
                minutes = int(duration_seconds // 60)
                seconds = int(duration_seconds % 60)
                durations['delta'] = f"{minutes:02}:{seconds:02}"
        if self.current_player_echo:
            player_id = self.current_player_echo['id']
            start_time = self.player_start_times.get(player_id)
            if start_time:
                duration_seconds = (now - start_time).total_seconds()
                minutes = int(duration_seconds // 60)
                seconds = int(duration_seconds % 60)
                durations['echo'] = f"{minutes:02}:{seconds:02}"        
        return durations

    def delete_player(self, player_id: str) -> None:
        """Elimina un giocatore dalla coda"""
        self.queue_couples = [p for p in self.queue_couples if p['id'] != player_id]
        self.queue_singles = [p for p in self.queue_singles if p['id'] != player_id]
        self.queue_couples2 = [p for p in self.queue_couples2 if p['id'] != player_id]
        self.queue_singles2 = [p for p in self.queue_singles2 if p['id'] != player_id]
        self.queue_charlie = [p for p in self.queue_charlie if p['id'] != player_id]
        self.queue_statico = [p for p in self.queue_statico if p['id'] != player_id]
        self.skipped_couples = [p for p in self.skipped_couples if p['id'] != player_id]
        self.skipped_singles = [p for p in self.skipped_singles if p['id'] != player_id]
        self.skipped_couples2 = [p for p in self.skipped_couples2 if p['id'] != player_id]
        self.skipped_singles2 = [p for p in self.skipped_singles2 if p['id'] != player_id]
        self.skipped_charlie = [p for p in self.skipped_charlie if p['id'] != player_id]
        self.skipped_statico = [p for p in self.skipped_statico if p['id'] != player_id]

        # Check if the deleted player was the next player in the queue
        if self.next_player_alfa_bravo_id == player_id:
            self.next_player_alfa_bravo_id = None
            self.next_player_alfa_bravo_name = None
            self.next_player_alfa_bravo_locked = False
            self.update_next_player()

        if self.next_player_alfa_bravo_id2 == player_id:
            self.next_player_alfa_bravo_id2 = None
            self.next_player_alfa_bravo_name2 = None
            self.next_player_alfa_bravo_locked2 = False
            self.update_next_player2()

        if self.next_player_charlie_id == player_id:
            self.next_player_charlie_id = None
            self.next_player_charlie_name = None
            self.next_player_charlie_locked = False
            self.update_next_player()

         # Check if the deleted player was the next player in the queue
        if self.next_player_statico_id == player_id:
            self.next_player_statico_id = None
            self.next_player_statico_name = None
            self.next_player_statico_locked = False
            self.update_next_player()
        
        

if __name__ == '__main__':
    backend = GameBackend()
    
    # Assicuriamoci che, al momento, non ci sia un game in corso
    # Aggiungiamo alcune coppie e alcuni singoli in coda
    # backend.add_couple("GIALLO-01")
    # backend.add_single("BLU-01")
    # backend.add_couple("GIALLO-02")
    # backend.add_single("BLU-02")
    # backend.add_couple("GIALLO-03")
    # backend.add_single("BLU-03")
    print("Tabellone Coppie (Gialli):")
    # Assicuriamoci che, al momento, non ci sia un game in corso
    now = datetime.datetime.now()
    backend.ALFA_next_available = now
    backend.BRAVO_next_available = now
    backend.ALFA2_next_available = now
    backend.BRAVO2_next_available = now
    # Otteniamo il tabellone d'attesa
    couples_board, singles_board, charlie_board, statico_board, couples2_board, singles2_board = backend.get_waiting_board()
    print("Tabellone Coppie (Gialli):")
    for pos, cid, time_est in couples_board:
      time_str = time_est.strftime('%H:%M:%S') if isinstance(time_est, datetime.datetime) else time_est if time_est else 'N/D'
    print(f"{pos}. {cid} - Ingresso stimato: {time_str}")
    print("\nTabellone Coppie (Blu):")
    for pos, cid, time_est in couples2_board:
      time_str = time_est.strftime('%H:%M:%S') if isinstance(time_est, datetime.datetime) else time_est if time_est else 'N/D'
    print(f"{pos}. {cid} - Ingresso stimato: {time_str}")
    print("\nTabellone Singoli (Blu):")
    for pos, sid, time_est in singles_board:
      time_str = time_est.strftime('%H:%M:%S') if isinstance(time_est, datetime.datetime) else time_est if time_est else 'N/D'
    print(f"{pos}. {sid} - Ingresso stimato: {time_str}")
    print("\nTabellone Charlie (Verde):")
    for pos, cid, time_est in charlie_board:
      time_str = time_est.strftime('%H:%M:%S') if isinstance(time_est, datetime.datetime) else time_est if time_est else 'N/D'
    print(f"{pos}. {cid} - Ingresso stimato: {time_str}")
    print("\nTabellone Statico (Rosso):")
    for pos, cid, time_est in statico_board:
      time_str = time_est.strftime('%H:%M:%S') if isinstance(time_est, datetime.datetime) else time_est if time_est else 'N/D'
    print(f"{pos}. {cid} - Ingresso stimato: {time_str}")

