
from SteuerungÜbung import Steuerung 


class Exercises: 
    def __init__(self, motor_controller): #MotionPattern
        self.Muster = Steuerung(motor_controller) #importieren Steuerung mit dem MotorController aus logic je nachdem welche Übung ausgewählt wird wird in Steuerung die body_head verwendet wenn
                                                       #die Bewegung nur hoch und runter ist, body_head_pause wenn die Bewegung Hoch runter mit Pausen ist oder asynchron wenn wir zum Beispiel zwei
                                                       #Bewegungen nach oben haben bevor wir wieder nach unten fahren



    def left(self, duration, stop_event=None): #keine Pause
        self.Muster.body_head(
            body_top=20, body_bottom=0,  #nicht sonderlich viel Raum würde immer Werte zwischen 0 und 25 anstreben oder es könnte passieren das es zu ungewollten Kontakt zwischen Material kommt
            head_top=20, head_bottom=0,
            move_up_time=4,
            move_down_time=6,
            total_runtime=duration,
            stop_event=stop_event
        )
        
    def Dankbarkeitsübung(self, duration, stop_event=None):
        self.Muster.body_head(
            body_top=20, body_bottom=0,
            head_top=20, head_bottom=0,
            move_up_time=4,
            move_down_time=4,
            total_runtime=duration,
            stop_event=stop_event
        )
        
    def middle(self, duration, stop_event=None): #Pause oben
        self.Muster.body_head_pause(
            body_top=20, body_bottom=0,
            head_top=20, head_bottom=0,
            move_up_time=4, pause_top=7,
            move_down_time=8, pause_bottom=0,
            total_runtime=duration,
            stop_event=stop_event
        )


    def right(self, duration, stop_event=None):
        sequence = [
            {
                "batch": 0,
                "body_pos": 12,
                "head_pos": 12,
                "move_time": 3,
                "pause_after": 0
            },
            {
                "batch": 1,
                "body_pos": 20,
                "head_pos": 20,
                "move_time": 1.5,
                "pause_after": 1.0
            },
            {
                "batch": 2,
                "body_pos": 0,
                "head_pos": 0,
                "move_time": 5,
                "pause_after": 0
            },
            {
                "batch": 0,
                "body_pos": 0,
                "head_pos": 0,
                "move_time": 0,
                "pause_after": 0
            }
        ]



        self.Muster.execute_sequence(
            sequence=sequence,
            total_runtime=duration,
            stop_event=stop_event
        )

  
  
  
  
    def custom(self, duration, stop_event=None,  #wenn in der Auswahl für die Pausen 0 gesetzt wird werden nur die Animationen für das hoch und runter fahren abgespielt
               move_up_time=4, pause_top_time=2,
               move_down_time=4, pause_bottom_time=2):
        self.Muster.body_head_pause(
            body_top=20, body_bottom=0,
            head_top=20, head_bottom=0,
            move_up_time=move_up_time,
            pause_top=pause_top_time,
            move_down_time=move_down_time,
            pause_bottom=pause_bottom_time,
            total_runtime=duration,
            stop_event=stop_event
        )



    def position_zero(self, duration=3, stop_event=None): 
        self.Muster.body_head(
            body_top=0, body_bottom=0,
            head_top=0, head_bottom=0,
            move_up_time=0,  #duration
            move_down_time=duration, #0
            total_runtime=duration,
            stop_event=stop_event
        )
        
    def movebackup(self, duration=3, stop_event=None): 
        self.Muster.body_head(
            body_top=5, body_bottom=0,
            head_top=15, head_bottom=0,
            move_up_time=duration,  #duration
            move_down_time=0, #0
            total_runtime=duration,
            stop_event=stop_event
        )

