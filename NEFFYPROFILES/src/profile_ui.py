"""
import pygame
import sys
import json
import os
from design_system import design
from settings_manager import settings_manager

class PygameProfileUI:
    def __init__(self, screen, clock, audio):
        self.screen = screen
        self.clock = clock
        self.audio = audio
        
        self.width, self.height = self.screen.get_size()
        self.ref_height = 1080
        self.scale = self.height / self.ref_height
        
        self.font = design.get_font("title", self.scale)
        self.small_font = design.get_font("small", self.scale)
        
        self.profiles_file = "profiles.json"
        self.profiles = self.load_profiles()
        self.current_profile = self.load_current_profile()
        
        # Layout
        self.left_width = int(self.width * 0.6)
        self.right_width = self.width - self.left_width
        
        # Scroll
        self.scroll_y = 0
        self.dragging = False
        self.last_mouse_y = 0
        self.max_scroll = 0
        
        # UI Elemente
        self.selected_profile = None
        self.new_profile_name = ""
        self.input_active = False
        self.input_rect = pygame.Rect(
            self.left_width + design.get_scaled_spacing("padding_large", self.scale),
            int(self.height * 0.15),
            self.right_width - design.get_scaled_spacing("padding_medium", self.scale) * 2,
            design.get_scaled_size("button_height", self.scale)
        )
        
        # Buttons
        button_width = self.right_width - design.get_scaled_spacing("padding_medium", self.scale) * 2
        button_height = design.get_scaled_size("button_height", self.scale)
        button_y = self.height - design.get_scaled_spacing("margin_large", self.scale) * 2
        
        self.create_button = pygame.Rect(
            self.left_width + design.get_scaled_spacing("padding_medium", self.scale),
            button_y - button_height * 2 - design.get_scaled_spacing("margin_small", self.scale),
            button_width,
            button_height
        )
        
        self.load_button = pygame.Rect(
            self.left_width + design.get_scaled_spacing("padding_medium", self.scale),
            button_y - button_height - design.get_scaled_spacing("margin_small", self.scale),
            button_width,
            button_height
        )
        
        self.delete_button = pygame.Rect(
            self.left_width + design.get_scaled_spacing("padding_medium", self.scale),
            button_y,
            button_width,
            button_height
        )
        
        self.back_button = pygame.Rect(
            self.left_width + design.get_scaled_spacing("padding_medium", self.scale),
            self.height - design.get_scaled_spacing("margin_large", self.scale) - button_height,
            button_width,
            button_height
        )
        
        self.button_radius = design.get_border_radius("button")
        self.list_radius = design.get_border_radius("list_item")
        self.panel_radius = design.get_border_radius("panel")
        
        self.gradient_surface = design.create_gradient_surface(
            self.width, self.height, "profile"
        )
        
        self.scale_buttons = {
            "create": 1.0,
            "load": 1.0,
            "delete": 1.0,
            "back": 1.0
        }
        
        self.input_active = False
        
        self.update_max_scroll()
    
    

    def load_profiles(self):
        try:
            if os.path.exists(self.profiles_file):
                with open(self.profiles_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"?? Fehler beim Laden der Profile: {e}")
        return {}
    
    def save_profiles(self):
        try:
            with open(self.profiles_file, "w", encoding="utf-8") as f:
                json.dump(self.profiles, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"?? Fehler beim Speichern der Profile: {e}")
    
    def load_current_profile(self):
        try:
            if os.path.exists("current_profile.txt"):
                with open("current_profile.txt", "r", encoding="utf-8") as f:
                    return f.read().strip()
        except:
            pass
        return None
    
    def save_current_profile(self, profile_name):
        try:
            with open("current_profile.txt", "w", encoding="utf-8") as f:
                f.write(profile_name)
        except Exception as e:
            print(f"?? Fehler beim Speichern des aktuellen Profils: {e}")
    
    def get_profile_settings(self, profile_name):
        if profile_name in self.profiles:
            return self.profiles[profile_name]
        return {
            "language": "de",
            "volume": 50,
            "duration": 180,
            "exercise": "middle",
            "custom_params": {
                "move_up": 4.0,
                "pause_top": 2.0,
                "move_down": 4.0,
                "pause_bottom": 2.0,
                "audio": "assets_mp3/audio/middle.mp3"
            }
        }
    
    def update_max_scroll(self):
        profile_height = design.get_scaled_size("flag_size", self.scale) + design.get_scaled_spacing("margin_medium", self.scale)
        margin = design.get_scaled_spacing("margin_medium", self.scale)
        total_height = len(self.profiles) * (profile_height + margin)
        visible_height = self.height - 200
        self.max_scroll = max(0, total_height - visible_height)
        self.scroll_y = max(-self.max_scroll, min(0, self.scroll_y))
    
    def draw_gradient(self):
        self.screen.blit(self.gradient_surface, (0, 0))
    
    def draw_profile_list(self, mouse):
        profile_height = design.get_scaled_size("flag_size", self.scale) + design.get_scaled_spacing("margin_medium", self.scale)
        margin = design.get_scaled_spacing("margin_medium", self.scale)
        start_y = design.get_scaled_spacing("margin_large", self.scale) + self.scroll_y
        
        result = []
        
        for i, (name, settings) in enumerate(self.profiles.items()):
            rect = pygame.Rect(
                design.get_scaled_spacing("margin_large", self.scale),
                start_y + i * (profile_height + margin),
                self.left_width - design.get_scaled_spacing("margin_medium", self.scale) * 2,
                profile_height
            )


            
            if rect.bottom < 0 or rect.top > self.height:
                continue
            
            hovered = rect.collidepoint(mouse)
            
            if hovered:
                color = design.get_color("info")
                alpha = design.get_ui("alpha_hover")
            elif self.selected_profile == name:
                color = design.get_color("success")
                alpha = design.get_ui("alpha_selected")
            else:
                color = design.get_color("primary")
                alpha = design.get_ui("alpha_normal")
            
            design.draw_rounded_rect(
                self.screen,
                color,
                rect,
                self.list_radius,
                alpha
            )
            
            # Profilname
            text = self.font.render(name.upper(), True, design.get_color("text"))
            text_rect = text.get_rect(
                center=(rect.centerx, rect.centery - 20)
            )
            self.screen.blit(text, text_rect)
            
            # Aktuelle Einstellungen anzeigen
            exercise = settings.get("exercise", "middle")
            duration = settings.get("duration", 180)
            volume = settings.get("volume", 50)
            
            info_text = f"{exercise.upper()} | {duration}s | {volume}%"
            info_surface = self.small_font.render(info_text, True, design.get_color("text_muted"))
            info_rect = info_surface.get_rect(
                center=(rect.centerx, rect.centery + 25)
            )
            self.screen.blit(info_surface, info_rect)
            
            # Aktuelles Profil markieren
            if name == self.current_profile:
                current_text = self.small_font.render("? AKTIV", True, design.get_color("success"))
                current_rect = current_text.get_rect(
                    center=(rect.centerx, rect.centery + 50)
                )
                self.screen.blit(current_text, current_rect)
            
            result.append((name, rect))
        
        return result
    
    def draw_right_panel(self, mouse):
        # Titel
        title = self.font.render("PROFIL VERWALTUNG", True, design.get_color("text"))
        title_x = self.left_width + design.get_scaled_spacing("padding_large", self.scale)
        title_y = design.get_scaled_spacing("margin_large", self.scale)
        self.screen.blit(title, (title_x, title_y))
        
        # Info zum ausgewhlten Profil
        if self.selected_profile:
            info_y = title_y + int(60 * self.scale)
            settings = self.profiles.get(self.selected_profile, {})
            exercise = settings.get("exercise", "middle")
            duration = settings.get("duration", 180)
            volume = settings.get("volume", 50)
            language = settings.get("language", "de")
            
            info_text = f"Ausgewählt: {self.selected_profile}"
            info_surface = self.small_font.render(info_text, True, design.get_color("info"))
            self.screen.blit(info_surface, (title_x, info_y))
            
            settings_y = info_y + int(35 * self.scale)
            settings_text = f"Übung: {exercise.upper()} | Dauer: {duration}s | Lautstärke: {volume}% | Sprache: {language.upper()}"
            settings_surface = self.small_font.render(settings_text, True, design.get_color("text_muted"))
            self.screen.blit(settings_surface, (title_x, settings_y))
        
        # Input-Feld fr neuen Profilnamen
        input_label = self.small_font.render("Neues Profil:", True, design.get_color("text"))
        label_y = title_y + int(140 * self.scale)
        self.screen.blit(input_label, (title_x, label_y))


        
        # Input-Feld zeichnen
        input_y = label_y + int(35 * self.scale)
        input_rect = pygame.Rect(
            title_x,
            input_y,
            self.right_width - design.get_scaled_spacing("padding_medium", self.scale) * 2,
            design.get_scaled_size("button_height", self.scale)
        )
        self.input_rect = input_rect
        
        # Input-Feld Hintergrund
        if self.input_active:
            color = design.get_color("input_active")
        else:
            color = design.get_color("input_inactive")
        
        design.draw_rounded_rect(
            self.screen,
            color,
            input_rect,
            self.button_radius,
            200
        )
        
        # Input-Text
        if self.new_profile_name:
            text_surface = self.small_font.render(
                self.new_profile_name,
                True,
                design.get_color("text")
            )
        else:
            text_surface = self.small_font.render(
                "Profilname eingeben...",
                True,
                design.get_color("text_muted")
            )
        
        text_x = input_rect.x + design.get_scaled_spacing("padding_small", self.scale)
        text_y = input_rect.centery - text_surface.get_height() // 2
        self.screen.blit(text_surface, (text_x, text_y))
        
        # Cursor blinken
        if self.input_active and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = text_x + text_surface.get_width() + 5
            cursor_y = input_rect.centery - design.get_scaled_size("button_height", self.scale) // 3
            pygame.draw.line(
                self.screen,
                design.get_color("text"),
                (cursor_x, cursor_y),
                (cursor_x, cursor_y + design.get_scaled_size("button_height", self.scale) * 2 // 3),
                2
            )
        
        # Buttons zeichnen
        buttons = [
            ("create", self.create_button, "Profil erstellen", self.scale_buttons["create"]),
            ("load", self.load_button, "Profil laden", self.scale_buttons["load"]),
            ("delete", self.delete_button, "Profil löschen", self.scale_buttons["delete"]),
            ("back", self.back_button, "Zurück", self.scale_buttons["back"])
        ]
        
        results = {}
        for name, rect, text, scale_var in buttons:
            hovered = rect.collidepoint(mouse)
            
            target_scale = design.get_animation("hover_scale") if hovered else 1.0
            self.scale_buttons[name] += (target_scale - self.scale_buttons[name]) * design.get_animation("animation_speed")
            scale = self.scale_buttons[name]
            
            draw_rect = pygame.Rect(0, 0,
                int(rect.width * scale),
                int(rect.height * scale)
            )
            draw_rect.center = rect.center
            

            
            if name == "delete":
                color_name = "danger_hover" if hovered else "danger"
            elif name == "back":
                color_name = "secondary_hover" if hovered else "secondary"
            elif name == "create":
                color_name = "success_hover" if hovered else "success"
            else:
                color_name = "button_confirm_hover" if hovered else "button_confirm"
            
            design.draw_rounded_rect(
                self.screen,
                design.get_color(color_name),
                draw_rect,
                self.button_radius,
                design.get_ui("alpha_button")
            )
            
            text_surface = self.small_font.render(text, True, design.get_color("text"))
            text_rect = text_surface.get_rect(center=draw_rect.center)
            self.screen.blit(text_surface, text_rect)
            
            results[name] = hovered
        
        return results
    
    def run(self):
        self.audio.play("ui")
        
        while True:
            mouse = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    
                    if event.key == pygame.K_RETURN:
                        if self.input_active and self.new_profile_name:
                            if self.new_profile_name not in self.profiles:
                                # Profil mit Standardeinstellungen erstellen
                                self.profiles[self.new_profile_name] = {
                                    "language": "de",
                                    "volume": 50,
                                    "duration": 180,
                                    "exercise": "middle",
                                    "custom_params": {
                                        "move_up": 4.0,
                                        "pause_top": 2.0,
                                        "move_down": 4.0,
                                        "pause_bottom": 2.0,
                                        "audio": "assets_mp3/audio/middle.mp3"
                                    }
                                }
                                self.save_profiles()
                                self.update_max_scroll()
                                self.selected_profile = self.new_profile_name
                                self.new_profile_name = ""
                                self.input_active = False
                                print(f"?? Profil '{self.selected_profile}' erstellt")
                            else:
                                print(f"?? Profil '{self.new_profile_name}' existiert bereits!")
                    
                    if self.input_active:
                        if event.key == pygame.K_BACKSPACE:
                            self.new_profile_name = self.new_profile_name[:-1]
                        elif event.unicode.isalnum() or event.unicode in " _-":
                            self.new_profile_name += event.unicode
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Input-Feld Fokus
                    if hasattr(self, 'input_rect') and self.input_rect.collidepoint(mouse):
                        self.input_active = True
                    else:
                        self.input_active = False
                    
                    # Profile Liste
                    if hasattr(self, 'profile_list'):
                        for name, rect in self.profile_list:
                            if rect.collidepoint(mouse):
                                self.selected_profile = name
                                print(f"?? Profil ausgewählt: {name}")
                                


                    
                    # Buttons
                    if self.create_button.collidepoint(mouse):
                        if self.new_profile_name and self.new_profile_name not in self.profiles:
                            self.profiles[self.new_profile_name] = {
                                "language": "de",
                                "volume": 50,
                                "duration": 180,
                                "exercise": "middle",
                                "custom_params": {
                                    "move_up": 4.0,
                                    "pause_top": 2.0,
                                    "move_down": 4.0,
                                    "pause_bottom": 2.0,
                                    "audio": "assets_mp3/audio/middle.mp3"
                                }
                            }
                            self.save_profiles()
                            self.update_max_scroll()
                            self.selected_profile = self.new_profile_name
                            self.new_profile_name = ""
                            self.input_active = False
                            print(f"?? Profil '{self.selected_profile}' erstellt")
                        else:
                            if not self.new_profile_name:
                                print("?? Bitte einen Profilnamen eingeben")
                            else:
                                print(f"?? Profil '{self.new_profile_name}' existiert bereits!")
                    
                    elif self.load_button.collidepoint(mouse):
                        if self.selected_profile:
                            self.current_profile = self.selected_profile
                            self.save_current_profile(self.selected_profile)
                            # Einstellungen in den Settings Manager laden
                            settings = self.get_profile_settings(self.selected_profile)
                            settings_manager.profile_name = self.selected_profile
                            settings_manager.current_settings.update(settings)
                            print(f"?? Profil geladen: {self.selected_profile}")
                            print(f"   Einstellungen: {settings}")
                            # Kurze Rckmeldung im UI (wird im nchsten Frame angezeigt)
                    
                    elif self.delete_button.collidepoint(mouse):
                        if self.selected_profile:
                            if self.selected_profile == self.current_profile:
                                print(f"?? Kann aktuelles Profil '{self.selected_profile}' nicht löschen!")
                            else:
                                del self.profiles[self.selected_profile]
                                self.save_profiles()
                                self.update_max_scroll()
                                if self.current_profile == self.selected_profile:
                                    self.current_profile = None
                                    if os.path.exists("current_profile.txt"):
                                        os.remove("current_profile.txt")
                                self.selected_profile = None
                                print(f"?? Profil gelöscht")
                    
                    elif self.back_button.collidepoint(mouse):
                        self.audio.stop()
                        return "back"
                    
                    self.dragging = True
                    self.last_mouse_y = mouse[1]
                
                if event.type == pygame.MOUSEMOTION and self.dragging:
                    dy = mouse[1] - self.last_mouse_y
                    self.scroll_y += dy
                    self.last_mouse_y = mouse[1]
                    self.scroll_y = max(-self.max_scroll, min(0, self.scroll_y))
                
                if event.type == pygame.MOUSEBUTTONUP:
                    self.dragging = False
                    
                    

                
                if event.type == pygame.MOUSEWHEEL:
                    scroll_step = design.get_animation("scroll_step") * int(self.scale)
                    self.scroll_y += event.y * scroll_step
                    self.scroll_y = max(-self.max_scroll, min(0, self.scroll_y))
            
            # Zeichnen
            self.draw_gradient()
            
            self.profile_list = self.draw_profile_list(mouse)
            button_results = self.draw_right_panel(mouse)
            
            pygame.display.flip()
            self.clock.tick(60)
"""




