
import json
import os

class SettingsManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.current_settings = {
            "language": "de",
            "volume": 50,
            "duration": 180,
            "exercise": "middle",
            "evaluation_enabled": True,
            "custom_params": {
                "move_up": 4.0,
                "pause_top": 2.0,
                "move_down": 4.0,
                "pause_bottom": 2.0,
                "audio": "assets_mp3/audio/middle.mp3"
            }
        }
        self.profile_name = None
        self.load_from_profile()
    
    def load_from_profile(self):
        #Lädt Einstellungen vom aktuellen Profil
        try:
            if os.path.exists("current_profile.txt"):
                with open("current_profile.txt", "r", encoding="utf-8") as f:
                    self.profile_name = f.read().strip()
                
                if os.path.exists("profiles.json"):
                    with open("profiles.json", "r", encoding="utf-8") as f:
                        profiles = json.load(f)
                        if self.profile_name in profiles:
                            settings = profiles[self.profile_name]
                            #schaut ob Evaluation enabled ist wenn nicht nimmt initalwert
                            if "evaluation_enabled" not in settings:
                                settings["evaluation_enabled"] = True
                            #schaut ob Parameter gesetzt sind ansonsten nimmt einen Basiswert
                            if "custom_params" not in settings:
                                settings["custom_params"] = {
                                    "move_up": 4.0,
                                    "pause_top": 2.0,
                                    "move_down": 4.0,
                                    "pause_bottom": 2.0,
                                    "audio": "assets_mp3/audio/middle.mp3"
                                }
                            self.current_settings.update(settings)
                            print(f"Einstellungen von Profil '{self.profile_name}' geladen: {self.current_settings}")
        except Exception as e:
            print(f"Fehler beim Laden der Profileinstellungen: {e}")

   
    def set_audio_enabled(self, enabled):
        self.current_settings["audio_enabled"] = enabled
        self.save_to_profile()
    

    def is_audio_enabled(self):
        return self.current_settings.get("audio_enabled", True)
    
    

    def save_to_profile(self):
        #Speichert aktuelle Einstellungen im Profil
        if not self.profile_name:
            return
        
        try:
            if os.path.exists("profiles.json"):
                with open("profiles.json", "r", encoding="utf-8") as f:
                    profiles = json.load(f)
            else:
                profiles = {}
            
            if self.profile_name not in profiles:
                profiles[self.profile_name] = {}
            
            profiles[self.profile_name].update(self.current_settings)
            
            with open("profiles.json", "w", encoding="utf-8") as f:
                json.dump(profiles, f, indent=2, ensure_ascii=False)
            
            print(f"Einstellungen in Profil '{self.profile_name}' gespeichert: {self.current_settings}")
        except Exception as e:
            print(f"Fehler beim Speichern der Profileinstellungen: {e}")
    
    def set_language(self, language):
        self.current_settings["language"] = language
        self.save_to_profile()
    
    def set_volume(self, volume):
        self.current_settings["volume"] = volume
        self.save_to_profile()
    
    def set_duration(self, duration):
        self.current_settings["duration"] = duration
        self.save_to_profile()
    
    def set_exercise(self, exercise):
        self.current_settings["exercise"] = exercise
        self.save_to_profile()
    
    def set_evaluation_enabled(self, enabled):
        #Setzt ob Evaluation aktiviert ist
        self.current_settings["evaluation_enabled"] = enabled
        self.save_to_profile()
    
    def is_evaluation_enabled(self):
        #Gibt zurück ob Evaluation aktiviert ist
        return self.current_settings.get("evaluation_enabled", True)
    
    def set_custom_params(self, params):
        #Speichert custum Paramter
        self.current_settings["custom_params"] = params
        self.save_to_profile()
    
    def get_custom_params(self):
        #gibt custum parameter zurück
        return self.current_settings.get("custom_params", {
            "move_up": 4.0,
            "pause_top": 2.0,
            "move_down": 4.0,
            "pause_bottom": 2.0,
            "audio": "assets_mp3/audio/middle.mp3"
        })
        

    
    def get_settings(self):
        return self.current_settings.copy()
    
    def get_language(self):
        #Gibt aktuell eingestellte Sprache zurück
        return self.current_settings.get("language", "de")
    
    def apply_language_to_manager(self, lang_manager):
        #wendet eingestellte Sprache auf den LanguageManager an
        language = self.get_language()
        try:
            lang_manager.load(language)
            print(f"Sprache '{language}' auf LanguageManager angewendet")
            return True
        except Exception as e:
            print(f"Fehler beim Laden der Sprache '{language}': {e}")
            #Fallback kann eigentlich raus weil es nur funktionieren und nicht funktionieren gibt
            try:
                lang_manager.load("Deutsch")
                print("Fallback auf Deutsch")
                return True
            except:
                print("Kritischer Fehler: Keine Sprache ladbar")
                return False

#Globale Instanz
settings_manager = SettingsManager()
