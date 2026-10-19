
#main ruft die jeweilige Übung in logic auf je nachdem welche Auswahl getroffen wurde
#logic definiert alle Komponenten für den AnimationPlayer und die Übung logic startet außerdem den Motor thread und gibt den MotorController vor
#Motor Funktionen enthält die konkreten Werte für die jeweilige Übung übergibt diese Werte und den MotorController an die Steuerung welche dann die Befehle losschickt und den jweiligen Animationbatch vorgibt


from webp_sequence_player import WebPSequencePlayer
import pygame
import threading
from MotorC import MotorController
from MotorFunktionen import Exercises
import os
from starting_pos_ui import MoveToStartPos 



#globales Motorsystem in allen Instanzen liegt der selbe MotorController vor
motor_controller = MotorController()
exercises = Exercises(motor_controller)



def _get_screen_size():
    screen = pygame.display.get_surface()
    if screen:
        return screen.get_size()
    return (1920, 1080)



#startet motorthread Übung und Animation
def run_exercise(player, motor_function, duration, motor_args=None):
    stop_event = threading.Event() 
    motor_thread = None

    motion_pattern = exercises.Muster 
                                               
    player.set_motion_pattern(motion_pattern) #kann man so verstehen das der AnimationPlayer einen Verweis bekommt wo die Steuerung liegt und was in der Steuerung passiert
                                              #wenn ein Wert in der Steuerung aktualisiert wird und wir rufen diesen Wert in dem Animationplayer auf dann haben wir den genau selben Wert

    if motor_args:
        motor_thread = threading.Thread(
            target=motor_function,   
            args=(duration, stop_event),   #wenn der Motorthread aufgerufen wird dann wird die exercises.Auswahl Funktion ausgeführt was die Referenzierung zu Exercises(motor_controller) enthält
            kwargs=motor_args              #es wird also die spezifische Übung in Exercises aufgerufen die auf Steuerung zugreift 
                                           #der MotorController der die Befehle schickt wird an Steuerung übergeben und Steuerung schickt die Befehle solange die Kondition für die Duration nicht erfüllt ist 
        )
    else:
        motor_thread = threading.Thread(   
            target=motor_function,
            args=(duration, stop_event)
        )

    try:
        motor_thread.daemon = True
        motor_thread.start()
        print("Motor thread started")

        print("Starting animation...")
        player.start(duration)        #AnimationPlayer spielt Animationen solange Kondition für Duration erfüllt ist die jeweilige Batchindex wird in der Steuerung gesetzt und mit 
                                      #player.set_motion_pattern(motion_pattern) an den Animationplayer übergeben
        print("Animation finished")

        motor_thread.join(timeout=duration + 10) 

        if motor_thread.is_alive():
            print("Motor thread still running, stopping...")
            stop_event.set()
            motor_controller.disable_motors()
            


    except KeyboardInterrupt:
        print("Stopping exercise...")
        stop_event.set()
        motor_controller.disable_motors()
        raise
    finally:
        if player:
            try:
                player.cleanup()
            except:
                pass
        motor_controller.disable_motors()
        print("Cleanup done")




def handle_left(cache, duration):
    print(f"handle_left called with duration={duration}")
    
    

#Ich hatte es ursprünglich so ausgelegt das nur eine kontinuierliche Animation eingeplant ist dann hätte man diese Aufteilung in Batches nicht gebraucht
#was wesentlich simpler gewesen wäre. Da Animationen aber so ausgelegt sind das -> initiale Animation -> Standbild jeweiliger Animation -> neue Phase #(zum Beispielt runterfahren

    

    sequence = [ #immer clip und Framerate
        ("assets/4x6anfinal/in.webp", 24),   #initale Animation nach oben fahren    
        ("assets/4x6anfinal/in2.webp", 5),   #Standbild oben
        ("assets/4x6anfinal/out.webp", 24),     #initale Animation nach unten fahren
        ("assets/4x6anfinal/out2.webp", 5)  #Standbild unten
    ]

    batches = [
        [0, 1],   #gibt Reihenfolge vor ein Batch ist immer für eine Phase der Übung verantwortlich so können wir die Animation aus unterschiedlichen clips zusammensetzen
        [2, 3],   #je nachdem wie komplex die Übung ist
    ]

    audio = "assets_mp3/audio/Meditation.mp3"
    
    if pygame.mixer.get_init():
        pygame.mixer.stop()

    screen_width, screen_height = _get_screen_size()

    player = WebPSequencePlayer(
        sequence, cache,
        size=(screen_width, screen_height),
        audio=audio
    )

    player.set_batches(batches)
    run_exercise(player, exercises.left, duration)






