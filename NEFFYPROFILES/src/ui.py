import pygame
import sys
import os
from language_manager import lang
from design_system import design
from settings_manager import settings_manager
from menu_navigation import NavigationHelper


class PygameDecisionUI:
    def __init__(self, screen, clock, audio, return_to_settings=True):
        self.screen = screen
        self.clock = clock
        self.audio = audio
        self.return_to_settings = return_to_settings
        pygame.display.set_caption("Decision")
        self.width, self.height = self.screen.get_size()
        
        self.ref_height = 1080
        self.scale = self.height / self.ref_height
        
        self.font = design.get_font("title", self.scale)
        self.info_font = design.get_font("small", self.scale)
        
        self.choice = None
        self.clicked = False
        self.click_time = None
        self.scale_values = {}
        self.icons = {}
        
        #
        panel_width = self.width // 5
        self.panels = {
            "left": pygame.Rect(0, 0, panel_width, self.height),
            "middle": pygame.Rect(panel_width, 0, panel_width, self.height),
            "right": pygame.Rect(panel_width * 2, 0, panel_width, self.height),
            "Dankbarkeitsübung": pygame.Rect(panel_width * 3, 0, panel_width, self.height),
            "custom": pygame.Rect(panel_width * 4, 0, panel_width, self.height)
        }
        
        self.gradient_surface = design.create_gradient_surface(
            self.width, self.height, "decision"
        )
        
        self.border_radius = design.get_border_radius("panel")
        self.load_icons()
        for key in self.panels:
            self.scale_values[key] = 1.0
        
        # Aktuelle Übung aus Settings laden
        current_settings = settings_manager.get_settings()
        self.current_exercise = current_settings.get("exercise", "middle")
        
        # Custom Status merken
        self.custom_params = current_settings.get("custom_params", {})
        
        # Navigation
        self.nav_helper = None
        self.use_navigation = False
        self.nav = None
        
        #Menü items
        self.nav_items = ["left", "middle", "right","Dankbarkeitsübung", "custom"]
    
    
    
    def load_icons(self):
        base = "assets/icons"
        self.icon_size = design.get_scaled_size("icon_size", self.scale)
        
        try:
            self.icons = {
                "left": pygame.image.load(os.path.join(base, "left.png")).convert_alpha(),
                "middle": pygame.image.load(os.path.join(base, "middle.png")).convert_alpha(),
                "right": pygame.image.load(os.path.join(base, "right.png")).convert_alpha(),
                "custom": pygame.image.load(os.path.join(base, "custom.png")).convert_alpha(),
            }
        except:
            print("Icons konnten nicht geladen werden")
            for key in self.panels:
                dummy_surface = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
                dummy_surface.fill((150, 150, 150))
                self.icons[key] = dummy_surface
    
    def draw_gradient(self):
        self.screen.blit(self.gradient_surface, (0, 0))


        
    def _wrap_text(self, text, font, max_width):
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
        
        
        is_selected = (name == self.current_exercise)
        
        target_scale = design.get_animation("hover_scale") if (hovered or is_highlighted) else 1.0
        self.scale_values[name] += (target_scale - self.scale_values[name]) * design.get_animation("animation_speed")
        scale = self.scale_values[name]
        
        scaled_width = int(rect.width * scale)
        scaled_height = int(rect.height * scale)
        
        if name == "custom":
            color_name = "info" if not hovered and not is_highlighted else "info_hover"
        else:
            color_name = "primary" if not hovered and not is_highlighted else "primary_hover"
        
        
        if is_selected and not hovered and not is_highlighted:
            color_name = "text_muted"
        
        alpha = design.get_ui("alpha_hover") if (hovered or is_highlighted) else design.get_ui("alpha_normal")
        if is_selected and not hovered and not is_highlighted:
            alpha = design.get_ui("alpha_selected")
        
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
                design.get_color("accent"),
                border_rect,
                self.border_radius,
                150,
                width=3
            )
            
            #sollte noch Icons für die Übungen folgen
        """
        
        if name in self.icons:
            icon = self.icons[name]
            icon_scaled = pygame.transform.smoothscale(icon, (self.icon_size, self.icon_size))
            icon_offset_y = design.get_scaled_spacing("padding_large", self.scale) * 2
            icon_rect = icon_scaled.get_rect(
                center=(draw_rect.centerx, draw_rect.centery - icon_offset_y)
            )
            self.screen.blit(icon_scaled, icon_rect)
        """


        
        display_text = lang.t(name) if hasattr(lang, 't') else name.upper()
        text_surface = self.font.render(display_text.upper(), True, design.get_color("text"))
        text_offset_y = design.get_scaled_spacing("margin_medium", self.scale) * -4.0  #*2
        text_rect = text_surface.get_rect(
            center=(draw_rect.centerx, draw_rect.centery + text_offset_y)
        )
        self.screen.blit(text_surface, text_rect)
        
        #Markierung für aktive Auswahl
        if is_selected:
            marker = self.font.render("O", True, design.get_color("text")) #success
            marker_rect = marker.get_rect(
                center=(draw_rect.centerx, draw_rect.top + int(40 * self.scale))
            )
            self.screen.blit(marker, marker_rect)
        
        # Bei Custom Parameter anzeigen
        if name == "custom" and is_selected:
            params = self.custom_params
            param_text = f"{params.get('move_up', 4):.1f}s? {params.get('pause_top', 2):.1f}s? {params.get('move_down', 4):.1f}s?"
            param_surface = self.info_font.render(param_text, True, design.get_color("text_muted"))
            param_rect = param_surface.get_rect(
                center=(draw_rect.centerx, draw_rect.centery + text_offset_y + int(50 * self.scale))
            )
            self.screen.blit(param_surface, param_rect)
        
        info_key = f"{name}_info"
        info_text = lang.t(info_key) if hasattr(lang, 't') and lang.t(info_key) != info_key else ""
            
        if info_text:
            max_text_width = int(rect.width * 0.4) #0.9  0.4 
            wrapped_lines = self._wrap_text(info_text, self.info_font, max_text_width)
            
            info_offset_y = text_offset_y + int(100 * self.scale)
            line_height = self.info_font.get_height()
            
            for i, line in enumerate(wrapped_lines):
                line_surface = self.info_font.render(line, True, design.get_color("text_muted"))
                line_rect = line_surface.get_rect(
                    center=(draw_rect.centerx, draw_rect.centery + info_offset_y + (i * line_height))
                )
                self.screen.blit(line_surface, line_rect)
    
    def run(self, nav=None):
        self.audio.play("Übung")
        
        self.choice = None
        self.clicked = False
        self.click_time = None
        
        self.nav = nav
        self.use_navigation = (nav is not None and nav.active)
        
        if self.use_navigation:
            self.nav_helper = NavigationHelper(nav)
            self.nav_helper.setup_ui("exercise")
            
            

            #Übungen als Items setzen
            self.nav_helper.set_items(self.nav_items)
            
            def on_navigate(item, index):
                pass
            
            def on_select(item):
                print(f"DecisionUI SELECT: {item}")
                self.choice = item
                self.clicked = True
                self.click_time = pygame.time.get_ticks()
            
            nav.set_on_navigate(on_navigate)
            nav.set_on_select(on_select)
        
        while True:
      
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
                        if self.return_to_settings:
                            return "settings"
                        else:
                            return None
                    
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
                    # Wenn Custom ausgewählt wurde speichern und zurückgeben
                    if self.choice == "custom":
                        settings_manager.set_exercise("custom")
                        self.audio.stop()
                        return "custom"
                    else:
                        settings_manager.set_exercise(self.choice)
                        self.audio.stop()
                        if self.return_to_settings:
                            return "settings"
                        else:
                            return self.choice
            
            pygame.display.flip()
            self.clock.tick(60)


