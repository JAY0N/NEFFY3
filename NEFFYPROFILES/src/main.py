
import pygame
import sys
import time
import threading

from language_ui import PygameLanguageUI
from volume_ui import PygameVolumeUI
from ui import PygameDecisionUI
from duration_ui import PygameDurationUI
from evaluation_ui import PygameEvaluationUI
from pre_evaluation_ui import PygamePreEvaluationUI
from custom_ui import PygameCustomUI
from greeting_ui import Begrüßung 
from main_menu_ui import PygameMainMenuUI
from profile_ui import PygameProfileUI
from settings_menu_ui import PygameSettingsMenuUI
from evaluation_settings_ui import PygameEvaluationSettingsUI
from logic import handle_left, handle_middle, handle_right, handle_custom, starting_motor, motor_controller ,handle_Dankbarkeitsübung, handle_movebackup
from logic import motor_controller
from animation_cache import AnimationCache
from audio_manager import AudioManager
from logger import DataLogger
from language_manager import lang
from settings_manager import settings_manager
from menu_navigation import ButtonNavigation
import json
import os
import traceback
import subprocess

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
        else:
            return False
    except Exception as e:
        return False




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
    # Audio Pre Init
    pygame.mixer.pre_init(
        frequency=44100,
        size=-16,
        channels=2,
        buffer=2048
    )

    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    screen_width, screen_height = screen.get_size()
    
    cache = AnimationCache()
    cache.set_screen_size(screen_width, screen_height)
    cache.preload_directory("assets")
    
    
    
    
    logger = DataLogger()
    audio = AudioManager()
    
    run_analyze_logs()
    

    
    # Sprache laden
    settings_manager.apply_language_to_manager(lang)
    audio.set_language(settings_manager.get_language())
    
    #Laustärke für Profil anwenden
    try:
        saved_volume = settings_manager.get_settings().get("volume", 50)
        audio.set_volume(saved_volume / 100.0)
        print(f"Startlautstärke aus Profil: {saved_volume}%")
    except Exception as e:
        print(f"Konnte Startlautstärke nicht laden: {e}")
    




    #Navigation initialisieren    
    nav = ButtonNavigation()
    nav.setup_menus()
    nav.activate(True)
    

    
    def on_nav_select(item):
        print(f"Navigation SELECT: {item}")
    
    def on_nav_back(menu):
        print(f"Navigation BACK to: {menu}")
    
    nav.set_on_select(on_nav_select)
    nav.set_on_back(on_nav_back)
    

    def on_button_event(action):
        
        print(f"BUTTON EVENT: {action}")
        
        if action == "left":
            # Navigation nach links
            nav.set_left(True)
            def release_left():
                time.sleep(0.15)
                nav.set_left(False)
            threading.Thread(target=release_left, daemon=True).start()
            
        elif action == "right":
            # Navigation nach rechts
            nav.set_right(True)
            def release_right():
                time.sleep(0.15)
                nav.set_right(False)
            threading.Thread(target=release_right, daemon=True).start()
            
        elif action == "select":
            # Auswahl beide Tasten gedrückt
            nav.set_left(True)
            nav.set_right(True)
            def release_select():
                time.sleep(0.15)
                nav.set_left(False)
                nav.set_right(False)
            threading.Thread(target=release_select, daemon=True).start()
    

    #callback für Navigation setzen
    motor_controller.set_nav_callback(on_button_event)

    def reset_navigation(nav):
        
        if nav:
            nav.active = False
            nav.reset()
            pygame.time.wait(50)
            nav.active = True
            nav.current_index = 0
            nav.highlighted_item = None
            print("Navigation zurückgesetzt")
    
    #Begrüßung
    try:
        greeting_ui = Begrüßung(screen, clock, audio)
        greeting_ui.run()
        full_cleanup()
    except Exception as e:
        print(f"Fehler bei der Begrüßung: {e}")
        traceback.print_exc()
    
    # Hauptmenü
    running = True
    while running:
        try:
            # Navigation update
            nav.update()
            
            main_menu = PygameMainMenuUI(screen, clock, audio)
            main_choice = main_menu.run(nav=nav)
            full_cleanup()
            reset_navigation(nav)
            
            if main_choice == "profile":
                profile_ui = PygameProfileUI(screen, clock, audio)
                profile_result = profile_ui.run()
                full_cleanup()
                reset_navigation(nav)
                
                settings = settings_manager.get_settings()
                volume_percent = settings.get("volume", 50)
                audio.set_volume(volume_percent / 100.0)
                if profile_result == "back":
                    continue
                    

                    
            elif main_choice == "settings":
                settings_running = True
                while settings_running:
                    nav.update()
                    
                    settings_menu = PygameSettingsMenuUI(screen, clock, audio)
                    settings_choice = settings_menu.run(nav=nav)
                    full_cleanup()
                    reset_navigation(nav)
                    
                    if settings_choice == "back":
                        settings_running = False
                        break
                    elif settings_choice == "language":
                        nav.enter_menu("language")
                        language_ui = PygameLanguageUI(screen, clock, return_to_settings=True)
                        result = language_ui.run(nav=nav)
                        full_cleanup()
                        reset_navigation(nav)
            
                        selected_lang = settings_manager.get_language()
                        print(f"[DEBUG] Sprachauswahl (aus Settings): '{selected_lang}'")
                    
                        if selected_lang:
                            lang.load(selected_lang)
                            audio.set_language(selected_lang)
            
                    elif settings_choice == "volume":
                        nav.enter_menu("volume")
                        volume_ui = PygameVolumeUI(screen, clock, audio, return_to_settings=True)
                        result = volume_ui.run(nav=nav)
                        full_cleanup()
                        reset_navigation(nav)
                    elif settings_choice == "duration":
                        nav.enter_menu("duration")
                        duration_ui = PygameDurationUI(screen, clock, audio, return_to_settings=True)
                        result = duration_ui.run(nav=nav)
                        full_cleanup()
                        reset_navigation(nav)
                    elif settings_choice == "exercise":
                        nav.enter_menu("exercise")
                        decision_ui = PygameDecisionUI(screen, clock, audio, return_to_settings=True)
                        result = decision_ui.run(nav=nav)
                        full_cleanup()
                        reset_navigation(nav)
                        
                        if result == "custom":
                            print("Öffne Custom für Parameteranpassung...")
                            custom_ui = PygameCustomUI(screen, clock, audio)
                            custom_params = custom_ui.run()
                            full_cleanup()
                            
                            if custom_params:
                                settings_manager.set_custom_params(custom_params)
                                print(f"Custom-Parameter gespeichert: {custom_params}")
                            else:
                                print("Custom abgebrochen")
                    elif settings_choice == "evaluation":
                        nav.enter_menu("evaluation_settings")
                        eval_settings_ui = PygameEvaluationSettingsUI(screen, clock, audio)
                        result = eval_settings_ui.run(nav=nav)
                        full_cleanup()
                        reset_navigation(nav)


                    
            elif main_choice == "start":
                try:
                    logger.start_session()
                    settings = settings_manager.get_settings()
                    
                    language = settings.get("language", "de")
                    lang.load(language)
                    audio.set_language(language)
                    
                    volume_percent = settings.get("volume", 50)
                    volume_float = volume_percent / 100.0
                    audio.set_volume(volume_float)
                    
                    duration = settings.get("duration", 180)
                    exercise = settings.get("exercise", "middle")
                    evaluation_enabled = settings_manager.is_evaluation_enabled()
                    
                    print("=" * 60)
                    print("STARTE ÜBUNG")
                    print(f"   Profil: {settings_manager.profile_name}")
                    print(f"   Sprache: {language}")
                    print(f"   Lautstaerke: {volume_percent}%")
                    print(f"   Dauer: {duration}s")
                    print(f"   Uebung: {exercise}")
                    print(f"   Evaluation aktiv: {evaluation_enabled}")
                    if exercise == "custom":
                        custom_params = settings_manager.get_custom_params()
                        print(f"   Custom-Parameter: {custom_params}")
                    print("=" * 60)
                    
                    if evaluation_enabled:
                        print("Zeige Pre-Evaluation...")
                        pre_eval_ui = PygamePreEvaluationUI(screen, clock, audio)
                        stress_before = pre_eval_ui.run(nav=nav)
                        full_cleanup()
                        reset_navigation(nav)
                        if stress_before is None:
                            print("Pre-Evaluation abgebrochen")
                            continue
                    else:
                        print("Pre-Evaluation deaktiviert, überspringe...")
                        stress_before = "N/A"
                    
                    logger.log_session(exercise, duration, stress_before)
                    
                    print("Starte Motor-Kalibrierung...")
                    starting_motor(cache, audio, screen, clock)
                    full_cleanup()
                    print("Motor-Kalibrierung abgeschlossen")
                    
                    print(f"Führe Übung '{exercise}' fuer {duration} Sekunden aus...")
                    
                    if exercise == "left":
                        handle_left(cache, duration)
                    elif exercise == "middle":
                        handle_middle(cache, duration)
                    elif exercise == "right":
                        handle_right(cache, duration)
                    elif exercise =="Dankbarkeitsübung":
                        duration = 125 #136
                        handle_Dankbarkeitsübung(cache, duration, audio)    
                    
                    elif exercise == "custom":
                        custom_params = settings_manager.get_custom_params()
                        print(f"Führe Custom Übung mit Parametern aus: {custom_params}")
                        handle_custom(cache, duration, custom_params)
                    else:
                        #kann nicht passieren
                        handle_middle(cache, duration)
                    
                    full_cleanup()
                    print("Übung abgeschlossen")
                    
                    handle_movebackup(cache, duration) #damit wenn es ausgeschaltet wird es etwas höher ist und der Klicker erreicht werden kann
                    
                    if evaluation_enabled:
                        eval_ui = PygameEvaluationUI(screen, clock, logger, audio)
                        eval_ui.run(nav=nav)
                        full_cleanup()
                        reset_navigation(nav)
                        print("Evaluation abgeschlossen")
                    else:
                        print("keine Evaluation")
                        
                    
                    print("Zurück zum Hauptmenü")
    

                    
                except Exception as e:
                    print(f"FEHLER bei der Übungsausführung:")
                    print(f"   Fehler: {e}")
                    traceback.print_exc()
                    full_cleanup()
                    continue
            
        except Exception as e:
            print(f"FEHLER im Hauptmenü-Loop:")
            print(f"   Fehler: {e}")
            traceback.print_exc()
            full_cleanup()
            continue
        
        pygame.event.pump()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()


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
