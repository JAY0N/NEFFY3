import pygame
import sys
import os
from design_system import design
from settings_manager import settings_manager
from menu_navigation import NavigationHelper


class PygameDurationUI:
    def __init__(self, screen, clock, audio, return_to_settings=True):
        self.screen = screen
        self.clock = clock
        self.audio = audio
        self.return_to_settings = return_to_settings

        self.width, self.height = self.screen.get_size()
        
        
        self.ref_height = 1080
        self.scale = self.height / self.ref_height

        self.font = design.get_font("title", self.scale)

        self.choice = None
        self.clicked = False
        self.click_time = None

        self.scale_values = {}

        
        self.icons = {}
        
        self.icon_size = design.get_scaled_size("icon_size", self.scale)

        panel_width = self.width // 3

        self.panels = {
            60: pygame.Rect(0, 0, panel_width, self.height),
            180: pygame.Rect(panel_width, 0, panel_width, self.height),
            300: pygame.Rect(panel_width * 2, 0, panel_width, self.height)
        }

        self.labels = {
            60: "1 MIN",
            180: "3 MIN",
            300: "5 MIN"
        }

        self.panel_radius = design.get_border_radius("panel")
        self.button_radius = design.get_border_radius("button")

        
        self.gradient_surface = design.create_gradient_surface(
            self.width, self.height, "duration"
        )

        self.load_icons()

        for key in self.panels:
            self.scale_values[key] = 1.0
        
        #aktuelle Daten aus settings laden
        current_settings = settings_manager.get_settings()
        self.current_duration = current_settings.get("duration", 180)
        self.selected_duration = self.current_duration
        

        self.nav_helper = None
        self.use_navigation = False
        self.nav = None


        
        #Einträge für nav items
        self.nav_items = ["60", "180", "300"]

    def load_icons(self):
        base = "assets/duration_icons"
        try:
            self.icons = {
                60: pygame.image.load(os.path.join(base, "60.png")).convert_alpha(),
                180: pygame.image.load(os.path.join(base, "180.png")).convert_alpha(),
                300: pygame.image.load(os.path.join(base, "300.png")).convert_alpha(),
            }
        except:
            print("?? Duration Icons konnten nicht geladen werden")

    def draw_gradient(self):
        self.screen.blit(self.gradient_surface, (0, 0))

    def draw_panel(self, key, rect, is_highlighted=False):
        mouse = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse)
        
        #prüfen ob diese Dauer ausgewählt ist
        is_selected = (key == self.selected_duration)

        
        target_scale = design.get_animation("hover_scale") if (hovered or is_highlighted) else 1.0
        self.scale_values[key] += (target_scale - self.scale_values[key]) * design.get_animation("animation_speed")
        scale = self.scale_values[key]

        scaled_width = int(rect.width * scale)
        scaled_height = int(rect.height * scale)

        # Farben aus Design-System
        if is_selected:
            color = design.get_color("text_muted") #primary_hover  text_muted
            alpha = design.get_ui("alpha_selected")  #alpha_selected
        elif hovered or is_highlighted:
            color = design.get_color("primary_hover") #success
            alpha = design.get_ui("alpha_hover") #alpha_hover
        else:
            color = design.get_color("primary")  #primary
            alpha = design.get_ui("alpha_normal")

        draw_rect = pygame.Rect(0, 0, scaled_width, scaled_height)
        draw_rect.center = rect.center

        design.draw_rounded_rect(
            self.screen,
            color,
            draw_rect,
            self.panel_radius,
            alpha
        )
        
        # Hervorhebungs Rahmen für Navigation
        if is_highlighted:
            border_rect = draw_rect.inflate(15, 15)
            design.draw_rounded_rect(
                self.screen,
                design.get_color("accent"),
                border_rect,
                self.panel_radius,
                150,
                width=3
            )

        #Icons zeichnen
        if key in self.icons:
            icon = self.icons[key]
            icon_scaled = pygame.transform.smoothscale(icon, (self.icon_size, self.icon_size))
            icon_offset_y = design.get_scaled_spacing("padding_large", self.scale) * 2
            icon_rect = icon_scaled.get_rect(
                center=(draw_rect.centerx, draw_rect.centery - icon_offset_y)
            )
            self.screen.blit(icon_scaled, icon_rect)

        #Text zeichnen
        text_surface = self.font.render(self.labels[key], True, design.get_color("text"))
        text_offset_y = design.get_scaled_spacing("margin_medium", self.scale) * 2
        text_rect = text_surface.get_rect(
            center=(draw_rect.centerx, draw_rect.centery + text_offset_y)
        )
        self.screen.blit(text_surface, text_rect)


        
        # Marker für aktuelle Auswahl O derzeit vielleicht anderes Zeichen?
        if is_selected:
            marker = self.font.render("O", True, design.get_color("text"))
            marker_rect = marker.get_rect(
                center=(draw_rect.centerx, draw_rect.top + int(40 * self.scale))
            )
            self.screen.blit(marker, marker_rect)

    def run(self, nav=None):
        self.audio.play("duration")
        
        self.choice = None
        self.clicked = False
        self.click_time = None
        
        self.nav = nav
        self.use_navigation = (nav is not None and nav.active)
        
        if self.use_navigation:
            self.nav_helper = NavigationHelper(nav)
            self.nav_helper.setup_ui("duration")
            self.nav_helper.set_items(self.nav_items)
            
            def on_navigate(item, index):
                # Bei Navigation Dauer hervorheben
                pass
            
            def on_select(item):
                print(f"DurationUI SELECT: {item}")
                try:
                    # Dauer auswählen speichern
                    value = int(item)
                    self.selected_duration = value
                    settings_manager.set_duration(value)
                    self.choice = value
                    self.clicked = True
                    self.click_time = pygame.time.get_ticks()
                    print(f"Dauer gespeichert: {value}s")
                except:
                    pass
            
            nav.set_on_navigate(on_navigate)
            nav.set_on_select(on_select)
            
            # Initiale Hervorhebung
            if self.nav_items:
                # Finde Index aktueller Dauer
                current_str = str(self.current_duration)
                if current_str in self.nav_items:
                    nav.current_index = self.nav_items.index(current_str)
                    nav.highlighted_item = current_str
                else:
                    nav.current_index = 0
                    nav.highlighted_item = self.nav_items[0]

        while True:
            # Navigation update
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
                    for value, rect in self.panels.items():
                        if rect.collidepoint(mouse):
                            self.selected_duration = value
                            settings_manager.set_duration(value)
                            self.choice = value
                            self.clicked = True
                            self.click_time = pygame.time.get_ticks()
                            break



            # Hintergrund
            self.draw_gradient()

            #Panel
            for key, rect in self.panels.items():
                is_highlighted = False
                if self.use_navigation and nav.active:
                    highlighted = nav.get_highlighted_item()
                    if highlighted == str(key):
                        is_highlighted = True
                self.draw_panel(key, rect, is_highlighted)

            # Klick Feedback
            if self.clicked and self.click_time is not None:
                if pygame.time.get_ticks() - self.click_time > design.get_animation("click_feedback_duration"):
                    self.audio.stop()
                    if self.use_navigation:
                        nav.active = True
                    if self.return_to_settings:
                        return "settings"
                    else:
                        return self.choice

            pygame.display.flip()
            self.clock.tick(60)