#jetzt mit korrekter Sprachanwendung
"""
import pygame
import sys
import json
import os
from design_system import design
from settings_manager import settings_manager
from language_manager import lang

class PygameProfileUI:
    def __init__(self, screen, clock, audio):
        self.screen = screen
        self.clock = clock
        self.audio = audio
        
        self.width, self.height = self.screen.get_size()
        self.ref_height = 1080
        self.scale = self.height / self.ref_height
        
        self.font = design.get_font("title", self.scale)
        self.small_font = design.get_font("small", self.scale)
        
        self.profiles_file = "profiles.json"
        self.profiles = self.load_profiles()
        self.current_profile = self.load_current_profile()
        
        # Layout
        self.left_width = int(self.width * 0.6)
        self.right_width = self.width - self.left_width
        
        # Scroll
        self.scroll_y = 0
        self.dragging = False
        self.last_mouse_y = 0
        self.max_scroll = 0
        
        # UI Elemente
        self.selected_profile = None
        self.new_profile_name = ""
        self.input_active = False
        self.input_rect = pygame.Rect(
            self.left_width + design.get_scaled_spacing("padding_large", self.scale),
            int(self.height * 0.15),
            self.right_width - design.get_scaled_spacing("padding_medium", self.scale) * 2,
            design.get_scaled_size("button_height", self.scale)
        )
        
        # Buttons
        button_width = self.right_width - design.get_scaled_spacing("padding_medium", self.scale) * 2
        button_height = design.get_scaled_size("button_height", self.scale)
        button_y = self.height - design.get_scaled_spacing("margin_large", self.scale) * 2
        
        self.create_button = pygame.Rect(
            self.left_width + design.get_scaled_spacing("padding_medium", self.scale),
            button_y - button_height * 2 - design.get_scaled_spacing("margin_small", self.scale),
            button_width,
            button_height
        )
        
        self.load_button = pygame.Rect(
            self.left_width + design.get_scaled_spacing("padding_medium", self.scale),
            button_y - button_height - design.get_scaled_spacing("margin_small", self.scale),
            button_width,
            button_height
        )
        
        self.delete_button = pygame.Rect(
            self.left_width + design.get_scaled_spacing("padding_medium", self.scale),
            button_y,
            button_width,
            button_height
        )
        

        
        self.back_button = pygame.Rect(
            self.left_width + design.get_scaled_spacing("padding_medium", self.scale),
            self.height - design.get_scaled_spacing("margin_large", self.scale) - button_height,
            button_width,
            button_height
        )
        
        self.button_radius = design.get_border_radius("button")
        self.list_radius = design.get_border_radius("list_item")
        self.panel_radius = design.get_border_radius("panel")
        
        self.gradient_surface = design.create_gradient_surface(
            self.width, self.height, "profile"
        )
        
        self.scale_buttons = {
            "create": 1.0,
            "load": 1.0,
            "delete": 1.0,
            "back": 1.0
        }
        
        self.input_active = False
        
        self.update_max_scroll()
    
    def load_profiles(self):
        try:
            if os.path.exists(self.profiles_file):
                with open(self.profiles_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"?? Fehler beim Laden der Profile: {e}")
        return {}
    
    def save_profiles(self):
        try:
            with open(self.profiles_file, "w", encoding="utf-8") as f:
                json.dump(self.profiles, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"?? Fehler beim Speichern der Profile: {e}")
    
    def load_current_profile(self):
        try:
            if os.path.exists("current_profile.txt"):
                with open("current_profile.txt", "r", encoding="utf-8") as f:
                    return f.read().strip()
        except:
            pass
        return None
    
    def save_current_profile(self, profile_name):
        try:
            with open("current_profile.txt", "w", encoding="utf-8") as f:
                f.write(profile_name)
        except Exception as e:
            print(f"?? Fehler beim Speichern des aktuellen Profils: {e}")
    

    def get_profile_settings(self, profile_name):
        if profile_name in self.profiles:
            return self.profiles[profile_name]
        return {
            "language": "de",
            "volume": 50,
            "duration": 180,
            "exercise": "middle",
            "custom_params": {
                "move_up": 4.0,
                "pause_top": 2.0,
                "move_down": 4.0,
                "pause_bottom": 2.0,
                "audio": "assets_mp3/audio/middle.mp3"
            }
        }
    
    def update_max_scroll(self):
        profile_height = design.get_scaled_size("flag_size", self.scale) + design.get_scaled_spacing("margin_medium", self.scale)
        margin = design.get_scaled_spacing("margin_medium", self.scale)
        total_height = len(self.profiles) * (profile_height + margin)
        visible_height = self.height - 200
        self.max_scroll = max(0, total_height - visible_height)
        self.scroll_y = max(-self.max_scroll, min(0, self.scroll_y))
    
    def draw_gradient(self):
        self.screen.blit(self.gradient_surface, (0, 0))
    
    def draw_profile_list(self, mouse):
        profile_height = design.get_scaled_size("flag_size", self.scale) + design.get_scaled_spacing("margin_medium", self.scale)
        margin = design.get_scaled_spacing("margin_medium", self.scale)
        start_y = design.get_scaled_spacing("margin_large", self.scale) + self.scroll_y
        
        result = []
        
        for i, (name, settings) in enumerate(self.profiles.items()):
            rect = pygame.Rect(
                design.get_scaled_spacing("margin_large", self.scale),
                start_y + i * (profile_height + margin),
                self.left_width - design.get_scaled_spacing("margin_medium", self.scale) * 2,
                profile_height
            )
            
            if rect.bottom < 0 or rect.top > self.height:
                continue
            
            hovered = rect.collidepoint(mouse)
            
            if hovered:
                color = design.get_color("info")
                alpha = design.get_ui("alpha_hover")
            elif self.selected_profile == name:
                color = design.get_color("success")
                alpha = design.get_ui("alpha_selected")
            else:
                color = design.get_color("primary")
                alpha = design.get_ui("alpha_normal")
            
            design.draw_rounded_rect(
                self.screen,
                color,
                rect,
                self.list_radius,
                alpha
            )


            
            # Profilname
            text = self.font.render(name.upper(), True, design.get_color("text"))
            text_rect = text.get_rect(
                center=(rect.centerx, rect.centery - 20)
            )
            self.screen.blit(text, text_rect)
            
            # Aktuelle Einstellungen anzeigen - MIT LANG
            exercise = settings.get("exercise", "middle")
            exercise_display = lang.t(exercise) if hasattr(lang, 't') else exercise.upper()
            duration = settings.get("duration", 180)
            volume = settings.get("volume", 50)
            
            info_text = f"{exercise_display} | {duration}s | {volume}%"
            info_surface = self.small_font.render(info_text, True, design.get_color("text_muted"))
            info_rect = info_surface.get_rect(
                center=(rect.centerx, rect.centery + 25)
            )
            self.screen.blit(info_surface, info_rect)
            
            # Aktuelles Profil markieren
            if name == self.current_profile:
                current_text = "? AKTIV"
                current_surface = self.small_font.render(current_text, True, design.get_color("success"))
                current_rect = current_surface.get_rect(
                    center=(rect.centerx, rect.centery + 50)
                )
                self.screen.blit(current_surface, current_rect)
            
            result.append((name, rect))
        
        return result
    
    def draw_right_panel(self, mouse):
        # Titel - MIT LANG
        title = self.font.render("PROFIL VERWALTUNG", True, design.get_color("text"))
        title_x = self.left_width + design.get_scaled_spacing("padding_large", self.scale)
        title_y = design.get_scaled_spacing("margin_large", self.scale)
        self.screen.blit(title, (title_x, title_y))
        
        # Info zum ausgewhlten Profil
        if self.selected_profile:
            info_y = title_y + int(60 * self.scale)
            settings = self.profiles.get(self.selected_profile, {})
            exercise = settings.get("exercise", "middle")
            exercise_display = lang.t(exercise) if hasattr(lang, 't') else exercise.upper()
            duration = settings.get("duration", 180)
            volume = settings.get("volume", 50)
            language = settings.get("language", "de")
            
            info_text = f"Ausgewählt: {self.selected_profile}"
            info_surface = self.small_font.render(info_text, True, design.get_color("info"))
            self.screen.blit(info_surface, (title_x, info_y))
            
            settings_y = info_y + int(35 * self.scale)
            settings_text = f"Übung: {exercise_display} | Dauer: {duration}s | Lautstärke: {volume}% | Sprache: {language.upper()}"
            settings_surface = self.small_font.render(settings_text, True, design.get_color("text_muted"))
            self.screen.blit(settings_surface, (title_x, settings_y))
        
        # Input-Feld für neuen Profilnamen
        input_label = self.small_font.render("Neues Profil:", True, design.get_color("text"))
        label_y = title_y + int(140 * self.scale)
        self.screen.blit(input_label, (title_x, label_y))
        


        # Input-Feld zeichnen
        input_y = label_y + int(35 * self.scale)
        input_rect = pygame.Rect(
            title_x,
            input_y,
            self.right_width - design.get_scaled_spacing("padding_medium", self.scale) * 2,
            design.get_scaled_size("button_height", self.scale)
        )
        self.input_rect = input_rect
        
        # Input-Feld Hintergrund
        if self.input_active:
            color = design.get_color("input_active")
        else:
            color = design.get_color("input_inactive")
        
        design.draw_rounded_rect(
            self.screen,
            color,
            input_rect,
            self.button_radius,
            200
        )
        
        # Input-Text
        if self.new_profile_name:
            text_surface = self.small_font.render(
                self.new_profile_name,
                True,
                design.get_color("text")
            )
        else:
            text_surface = self.small_font.render(
                "Profilname eingeben...",
                True,
                design.get_color("text_muted")
            )
        
        text_x = input_rect.x + design.get_scaled_spacing("padding_small", self.scale)
        text_y = input_rect.centery - text_surface.get_height() // 2
        self.screen.blit(text_surface, (text_x, text_y))
        
        # Cursor blinken
        if self.input_active and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = text_x + text_surface.get_width() + 5
            cursor_y = input_rect.centery - design.get_scaled_size("button_height", self.scale) // 3
            pygame.draw.line(
                self.screen,
                design.get_color("text"),
                (cursor_x, cursor_y),
                (cursor_x, cursor_y + design.get_scaled_size("button_height", self.scale) * 2 // 3),
                2
            )
        
        # Buttons zeichnen - MIT LANG
        buttons = [
            ("create", self.create_button, lang.t("create") if hasattr(lang, 't') else "Profil erstellen", self.scale_buttons["create"]),
            ("load", self.load_button, lang.t("load") if hasattr(lang, 't') else "Profil laden", self.scale_buttons["load"]),
            ("delete", self.delete_button, lang.t("delete") if hasattr(lang, 't') else "Profil löschen", self.scale_buttons["delete"]),
            ("back", self.back_button, lang.t("back") if hasattr(lang, 't') else "Zurück", self.scale_buttons["back"])
        ]
        
        results = {}
        for name, rect, text, scale_var in buttons:
            hovered = rect.collidepoint(mouse)
            
            target_scale = design.get_animation("hover_scale") if hovered else 1.0
            self.scale_buttons[name] += (target_scale - self.scale_buttons[name]) * design.get_animation("animation_speed")
            scale = self.scale_buttons[name]



            
            draw_rect = pygame.Rect(0, 0,
                int(rect.width * scale),
                int(rect.height * scale)
            )
            draw_rect.center = rect.center
            
            if name == "delete":
                color_name = "danger_hover" if hovered else "danger"
            elif name == "back":
                color_name = "secondary_hover" if hovered else "secondary"
            elif name == "create":
                color_name = "success_hover" if hovered else "success"
            else:
                color_name = "button_confirm_hover" if hovered else "button_confirm"
            
            design.draw_rounded_rect(
                self.screen,
                design.get_color(color_name),
                draw_rect,
                self.button_radius,
                design.get_ui("alpha_button")
            )
            
            text_surface = self.small_font.render(text, True, design.get_color("text"))
            text_rect = text_surface.get_rect(center=draw_rect.center)
            self.screen.blit(text_surface, text_rect)
            
            results[name] = hovered
        
        return results
    
    def run(self):
        self.audio.play("ui")
        
        while True:
            mouse = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    
                    if event.key == pygame.K_RETURN:
                        if self.input_active and self.new_profile_name:
                            if self.new_profile_name not in self.profiles:
                                # Profil mit Standardeinstellungen erstellen
                                self.profiles[self.new_profile_name] = {
                                    "language": "de",
                                    "volume": 50,
                                    "duration": 180,
                                    "exercise": "middle",
                                    "custom_params": {
                                        "move_up": 4.0,
                                        "pause_top": 2.0,
                                        "move_down": 4.0,
                                        "pause_bottom": 2.0,
                                        "audio": "assets_mp3/audio/middle.mp3"
                                    }
                                }
                                self.save_profiles()
                                self.update_max_scroll()
                                self.selected_profile = self.new_profile_name
                                self.new_profile_name = ""
                                self.input_active = False
                                print(f"?? Profil '{self.selected_profile}' erstellt")
                            else:
                                print(f"?? Profil '{self.new_profile_name}' existiert bereits!")
                                
                                

                    
                    if self.input_active:
                        if event.key == pygame.K_BACKSPACE:
                            self.new_profile_name = self.new_profile_name[:-1]
                        elif event.unicode.isalnum() or event.unicode in " _-":
                            self.new_profile_name += event.unicode
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Input-Feld Fokus
                    if hasattr(self, 'input_rect') and self.input_rect.collidepoint(mouse):
                        self.input_active = True
                    else:
                        self.input_active = False
                    
                    # Profile Liste
                    if hasattr(self, 'profile_list'):
                        for name, rect in self.profile_list:
                            if rect.collidepoint(mouse):
                                self.selected_profile = name
                                print(f"?? Profil ausgewählt: {name}")
                    
                    # Buttons
                    if self.create_button.collidepoint(mouse):
                        if self.new_profile_name and self.new_profile_name not in self.profiles:
                            self.profiles[self.new_profile_name] = {
                                "language": "de",
                                "volume": 50,
                                "duration": 180,
                                "exercise": "middle",
                                "custom_params": {
                                    "move_up": 4.0,
                                    "pause_top": 2.0,
                                    "move_down": 4.0,
                                    "pause_bottom": 2.0,
                                    "audio": "assets_mp3/audio/middle.mp3"
                                }
                            }
                            self.save_profiles()
                            self.update_max_scroll()
                            self.selected_profile = self.new_profile_name
                            self.new_profile_name = ""
                            self.input_active = False
                            print(f"?? Profil '{self.selected_profile}' erstellt")
                        else:
                            if not self.new_profile_name:
                                print("?? Bitte einen Profilnamen eingeben")
                            else:
                                print(f"?? Profil '{self.new_profile_name}' existiert bereits!")
                    
                    elif self.load_button.collidepoint(mouse):
                        if self.selected_profile:
                            self.current_profile = self.selected_profile
                            self.save_current_profile(self.selected_profile)
                            # Einstellungen in den Settings Manager laden
                            settings = self.get_profile_settings(self.selected_profile)
                            settings_manager.profile_name = self.selected_profile
                            settings_manager.current_settings.update(settings)
                            print(f"?? Profil geladen: {self.selected_profile}")
                            print(f"   Einstellungen: {settings}")
                    

                    elif self.delete_button.collidepoint(mouse):
                        if self.selected_profile:
                            if self.selected_profile == self.current_profile:
                                print(f"?? Kann aktuelles Profil '{self.selected_profile}' nicht löschen!")
                            else:
                                del self.profiles[self.selected_profile]
                                self.save_profiles()
                                self.update_max_scroll()
                                if self.current_profile == self.selected_profile:
                                    self.current_profile = None
                                    if os.path.exists("current_profile.txt"):
                                        os.remove("current_profile.txt")
                                self.selected_profile = None
                                print(f"?? Profil gelöscht")
                    
                    elif self.back_button.collidepoint(mouse):
                        self.audio.stop()
                        return "back"
                    
                    self.dragging = True
                    self.last_mouse_y = mouse[1]
                
                if event.type == pygame.MOUSEMOTION and self.dragging:
                    dy = mouse[1] - self.last_mouse_y
                    self.scroll_y += dy
                    self.last_mouse_y = mouse[1]
                    self.scroll_y = max(-self.max_scroll, min(0, self.scroll_y))
                
                if event.type == pygame.MOUSEBUTTONUP:
                    self.dragging = False
                
                if event.type == pygame.MOUSEWHEEL:
                    scroll_step = design.get_animation("scroll_step") * int(self.scale)
                    self.scroll_y += event.y * scroll_step
                    self.scroll_y = max(-self.max_scroll, min(0, self.scroll_y))
            
            # Zeichnen
            self.draw_gradient()
            
            self.profile_list = self.draw_profile_list(mouse)
            button_results = self.draw_right_panel(mouse)
            
            pygame.display.flip()
            self.clock.tick(60)
"""





