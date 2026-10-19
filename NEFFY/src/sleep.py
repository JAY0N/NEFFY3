import pygame
import gc
import time
import threading
from webp_sequence_player import WebPSequencePlayer
from language_manager import lang
from design_system import design
from navigation import NavigationHelper


class SleepMode: 
    def __init__(self, screen, clock, cache, motor_controller, audio, nav=None):
        self.screen = screen
        self.clock = clock
        self.cache = cache
        self.motor_controller = motor_controller
        self.audio = audio
        self.nav = nav
        
        self.width, self.height = self.screen.get_size()
        self.ref_height = 1080
        self.scale = self.height / self.ref_height
        
        #Sleep Animation
        self.sleep_sequence = [
            ("assets/sleep_animation/AugenZuAtemen1.webp", 12),
            ("assets/sleep_animation/AugenZU1.webp", 0.5),
            ("assets/sleep_animation/AugenZuAtemen.webp", 12),
            ("assets/sleep_animation/AugenZU.webp", 0.5),
        ]
        
        self.sleep_batches = [
            [0],  #Batch 0
            [1],  #Batch 1
            [2],  #Batch 2
            [3],  #Batch 3
        ]
        
        #Aufwachen
        self.wake_sequence = [
            ("assets/sleep_animation/wakeup.webp", 4),
           
            ("assets/intro_animation/open.webp", 0.5),
            ("assets/intro_animation/blink.webp", 24)
            
#            ("assets/intro_animation/open.webp", 0.6),
#            ("assets/intro_animation/blink.webp", 24),
#            ("assets/intro_animation/open.webp", 0.5),
        ]
        
        # WakeBatches
        self.wake_batches = [
            [0],  # Batch 0: wake1
            [1],  # Batch 1: wake2
            [2],  # Batch 2: wake3
            #[3],
            #[4],
            #[5],
        ]
        
        # Aufwach Audio derzeit nicht vorhanden Einatmen Ausatmen sound?
        self.wake_audio = "assets_mp3/audio/wake.mp3"
        

        self.sleep_player = WebPSequencePlayer(
            self.sleep_sequence,
            self.cache,
            size=(self.width, self.height),
            audio=None
        )
        
        
        self.wake_player = None
        
        # Batch Status
        self.batch_index = 0
        self.clip_index_in_batch = 0
        self.batch_counter = 0
        
        #Reinigungsinterval
        self.cleanup_interval = 5
        
        # Status
        self.is_sleeping = True
        self.is_waking = False
        self.exit_sleep = False
        self.wake_complete = False
        
        # Sensor Status
        self.sensor_detected = False
        self.last_sensor_time = 0
        self.sensor_debounce = 500  # ms
        
        # Motor Positionen nochmal anpassen?
        self.sleep_position = 0
        self.wake_position_head = 17
        self.wake_position_body = 4
 

        

        self.nav_helper = None
        self.use_navigation = (nav is not None and nav.active)
        
        # Nav-Items (keine sichtbaren Items)
        self.nav_items = []
    
    def _prepare_sleep(self):
        self.sleep_player._prepare()
        self.batch_index = 0
        self.clip_index_in_batch = 0
        self.batch_counter = 0
        self.is_sleeping = True
        self.is_waking = False
        self.exit_sleep = False
        self.wake_complete = False
        self.sensor_detected = False
    
    def _prepare_wake(self):
        self.wake_player = WebPSequencePlayer(
            self.wake_sequence,
            self.cache,
            size=(self.width, self.height),
            audio=self.wake_audio
        )
        self.wake_player._prepare()
        self.batch_index = 0
        self.clip_index_in_batch = 0
        self.batch_counter = 0
        self.is_waking = True
    
    def _cleanup(self):
        print(f"Cleanup nach Batch {self.batch_counter}")
        
        pygame.event.clear()
        pygame.event.pump()
        pygame.mixer.stop()
        pygame.mixer.music.stop()
        gc.collect()
    
    def _move_to_sleep_position(self):
        try:
            self.motor_controller.move_body_head_in_time(0, 40, 0, 40) #2000 2000 bei Zeiten etwas unsicher müsste 4 Sekunden jeweils entsprechen
            time.sleep(0) #1
            return True
        except Exception as e:
            print(f"Fehler beim Fahren in Schlafposition: {e}")
            return False
    
    def _move_to_wake_position(self):
        try:
            self.motor_controller.move_body_head_in_time(
                self.wake_position_body, 40,  #muss vielleicht umgetauscht werden
                self.wake_position_head, 40  #4000
            )
            return True
        except Exception as e:
            print(f"Fehler beim Fahren in Aufwach-Position: {e}")
            return False
    
    def _check_navigation(self):
        if self.nav and self.nav.active:
            if self.nav.selected_item is not None or self.nav.highlighted_item is not None:
                self.exit_sleep = True
                return True
        return False



    
    def _check_sensor(self): #Sensor erkannt oder nicht
        current_time = time.time() * 1000
        if self.sensor_detected and (current_time - self.last_sensor_time > self.sensor_debounce):
            return True
        return False
    
    def _play_sleep_batch(self): #spielt sleep animation
        if self.batch_index >= len(self.sleep_batches):
            return False
        
        current_batch = self.sleep_batches[self.batch_index]
        
        for clip_idx in current_batch:
            if clip_idx >= len(self.sleep_player.clips):
                continue
            
            frames, fps = self.sleep_player.clips[clip_idx]
            
            for frame in frames:
 
                if self.nav:
                    self.nav.update()
                
                 #Navigation Auswahl ja neun
                if self._check_navigation():
                    return False
                
                 #Sensor da ja nein
                if self._check_sensor():
                    print("SENSOR DETEKTED - Aufwachen!")
                    self.exit_sleep = True
                    return False
                
                   #Events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
                    
                    # Jede Interaktion beendet Sleep
                    if event.type in [
                        pygame.MOUSEBUTTONDOWN,   
                        pygame.MOUSEMOTION,
                        pygame.FINGERDOWN,
                        pygame.KEYDOWN
                    ]:
                        self.exit_sleep = True
                        return False
                    
                    # Tastatur Interaktion kann rausgrnommen werden da schon Logik besteht das Tastatur sleep abbricht
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.exit_sleep = True
                            return False
                        
                        if self.nav and self.nav.active:
                            if event.key == pygame.K_l:
                                self.nav.set_left(True)
                            elif event.key == pygame.K_r:
                                self.nav.set_right(True)
                    
                    if event.type == pygame.KEYUP:
                        if self.nav and self.nav.active:
                            if event.key == pygame.K_l:
                                self.nav.set_left(False)
                            elif event.key == pygame.K_r:
                                self.nav.set_right(False)
                                

                
                if self.exit_sleep:
                    return False
                
                #Frame zeichnen
                self.screen.blit(frame, (0, 0))
                pygame.display.flip()
                self.clock.tick(fps)
        
        #next Batch
        self.batch_index += 1
        self.clip_index_in_batch = 0
        self.batch_counter += 1
        
     
        if self.batch_counter % self.cleanup_interval == 0:
            self._cleanup()
        
        return True
    
    def _play_wake_batch(self):
        if self.batch_index >= len(self.wake_batches):
            return False
        
        current_batch = self.wake_batches[self.batch_index]
        
        for clip_idx in current_batch:
            if clip_idx >= len(self.wake_player.clips):
                continue
            
            frames, fps = self.wake_player.clips[clip_idx]
            
            for frame in frames:
 
 
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
                
                # Frame zeichnen
                self.screen.blit(frame, (0, 0))
                pygame.display.flip()
                self.clock.tick(fps)
        
        # next Batch
        self.batch_index += 1
        self.clip_index_in_batch = 0
        self.batch_counter += 1
        
        return True
        

    
    def run(self, nav=None): #starte sleep modus
        #nav aktualisieren
        if nav is not None:
            self.nav = nav
            self.use_navigation = (nav is not None and nav.active)
            
            if self.use_navigation:
                self.nav_helper = NavigationHelper(nav)
                self.nav_helper.setup_ui("sleep")
                self.nav_helper.set_items([])
                
                
                
                def on_navigate(item, index):
                    self.exit_sleep = True
                
                def on_select(item):
                    print("Sleep: Navigation SELECT - beende Sleep")
                    self.exit_sleep = True
                    
                
                nav.set_on_navigate(on_navigate)
                nav.set_on_select(on_select)
        
        if not self._move_to_sleep_position():
            print("Fehler beim Fahren in Schlafposition")
            return False
        
        

        #Sleep vorbereiten
        self._prepare_sleep()
        
 
        
        # Sleep in Loop bis aktion kommt
        running = True
        while running and not self.exit_sleep:
            result = self._play_sleep_batch()
            
            if result is False:
                running = False
                break
            
            # Wenn alle Batches durchlaufen zurück zum Anfang
            if self.batch_index >= len(self.sleep_batches):
                self.batch_index = 0
                self.clip_index_in_batch = 0
        
  
        if self.exit_sleep:
            print("Aufwachen...")
            self._wake_up()
        
        
        self._cleanup()
        pygame.time.wait(30)
        pygame.event.clear()
        
        return True
    
    def _wake_up(self): #Aufwachen
        self._prepare_wake()
        
        self._move_to_wake_position() #Motorbewegung
        
        if self.wake_audio:

            try:
                pygame.mixer.music.load(self.wake_audio)
                pygame.mixer.music.play()
            except Exception as e:
                print(f"Fehler beim Abspielen des Aufwach-Sounds: {e}")
        
        
        running = True
        while running:
            result = self._play_wake_batch()
            if result is False:
                break
            if self.batch_index >= len(self.wake_batches):
                break
        
        # Audio stoppen
        pygame.mixer.music.stop()
                
        self.wake_complete = True
    


    def set_sensor_detected(self, payload):


        
        current_time = time.time() *1000
        

        """
        
        if payload == 0:
            print("?? SENSOR: keine Person (0)")
            self.sensor_detected = False
            return"""
            
        
        if payload == 2 or payload == 1:  #or 0
            if current_time - self.last_sensor_time > self.sensor_debounce:
                self.sensor_detected = True
                self.last_sensor_time = current_time
                self.exit_sleep = True
                print("SENSOR: Person erkannt")