def handle_middle(cache, duration):
    print(f"handle_middle called with duration={duration}")

    sequence = [
        ("assets/4x7x8final/in.webp", 24),
        ("assets/4x7x8final/in2.webp", 5),
        ("assets/4x7x8final/hold.webp", 24),   #("assets/4x7x8final/478hold.webp", 1.3),
        ("assets/4x7x8final/out3.webp", 24),
        ("assets/4x7x8final/out2.webp", 5)
    ]



    batches = [
        [0,1],  #hoch
        [2],  #Pause
        [3,4],  # unten    
        ]

    audio = "assets_mp3/audio/bowlsinging.mp3"

    if pygame.mixer.get_init():
        pygame.mixer.stop()

    screen_width, screen_height = _get_screen_size()

    player = WebPSequencePlayer(
        sequence, cache,
        size=(screen_width, screen_height),
        audio=audio
    )

    player.set_batches(batches)
    run_exercise(player, exercises.middle, duration)




def handle_right(cache, duration):
    print(f"handle_right called with duration={duration}")

    
    sequence = [
        ("assets/4x6anfinal/in.webp", 24),    
        ("assets/4x6anfinal/in2.webp", 5),   
        ("assets/4x6anfinal/in3.webp", 24),      
        ("assets/4x6anfinal/in2.webp", 5),   
        ("assets/4x6anfinal/out.webp", 24),    
        ("assets/4x6anfinal/out2.webp", 5) 
    ]

 #da asynchrone Übung 2 Batches für das einatmen
    batches = [
        [0, 1],   #einatmen
        [2, 3],   #einatmen
        [4, 5],   #ausatmen 
    ]

    audio = "assets_mp3/audio/Meditation.mp3" #Mixed.mp3"

    if pygame.mixer.get_init():
        pygame.mixer.stop()

    screen_width, screen_height = _get_screen_size()



    player = WebPSequencePlayer(
        sequence, cache,
        size=(screen_width, screen_height),
        audio=audio
    )

    player.set_batches(batches)
    run_exercise(player, exercises.right, duration)
    

def handle_Dankbarkeitsübung(cache, duration,audio):
    print(f"handle_right called with duration={duration}")



    sequence = [
            ("assets/sleep_animation/AugenZuAtemen1.webp", 24),
            ("assets/sleep_animation/AugenZU1.webp", 5),
            ("assets/sleep_animation/AugenZuAtemen.webp", 24),
            ("assets/sleep_animation/AugenZU.webp", 5),

    ]


    batches = [
        [0, 1],    #Einatmen geschlossenen Augen
        [2, 3],    #Ausatmen geschlossenen Augen
                   #könnte im anderen System erwägen Option hinzuzufügen die steuert ob Animationen mit geschlossenen oder geöffneten Augen stattfinden sollen

    ]


    audioloop = audio.play("Dankbarkeitsübung3") #einzige Übung die unterschiedliche Audios für unterschieldiche Sprachen benötigt
                                                #Audios für die anderen Übungen sind alle identisch



    screen_width, screen_height = _get_screen_size()



    player = WebPSequencePlayer( #Duration wird manuell in main gesetzt muss an Länge des Audios der Dankbarkeitsübung angepasst werden deshalb auch keine DurationAuswahl
        sequence, cache,
        size=(screen_width, screen_height),
        audio=audioloop
    )

    player.set_batches(batches)
    run_exercise(player, exercises.Dankbarkeitsübung, duration)    