#sollte jetzt auch bei Änderung des Profils korrekt die Sprache sofort anwenden
"""
import pygame
import sys
import json
import os
from design_system import design
from settings_manager import settings_manager
from language_manager import lang

class PygameProfileUI:
    def __init__(self, screen, clock, audio):
        self.screen = screen
        self.clock = clock
        self.audio = audio
        
        self.width, self.height = self.screen.get_size()
        self.ref_height = 1080
        self.scale = self.height / self.ref_height
        
        self.font = design.get_font("title", self.scale)
        self.small_font = design.get_font("small", self.scale)
        
        self.profiles_file = "profiles.json"
        self.profiles = self.load_profiles()
        self.current_profile = self.load_current_profile()
        
        # Layout
        self.left_width = 0.8* int(self.width * 0.6)
        self.right_width = self.width - self.left_width
        
        # Scroll
        self.scroll_y = 0
        self.dragging = False
        self.last_mouse_y = 0
        self.max_scroll = 0
        
        # UI Elemente
        self.selected_profile = None
        self.new_profile_name = ""
        self.input_active = False
        self.input_rect = pygame.Rect(
            self.left_width + design.get_scaled_spacing("padding_large", self.scale),     
            int(self.height * 0.15),
            self.right_width - design.get_scaled_spacing("padding_medium", self.scale) * 2,
            design.get_scaled_size("button_height", self.scale)
        )
        
        # Buttons
        button_width = 0.7 * self.right_width - design.get_scaled_spacing("padding_medium", self.scale) * 2
        button_height = 1.3 * design.get_scaled_size("button_height", self.scale)
        button_y = self.height - design.get_scaled_spacing("margin_large", self.scale) * 2
        
        self.create_button = pygame.Rect(
            1.1 * self.left_width + design.get_scaled_spacing("padding_medium", self.scale),
            button_y - button_height * 6.7 - design.get_scaled_spacing("margin_small", self.scale),   #2
            1.15 * button_width,
            1.5 * button_height
        )
        
        self.load_button = pygame.Rect(
            1.1 * self.left_width + design.get_scaled_spacing("padding_medium", self.scale),
            button_y - button_height * 4.7 - design.get_scaled_spacing("margin_small", self.scale),
            1.15 * button_width,
            1.5 * button_height
        )
        
        
        self.delete_button = pygame.Rect(
            1.1 * self.left_width + design.get_scaled_spacing("padding_medium", self.scale),
            button_y - button_height * 2.7 - design.get_scaled_spacing("margin_small", self.scale),
            1.15 * button_width,
            1.5 * button_height
        )
        
        
        self.back_button = pygame.Rect(
            1.1 * self.left_width + design.get_scaled_spacing("padding_medium", self.scale),
            button_y - button_height  *0.7- design.get_scaled_spacing("margin_small", self.scale),
            1.15 * button_width,
            1.5* button_height
        )
        
    
        self.button_radius = design.get_border_radius("button")
        self.list_radius = design.get_border_radius("list_item")
        self.panel_radius = design.get_border_radius("panel")
        
        self.gradient_surface = design.create_gradient_surface(
            self.width, self.height, "profile"
        )
        
        self.scale_buttons = {
            "create": 1.0,
            "load": 1.0,
            "delete": 1.0,
            "back": 1.0
        }


        
        self.input_active = False
        
        self.update_max_scroll()
    
    def load_profiles(self):
        try:
            if os.path.exists(self.profiles_file):
                with open(self.profiles_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"?? Fehler beim Laden der Profile: {e}")
        return {}
    
    def save_profiles(self):
        try:
            with open(self.profiles_file, "w", encoding="utf-8") as f:
                json.dump(self.profiles, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"?? Fehler beim Speichern der Profile: {e}")
    
    def load_current_profile(self):
        try:
            if os.path.exists("current_profile.txt"):
                with open("current_profile.txt", "r", encoding="utf-8") as f:
                    return f.read().strip()
        except:
            pass
        return None
    
    def save_current_profile(self, profile_name):
        try:
            with open("current_profile.txt", "w", encoding="utf-8") as f:
                f.write(profile_name)
        except Exception as e:
            print(f"?? Fehler beim Speichern des aktuellen Profils: {e}")
    
    def get_profile_settings(self, profile_name):
        if profile_name in self.profiles:
            return self.profiles[profile_name]
        return {
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
    
    def update_max_scroll(self):
        profile_height = design.get_scaled_size("flag_size", self.scale) + design.get_scaled_spacing("margin_medium", self.scale)
        margin = design.get_scaled_spacing("margin_medium", self.scale)
        total_height = len(self.profiles) * (profile_height + margin)
        visible_height = self.height - 200
        self.max_scroll = max(0, total_height - visible_height)
        self.scroll_y = max(-self.max_scroll, min(0, self.scroll_y))
    
    def draw_gradient(self):
        self.screen.blit(self.gradient_surface, (0, 0))
        
            
    def draw_profile_list(self, mouse):
        # ========================================
        # EINFACHE POSITIONIERUNG
        # ========================================
        # Hhe eines Listeneintrags (kleiner)
        profile_height = int(100 * self.scale)  # Feste Hhe, einfacher zu kontrollieren60
        
        # Abstand zwischen den Eintrgen
        margin = int(30 * self.scale)   #10
        
        # Startposition: 150px vom oberen Rand, 100px vom linken Rand
        start_x = int(100 * self.scale)
        start_y = int(100 * self.scale) + self.scroll_y
        
        # Breite der Liste: bis zum rechten Panel
        list_width = self.left_width - start_x - int(100 * self.scale)  #50
        
        result = []
        
        for i, (name, settings) in enumerate(self.profiles.items()):
            # Rechteck fr jeden Eintrag
            rect = pygame.Rect(
                start_x,
                start_y + i * (profile_height + margin),
                list_width,
                profile_height
            )
            
            # berspringe Eintrge auerhalb des sichtbaren Bereichs
            if rect.bottom < 0 or rect.top > self.height:
                continue
            
            # Hover-Effekt
            hovered = rect.collidepoint(mouse)
            
            # Farbe je nach Status
            if hovered:
                color = design.get_color("info")
                alpha = design.get_ui("alpha_hover")
            elif self.selected_profile == name:
                color = design.get_color("success")
                alpha = design.get_ui("alpha_selected")
            else:
                color = design.get_color("primary")
                alpha = design.get_ui("alpha_normal")
            
            # Hintergrund zeichnen
            design.draw_rounded_rect(
                self.screen,
                color,
                rect,
                self.list_radius,
                alpha
            )
    
            
            # ========================================
            # NUR PROFILNAME (zentriert)
            # ========================================
            text = self.font.render(name.upper(), True, design.get_color("text"))
            text_rect = text.get_rect(
                center=(rect.centerx - 40, rect.centery)  # Etwas nach links fr "AKTIV"
            )
            self.screen.blit(text, text_rect)
            
            # ========================================
            # "AKTIV" MIT SPRACHLOGIK
            # ========================================
            if name == self.current_profile:
                # "AKTIV" aus der Sprachdatei laden
                active_text = lang.t("active") if hasattr(lang, 't') else "AKTIV"
                active_surface = self.small_font.render(active_text, True, design.get_color("success"))
                active_rect = active_surface.get_rect(
                    center=(rect.right - 100, rect.centery)  # Rechts neben dem Namen
                )
                self.screen.blit(active_surface, active_rect)
            
            result.append((name, rect))
        
        return result

	        
    def draw_right_panel(self, mouse):
        # Titel - MIT LANG
        title_text = lang.t("profile") if hasattr(lang, 't') else "PROFIL VERWALTUNG"
        title = self.font.render(title_text.upper(), True, design.get_color("text"))
        title_x = self.left_width + design.get_scaled_spacing("padding_large", self.scale)
        title_y = design.get_scaled_spacing("margin_large", self.scale)
        self.screen.blit(title, (title_x, title_y))
        
        # ========================================
        # INFO ZUM AUSGEWHLTEN PROFIL (MEHRZEILIG)
        # ========================================
        if self.selected_profile:
            info_y = title_y + int(80 * self.scale) #60
            settings = self.profiles.get(self.selected_profile, {})
            exercise = settings.get("exercise", "middle")
            exercise_display = lang.t(exercise) if hasattr(lang, 't') else exercise.upper()
            duration = settings.get("duration", 180)
            volume = settings.get("volume", 50)
            language = settings.get("language", "de")
            
            # "Ausgewhlt:" mit lang
            selected_text = lang.t("selected") if hasattr(lang, 't') else "Ausgewählt:"
            info_text = f"{selected_text} {self.selected_profile}"
            info_surface = self.small_font.render(info_text, True, design.get_color("info"))
            self.screen.blit(info_surface, (title_x, info_y))
            
            # ========================================
            # MEHRZEILIGE INFORMATIONEN
            # ========================================
            settings_y = info_y + int(40 * self.scale)
            
            # Labels mit lang
            exercise_label = lang.t("exercise") if hasattr(lang, 't') else "Übung"
            duration_label = lang.t("duration") if hasattr(lang, 't') else "Dauer"
            volume_label = lang.t("volume") if hasattr(lang, 't') else "Lautstärke"
            language_label = lang.t("language") if hasattr(lang, 't') else "Sprache"
            
            # Zeile 1: bung und Dauer
            line1 = f"{exercise_label}: {exercise_display}  |  {duration_label}: {duration}s"
            line1_surface = self.small_font.render(line1, True, design.get_color("text_muted"))
            self.screen.blit(line1_surface, (title_x, settings_y + int(20 * self.scale)))
            
            # Zeile 2: Lautstrke und Sprache
            line2 = f"{volume_label}: {volume}%  |  {language_label}: {language.upper()}"
            line2_surface = self.small_font.render(line2, True, design.get_color("text_muted"))
            self.screen.blit(line2_surface, (title_x, settings_y + int(80 * self.scale))) #30
        
        # ========================================
        # INPUT-FELD
        # ========================================
        input_y = title_y + int(280 * self.scale)  # Mehr Abstand fr 2 Zeilen Info  180
        input_rect = pygame.Rect(
            title_x,
            input_y,
            self.right_width - design.get_scaled_spacing("padding_medium", self.scale) * 4,  #2
            design.get_scaled_size("button_height", self.scale)
        )
        self.input_rect = input_rect
        
        # Input-Feld Hintergrund
        if self.input_active:
            color = design.get_color("input_active")
        else:
            color = design.get_color("input_inactive")
        
        design.draw_rounded_rect(
            self.screen,
            color,
            input_rect,
            self.button_radius,
            200
        )
        
    
        
        # Input-Text - MIT LANG fr Platzhalter
        if self.new_profile_name:
            text_surface = self.small_font.render(
                self.new_profile_name,
                True,
                design.get_color("text")
            )
        else:
            placeholder_text = lang.t("enter_profile_name") if hasattr(lang, 't') else "Profilname eingeben..."
            text_surface = self.small_font.render(
                placeholder_text,
                True,
                design.get_color("text_muted")
            )
        
        text_x = input_rect.x + design.get_scaled_spacing("padding_small", self.scale)
        text_y = input_rect.centery - text_surface.get_height() // 2
        self.screen.blit(text_surface, (text_x, text_y))
        
        # Cursor blinken
        if self.input_active and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = text_x + text_surface.get_width() + 5
            cursor_y = input_rect.centery - design.get_scaled_size("button_height", self.scale) // 3
            pygame.draw.line(
                self.screen,
                design.get_color("text"),
                (cursor_x, cursor_y),
                (cursor_x, cursor_y + design.get_scaled_size("button_height", self.scale) * 2 // 3),
                2
            )
        
        # ========================================
        # BUTTONS
        # ========================================
        buttons = [
            ("create", self.create_button, lang.t("create") if hasattr(lang, 't') else "Profil erstellen", self.scale_buttons["create"]),
            ("load", self.load_button, lang.t("load") if hasattr(lang, 't') else "Profil laden", self.scale_buttons["load"]),
            ("delete", self.delete_button, lang.t("delete") if hasattr(lang, 't') else "Profil löschen", self.scale_buttons["delete"]),
            ("back", self.back_button, lang.t("back") if hasattr(lang, 't') else "Zurück", self.scale_buttons["back"])
        ]
        
        results = {}
        for name, rect, text, scale_var in buttons:
            hovered = rect.collidepoint(mouse)
            
            target_scale = design.get_animation("hover_scale") if hovered else 1.0
            self.scale_buttons[name] += (target_scale - self.scale_buttons[name]) * design.get_animation("animation_speed")
            scale = self.scale_buttons[name]
            
            draw_rect = pygame.Rect(0, 0,
                int(rect.width * scale),
                int(rect.height * scale)
            )
            draw_rect.center = rect.center
    
    
            
            if name == "delete":
                color_name = "danger_hover" if hovered else "danger"
            elif name == "back":
                color_name = "secondary_hover" if hovered else "secondary"
            elif name == "create":
                color_name = "success_hover" if hovered else "success"
            else:
                color_name = "button_confirm_hover" if hovered else "button_confirm"
            
            design.draw_rounded_rect(
                self.screen,
                design.get_color(color_name),
                draw_rect,
                self.button_radius,
                design.get_ui("alpha_button")
            )
            
            text_surface = self.small_font.render(text, True, design.get_color("text"))
            text_rect = text_surface.get_rect(center=draw_rect.center)
            self.screen.blit(text_surface, text_rect)
            
            results[name] = hovered
        
        return results
    
        

    
    def _apply_profile_language(self, profile_name):
        #Wendet die Sprache des Profils an
        if profile_name in self.profiles:
            settings = self.profiles[profile_name]
            language = settings.get("language", "de")
            try:
                lang.load(language)
                # Auch AudioManager Sprache setzen
                if hasattr(self, 'audio') and self.audio:
                    self.audio.set_language(language)
                print(f"?? Sprache auf '{language}' umgestellt für Profil '{profile_name}'")
                return True
            except Exception as e:
                print(f"?? Fehler beim Laden der Sprache '{language}' für Profil '{profile_name}': {e}")
                return False
        return False
    
    def run(self):
        self.audio.play("ui")
        

        
        while True:
            mouse = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    
                    if event.key == pygame.K_RETURN:
                        if self.input_active and self.new_profile_name:
                            if self.new_profile_name not in self.profiles:
                                # Profil mit Standardeinstellungen erstellen
                                self.profiles[self.new_profile_name] = {
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
                                self.save_profiles()
                                self.update_max_scroll()
                                self.selected_profile = self.new_profile_name
                                self.new_profile_name = ""
                                self.input_active = False
                                print(f"?? Profil '{self.selected_profile}' erstellt")
                            else:
                                print(f"?? Profil '{self.new_profile_name}' existiert bereits!")
                    
                    if self.input_active:
                        if event.key == pygame.K_BACKSPACE:
                            self.new_profile_name = self.new_profile_name[:-1]
                        elif event.unicode.isalnum() or event.unicode in " _-":
                            self.new_profile_name += event.unicode
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Input-Feld Fokus
                    if hasattr(self, 'input_rect') and self.input_rect.collidepoint(mouse):
                        self.input_active = True
                    else:
                        self.input_active = False
                    
                    # Profile Liste
                    if hasattr(self, 'profile_list'):
                        for name, rect in self.profile_list:
                            if rect.collidepoint(mouse):
                                self.selected_profile = name
                                print(f"?? Profil ausgewählt: {name}")
                                

                    
                    # Buttons
                    if self.create_button.collidepoint(mouse):
                        if self.new_profile_name and self.new_profile_name not in self.profiles:
                            self.profiles[self.new_profile_name] = {
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
                            self.save_profiles()
                            self.update_max_scroll()
                            self.selected_profile = self.new_profile_name
                            self.new_profile_name = ""
                            self.input_active = False
                            print(f"?? Profil '{self.selected_profile}' erstellt")
                        else:
                            if not self.new_profile_name:
                                print("?? Bitte einen Profilnamen eingeben")
                            else:
                                print(f"?? Profil '{self.new_profile_name}' existiert bereits!")
                    
                    elif self.load_button.collidepoint(mouse):
                        if self.selected_profile:
                            # Profil als aktuelles setzen
                            self.current_profile = self.selected_profile
                            self.save_current_profile(self.selected_profile)
                            
                            # Einstellungen in den Settings Manager laden
                            settings = self.get_profile_settings(self.selected_profile)
                            settings_manager.profile_name = self.selected_profile
                            settings_manager.current_settings.update(settings)
                            
                            # !!! WICHTIG: Sprache des Profils anwenden !!!
                            self._apply_profile_language(self.selected_profile)
                            
                            print(f"?? Profil geladen: {self.selected_profile}")
                            print(f"   Einstellungen: {settings}")
                            
                            # Kurze Rckmeldung - die UI wird im nchsten Frame aktualisiert
                        else:
                            print("?? Bitte zuerst ein Profil auswählen!")
                    
                    elif self.delete_button.collidepoint(mouse):
                        if self.selected_profile:
                            if self.selected_profile == self.current_profile:
                                print(f"?? Kann aktuelles Profil '{self.selected_profile}' nicht löschen!")



                            else:
                                del self.profiles[self.selected_profile]
                                self.save_profiles()
                                self.update_max_scroll()
                                if self.current_profile == self.selected_profile:
                                    self.current_profile = None
                                    if os.path.exists("current_profile.txt"):
                                        os.remove("current_profile.txt")
                                self.selected_profile = None
                                print(f"?? Profil gelöscht")
                    
                    elif self.back_button.collidepoint(mouse):
                        self.audio.stop()
                        return "back"
                    
                    self.dragging = True
                    self.last_mouse_y = mouse[1]
                
                if event.type == pygame.MOUSEMOTION and self.dragging:
                    dy = mouse[1] - self.last_mouse_y
                    self.scroll_y += dy
                    self.last_mouse_y = mouse[1]
                    self.scroll_y = max(-self.max_scroll, min(0, self.scroll_y))
                
                if event.type == pygame.MOUSEBUTTONUP:
                    self.dragging = False
                
                if event.type == pygame.MOUSEWHEEL:
                    scroll_step = design.get_animation("scroll_step") * int(self.scale)
                    self.scroll_y += event.y * scroll_step
                    self.scroll_y = max(-self.max_scroll, min(0, self.scroll_y))
            
            # Zeichnen
            self.draw_gradient()
            
            self.profile_list = self.draw_profile_list(mouse)
            button_results = self.draw_right_panel(mouse)
            
            pygame.display.flip()
            self.clock.tick(60)

"""


