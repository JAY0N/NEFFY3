import os
import pygame
from PIL import Image
from PIL import ImageSequence


class AnimationCache:
    def __init__(self):
        self.cache = {}
        self.screen_width = 1920
        self.screen_height = 1080
        self.last_cleanup = 0
        self.cleanup_interval = 5  # Sekunden

    def set_screen_size(self, width, height):
        self.screen_width = width
        self.screen_height = height

    def preload_directory(self, directory):
        #läd alle webp dateien aus einem Verzeichnis
        if not os.path.exists(directory):
            return
        
        for root, dirs, files in os.walk(directory): 
            for file in files:   
                if file.lower().endswith(".webp"): #reduziert alle Buchstaben auf Kleinbuchstaben und wenn es mit webp als Dateiformat endet 
                    path = os.path.join(root, file) #wird ein Absoluter Paf erstellt der mit der entsprechenden Datei verbunden ist und je nachdem wie viele Dateien mit .webp wir
                    self.load(path)                 #haben werden dann mit self load geladen

 
    def load(self, path): #wenn wir spezifische Dateien in die Cache laden wollen
        if path in self.cache:
            return self.cache[path]
        
        try:
            frames = self._load_webp(path) #frames enthält webp für spezifischen Pfad
            self.cache[path] = frames   #self.cache wird für diesen Pfad mit diesen Frames gefüllt
            return frames
        except Exception as e:
            print(f"Fehler beim Laden von {path}: {e}")
            return []

    def _load_webp(self, path):
        #läd alle Frames einer WebP-Datei als Pygame Surfaces
        frames = []
        try:
            img = Image.open(path)
            for frame in ImageSequence.Iterator(img):
                frame = frame.convert("RGBA")   
                frame_data = frame.tobytes()  #tobytes
                size = frame.size
                surf = pygame.image.fromstring(frame_data, size, "RGBA") 
                surf = pygame.transform.smoothscale(surf, (self.screen_width, self.screen_height))  #transform.smoothscale
                frames.append(surf)
        except Exception as e:
            print(f"Fehler beim Laden von {path}: {e}")
        return frames



    def clear(self):
        #leer gesammte chache Animationen müssen also neu geladen werden bei Animationen wenig Problematisch da gering filsize. Große Audiodateien verursachen mehr Probleme
        self.cache.clear()  #clear löscht alles inerhalb der cache
        print(f"AnimationCache geleert (Frames: 0)")

    def cleanup(self, force=False):
        
        #führt periodisches Cleanup durch
        #Entfernt Surfaces aus dem Cache, die nicht mehr verwendet werden
        
        import gc
        
        current_time = pygame.time.get_ticks() / 1000.0
        
        if not force and (current_time - self.last_cleanup < self.cleanup_interval):
            return
        
        self.last_cleanup = current_time
        
        #zält Frames vor Cleanup
        frame_count_before = sum(len(frames) for frames in self.cache.values())
        
         #Surface reinigen cache beibehalten
        # Events leeren
        pygame.event.clear()
        pygame.event.pump()
        
        #PyGame Mixer aufräumen
        try:
            pygame.mixer.stop()
            pygame.mixer.music.stop()
        except:
            pass
        
        # Garbage Collector aufrufen räumt nicht referenzierte Surfaces auf
        gc.collect()
        

        frame_count_after = sum(len(frames) for frames in self.cache.values())
        
        print(f"Cleanup: {frame_count_before} -> {frame_count_after} Frames (GC aufgerufen)")
