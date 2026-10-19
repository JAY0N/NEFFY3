
#Animation wird mit Befehlen die an Motor geschickt werden gesteuert


"""
Steuerung liefert einen Batch to play Wert je nachdem welche Übung es ist kann das 0 1 sein oder 0 1 2 3 wenn es mit Pausen ist zum Beispiel. Der Wert kommt an wird 
mit dem last_batch (vorhergehnder batch_to_play) verglichen wenn ungleich wird letzter Batch auf den neuen Batch Wert gestellt und der current_batch_index auch aktualisiert. current_batch_index 
steuert in welchem Batch wir uns befinden also [0, 1] oder [2, 3] zum Beispiel wenn der ankommenden batch_to_play zum Beispiel 1 ist dann würden wir Batch [2,3] als abzuspielenden Batch haben 
da current_batch_index auf diesen Batch zeigt. Clip_index wird auf null zurückgesetzt und clip_idx wird gezeichnet was auf die clips zeigt die in dem Batch liegen auf den der current_batch_index zeigt. 
Der clip wird gezeichnet und der clip_index +1  gesetzt es wird also clip 3 abgespielt. Wenn der clip_index größer oder gleich der Länge aller Elemente in diesem Batch ist ist dieser Batch abgeschlossen. 
Was bedeutet das dass letzte gezeichnete Bild verbleibt bis der nächste batch_to_play von Steuerung kommt nachdem wir den Prozess wiederholen. Das bedeutet auch das für jede Übung die jeweilige Aufteilung 
in der logic relevant ist. Wenn mehr clips vorhanden sind also mit batch_to_play angepeilt werden können dann werden diese nie abgespielt werden. Diese Aufteilung des Sytems macht es auch möglich 
 das wenn custum zum Beispiel gewählt wird und die Pausen auf 0 sind nur Batchtoplay 0 und 2 geschickt werden und der current_batch_index dementsprechend 
 auch nur auf diese Batches die die clips für das hoch und runterfahren enthalten zeigt also auch nur diese in den Animationen abgespielt werden."""


import pygame
import time
from animation_cache import AnimationCache


