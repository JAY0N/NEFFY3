#Atemerkennung derzeit wenn in den ersten 30 Sekunden kein Input kommt schaltet es einfach ab weil auf dem Board nur 30 Sekunden schaut besser wäre gewesen eine Menge an Ein Ausatmen unabhängig von 
#der Zeit zu verwenden

import pygame
import sys
import time
import threading
from intro import IntroMode 
from language_ui import Language 
from volume_ui import Volume   
from evaluation_ui import Evaluation  
from pre_evaluation_ui import PreEvaluation 
from greeting_ui import Begrüßung 
from logic import handle_left, handle_middle, handle_right, handle_custom, handle_Dankbarkeitsübung, starting_motor, motor_controller ,handle_movebackup
from animation_cache import AnimationCache
from audio_manager import AudioManager
from logger import DataLogger
from language_manager import lang
from navigation import ButtonNavigation
import json
import os
import traceback
from sleep import SleepMode 
from Atemerkennung import Stressidentifikation

import subprocess #damit die Erstellung der Analysedatei am Anfang des Programms durchgeführt werden kann 


def run_analyze_logs(): #analyze_logs wird zu jedem Programmstart ausgeführt hat den Nachtteil das eine Sitzung immer nicht enthalten sein wird 
    try:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
        script = os.path.join(base, "src", "analyze_logs.py")
        if not os.path.exists(script):
            return False
        result = subprocess.run(
            ["python3", script],
            cwd=base,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return True
            print("success")
        else:
            return False
    except Exception as e:
        return False
        
        
def cooldown(seconds): ##Damit nicht sofort Aufwachen getriggert wird amn hätte auch time.sleep(20) verwenden können aber dann hätte man Evaluation für die Zeit gesehen
    screen = pygame.display.get_surface()
    font = pygame.font.Font(None, 60)
    
    start = time.time()
    while time.time() - start < seconds:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        screen.fill((255, 255, 255))
        remaining = int(seconds - (time.time() - start)) + 1
        text = font.render(f"Resetting... {remaining}s", True, (0, 0, 0))
        text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.wait(200)
    
    pygame.event.clear()



def clear_events():
    pygame.event.clear()
    pygame.time.wait(50)
    pygame.event.clear()


def full_cleanup():
    pygame.event.clear()
    pygame.event.pump()
    pygame.mixer.stop()
    pygame.mixer.music.stop()
    pygame.time.wait(50)
    pygame.event.clear()


def periodic_cleanup(cache, last_cleanup_time, interval=5.0):
    current_time = time.time()
    if current_time - last_cleanup_time >= interval:
        cache.cleanup(force=False)
        full_cleanup()
        return current_time
    return last_cleanup_time


def main():
    #Audio PreInitilize 
    pygame.mixer.pre_init(
        frequency=44100,
        size=-16,
        channels=2,
        #buffer=2048
        buffer=8192
    )

    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    screen_width, screen_height = screen.get_size()
    
    cache = AnimationCache()
    cache.set_screen_size(screen_width, screen_height)
    #cache.preload_directory("assets")
    
    logger = DataLogger()
    audio = AudioManager()
    
    run_analyze_logs()
    


    nav = ButtonNavigation()
    nav.activate(True)

    
    def on_nav_select(item):
        print(f"Navigation SELECT: {item}")
    
    def on_nav_back(menu):
        print(f"Navigation BACK to: {menu}")
    
    nav.set_on_select(on_nav_select)
    nav.set_on_back(on_nav_back)
    


    #Logik für ankommende Befehle
    def on_button_event(action):
        print(f"BUTTON EVENT: {action}")
        
        if action == "left":
            nav.set_left(True)
            def release_left():
                time.sleep(0.15)
                nav.set_left(False)
            threading.Thread(target=release_left, daemon=True).start()
            

            
        elif action == "right":
            nav.set_right(True)
            def release_right():
                time.sleep(0.15)
                nav.set_right(False)
            threading.Thread(target=release_right, daemon=True).start()
            
        elif action == "select":
            nav.set_left(True)
            nav.set_right(True)
            def release_select():
                time.sleep(0.15)
                nav.set_left(False)
                nav.set_right(False)
            threading.Thread(target=release_select, daemon=True).start()
    



    motor_controller.set_nav_callback(on_button_event)  #es kommen Befehle an -> set_nav_callback gibt die jeweilige Auswahl zurück (left, right, select)-> Auswahl wird in on_button_event verarbeitet
                                                        #-> in der Navigation wird set_right, set_left True ider False gesetzt die Logik in der Navigationsdatei bestimmt dann welcher Art das Event ist
                                                        #und schickt es an die jeweilige Auswahl in der sich der User befindet wonach dann die Auswahl eines Panels oder die Bewegung durch die panel stattfindet

    def reset_navigation(nav):
        if nav:
            nav.active = False
            nav.reset()
            pygame.time.wait(50)
            nav.active = True
            nav.current_index = 0
            nav.highlighted_item = None
            print("Navigation zurueckgesetzt")
    

    #Beginn des Programms einmal wird die Begrüßung abgespielt dann geht es in den eigentlichen Programmloop
    try:
        greeting_ui = Begrüßung(screen, clock, audio) 
        greeting_ui.run()
        full_cleanup()
    except Exception as e:
        print(f"Fehler bei der Begruessung: {e}")
        traceback.print_exc()
    
    
    running = True    #eigentlicher Programmloop
    while running:  
        logger.start_session()



        try:
            print("\n" + "=" * 60)
            print("STARTE SLEEP-MODUS")
            print("=" * 60)
            


            sleep_ui = SleepMode(screen, clock, cache, motor_controller, audio, nav=nav) 
            


            motor_controller.set_sensor_callback(sleep_ui.set_sensor_detected)  #wenn der Sensor eine Person registriert wird das sensor_callback(True) vom MotorController an set_sensor_detected übergeben
                                                                                #set_sensor_detected bekommt also die Information detected die dann denn Übergang in die Aufwachanimation und das Hochfahren 
                                                                                #steuert
                                                                                 

            
            # Sleep-Modus starten (blockiert bis Sensor oder Interaktion)
            sleep_result = sleep_ui.run(nav=nav)
            
            
            
            motor_controller.set_sensor_callback(None) #sobald sleep abgeschlossen ist wird set_sensor_callback wieder zurückgesetzt vermutlich muss man am Ende des Programms noch eine Bedingung einfügen 
                                                       #die dafür sorgt das set_sensor_callback für einen bestimmten Zeitraum nicht auf True gesetzt werden kann damit der sleep Modus nicht sofort beended 
                                                       #wird wenn der vorherige User aufsteht
            print("Sensor Callback freigegeben")


            
            full_cleanup()
            reset_navigation(nav)
            
            print("Sleep-Modus beendet")
            print("=" * 60 + "\n")
            
        except Exception as e:
            print(f"Fehler im Sleep-Modus: {e}")
            traceback.print_exc()
            try:
                motor_controller.set_sensor_callback(None)
            except:
                pass
        
        #Intro loop sollte solange laufen bis der User entweder den Bildschirm berührt oder die Tasten aktiviert
        
        clear_events
        intro_ui = IntroMode(screen, clock, cache, nav=nav)
        motor_controller.set_sensor_callback(intro_ui.set_sensor_detected)
        
        intro_result = intro_ui.run()
        full_cleanup()
        reset_navigation(nav)
        
        #Callback freigeben
        motor_controller.set_sensor_callback(None)
        
        if intro_result == "sleep":
            continue  # zurück in Sleep-Modus
        
        #intro logik die ohne zurück in sleep fahren war 
        """
        clear_events()
        intro_ui = IntroMode(screen, clock, cache, nav=nav)  
        intro_ui.run()
        full_cleanup()
        reset_navigation(nav)
        """

        language_ui = Language(screen, clock) 
        selected_language = language_ui.run(nav=nav)
        full_cleanup()
        reset_navigation(nav)
        if selected_language is None:
            continue
        audio.set_language(selected_language)
        


        volume_ui = Volume(screen, clock, audio)
        volume_ui.run(nav=nav)
        full_cleanup()
        reset_navigation(nav)
        


        pre_eval_ui = PreEvaluation(screen, clock, audio) 
        stress_before = pre_eval_ui.run(nav=nav)
        full_cleanup()
        reset_navigation(nav)
        if stress_before is None:
            continue
            
            
            

        
            
        #            
        try:
            atemerkennung = Stressidentifikation(screen, clock, audio, motor_controller)
            motor_controller.set_breath_callback(atemerkennung.set_breath_result)
        
            breath_result = atemerkennung.run()
        
            motor_controller.set_breath_callback(None)
            full_cleanup()
            reset_navigation(nav)
        
            if breath_result is None:
                continue  # zurück zum Anfang
        
             #Stresszustand wird mit beliebigen Übungen zugewiesen leider keine Daten zur Verfügung :(
            if breath_result == 0x0F:          #entspannt
                exercise = "right"
                duration = 180
            elif breath_result == 0x0D:        #normal
                exercise = "middle"
                duration = 180
            elif breath_result == 0x0E:        #gestressst
                exercise = "left"
                duration = 60
            else:
                print(f"Unbekannter Breath-Befehl: 0x{breath_result:02X}")
                continue
        

        
            logger.log_pre_evaluation(exercise, duration, stress_before)
        

            starting_motor(cache, audio, screen, clock)
            full_cleanup()
            reset_navigation(nav)
        
            #Übung ausführen
            if exercise == "left":
                handle_left(cache, duration)
            elif exercise == "middle":
                handle_middle(cache, duration)
            elif exercise == "right":
                handle_right(cache, duration)
        
            full_cleanup()
            reset_navigation(nav)
            
            handle_movebackup(cache, duration)
        
    
            
            eval_ui = Evaluation(screen, clock, logger, audio)
            eval_ui.run(nav=nav)
            full_cleanup()
            reset_navigation(nav)
        
        except Exception as e:
            print(f"Fehler in der Atemerkennung: {e}")
            traceback.print_exc()
            try:
                motor_controller.set_breath_callback(None)
            except:
                pass
            full_cleanup()
            reset_navigation(nav)
            continue
        
        cooldown(20)
        pygame.event.pump()
        #time.sleep(20) #damit Sensor nicht sofort triggert wenn User noch vor Neffy sitzt  
        clock.tick(60)
                    




if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program stopped by user")
    except Exception as e:
        print(f"Schwerwiegender Fehler: {e}")
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()