#jetzt noch eine Tastatur hinzugefügt. Prinzipiell für alle Sprachen aktualisierbar aber bei Sprachen die nicht das lateinische Alphabet verwenden müsste man größere Änderungen in der zukunft vornehmen

import pygame
import sys
import json
import os
from design_system import design
from settings_manager import settings_manager
from language_manager import lang

class PygameProfileUI:
    def __init__(self, screen, clock, audio):
        self.screen = screen
        self.clock = clock
        self.audio = audio
        
        self.width, self.height = self.screen.get_size()
        self.ref_height = 1080
        self.scale = self.height / self.ref_height
        
        self.font = design.get_font("title", self.scale)
        self.small_font = design.get_font("small", self.scale)
        
        self.profiles_file = "profiles.json"
        self.profiles = self.load_profiles()
        self.current_profile = self.load_current_profile()
        
        # Layout
        self.left_width = 0.8* int(self.width * 0.6)
        self.right_width = self.width - self.left_width
        
        # Scroll
        self.scroll_y = 0
        self.dragging = False
        self.last_mouse_y = 0
        self.max_scroll = 0
        
        # UI Elemente
        self.selected_profile = None
        self.new_profile_name = ""
        self.input_active = False
        self.input_rect = pygame.Rect(
            self.left_width + design.get_scaled_spacing("padding_large", self.scale),     
            int(self.height * 0.15),
            self.right_width - design.get_scaled_spacing("padding_medium", self.scale) * 2,
            design.get_scaled_size("button_height", self.scale)
        )
        
        # Buttons
        button_width = 0.7 * self.right_width - design.get_scaled_spacing("padding_medium", self.scale) * 2
        button_height = 1.3 * design.get_scaled_size("button_height", self.scale)
        button_y = self.height - design.get_scaled_spacing("margin_large", self.scale) * 2
        
        self.create_button = pygame.Rect(
            1.1 * self.left_width + design.get_scaled_spacing("padding_medium", self.scale),
            button_y - button_height * 6.7 - design.get_scaled_spacing("margin_small", self.scale),
            1.15 * button_width,
            1.5 * button_height
        )
        
        self.load_button = pygame.Rect(
            1.1 * self.left_width + design.get_scaled_spacing("padding_medium", self.scale),
            button_y - button_height * 4.7 - design.get_scaled_spacing("margin_small", self.scale),
            1.15 * button_width,
            1.5 * button_height
        )
        
        self.delete_button = pygame.Rect(
            1.1 * self.left_width + design.get_scaled_spacing("padding_medium", self.scale),
            button_y - button_height * 2.7 - design.get_scaled_spacing("margin_small", self.scale),
            1.15 * button_width,
            1.5 * button_height
        )
        
        self.back_button = pygame.Rect(
            1.1 * self.left_width + design.get_scaled_spacing("padding_medium", self.scale),
            button_y - button_height * 0.7 - design.get_scaled_spacing("margin_small", self.scale),
            1.15 * button_width,
            1.5 * button_height
        )
        
        self.button_radius = design.get_border_radius("button")
        self.list_radius = design.get_border_radius("list_item")
        self.panel_radius = design.get_border_radius("panel")
        
        self.gradient_surface = design.create_gradient_surface(
            self.width, self.height, "profile"
        )
        

        
        self.scale_buttons = {
            "create": 1.0,
            "load": 1.0,
            "delete": 1.0,
            "back": 1.0
        }

        self.input_active = False
        self.update_max_scroll()

        # =============================================
        # VIRTUELLE TASTATUR
        # =============================================
        self.keyboard_active = False
        self._init_keyboard()

    def _init_keyboard(self):
        #Initialisiert die virtuelle Tastatur mit Layout aus JSON
        
        # =============================================
        # Lade Tastatur-Layout aus der aktuellen Sprache
        # =============================================
        # Verwende das aktuelle Language-System
        keyboard_rows = []
        
        # Versuche das Layout aus der JSON zu laden
        try:
            # Hole die Tastatur-Zeilen aus der Sprachdatei
            if hasattr(lang, 'data'):
                keyboard_rows = lang.data.get("keyboard_rows", [])
        except:
            pass
        
        # Fallback: Standard-Englisch-Layout
        if not keyboard_rows:
            keyboard_rows = [
                ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
                ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
                ["Z", "X", "C", "V", "B", "N", "M"]
            ]
        
        self.keyboard_rows = keyboard_rows
        
        # =============================================
        # Sonderzeichen aus JSON laden
        # =============================================
        self.special_labels = {
            "space": lang.t("keyboard_space") if hasattr(lang, 't') else "Space",
            "enter": lang.t("keyboard_enter") if hasattr(lang, 't') else "Enter",
            "clear": lang.t("keyboard_clear") if hasattr(lang, 't') else "Clear",
            "backspace": lang.t("keyboard_backspace") if hasattr(lang, 't') else "Back"
        }
        
        self.special_row = ["Back", "Space", "Enter", "Clear"]
        
        # =============================================
        # Tastatur-Gre und Position
        # =============================================
        kb_width = int(self.width * 1) #85 0.95
        kb_height = int(self.height * 0.60)  #40
        kb_x = (self.width - kb_width) // 2
        kb_y = self.height - kb_height - 0 #20 40
        
        self.keyboard_rect = pygame.Rect(kb_x, kb_y, kb_width, kb_height)
        self.key_rects = {}
        self.key_labels = {}
        
        # Key-Gre berechnen
        key_spacing = 6
        num_rows = len(self.keyboard_rows) + 1
        key_height = int((kb_height - key_spacing * (num_rows + 1)) / num_rows)
        
        # =============================================
        # BUCHSTABEN-ZEILEN aus JSON
        # =============================================
        y_offset = kb_y + key_spacing
        for row_idx, row in enumerate(self.keyboard_rows):
            row_width = kb_width - key_spacing * 2
            key_width = int((row_width - key_spacing * (len(row) - 1)) / len(row))
            
            x_offset = kb_x + key_spacing
            for key in row:
                rect = pygame.Rect(x_offset, y_offset, key_width, key_height)
                self.key_rects[key] = rect
                self.key_labels[key] = key
                x_offset += key_width + key_spacing
            
            y_offset += key_height + key_spacing
        
        # =============================================
        # SONDERZEICHEN-ZEILE
        # =============================================
        special_widths = {
            "Back": int(kb_width * 0.2),
            "Space": int(kb_width * 0.35),
            "Enter": int(kb_width * 0.20),
            "Clear": int(kb_width * 0.2)
        }
        
        total_special_width = sum(special_widths.values()) + key_spacing * (len(self.special_row) - 1)
        start_x = kb_x + (kb_width - total_special_width) // 2
        
        x_offset = start_x
        for key in self.special_row:
            width = special_widths.get(key, int(kb_width * 0.15))
            rect = pygame.Rect(x_offset, y_offset, width, key_height)
            self.key_rects[key] = rect
            # Verwende bersetzte Labels
            if key == "Back":
                self.key_labels[key] = self.special_labels["backspace"]
            elif key == "Space":
                self.key_labels[key] = self.special_labels["space"]
            elif key == "Enter":
                self.key_labels[key] = self.special_labels["enter"]
            elif key == "Clear":
                self.key_labels[key] = self.special_labels["clear"]
            x_offset += width + key_spacing



    def _draw_keyboard(self):
        #Zeichnet die virtuelle Tastatur mit Labels aus JSON
        # Hintergrund der Tastatur
        kb_bg_color = design.get_color("panel_bg")
        kb_border_color = design.get_color("panel_border")
        
        # Hintergrund mit Transparenz
        bg_surface = pygame.Surface((self.keyboard_rect.width, self.keyboard_rect.height), pygame.SRCALPHA)
        bg_surface.fill((*kb_bg_color, 230))
        self.screen.blit(bg_surface, self.keyboard_rect)
        
        # Border
        pygame.draw.rect(self.screen, kb_border_color, self.keyboard_rect, 2, border_radius=10)
        
        # Keys zeichnen
        mouse_pos = pygame.mouse.get_pos()
        key_color = design.get_color("secondary")
        key_hover_color = design.get_color("primary_hover")
        key_text_color = design.get_color("text")
        
        for key, rect in self.key_rects.items():
            # Hover-Effekt
            hovered = rect.collidepoint(mouse_pos)
            color = key_hover_color if hovered else key_color
            
            # Sonderfarben fr Sonderzeichen
            if key == "Back":
                color = design.get_color("primary_hover") if hovered else design.get_color("secondary")
            elif key == "Enter":
                color = design.get_color("primary_hover") if hovered else design.get_color("secondary")
            elif key == "Clear":
                color = design.get_color("primary_hover") if hovered else design.get_color("secondary")
            elif key == "Space":
                color = design.get_color("primary_hover") if hovered else design.get_color("secondary")
            
            # Key zeichnen
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            pygame.draw.rect(self.screen, key_text_color, rect, 1, border_radius=5)
            
            # =============================================
            # Text aus self.key_labels verwenden (aus JSON)
            # =============================================
            label = self.key_labels.get(key, key)
            
            # Fr Sonderzeichen die bersetzten Labels verwenden
            if key == "Space":
                text_surface = self.small_font.render(label, True, key_text_color)
            elif key == "Back":
                text_surface = self.small_font.render(label, True, key_text_color)
            elif key == "Enter":
                text_surface = self.small_font.render(label, True, key_text_color)
            elif key == "Clear":
                text_surface = self.small_font.render(label, True, key_text_color)
            else:
                text_surface = self.small_font.render(label, True, key_text_color)
            
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)

    def _handle_keyboard_click(self, pos):
        #Verarbeitet Klicks auf die virtuelle Tastatur
        for key, rect in self.key_rects.items():
            if rect.collidepoint(pos):
                if key == "Back":  # Backspace
                    self.new_profile_name = self.new_profile_name[:-1]
                elif key == "Space":
                    self.new_profile_name += " "
                
                elif key == "Clear":  # Alles lschen
                    self.new_profile_name = ""
                elif key == "Enter":
                    # Profil erstellen (wie bei Return-Taste)
                    if self.new_profile_name and self.new_profile_name not in self.profiles:
                        self.profiles[self.new_profile_name] = {
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
                        self.save_profiles()
                        self.update_max_scroll()
                        self.selected_profile = self.new_profile_name
                        self.new_profile_name = ""
                        self.input_active = False
                        self.keyboard_active = False
                        print(f"?? Profil '{self.selected_profile}' erstellt")
                    else:
                        if not self.new_profile_name:
                            print("?? Bitte einen Profilnamen eingeben")

                        else:
                            print(f"?? Profil '{self.new_profile_name}' existiert bereits!")
                else:  # Buchstabe/Zahl
                    self.new_profile_name += key
                return True
        return False

    def load_profiles(self):
        try:
            if os.path.exists(self.profiles_file):
                with open(self.profiles_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"?? Fehler beim Laden der Profile: {e}")
        return {}
    
    def save_profiles(self):
        try:
            with open(self.profiles_file, "w", encoding="utf-8") as f:
                json.dump(self.profiles, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"?? Fehler beim Speichern der Profile: {e}")
    
    def load_current_profile(self):
        try:
            if os.path.exists("current_profile.txt"):
                with open("current_profile.txt", "r", encoding="utf-8") as f:
                    return f.read().strip()
        except:
            pass
        return None
    
    def save_current_profile(self, profile_name):
        try:
            with open("current_profile.txt", "w", encoding="utf-8") as f:
                f.write(profile_name)
        except Exception as e:
            print(f"?? Fehler beim Speichern des aktuellen Profils: {e}")
    
    def get_profile_settings(self, profile_name):
        if profile_name in self.profiles:
            return self.profiles[profile_name]
        return {
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
    
    def update_max_scroll(self):
        profile_height = design.get_scaled_size("flag_size", self.scale) + design.get_scaled_spacing("margin_medium", self.scale)
        margin = design.get_scaled_spacing("margin_medium", self.scale)
        total_height = len(self.profiles) * (profile_height + margin)
        visible_height = self.height - 200
        self.max_scroll = max(0, total_height - visible_height)
        self.scroll_y = max(-self.max_scroll, min(0, self.scroll_y))
    
    def draw_gradient(self):
        self.screen.blit(self.gradient_surface, (0, 0))
            
    def draw_profile_list(self, mouse):
        profile_height = int(100 * self.scale)
        margin = int(30 * self.scale)
        start_x = int(100 * self.scale)
        start_y = int(100 * self.scale) + self.scroll_y
        list_width = self.left_width - start_x - int(100 * self.scale)
        
        

        result = []
        
        for i, (name, settings) in enumerate(self.profiles.items()):
            rect = pygame.Rect(
                start_x,
                start_y + i * (profile_height + margin),
                list_width,
                profile_height
            )
            
            if rect.bottom < 0 or rect.top > self.height:
                continue
            
            hovered = rect.collidepoint(mouse)
            
            if hovered:
                color = design.get_color("info")
                alpha = design.get_ui("alpha_hover")
            elif self.selected_profile == name:
                color = design.get_color("success")
                alpha = design.get_ui("alpha_selected")
            else:
                color = design.get_color("primary")
                alpha = design.get_ui("alpha_normal")
            
            design.draw_rounded_rect(
                self.screen,
                color,
                rect,
                self.list_radius,
                alpha
            )
            
            text = self.font.render(name.upper(), True, design.get_color("text"))
            text_rect = text.get_rect(
                center=(rect.centerx - 40, rect.centery)
            )
            self.screen.blit(text, text_rect)
            
            if name == self.current_profile:
                active_text = lang.t("active") if hasattr(lang, 't') else "AKTIV"
                active_surface = self.small_font.render(active_text, True, design.get_color("text_muted"))  #success
                active_rect = active_surface.get_rect(
                    center=(rect.right - 100, rect.centery)
                )
                self.screen.blit(active_surface, active_rect)
            
            result.append((name, rect))
        
        return result

    def draw_right_panel(self, mouse):
        title_text = lang.t("profile") if hasattr(lang, 't') else "PROFIL VERWALTUNG"
        title = self.font.render(title_text.upper(), True, design.get_color("text"))
        title_x = self.left_width + design.get_scaled_spacing("padding_large", self.scale)
        title_y = design.get_scaled_spacing("margin_large", self.scale)
        self.screen.blit(title, (title_x, title_y))
        
        if self.selected_profile:
            info_y = title_y + int(80 * self.scale)
            settings = self.profiles.get(self.selected_profile, {})
            exercise = settings.get("exercise", "middle")
            exercise_display = lang.t(exercise) if hasattr(lang, 't') else exercise.upper()
            duration = settings.get("duration", 180)
            volume = settings.get("volume", 50)
            language = settings.get("language", "de")


            
            selected_text = lang.t("selected") if hasattr(lang, 't') else "Ausgewählt:"
            info_text = f"{selected_text} {self.selected_profile}"
            info_surface = self.small_font.render(info_text, True, design.get_color("text"))   #info
            self.screen.blit(info_surface, (title_x, info_y))
            
            settings_y = info_y + int(40 * self.scale)
            
            exercise_label = lang.t("exercise") if hasattr(lang, 't') else "Übung"
            duration_label = lang.t("duration") if hasattr(lang, 't') else "Dauer"
            volume_label = lang.t("volume") if hasattr(lang, 't') else "Lautstärke"
            language_label = lang.t("language") if hasattr(lang, 't') else "Sprache"
            
            line1 = f"{exercise_label}: {exercise_display}  |  {duration_label}: {duration}s"
            line1_surface = self.small_font.render(line1, True, design.get_color("text_muted"))
            self.screen.blit(line1_surface, (title_x, settings_y + int(20 * self.scale)))
            
            line2 = f"{volume_label}: {volume}%  |  {language_label}: {language.upper()}"
            line2_surface = self.small_font.render(line2, True, design.get_color("text_muted"))
            self.screen.blit(line2_surface, (title_x, settings_y + int(80 * self.scale)))
        
        input_y = title_y + int(280 * self.scale)
        input_rect = pygame.Rect(
            title_x,
            input_y,
            self.right_width - design.get_scaled_spacing("padding_medium", self.scale) * 4,
            design.get_scaled_size("button_height", self.scale)
        )
        self.input_rect = input_rect
        
        if self.input_active:
            color = design.get_color("input_active")
        else:
            color = design.get_color("input_inactive")
        
        design.draw_rounded_rect(
            self.screen,
            color,
            input_rect,
            self.button_radius,
            200
        )
        
        if self.new_profile_name:
            text_surface = self.small_font.render(
                self.new_profile_name,
                True,
                design.get_color("text")
            )
        else:
            placeholder_text = lang.t("enter_profile_name") if hasattr(lang, 't') else "Profilname eingeben..."
            text_surface = self.small_font.render(
                placeholder_text,
                True,
                design.get_color("text_muted")
            )
            

        
        text_x = input_rect.x + design.get_scaled_spacing("padding_small", self.scale)
        text_y = input_rect.centery - text_surface.get_height() // 2
        self.screen.blit(text_surface, (text_x, text_y))
        
        if self.input_active and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = text_x + text_surface.get_width() + 5
            cursor_y = input_rect.centery - design.get_scaled_size("button_height", self.scale) // 3
            pygame.draw.line(
                self.screen,
                design.get_color("text"),
                (cursor_x, cursor_y),
                (cursor_x, cursor_y + design.get_scaled_size("button_height", self.scale) * 2 // 3),
                2
            )
        
        buttons = [
            ("create", self.create_button, lang.t("create") if hasattr(lang, 't') else "Profil erstellen", self.scale_buttons["create"]),
            ("load", self.load_button, lang.t("load") if hasattr(lang, 't') else "Profil laden", self.scale_buttons["load"]),
            ("delete", self.delete_button, lang.t("delete") if hasattr(lang, 't') else "Profil löschen", self.scale_buttons["delete"]),
            ("back", self.back_button, lang.t("back") if hasattr(lang, 't') else "Zurück", self.scale_buttons["back"])
        ]
        
        results = {}
        for name, rect, text, scale_var in buttons:
            hovered = rect.collidepoint(mouse)
            
            target_scale = design.get_animation("hover_scale") if hovered else 1.0
            self.scale_buttons[name] += (target_scale - self.scale_buttons[name]) * design.get_animation("animation_speed")
            scale = self.scale_buttons[name]
            
            draw_rect = pygame.Rect(0, 0,
                int(rect.width * scale),
                int(rect.height * scale)
            )
            draw_rect.center = rect.center
    
            if name == "delete":
                color_name = "danger_hover" if hovered else "danger"
            elif name == "back":
                color_name = "secondary_hover" if hovered else "secondary"
            elif name == "create":
                color_name = "success_hover" if hovered else "success"
            else:
                color_name = "button_confirm_hover" if hovered else "button_confirm"
            
            design.draw_rounded_rect(
                self.screen,
                design.get_color(color_name),
                draw_rect,
                self.button_radius,
                design.get_ui("alpha_button")
            )


            
            text_surface = self.small_font.render(text, True, design.get_color("text"))
            text_rect = text_surface.get_rect(center=draw_rect.center)
            self.screen.blit(text_surface, text_rect)
            
            results[name] = hovered
        
        return results

    def _apply_profile_language(self, profile_name):
        if profile_name in self.profiles:
            settings = self.profiles[profile_name]
            language = settings.get("language", "de")
            try:
                lang.load(language)
                if hasattr(self, 'audio') and self.audio:
                    self.audio.set_language(language)
                print(f"?? Sprache auf '{language}' umgestellt für Profil '{profile_name}'")
                return True
            except Exception as e:
                print(f"?? Fehler beim Laden der Sprache '{language}' für Profil '{profile_name}': {e}")
                return False
        return False
    
    def run(self):
        self.audio.play("Profile")
        
        while True:
            mouse = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    
                    if event.key == pygame.K_RETURN:
                        if self.input_active and self.new_profile_name:
                            if self.new_profile_name not in self.profiles:
                                self.profiles[self.new_profile_name] = {
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
                                self.save_profiles()
                                self.update_max_scroll()
                                self.selected_profile = self.new_profile_name
                                self.new_profile_name = ""
                                self.input_active = False
                                self.keyboard_active = False
                                print(f"?? Profil '{self.selected_profile}' erstellt")
                            else:
                                print(f"?? Profil '{self.new_profile_name}' existiert bereits!")
                    
                    if self.input_active:
                        if event.key == pygame.K_BACKSPACE:
                            self.new_profile_name = self.new_profile_name[:-1]
                        elif event.unicode.isalnum() or event.unicode in " _-":
                            self.new_profile_name += event.unicode
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # =============================================
                    # WENN TASTATUR AKTIV IST: NUR TASTATUR-KLICKS
                    # =============================================
                    if self.keyboard_active:
                        # Prfe ob Klick auf Tastatur ist
                        keyboard_hit = self._handle_keyboard_click(event.pos)
                        
                        # Wenn Klick auf Tastatur war, weiter mit nchstem Event
                        if keyboard_hit:
                            continue
    
    
                        
                        # Wenn Klick AUERHALB der Tastatur ist, Tastatur ausblenden
                        # Aber NICHTS anderes ausfhren!
                        self.input_active = False
                        self.keyboard_active = False
                        continue  # WICHTIG: Hier wird der Klick ignoriert!
                    
                    # =============================================
                    # NUR AUSFHREN, WENN TASTATUR NICHT AKTIV IST
                    # =============================================
                    
                    # Input-Feld Fokus
                    if hasattr(self, 'input_rect') and self.input_rect.collidepoint(mouse):
                        self.input_active = True
                        self.keyboard_active = True
                        continue
                    
                    # Profile Liste
                    if hasattr(self, 'profile_list'):
                        for name, rect in self.profile_list:
                            if rect.collidepoint(mouse):
                                self.selected_profile = name
                                print(f"?? Profil ausgewählt: {name}")
                                break
                    
                    # Buttons
                    if self.create_button.collidepoint(mouse):
                        if self.new_profile_name and self.new_profile_name not in self.profiles:
                            self.profiles[self.new_profile_name] = {
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
                            self.save_profiles()
                            self.update_max_scroll()
                            self.selected_profile = self.new_profile_name
                            self.new_profile_name = ""
                            self.input_active = False
                            self.keyboard_active = False
                            print(f"?? Profil '{self.selected_profile}' erstellt")
                        else:
                            if not self.new_profile_name:
                                print("?? Bitte einen Profilnamen eingeben")
                            else:
                                print(f"?? Profil '{self.new_profile_name}' existiert bereits!")
                        continue
    
    
                    
                    elif self.load_button.collidepoint(mouse):
                        if self.selected_profile:
                            self.current_profile = self.selected_profile
                            self.save_current_profile(self.selected_profile)
                            settings = self.get_profile_settings(self.selected_profile)
                            settings_manager.profile_name = self.selected_profile
                            settings_manager.current_settings.update(settings)
                            self._apply_profile_language(self.selected_profile)
                            print(f"?? Profil geladen: {self.selected_profile}")
                            print(f"   Einstellungen: {settings}")
                        else:
                            print("?? Bitte zuerst ein Profil auswählen!")
                        continue
                    
                    elif self.delete_button.collidepoint(mouse):
                        if self.selected_profile:
                            if self.selected_profile == self.current_profile:
                                print(f"?? Kann aktuelles Profil '{self.selected_profile}' nicht löschen!")
                            else:
                                del self.profiles[self.selected_profile]
                                self.save_profiles()
                                self.update_max_scroll()
                                if self.current_profile == self.selected_profile:
                                    self.current_profile = None
                                    if os.path.exists("current_profile.txt"):
                                        os.remove("current_profile.txt")
                                self.selected_profile = None
                                print(f"?? Profil gelöscht")
                        else:
                            print("?? Bitte zuerst ein Profil auswählen!")
                        continue
                    
                    elif self.back_button.collidepoint(mouse):
                        self.audio.stop()
                        return "back"
                    
                    # Wenn auf nichts geklickt wurde, Input-Feld deaktivieren
                    self.input_active = False
                    self.keyboard_active = False
                    self.dragging = True
                    self.last_mouse_y = mouse[1]
                
                if event.type == pygame.MOUSEMOTION and self.dragging:
                    dy = mouse[1] - self.last_mouse_y
                    self.scroll_y += dy
                    self.last_mouse_y = mouse[1]
                    self.scroll_y = max(-self.max_scroll, min(0, self.scroll_y))
                
                if event.type == pygame.MOUSEBUTTONUP:
                    self.dragging = False
                    
    
                
                if event.type == pygame.MOUSEWHEEL:
                    scroll_step = design.get_animation("scroll_step") * int(self.scale)
                    self.scroll_y += event.y * scroll_step
                    self.scroll_y = max(-self.max_scroll, min(0, self.scroll_y))
            
            # Zeichnen
            self.draw_gradient()
            
            self.profile_list = self.draw_profile_list(mouse)
            button_results = self.draw_right_panel(mouse)
            
            # Tastatur zeichnen (wenn aktiv)
            if self.keyboard_active:
                self._draw_keyboard()
            
            pygame.display.flip()
            self.clock.tick(60)



#
#
#

