
#sollte jetzt auch die Tasten korrekt steuern

import pygame
import gc
from webp_sequence_player import WebPSequencePlayer
from language_manager import lang
from design_system import design
from navigation import NavigationHelper


class IntroMode:  
    def __init__(self, screen, clock, cache, nav=None):
        self.screen = screen
        self.clock = clock
        self.cache = cache
        self.nav = nav

        self.width, self.height = self.screen.get_size()
        self.ref_height = 1080
        self.scale = self.height / self.ref_height


        self.sequence = [
            ("assets/intro_animation/blink.webp", 24),
            ("assets/intro_animation/open.webp", 0.6),
        ]


        self.batches = [
            [0],  # Batch 0 Clip 0
            [1],  # Batch 1 Clip 1
        ]

        self.player = WebPSequencePlayer(
            self.sequence,
            self.cache,
            audio=None
        )

        
        self.batch_index = 0
        self.clip_index_in_batch = 0

        #wird alle 5 s gereinigt
        self.cleanup_interval = 5
        self.batch_counter = 0
 
         #Naivgation
        self.nav_helper = None
        self.use_navigation = (nav is not None and nav.active)
        self.exit_intro = False


        self.nav_items = ["dummy"]


        self.exit_to_sleep = False   


    def _prepare(self):
        self.player._prepare()
        self.batch_index = 0
        self.clip_index_in_batch = 0
        self.batch_counter = 0
        self.exit_intro = False
        self.exit_to_sleep = False

    def _cleanup(self):
        print(f"?? Cleanup nach Batch {self.batch_counter}")

        pygame.event.clear()
        pygame.event.pump()
        pygame.mixer.stop()
        pygame.mixer.music.stop()
        gc.collect()




    def set_sensor_detected(self, payload):
        #logik für Wechsel in Sleep
        if payload == 1:  #or 2
            return
        
        #rausgenommen fürs erste bis Sensoren korrekt funktionieren
        
        if payload == 0:
            print("?? INTRO: keine Person (0)  zurck in Sleep")
            self.exit_to_sleep = True
            self.exit_intro = True

  



    def _check_navigation(self):

        if self.exit_intro or self.exit_to_sleep:
            return True
        return False

    def _play_batch(self):
        if self.batch_index >= len(self.batches):
            return False

        current_batch = self.batches[self.batch_index]

        for clip_idx in current_batch:
            if clip_idx >= len(self.player.clips):
                continue

            frames, fps = self.player.clips[clip_idx]

            for frame in frames:
  
                 #Nav update
                if self.nav:
                    self.nav.update()
                    
                if self.nav and self.nav.active:   #drücken Taste beendet Intro
                    if self.nav.left_pressed or self.nav.right_pressed:
                        print("Intro: Taste gedrckt  beende Intro")
                        self.exit_intro = True
                        return False                

                #wenn Event stattfindet
                if self._check_navigation():
                    return False



                #Events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False

                    # Jede Interaktion beendet Intro
                    if event.type in [
                        pygame.MOUSEBUTTONDOWN,
                        pygame.MOUSEMOTION,
                        pygame.FINGERDOWN,
                        pygame.KEYDOWN
                    ]:
                        return False

                # Frame zeichnen
                self.screen.blit(frame, (0, 0))
                pygame.display.flip()
                self.clock.tick(fps)

        #nächster Batch an Animationen
        self.batch_index += 1
        self.clip_index_in_batch = 0
        self.batch_counter += 1

    
        if self.batch_counter % self.cleanup_interval == 0:
            self._cleanup()

        return True

    def run(self, nav=None):
         #wird gelooped bis Aktion stattfindet
        if nav is not None:
            self.nav = nav
            self.use_navigation = (nav is not None and nav.active)

            if self.use_navigation:
                self.nav_helper = NavigationHelper(nav)
                self.nav_helper.setup_ui("intro")
                self.nav_helper.set_items(self.nav_items)   #dummy item da sonst keine Auswahl getroffen werden kann

                def on_navigate(item, index):
                    print(f"Intro: Navigation '{item}'  beende Intro")
                    self.exit_intro = True

                def on_select(item):
                    print("Intro: Navigation SELECT  beende Intro")
                    self.exit_intro = True

                nav.set_on_navigate(on_navigate)
                nav.set_on_select(on_select)

        pygame.event.clear()
        pygame.time.wait(30)
        pygame.event.clear()

        # Animation vorbereiten
        self._prepare()



        # EndlosschleifeBatches werden wiederholt
        running = True
        while running and not self.exit_intro:
            result = self._play_batch()

            if result is False:
                running = False
                break



            # wenn Batches vorbei zurück zum Anfang
            if self.batch_index >= len(self.batches):
                self.batch_index = 0
                self.clip_index_in_batch = 0

        # Finales Reinigung
        self._cleanup()
        pygame.time.wait(30)
        pygame.event.clear()

        #wenn kein Sensor mehr gitb Sleep zurück
        if self.exit_to_sleep:
            return "sleep"
        return True



    #kann raus
    def set_sequence(self, sequence):

        self.sequence = sequence
        self.player = WebPSequencePlayer(
            self.sequence,
            self.cache,
            audio=None
        )
        self._prepare()

    def set_batches(self, batches):
        self.batches = batches
        self._prepare()

    def set_cleanup_interval(self, interval):
        self.cleanup_interval = interval