def handle_custom(cache, duration, custom_params):
    print(f"handle_custom called with duration={duration}")
    print(f"custom_params={custom_params}")

    move_up_time = custom_params.get("move_up", 4.0)
    pause_top_time = custom_params.get("pause_top", 2.0)
    move_down_time = custom_params.get("move_down", 4.0)
    pause_bottom_time = custom_params.get("pause_bottom", 2.0)

    #fps_in = 12 / move_up_time
    fps_hold1 = 9 / pause_top_time if pause_top_time > 0 else 0  #Überlegungen für die Steuerung der fps Rate wenn in custum ein Wert gesetzt wird so würde für jede Auswahl für Einatmen, Ausatmen,
    #fps_out = 18 / move_down_time                               #Pausen die Animation entsprechend langsamer oder schneller gemacht weerden wird nicht verwendet da Aufbau jetzt initale Animation  
    fps_hold2 = 9 / pause_bottom_time if pause_bottom_time > 0 else 0    #und Standbild ist. Könnte aber spannend sein sollten zu späteren Zeitpunkten doch nochmal komplette Animationen erstellt werden die 
                                                                         #ohne Standbilder operieren
    #sequence = [
    #    ("assets/4x7x8/in.webp", fps_in),
    #    ("assets/4x7x8/hold.webp", fps_hold1),
    #    ("assets/4x7x8/out.webp", fps_out),
    #    ("assets/4x7x8/hold.webp", fps_hold2)
    #]


    #sequence = [
    #    ("assets/4x7x8final/in.webp", 24),
    #    ("assets/4x7x8final/in2.webp", 1),
    #    ("assets/4x7x8final/478hold.webp", fps_hold1),
    #    ("assets/4x7x8final/out.webp", 24),
    #    ("assets/4x7x8final/out2.webp", 1),
    #    ("assets/4x7x8final/478hold.webp", fps_hold2)
    #]
    
    sequence = [
        ("assets/4x7x8final/in.webp", 24),
        ("assets/4x7x8final/in2.webp", 5),
        ("assets/4x7x8final/478hold.webp", 24),
        ("assets/4x7x8final/out.webp", 24),
        ("assets/4x7x8final/out2.webp", 5),
        ("assets/4x7x8final/478hold.webp", 24)
    ]

     

    batches = [   #in der custumAuswahl wird kontrolliert welche Werte übergeben werden also ob Pausen ausgeführt werden oder nicht
        [0,1],  
        [2],  
        [3,4],  
        [5],  
    ]

    audio = custom_params.get("audio")
    if not audio or not os.path.exists(audio):
        audio = "assets_mp3/audio/middle.mp3"
        print(f"Audio not found, using {audio}")

    if pygame.mixer.get_init():
        pygame.mixer.stop()

    screen_width, screen_height = _get_screen_size()

    player = WebPSequencePlayer(
        sequence, cache,
        size=(screen_width, screen_height),
        audio=audio
    )

    player.set_batches(batches)



    motor_kwargs = {
        "move_up_time": move_up_time,
        "pause_top_time": pause_top_time,
        "move_down_time": move_down_time,
        "pause_bottom_time": pause_bottom_time
    }

    run_exercise(player, exercises.custom, duration, motor_args=motor_kwargs)


        
def starting_motor(cache, audio, screen, clock):
    stop_event = threading.Event()
    
    ui_duration = 34       # Länge Erklärung 
    motor_duration = 3     # Dauer Motorbewegung fährt runter wenn übersrpungen wird nach runterfahren Übung gestartet
    
    try:
        #Audio starten
        audio.play("Start")
        
        
        starting_pos_ui = MoveToStartPos(screen, clock, audio)
        

        motor_thread = threading.Thread(
            target=exercises.position_zero,
            args=(motor_duration, stop_event)   # 4s statt 34s jetzt
        )
        motor_thread.start()
        
        #Bildschirm starting pos läuft 34 s außer Überspringen wird gedrückt
        starting_pos_ui.run(ui_duration)
        
        # Wenn übersprungen Audio wird gestoppt
        if starting_pos_ui.skip_requested:
            print("? Erklrung bersprungen  Audio gestoppt")
            audio.stop()
        
        #
        motor_thread.join()
        
        print("? Starting Position abgeschlossen")
        return True
        
    except Exception as e:
        print(f"? Fehler bei Starting Position: {e}")
        stop_event.set()
        motor_controller.disable_motors()
        return False
    finally:
        pygame.event.clear()





def handle_movebackup(cache, duration): #nachdem Übung beendet fährt hoch damit wenn Gerätt ausgeschaltet wird homing durchgeführt werden kann beim nächsten Start eher Alibi
    #Lösung auf Board muss homing angepasst werden
    print(f"handle_left called with duration={duration}")
    
    duration= 3
    

    

    sequence = [ #immer clip und Framerate
        ("assets/4x6anfinal/in.webp", 24),   #initale Animation nach oben fahren    
        ("assets/4x6anfinal/in2.webp", 5),   #Standbild oben

    ]

    batches = [
        [0, 1], 

    ]

    audio = "assets_mp3/audio/still.mp3" #keine existierende Audio nur als Platzhalter gedacht

    if pygame.mixer.get_init():
        pygame.mixer.stop()

    screen_width, screen_height = _get_screen_size()

    player = WebPSequencePlayer(
        sequence, cache,
        size=(screen_width, screen_height),
        audio=audio
    )

    player.set_batches(batches)
    run_exercise(player, exercises.movebackup, duration)
