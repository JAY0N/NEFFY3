import pygame
import sys
import os
from language_manager import lang
from design_system import design
from menu_navigation import NavigationHelper


class PygameMainMenuUI:
    def __init__(self, screen, clock, audio):
        self.screen = screen
        self.clock = clock
        self.audio = audio
        
        self.width, self.height = self.screen.get_size()
        self.ref_height = 1080
        self.scale = self.height / self.ref_height
        
        self.font = design.get_font("title", self.scale)
        self.info_font = design.get_font("small", self.scale)
        
        panel_width = self.width // 3
        
        self.panels = {
            "profile": pygame.Rect(0, 0, panel_width, self.height),
            "settings": pygame.Rect(panel_width, 0, panel_width, self.height),
            "start": pygame.Rect(panel_width * 2, 0, panel_width, self.height)
        }
        
        self.scale_values = {
            "profile": 1.0,
            "settings": 1.0,
            "start": 1.0
        }
        
        self.icons = {}
        self.icon_size = design.get_scaled_size("icon_size", self.scale)
        self.load_icons()
        
        self.border_radius = design.get_border_radius("panel")
        self.gradient_surface = design.create_gradient_surface(
            self.width, self.height, "main_menu"
        )
        
        self.choice = None
        self.clicked = False
        self.click_time = None
        
        self.nav_helper = None
        self.use_navigation = False
        self.nav = None
    
    def load_icons(self):
        base = "assets/icons"
        try:
            self.icons = {
                "profile": pygame.image.load(os.path.join(base, "profile.png")).convert_alpha(),
                "settings": pygame.image.load(os.path.join(base, "settings.png")).convert_alpha(),
                "start": pygame.image.load(os.path.join(base, "start.png")).convert_alpha(),
            }
        except:
            print("Main Menu Icons konnten nicht geladen werden")
            for key in self.panels:
                dummy = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
                dummy.fill((150, 150, 150))
                self.icons[key] = dummy


    
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
    
    def draw_gradient(self):
        self.screen.blit(self.gradient_surface, (0, 0))
    
    def draw_panel(self, name, rect, is_highlighted=False):
        mouse = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse)
        
        target_scale = design.get_animation("hover_scale") if (hovered or is_highlighted) else 1.0
        self.scale_values[name] += (target_scale - self.scale_values[name]) * design.get_animation("animation_speed")
        scale = self.scale_values[name]
        
        scaled_width = int(rect.width * scale)
        scaled_height = int(rect.height * scale)
        
        if name == "profile":
            color_name = "info" if not hovered and not is_highlighted else "info_hover"
        elif name == "settings":
            color_name = "primary" if not hovered and not is_highlighted else "primary_hover"
        else:
            color_name = "info" if not hovered and not is_highlighted else "info_hover"
        
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
                design.get_color("accent"),
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


        
        info_key = f"{name}_info"
        info_text = lang.t(info_key) if hasattr(lang, 't') and lang.t(info_key) != info_key else ""
        
        if info_text:
            max_text_width = int(rect.width * 0.9)
            wrapped_lines = self._wrap_text(info_text, self.info_font, max_text_width)
            
            info_offset_y = text_offset_y + int(80 * self.scale)
            line_height = self.info_font.get_height()
            
            for i, line in enumerate(wrapped_lines):
                line_surface = self.info_font.render(line, True, design.get_color("text_muted"))
                line_rect = line_surface.get_rect(
                    center=(draw_rect.centerx, draw_rect.centery + info_offset_y + (i * line_height))
                )
                self.screen.blit(line_surface, line_rect)
    
    def run(self, nav=None):
        self.audio.play("Hauptmenü")
 
        self.choice = None
        self.clicked = False
        self.click_time = None
        
        self.nav = nav
        self.use_navigation = (nav is not None and nav.active)
        
        if self.use_navigation:
            self.nav_helper = NavigationHelper(nav)
            self.nav_helper.setup_ui("main")
            
            def on_navigate(item, index):
                pass
            
            def on_select(item):
                print(f"MainMenu SELECT: {item}")
                self.choice = item
                self.clicked = True
                self.click_time = pygame.time.get_ticks()
            
            nav.set_on_navigate(on_navigate)
            nav.set_on_select(on_select)
        
        while True:
            
            if self.use_navigation:
                nav.update()
            
            mouse = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.audio.stop()
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.audio.stop()
                        pygame.quit()
                        sys.exit()
                    
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
                    return self.choice  #Auswahl des jweiligen Menüs zurückgegeben woanch wir entweder ein Profil erstellen, in die settings gehen oder die Übung starten
            
            pygame.display.flip()
            self.clock.tick(60)
