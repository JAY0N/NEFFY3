
import pygame
import sys
import os
from language_manager import lang
from design_system import design
from settings_manager import settings_manager
from menu_navigation import NavigationHelper


class PygameEvaluationSettingsUI:
    def __init__(self, screen, clock, audio):
        self.screen = screen
        self.clock = clock
        self.audio = audio
        
        self.width, self.height = self.screen.get_size()
        self.ref_height = 1080
        self.scale = self.height / self.ref_height
        
        self.font = design.get_font("title", self.scale)
        self.small_font = design.get_font("small", self.scale)
        self.large_font = design.get_font("large", self.scale)
        
        # Aktuelle Einstellungen laden
        self.evaluation_enabled = settings_manager.is_evaluation_enabled()
        self.audio_enabled = settings_manager.is_audio_enabled()
        
        #2 x 2 Muster anders als die anderen Auswahlen wenn noch mehr Optionen filgen müsste man nochmal umbauen
        panel_width = self.width // 2
        panel_height = self.height // 2
        
        self.panels = {
            "evaluation_on": pygame.Rect(0, 0, panel_width, panel_height),
            "evaluation_off": pygame.Rect(panel_width, 0, panel_width, panel_height),
            "audio_on": pygame.Rect(0, panel_height, panel_width, panel_height),
            "audio_off": pygame.Rect(panel_width, panel_height, panel_width, panel_height)
        }
        
        self.scale_values = {
            "evaluation_on": 1.0,
            "evaluation_off": 1.0,
            "audio_on": 1.0,
            "audio_off": 1.0
        }
        
        self.border_radius = design.get_border_radius("panel")
        self.gradient_surface = design.create_gradient_surface(
            self.width, self.height, "evaluation_settings"
        )
        
        self.choice = None
        self.clicked = False
        self.click_time = None
        
        # Icons laden
        self.icons = {}
        self.icon_size = design.get_scaled_size("icon_size", self.scale) * 2
        self.load_icons()
        
        # Navigation
        self.nav_helper = None
        self.use_navigation = False
        self.nav = None
        
        #Menü items
        self.nav_items = ["evaluation_on", "evaluation_off", "audio_on", "audio_off"]
    
    def load_icons(self):
        base = "assets/icons"
        
        try:
            self.icons = {
                "evaluation_on": pygame.image.load(os.path.join(base, "check.png")).convert_alpha(),
                "evaluation_off": pygame.image.load(os.path.join(base, "cross.png")).convert_alpha(),
                "audio_on": pygame.image.load(os.path.join(base, "sound_on.png")).convert_alpha(),
                "audio_off": pygame.image.load(os.path.join(base, "sound_off.png")).convert_alpha(),
            }
        except:
            print("Evaluation Settings Icons konnten nicht geladen werden")
            for key in self.panels:
                dummy = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
                dummy.fill((150, 150, 150))
                self.icons[key] = dummy
    
    def draw_gradient(self):
        self.screen.blit(self.gradient_surface, (0, 0))
    
    def draw_panel(self, name, rect, is_highlighted=False):
        mouse = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse)
        

        
        # schauen welche Option ausgewählt
        is_selected = False
        if name == "evaluation_on" and self.evaluation_enabled:
            is_selected = True
        elif name == "evaluation_off" and not self.evaluation_enabled:
            is_selected = True
        elif name == "audio_on" and self.audio_enabled:
            is_selected = True
        elif name == "audio_off" and not self.audio_enabled:
            is_selected = True
        
        target_scale = design.get_animation("hover_scale") if (hovered or is_highlighted) else 1.0
        self.scale_values[name] += (target_scale - self.scale_values[name]) * design.get_animation("animation_speed")
        scale = self.scale_values[name]
        
        scaled_width = int(rect.width * scale)
        scaled_height = int(rect.height * scale)
        
        if is_selected:
            color_name = "text_muted" #success
            alpha = design.get_ui("alpha_selected")
        elif hovered or is_highlighted:
            color_name = "primary_hover"
            alpha = design.get_ui("alpha_hover")
        else:
            color_name = "primary"
            alpha = design.get_ui("alpha_normal")
        
        draw_rect = pygame.Rect(0, 0, scaled_width, scaled_height)
        draw_rect.center = rect.center
        
        design.draw_rounded_rect(
            self.screen,
            design.get_color(color_name),
            draw_rect,
            self.border_radius,
            alpha
        )
        
        # Hervorhebungs Rahmen bei Navigation breiter machen?
        if is_highlighted:
            border_rect = draw_rect.inflate(15, 15)
            design.draw_rounded_rect(
                self.screen,
                design.get_color("accent"),
                border_rect,
                self.border_radius,
                150,
                width=3
            )
        
        # Titel
        if "evaluation" in name:
            if name == "evaluation_on":
                display_text = lang.t("evaluation_on") if hasattr(lang, 't') else "EVALUATION AKTIV"
                info_text = lang.t("evaluation_on_info") if hasattr(lang, 't') else "Pre- und Post-Evaluation werden angezeigt"
            else:
                display_text = lang.t("evaluation_off") if hasattr(lang, 't') else "EVALUATION DEAKTIVIERT"
                info_text = lang.t("evaluation_off_info") if hasattr(lang, 't') else "Pre- und Post-Evaluation werden uebersprungen"
        else:
            if name == "audio_on":
                display_text = lang.t("audio_on") if hasattr(lang, 't') else "AUDIO AKTIV"
                info_text = lang.t("audio_on_info") if hasattr(lang, 't') else "Alle UI-Sounds werden abgespielt"
            else:
                display_text = lang.t("audio_off") if hasattr(lang, 't') else "AUDIO DEAKTIVIERT"
                info_text = lang.t("audio_off_info") if hasattr(lang, 't') else "UI-Sounds werden uebersprungen"
                

        
        text_surface = self.font.render(display_text, True, design.get_color("text"))
        text_offset_y = design.get_scaled_spacing("margin_medium", self.scale) * -4
        text_rect = text_surface.get_rect(
            center=(draw_rect.centerx, draw_rect.centery + text_offset_y)
        )
        self.screen.blit(text_surface, text_rect)
        
        # Info Text
        if info_text:
            max_width = int(rect.width * 0.85)
            wrapped_lines = self._wrap_text(info_text, self.small_font, max_width)
            
            info_offset_y = text_offset_y + int(60 * self.scale)
            line_height = self.small_font.get_height()
            
            for i, line in enumerate(wrapped_lines[:3]):
                line_surface = self.small_font.render(line, True, design.get_color("text_muted"))
                line_rect = line_surface.get_rect(
                    center=(draw_rect.centerx, draw_rect.centery + info_offset_y + (i * line_height))
                )
                self.screen.blit(line_surface, line_rect)
        
        # weche Auswahl gerade aktiv ist
        if is_selected:
            marker = self.large_font.render("O", True, design.get_color("text")) #success
            marker_rect = marker.get_rect(
                center=(draw_rect.centerx, draw_rect.top + int(60 * self.scale))
            )
            self.screen.blit(marker, marker_rect)
    
    def _wrap_text(self, text, font, max_width):
        if not text:
            return []
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = font.render(test_line, True, (255, 255, 255))
            
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def run(self, nav=None):
        # Audio nur abspielen wenn aktiviert
        if settings_manager.is_audio_enabled():
            self.audio.play("Settings")
        
        self.choice = None
        self.clicked = False
        self.click_time = None


        
        self.nav = nav
        self.use_navigation = (nav is not None and nav.active)
        
        if self.use_navigation:
            self.nav_helper = NavigationHelper(nav)

            self.nav_helper.setup_ui("evaluation_settings")
            self.nav_helper.set_items(self.nav_items)
            
            def on_navigate(item, index):
                pass
            
            def on_select(item):
                print(f"EvaluationSettingsUI SELECT: {item}")
                self.choice = item
                self.clicked = True
                self.click_time = pygame.time.get_ticks()
            
            nav.set_on_navigate(on_navigate)
            nav.set_on_select(on_select)
            
            # Initiale Hervorhebung
            if self.nav_items:
                nav.current_index = 0
                nav.highlighted_item = self.nav_items[0]
        
        while True:
            # Navigation update
            if self.use_navigation:
                nav.update()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.audio.stop()
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.audio.stop()
                        return "back"
                    
                    if self.use_navigation and nav.active:
                        if event.key == pygame.K_l:
                            nav.set_left(True)
                        elif event.key == pygame.K_r:
                            nav.set_right(True)
                
                if event.type == pygame.KEYUP:
                    if self.use_navigation and nav.active:
                        if event.key == pygame.K_l:
                            nav.set_left(False)
                        elif event.key == pygame.K_r:
                            nav.set_right(False)
                
                if event.type == pygame.MOUSEBUTTONDOWN and not self.clicked:
                    if self.use_navigation:
                        nav.active = False
                    
                    mouse = pygame.mouse.get_pos()
                    for name, rect in self.panels.items():
                        if rect.collidepoint(mouse):
                            self.choice = name
                            self.clicked = True
                            self.click_time = pygame.time.get_ticks()
                            break
            
            self.draw_gradient()
            
            for name, rect in self.panels.items():
                is_highlighted = False
                if self.use_navigation and nav.active:
                    is_highlighted = (name == nav.get_highlighted_item())
                self.draw_panel(name, rect, is_highlighted)
                

            
            if self.clicked and self.click_time is not None:
                rect = self.panels[self.choice]
                design.draw_rounded_rect(
                    self.screen,
                    design.get_color("accent"),
                    rect,
                    self.border_radius,
                    design.get_ui("alpha_overlay")
                )
                if pygame.time.get_ticks() - self.click_time > design.get_animation("click_feedback_duration"):
                    # Einstellungen speichern
                    if self.choice == "evaluation_on":
                        settings_manager.set_evaluation_enabled(True)
                    elif self.choice == "evaluation_off":
                        settings_manager.set_evaluation_enabled(False)
                    elif self.choice == "audio_on":
                        settings_manager.set_audio_enabled(True)
                    elif self.choice == "audio_off":
                        settings_manager.set_audio_enabled(False)
                    
                    self.audio.stop()
                    if self.use_navigation:
                        nav.active = True
                    return "settings"
            
            pygame.display.flip()
            self.clock.tick(60)
