import pygame
import sys
import os
from language_manager import lang
from design_system import design
from settings_manager import settings_manager
from menu_navigation import NavigationHelper


class PygameSettingsMenuUI:  #Einstellungen von denen aus wir alle Parameter für die Übungen anpassen können
    def __init__(self, screen, clock, audio):
        self.screen = screen
        self.clock = clock
        self.audio = audio
        
        self.width, self.height = self.screen.get_size()
        self.ref_height = 1080
        self.scale = self.height / self.ref_height
        
        self.font = design.get_font("title", self.scale)
        self.small_font = design.get_font("small", self.scale)
        
        self.settings = settings_manager.get_settings()
        
        panel_width = self.width // 6
        
        self.panels = {
            "language": pygame.Rect(0, 0, panel_width, self.height),
            "volume": pygame.Rect(panel_width, 0, panel_width, self.height),
            "duration": pygame.Rect(panel_width * 2, 0, panel_width, self.height),
            "exercise": pygame.Rect(panel_width * 3, 0, panel_width, self.height),
            "evaluation": pygame.Rect(panel_width * 4, 0, panel_width, self.height),
            "back": pygame.Rect(panel_width * 5, 0, panel_width, self.height)
        }
        
        self.scale_values = {
            "language": 1.0,
            "volume": 1.0,
            "duration": 1.0,
            "exercise": 1.0,
            "evaluation": 1.0,
            "back": 1.0
        }
        
        self.icons = {}
        self.icon_size = design.get_scaled_size("icon_size", self.scale)
        self.load_icons()
        
        self.border_radius = design.get_border_radius("panel")
        self.gradient_surface = design.create_gradient_surface(
            self.width, self.height, "settings"
        )
        
        self.choice = None
        self.clicked = False
        self.click_time = None
        self.last_update = pygame.time.get_ticks()
        
        self.nav_helper = None
        self.use_navigation = False
        self.nav = None
    
    def load_icons(self):
        base = "assets/icons"
        try:
            self.icons = {
                "language": pygame.image.load(os.path.join(base, "language.png")).convert_alpha(),
                "volume": pygame.image.load(os.path.join(base, "volume.png")).convert_alpha(),
                "duration": pygame.image.load(os.path.join(base, "duration.png")).convert_alpha(),
                "exercise": pygame.image.load(os.path.join(base, "exercise.png")).convert_alpha(),
                "evaluation": pygame.image.load(os.path.join(base, "evaluation.png")).convert_alpha(),
            }
        except:
            print("Settings Icons konnten nicht geladen werden")
            for key in self.panels:
                dummy = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
                dummy.fill((150, 150, 150))
                self.icons[key] = dummy
    

    
    def draw_gradient(self):
        self.screen.blit(self.gradient_surface, (0, 0))
    
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
    
    def draw_panel(self, name, rect, is_highlighted=False):
        mouse = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse)
        
        target_scale = design.get_animation("hover_scale") if (hovered or is_highlighted) else 1.0
        self.scale_values[name] += (target_scale - self.scale_values[name]) * design.get_animation("animation_speed")
        scale = self.scale_values[name]
        
        scaled_width = int(rect.width * scale)
        scaled_height = int(rect.height * scale)
        
        if name == "back":
            color_name = "info" if not hovered and not is_highlighted else "info_hover"
        else:
            color_name = "primary" if not hovered and not is_highlighted else "primary_hover"
        
        alpha = design.get_ui("alpha_hover") if (hovered or is_highlighted) else design.get_ui("alpha_normal")
        
        draw_rect = pygame.Rect(0, 0, scaled_width, scaled_height)
        draw_rect.center = rect.center
        
        design.draw_rounded_rect(
            self.screen,
            design.get_color(color_name),
            draw_rect,
            self.border_radius,
            alpha

        )
        
        if is_highlighted:
            border_rect = draw_rect.inflate(15, 15)
            design.draw_rounded_rect(
                self.screen,
                design.get_color("accent"), #accent
                border_rect,
                self.border_radius,
                150,
                width=3
            )
        
        if name in self.icons:
            icon = self.icons[name]
            icon_scaled = pygame.transform.smoothscale(icon, (self.icon_size, self.icon_size))
            icon_offset_y = design.get_scaled_spacing("padding_large", self.scale) * 2
            icon_rect = icon_scaled.get_rect(
                center=(draw_rect.centerx, draw_rect.centery - icon_offset_y)
            )
            self.screen.blit(icon_scaled, icon_rect)
        
        display_text = lang.t(name) if hasattr(lang, 't') else name.upper()
        text_surface = self.font.render(display_text.upper(), True, design.get_color("text"))
        text_offset_y = design.get_scaled_spacing("margin_medium", self.scale) * 2
        text_rect = text_surface.get_rect(
            center=(draw_rect.centerx, draw_rect.centery + text_offset_y)
        )
        self.screen.blit(text_surface, text_rect)
        
        if name != "back":
            current_value = ""
            if name == "language":
                lang_code = self.settings.get("language", "de")
                try:
                    if hasattr(lang, 'get_language_name'):
                        current_value = lang.get_language_name(lang_code)
                    else:
                        current_value = lang_code.upper()
                except:
                    current_value = lang_code.upper()
            elif name == "volume":
                current_value = f"{self.settings.get('volume', 50)}%"
            elif name == "duration":
                duration = self.settings.get('duration', 180)
                current_value = f"{duration//60} MIN"
            elif name == "exercise":
                exercise = self.settings.get('exercise', 'middle')
                if exercise == "custom":
                    custom_params = self.settings.get('custom_params', {})
                    move_up = custom_params.get('move_up', 4.0)
                    pause_top = custom_params.get('pause_top', 2.0)
                    move_down = custom_params.get('move_down', 4.0)
                    pause_bottom = custom_params.get('pause_bottom', 2.0)
                    try:
                        exercise_name = lang.t(exercise) if hasattr(lang, 't') else exercise.upper()
                        current_value = f"{exercise_name} ({move_up:.1f}s, {pause_top:.1f}s, {move_down:.1f}s, {pause_bottom:.1f}s)"
                    except:
                        current_value = f"CUSTOM ({move_up:.1f}s, {pause_top:.1f}s, {move_down:.1f}s, {pause_bottom:.1f}s)"
                else:
                    try:
                        current_value = lang.t(exercise) if hasattr(lang, 't') else exercise.upper()
                    except:
                        current_value = exercise.upper()
            elif name == "evaluation":
                enabled = self.settings.get('evaluation_enabled', True)
                #current_value = "ON" if enabled else "OFF"
                current_value = lang.t("ON") if enabled else lang.t("OFF") #nimmt nur einen Wert in Betrachtung 

            
            if current_value:
                max_width = int(rect.width * 0.85)
                wrapped_lines = self._wrap_text(current_value, self.small_font, max_width)
                
                if wrapped_lines:
                    value_offset_y = text_offset_y + int(100 * self.scale)
                    line_height = self.small_font.get_height()
                    
                    for i, line in enumerate(wrapped_lines[:3]):
                        value_surface = self.small_font.render(line, True, design.get_color("text_muted"))
                        value_rect = value_surface.get_rect(
                            center=(draw_rect.centerx, draw_rect.centery + value_offset_y + (i * line_height))
                        )
                        self.screen.blit(value_surface, value_rect)
                else:
                    value_surface = self.small_font.render(current_value, True, design.get_color("text_muted"))
                    value_offset_y = text_offset_y + int(50 * self.scale)
                    value_rect = value_surface.get_rect(
                        center=(draw_rect.centerx, draw_rect.centery + value_offset_y)
                    )
                    self.screen.blit(value_surface, value_rect)
    
    def run(self, nav=None):
        self.audio.play("Einstellungen")
        
        self.choice = None
        self.clicked = False
        self.click_time = None
        
        self.nav = nav
        self.use_navigation = (nav is not None and nav.active)
        
        if self.use_navigation:
            self.nav_helper = NavigationHelper(nav)
            self.nav_helper.setup_ui("settings")
            
            def on_navigate(item, index):
                pass
            
            def on_select(item):
                print(f"SettingsMenu SELECT: {item}")
                self.choice = item
                self.clicked = True
                self.click_time = pygame.time.get_ticks()
            
            nav.set_on_navigate(on_navigate)
            nav.set_on_select(on_select)
        
        self.settings = settings_manager.get_settings()
        
        while True:
            if self.use_navigation:
                nav.update()



            
            current_time = pygame.time.get_ticks()
            
            if current_time - self.last_update > 1000:
                self.settings = settings_manager.get_settings()
                self.last_update = current_time
            
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
                    if self.use_navigation:
                        nav.active = True
                    self.audio.stop()
                    return self.choice


            
            pygame.display.flip()
            self.clock.tick(60)


