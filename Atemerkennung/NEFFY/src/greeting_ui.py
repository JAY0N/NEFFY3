import pygame
import sys
import os
from language_manager import lang
from design_system import design


class Begrüßung: 
    def __init__(self, screen, clock, audio):
        self.screen = screen
        self.clock = clock
        self.audio = audio
        self.width, self.height = self.screen.get_size()
        
        
        self.ref_height = 1080
        self.scale = self.height / self.ref_height
        
        # Fonts aus Design
        self.title_font = design.get_font("greeting_title", self.scale)
        self.subtitle_font = design.get_font("greeting_subtitle", self.scale)
        
        # Definiere die Begrüßungen für verschiedene Sprachen wenn weitere müssen hier angegeben und in Audio Ordner hinzugefügt werden
        self.greetings = [
            ("de", "Hallo!", "assets_mp3/greetings/hallo.mp3"),
            ("en", "Hello!", "assets_mp3/greetings/hello.mp3"),
            ("es", "Hola!", "assets_mp3/greetings/hola.mp3"),
            ("fr", "Bonjour!", "assets_mp3/greetings/bonjour.mp3"),
            ("it", "Ciao!", "assets_mp3/greetings/ciao.mp3"),
            ("tr", "Merhaba!", "assets_mp3/greetings/merhaba.mp3"),
        ]
        
        self.current_index = 0
        self.is_playing = False
        self.audio_start_time = 0
        self.audio_duration = 0
        self.finished = False
        
        #aktive Begrüßung
        self.active_greeting = None
        self.showing_greeting = False
        self.greeting_start_time = 0
        
        #Fortschrittsbalken
        self.progress = 0
        

        self.greeting_complete = False
        

        self.skip_timeout = design.get_audio("greeting_timeout")
        self.start_time = 0
        

        self.bar_radius = design.get_border_radius("slider")
        
        # Gradient Hintergrund
        self.gradient_surface = design.create_gradient_surface(
            self.width, self.height, "greeting"
        )
    
    def _get_audio_duration(self, audio_path):
        try:
            if os.path.exists(audio_path):
                sound = pygame.mixer.Sound(audio_path)
                return sound.get_length() * 1000
        except Exception as e:
            print(f"Kann Dauer nicht ermitteln für {audio_path}: {e}")
        return 3000
    
    def _play_current_greeting(self):
        if self.current_index >= len(self.greetings):
            self.greeting_complete = True
            return
            

        
        lang_code, text, audio_path = self.greetings[self.current_index]
        
        if not os.path.exists(audio_path):
            print(f"?? Audio nicht gefunden: {audio_path}")
            self.current_index += 1
            self._play_current_greeting()
            return
        
        try:
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            
            self.active_greeting = {
                "lang": lang_code,
                "text": text,
                "audio": audio_path,
                "duration": self._get_audio_duration(audio_path)
            }
            self.showing_greeting = True
            self.greeting_start_time = pygame.time.get_ticks()
            self.is_playing = True
            
            print(f"Begrüßung {self.current_index + 1}/{len(self.greetings)}: {text}")
            
        except Exception as e:
            print(f"Fehler beim Abspielen von {audio_path}: {e}")
            self.current_index += 1
            self._play_current_greeting()
    
    def _update(self):
        current_time = pygame.time.get_ticks()
        
        if current_time - self.start_time > self.skip_timeout:
            print("Begrüßung Übersprungen (Timeout)")
            self.greeting_complete = True
            return
        
        if self.showing_greeting and self.active_greeting:
            elapsed = current_time - self.greeting_start_time
            duration = self.active_greeting["duration"]
            
            self.progress = min(100, (elapsed / duration) * 100)
            
            if elapsed >= duration or not pygame.mixer.music.get_busy():
                self.showing_greeting = False
                self.is_playing = False
                self.current_index += 1
                self.progress = 0
                
                pygame.time.wait(200)
                self._play_current_greeting()
                

    
    def draw_gradient(self):
        self.screen.blit(self.gradient_surface, (0, 0))
    
    def draw_greeting(self):
        if self.showing_greeting and self.active_greeting:
            text = self.active_greeting["text"]
            
            # Willkomenstext
            text_surface = self.title_font.render(text, True, design.get_color("text"))
            text_rect = text_surface.get_rect(
                center=(self.width // 2, self.height // 2 - int(100 * self.scale))
            )
            self.screen.blit(text_surface, text_rect)
            
            #Hinweis
            lang_hint = f"({self.active_greeting['lang'].upper()})"
            hint_surface = self.subtitle_font.render(lang_hint, True, design.get_color("text_muted"))
            hint_rect = hint_surface.get_rect(
                center=(self.width // 2, self.height // 2 + int(20 * self.scale))
            )
            self.screen.blit(hint_surface, hint_rect)
            
            #Fortschrittsbalken
            bar_width = int(400 * self.scale)
            bar_height = int(10 * self.scale)
            bar_x = (self.width - bar_width) // 2
            bar_y = self.height // 2 + int(100 * self.scale)
            
            #Hintergrund
            design.draw_rounded_rect(
                self.screen,
                design.get_color("slider_bg"),
                pygame.Rect(bar_x, bar_y, bar_width, bar_height),
                self.bar_radius
            )
            
            #Fortschritt Balken
            filled_width = int(bar_width * (self.progress / 100))
            if filled_width > 0:
                design.draw_rounded_rect(
                    self.screen,
                    design.get_color("slider_fill"),
                    pygame.Rect(bar_x, bar_y, filled_width, bar_height),
                    self.bar_radius
                )
            
            # Info-Text
            """
            info_text = f"Begrüßung {self.current_index + 1}/{len(self.greetings)}"
            info_surface = self.subtitle_font.render(info_text, True, design.get_color("text_muted"))
            info_rect = info_surface.get_rect(
                center=(self.width // 2, bar_y + int(40 * self.scale))
            )
            self.screen.blit(info_surface, info_rect)"""
    
    def draw_welcome_message(self):
        welcome_text = lang.t("welcome") if hasattr(lang, 't') else "WELCOME"
        text_surface = self.title_font.render(welcome_text, True, design.get_color("text"))
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text_surface, text_rect)
        
        dots = "." * ((pygame.time.get_ticks() // 500) % 4)
        loading_text = self.subtitle_font.render(f"Loading{dots}", True, design.get_color("text_muted"))
        loading_rect = loading_text.get_rect(
            center=(self.width // 2, self.height // 2 + int(80 * self.scale))
        )
        self.screen.blit(loading_text, loading_rect)
    

    def draw_skip_hint(self):
        skip_text = self.subtitle_font.render(
            "",     #  "Drücke ESC oder klicke zum Überspringen",
            True, 
            design.get_color("text_muted")
        )
        skip_rect = skip_text.get_rect(
            center=(self.width // 2, self.height - int(50 * self.scale))
        )
        self.screen.blit(skip_text, skip_rect)
    
    def run(self):
        

        self.start_time = pygame.time.get_ticks()
        self._play_current_greeting()
        
        clock = pygame.time.Clock()
        
        while not self.greeting_complete:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        print("Begrüßung Übersprungen (Benutzer)")
                        self.greeting_complete = True
                        break
                
                if event.type in [pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN]:
                    print(" Begrüßung Übersprungen (Benutzer)")
                    self.greeting_complete = True
                    break
            
            self._update()
            
            self.draw_gradient()
            
            if self.showing_greeting:
                self.draw_greeting()
            else:
                self.draw_welcome_message()
            
            self.draw_skip_hint()
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.mixer.music.stop()
        pygame.event.clear()
        
        print("Begrüßung abgeschlossen")
        return True
