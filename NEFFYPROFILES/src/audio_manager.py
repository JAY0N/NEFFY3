
import os
import pygame
from settings_manager import settings_manager


class AudioManager:
    def __init__(self, base_path="assets_mp3/ui"):
        self.base_path = base_path
        self.language = None
        self.cache = {}
        self._volume = 0.5
        
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        
        self.channel = pygame.mixer.Channel(0)
    
    def set_language(self, lang):
        self.language = lang
        self.cache.clear()
        print(f"[AUDIO] Sprache gesetzt: {lang}")
    

        
    def set_volume(self, volume):
        self._volume = max(0.0, min(1.0, volume))
        
        
        pygame.mixer.music.set_volume(self._volume)
        
        # Alle Channels
        for i in range(pygame.mixer.get_num_channels()):
            pygame.mixer.Channel(i).set_volume(self._volume)
        
        #alle sounds on cache
        for sound in self.cache.values():
            sound.set_volume(self._volume)
        
        print(f"[AUDIO] Lautstärke gesetzt: {int(self._volume * 100)}%")
    
    def get_volume(self):
        return self._volume
    
  
    #audio aktiviertja nein
    def is_audio_enabled(self):
        return settings_manager.is_audio_enabled()
    
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
            fallback_path = os.path.join(self.base_path, f"{key}.mp3")
            if os.path.exists(fallback_path):
                return fallback_path
            print(f"[AUDIO] Datei fehlt: {path}")
            return None
        
        return path
    
    def get_sound(self, key):
        path = self._get_path(key)
        if not path:
            return None
        
        if path in self.cache:
            return self.cache[path]
        
        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(self._volume)
            self.cache[path] = sound
            return sound
        except Exception as e:
            print(f"[AUDIO] Fehler bei {path}: {e}")
            return None


    


    def play(self, key, loop=False): #only when enabled
        if not self.is_audio_enabled():
            return False
        
        sound = self.get_sound(key)
        if sound:
            self.channel.fadeout(100)
            sound.set_volume(self._volume)
            self.channel.set_volume(self._volume)   
            loops = -1 if loop else 0
            self.channel.play(sound, loops=loops)
            return True
        return False

    def stop(self):
        self.channel.fadeout(100)
        pygame.mixer.music.stop()
        pygame.mixer.stop()
        #Volumen wird nach stop wieder angewendet würde sonst inkonsistent werden
        self._reapply_volume()
    
    def _reapply_volume(self):
        #setztLautstärke auf alle channel
        pygame.mixer.music.set_volume(self._volume)
        for i in range(pygame.mixer.get_num_channels()):
            pygame.mixer.Channel(i).set_volume(self._volume)
        for sound in self.cache.values():
            sound.set_volume(self._volume)

    
    def play_music(self, file_path, loop=False):
        if not self.is_audio_enabled():
            return False
        
        if not os.path.exists(file_path):
            
            return False
        
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.set_volume(self._volume)
            loops = -1 if loop else 0
            pygame.mixer.music.play(loops)
            return True
        except Exception as e:
            print(f"[AUDIO] Fehler beim Abspielen der Musik: {e}")
            return False
    
     
     #damit Audios während Übung immer Spielen auch wenn wir die Audiohinweise abschalten
    def play_forced(self, key, loop=False):
        sound = self.get_sound(key)
        if sound:
            self.channel.fadeout(100)
            sound.set_volume(self._volume)
            self.channel.set_volume(self._volume)   
            loops = -1 if loop else 0
            self.channel.play(sound, loops=loops)
            return True
        return False



    
    def stop_music(self):
        pygame.mixer.music.stop()
    
    def is_playing(self):
        return self.channel.get_busy() or pygame.mixer.music.get_busy()
    
    def fadeout(self, duration=100):
        self.channel.fadeout(duration)
        pygame.mixer.music.fadeout(duration)