class WebPSequencePlayer:
    def __init__(self, sequence, cache, size=None, audio=None):
        self.sequence = sequence
        self.cache = cache
        self.size = size
        self.audio_file = audio
        self.clips = []
        self.is_playing = False
        self.current_sound = None
        
        
        
        
        self.volume = 0.5 
        #
        
        # Motor Pattern Referenz für Batch info
        self.motion_pattern = None
        
        # Batch Info
        self.batches = [] # #[[0,1], [2,3]] z.B. für die 4x6 Übung
        self.current_batch_index = 0
        self.clip_index_in_batch = 0
        self.last_batch = -1

        if not pygame.mixer.get_init():
            pygame.mixer.init()

    def set_screen_size(self, width, height):
        self.size = (width, height)

    def _prepare(self):
        self.clips = [] 
        for file, fps in self.sequence: #schauen was in logic an Animationen und ihrer fps Zahl vorliegt und wenden es auf alle an
            frames = self.cache.load(file) #laden alle Animationsteile und hängen sie dann untereinander
            self.clips.append((frames, fps))

    def set_motion_pattern(self, motion_pattern):
        self.motion_pattern = motion_pattern

    def set_batches(self, batches): 
        self.batches = batches  #enthält alle Batches der jeweils ausgewählten Übung
        self.current_batch_index = 0   #verweist auf welchen Batch wir zeigen Batch [0, 1] = Batch_index = 0 , [2,3] = Batch_index = 1 usw.
        self.clip_index_in_batch = 0   #verweist auf den Index innerhalb des Batches also die jeweilige Position der clips [0, 1] = 0 ist gleich clip_index 0, 1 ist gleich clip index 1
                                       #[2, 3] 2 = clip_index 0 , 3 = clip_index 1  
        self.last_batch = -1 #-1
        print(f"Batches set: {batches}")

    def stop(self):
        self.is_playing = False
        if self.current_sound:
            try:
                self.current_sound.stop()
                self.current_sound = None
            except:
                pass
        try:
            pygame.mixer.stop()
            pygame.mixer.music.stop()
        except:
            pass

    def cleanup(self): #setzen alles zurück
        self.stop()
        self.clips = []
        self.sequence = None
        self.cache = None
        self.motion_pattern = None

    def start(self, duration=None):

        screen = pygame.display.get_surface()
        pygame.display.set_caption("Animation Player")
        clock = pygame.time.Clock()



        if self.size is None and screen:
            self.size = screen.get_size()
            self.cache.set_screen_size(self.size[0], self.size[1])

        self._prepare()
        self.is_playing = True
        self.current_batch_index = 0
        self.clip_index_in_batch = 0
        self.last_batch = -1

        if self.audio_file:
            try:
                self.volume = pygame.mixer.music.get_volume()
 
                self.current_sound = pygame.mixer.Sound(self.audio_file)
                self.current_sound.set_volume(self.volume)
                
                #alle channels werden auf die gleiche Lautstärke gesetzt
                for i in range(pygame.mixer.get_num_channels()):
                    pygame.mixer.Channel(i).set_volume(self.volume)
                
                self.current_sound.play(-1)
            except Exception as e:
                print(f"Audio Error: {e}")
                self.current_sound = None


        running = True
        start_time = time.time() 

        print("Animation started - waiting for motor commands")

        try:    #duration and
            while running and self.is_playing:
                if (time.time() - start_time) > duration: 
                    break                                              #itime.time der ständig aktualisierte Wert der Zeit und start_time vergangener Wert der Zeit es wird im Prinzip ein Punkt auf einem
                                                                       #Zeitstrahl gesetzt der dann als Referenz dient 


                
                #Lesen aktuellen AnimationBatch aus
                if self.motion_pattern:     #schauen ob die Verbindung zur Steuerung in logic besteht wenn ja wird batch_to_play aus get_animation_batch in der Steuerung gelesen
                    batch_to_play = self.motion_pattern.get_animation_batch()   
                else:
                    batch_to_play = 0  #Bedingung die eigentlich rausgetrennt werden könnte
                
                
                #wenn ein neuer batch_to_play von Steuerung gesetzt wird
                if batch_to_play != self.last_batch:    
                    
                    print(f"ANIMATION: Batch change {self.last_batch} -> {batch_to_play}")
                    self.last_batch = batch_to_play  
                                                     
                                                   
                    self.current_batch_index = batch_to_play #wenn ein neuer batch_to_play ausgelesen wird wird auch der current_batch_index akttualisiert und wir gehen zum Beoispiel von Batch_index 0 ([0,1])
                                                             #auf current_batch_index 1 ([2,3])
                    self.clip_index_in_batch = 0 #setzen den clip index auf null sind also inerhalb des Batches wieder beim ersten clip




                if self.current_batch_index >= len(self.batches): #wenn der current_batch_index nicht mehr der Menge an Einträgen in self.batches entspricht sondern größer ist setzen wir zurück und sind wieder 
                    print(f"Batch {self.current_batch_index} not found, reset")  #im ersten Batch mit dem clip index 0 was bedeutet das wir Batch 0 clip 0 sind
                    self.current_batch_index = 0
                    self.clip_index_in_batch = 0
                    continue




                current_batch = self.batches[self.current_batch_index] #haben batches also [0, 1] [2, 3] welche jeweils einen index zugewiesen bekommen also 0 1 2 ... je nach index wird dann der 
                                                                       #jeweilige Batch ausgewählt Batch 0 ist [0,1] Batch 1 ist [2,3] etc. hier holen wir uns den jeweiligen Batch in dem wir uns befinden
                


                if self.clip_index_in_batch >= len(current_batch): #wenn index größer als enthaltene Menge an clips ist gehen wir davons aus das Batch abgeschlossen ist
                    time.sleep(0.02)
                    continue





                
                # Batch 1 zum Beispiel [mit clip_index_in_batch 1] würde verweisen auf clip 3 in Batch 1
                clip_idx = current_batch[self.clip_index_in_batch] 
        
        
                """
                if clip_idx >= len(self.clips):
                    print(f"Clip {clip_idx} not found")   #könnte rausgetrennt werden?
                    self.clip_index_in_batch += 1
                    continue
                """
                
                
                
                frames, fps = self.clips[clip_idx] #spielt erst clip mit clip_index 0 dann den zweiten clip mit clip_index 1 also zum Beispiel clip 2 und 3 aus Batch 1
                
                
                for frame in frames:  
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                running = False

                    if not self.is_playing:
                        break
                        
                    screen.blit(frame, (0, 0)) #zeichnet jeden clip/frame
                    pygame.display.flip()
                    clock.tick(fps)

                    if (time.time() - start_time) > duration:
                        break  #duration and
                
                
                
                self.clip_index_in_batch += 1       #nächster clip im Batch

                
        finally:
            self.stop()
            print("Animation stopped")
