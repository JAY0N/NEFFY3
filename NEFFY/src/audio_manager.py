
#Sprache wird in Language ausgewählt
#set_language zur jeweiligen Sprache gesetzt
#wenn wir in nachvollgenden Auswahlen play mit einem bestimmten key zum Beispiel "Volume" aufrufen
#play ruft get_sound mit key "Volume" auf
#get_sound verwendet einen Pfad der über set_language vorgegeben ist, der jeweilige key gibt dann die Datei für den Pfad vor in diesem Beispiel Volume.mp3
import os
import pygame


class AudioManager:

    def __init__(self, base_path="assets_mp3/ui"):
        self.base_path = base_path
        self.language = None
        self.cache = {}


        self.current_volume = 0.5

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self.channel = pygame.mixer.Channel(0)


    def set_language(self, lang):

        self.language = lang
        self.cache.clear()
        print(f"[AUDIO] Sprache gesetzt: {lang}")


    def set_volume(self, volume):

        self.current_volume = max(0.0, min(1.0, volume))


        for sound in self.cache.values():
            sound.set_volume(1.0)

        #channel Laustärken setzen
        self.channel.set_volume(self.current_volume)

        pygame.mixer.music.set_volume(self.current_volume)



    def get_volume(self):
        return self.current_volume


    def _get_path(self, key):
        if not self.language:
            print("[AUDIO] Keine Sprache gesetzt")
            return None

        path = os.path.join(
            self.base_path,
            self.language,
            f"{key}.mp3"
        )

        if not os.path.exists(path):
            print(f"[AUDIO] Datei fehlt: {path}")
            return None

        return path


    #sound ladne
    def get_sound(self, key):

        path = self._get_path(key)
        if not path:
            return None

        if path in self.cache:
            return self.cache[path]

        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(1.0)          
            self.cache[path] = sound
            return sound
        except Exception as e:
            print(f"[AUDIO] Fehler bei {path}")
            print(e)
            return None


    def play(self, key, loop=False):
      
        sound = self.get_sound(key)
        if sound:
            self.channel.fadeout(100)
            sound.set_volume(1.0)                   
            self.channel.set_volume(self.current_volume) 
            loops = -1 if loop else 0
            self.channel.play(sound, loops=loops)
            return True
        return False



    def stop(self):
        
        self.channel.fadeout(100)
        pygame.mixer.music.stop()
        pygame.mixer.stop()

        # Nach pygame.mixer.stop() werden channel Lautstärken zurückgesetzt wir müssen die Laustärke also erneut setzen
        self.channel.set_volume(self.current_volume)
        pygame.mixer.music.set_volume(self.current_volume)

    def stop_music(self):
        pygame.mixer.music.stop()

    def fadeout(self, duration=100):
        self.channel.fadeout(duration)
        pygame.mixer.music.fadeout(duration)

