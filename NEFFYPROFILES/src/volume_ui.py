import pygame
import sys
import os
from language_manager import lang
from design_system import design
from settings_manager import settings_manager
from menu_navigation import NavigationHelper


class PygameVolumeUI:
    def __init__(self, screen, clock, audio, return_to_settings=True):
        self.screen = screen
        self.clock = clock
        self.audio = audio
        self.return_to_settings = return_to_settings

        self.width, self.height = self.screen.get_size()

        self.ref_height = 1080
        self.scale = self.height / self.ref_height

        
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        
        self.icon = None
        self.icon_low = None
        self.icon_high = None

        # Test Sound
        try:
            self.test_sound = pygame.mixer.Sound("assets_mp3/audio/waves.mp3")
            self.audio_available = True
        except Exception:
            print("Test sound not found")
            self.audio_available = False

        # Volume aus Settings laden
        current_settings = settings_manager.get_settings()
        self.volume = current_settings.get("volume", 50)

        
        self.scale_test = 1.0
        self.scale_continue = 1.0

        self.button_radius = design.get_border_radius("button")
        self.slider_radius = design.get_border_radius("slider")
        self.icon_radius = design.get_border_radius("icon_frame")

        
        slider_y = int(self.height * design.get_spacing("volume_slider_y"))
        self.slider_rect = pygame.Rect(
            int(self.width * 0.20),
            slider_y,
            int(self.width * 0.60),
            design.get_scaled_size("slider_height", self.scale)
        )

        buttons_y = int(self.height * design.get_spacing("volume_buttons_y"))
        self.test_rect = pygame.Rect(
            int(self.width * 0.20),
            buttons_y,
            int(self.width * 0.25),
            design.get_scaled_size("button_height", self.scale) * 2
        )

        self.continue_rect = pygame.Rect(
            int(self.width * 0.55),
            buttons_y,
            int(self.width * 0.25),
            design.get_scaled_size("button_height", self.scale) * 2
        )



        
        self.font = design.get_font("title", self.scale)

    
        self.gradient_surface = design.create_gradient_surface(
            self.width, self.height, "volume"
        )

        # Assets laden
        self.load_icon()
        self.load_volume_icons()

        # Anfangslautstärke setzen
        self.apply_volume()
        
        # Navigation
        self.nav_helper = None
        self.use_navigation = False
        self.nav = None
        
        # nav items kein slider zu aufwendig
        self.nav_items = ["test", "continue"]

    def load_icon(self):
        try:
            icon_width = design.get_scaled_size("volume_icon_width", self.scale)
            icon_height = design.get_scaled_size("volume_icon_height", self.scale)
            
            self.icon = self._load_rounded_image(
                "assets/volume_icons/chart.png",
                size=(icon_width, icon_height),
                radius=self.icon_radius
            )
        except Exception as e:
            print(f"Volume icon not found: {e}")

    def load_volume_icons(self):
        try:
            icon_size = design.get_scaled_size("volume_small_icon_width", self.scale)

            self.icon_low = self._load_rounded_image(
                "assets/volume_icons/low.jpeg",
                size=(icon_size, icon_size),
                radius=self.icon_radius
            )

            self.icon_high = self._load_rounded_image(
                "assets/volume_icons/high.jpeg",
                size=(icon_size, icon_size),
                radius=self.icon_radius
            )
        except Exception as e:
            print(f"Volume icons not found: {e}")

    def _load_rounded_image(self, path, size, radius):
        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.smoothscale(img, size)
            
            if radius <= 0:
                return img
            
            mask = pygame.Surface(size, pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)
            
            result = img.copy()
            result.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            return result
        except Exception as e:
            print(f"Fehler beim Laden von {path}: {e}")
            return None
    
    

    
    def apply_volume(self):
        volume_float = self.volume / 100.0
        
        
        self.audio.set_volume(volume_float)
        
       
        if self.audio_available:
            self.test_sound.set_volume(volume_float)

        
    def set_volume(self, value):
        self.volume = max(0, min(100, value))
        self.apply_volume()
        settings_manager.set_volume(self.volume)
        
        

    def draw_gradient(self):
        self.screen.blit(self.gradient_surface, (0, 0))




    def draw_slider(self):
        
        design.draw_rounded_rect(
            self.screen,
            design.get_color("slider_track"),
            self.slider_rect,
            self.slider_radius
        )

        # Fill
        fill_width = int(self.slider_rect.width * (self.volume / 100))
        fill_rect = pygame.Rect(
            self.slider_rect.x,
            self.slider_rect.y,
            fill_width,
            self.slider_rect.height
        )

        design.draw_rounded_rect(
            self.screen,
            design.get_color("slider_fill_volume"),
            fill_rect,
            self.slider_radius
        )


        #kleine Lautstärke Icon
        if self.icon_low:
            icon_offset = design.get_scaled_spacing("volume_icon_offset", self.scale)
            rect = self.icon_low.get_rect(
                center=(
                    self.slider_rect.left - icon_offset,
                    self.slider_rect.centery
                )
            )
            self.screen.blit(self.icon_low, rect)

        #hohe Lautstärke icon
        if self.icon_high:
            icon_offset = design.get_scaled_spacing("volume_icon_offset", self.scale)
            rect = self.icon_high.get_rect(
                center=(
                    self.slider_rect.right + icon_offset,
                    self.slider_rect.centery
                )
            )
            self.screen.blit(self.icon_high, rect)

    def draw_button(self, rect, text, hovered, scale_value, is_highlighted=False):
        target_scale = design.get_animation("hover_scale") if (hovered or is_highlighted) else 1.0
        scale_value += (target_scale - scale_value) * design.get_animation("animation_speed")

        draw_w = int(rect.width * scale_value)
        draw_h = int(rect.height * scale_value)


        draw_rect = pygame.Rect(0, 0, draw_w, draw_h)
        draw_rect.center = rect.center

        color_name = "button_test_hover" if (hovered or is_highlighted) else "button_test"
        design.draw_rounded_rect(
            self.screen,
            design.get_color(color_name),
            draw_rect,
            self.button_radius,
            design.get_ui("alpha_button")
        )
        
        
        if is_highlighted:
            border_rect = draw_rect.inflate(15, 15)
            design.draw_rounded_rect(
                self.screen,
                design.get_color("accent"),
                border_rect,
                self.button_radius,
                100,
                width=3
            )

        text_surface = self.font.render(text.upper(), True, design.get_color("text"))
        text_rect = text_surface.get_rect(center=draw_rect.center)
        self.screen.blit(text_surface, text_rect)

        return scale_value

    def run(self, nav=None):
        self.audio.play("volume")
        
        self.choice = None
        self.clicked = False
        self.click_time = None
        
        self.nav = nav
        self.use_navigation = (nav is not None and nav.active)
        
        if self.use_navigation:
            self.nav_helper = NavigationHelper(nav)
            self.nav_helper.setup_ui("volume")
            self.nav_helper.set_items(self.nav_items)
            
            def on_navigate(item, index):
                pass
            
            def on_select(item):
                print(f"VolumeUI SELECT: {item}")
                if item == "test":
                    if self.audio_available:
                        pygame.mixer.stop()
                        self.test_sound.play()
                elif item == "continue":
                    pygame.mixer.stop()
                    self.audio.stop()
                    self.choice = "settings"
                    self.clicked = True
                    self.click_time = pygame.time.get_ticks()
            
            nav.set_on_navigate(on_navigate)
            nav.set_on_select(on_select)

        pygame.event.clear()
        pygame.time.wait(80)
        pygame.event.clear()

        while True:
            
            if self.use_navigation:
                nav.update()
            
            mouse = pygame.mouse.get_pos()

            hover_test = self.test_rect.collidepoint(mouse)
            hover_continue = self.continue_rect.collidepoint(mouse)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
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

                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                    if self.use_navigation:
                        nav.active = False
                    
                    if hasattr(event, "pos"):
                        pos = event.pos
                    else:
                        pos = (
                            int(event.x * self.width),
                            int(event.y * self.height)
                        )

                    if self.slider_rect.collidepoint(pos):
                        rel_x = pos[0] - self.slider_rect.x
                        percent = int((rel_x / self.slider_rect.width) * 100)
                        self.set_volume(percent)
                        print(f"Volume: {self.volume}%")

                    # Test Button
                    elif self.test_rect.collidepoint(pos):
                        if self.audio_available:
                            pygame.mixer.stop()
                            self.test_sound.play()

                    # Continue Button
                    elif self.continue_rect.collidepoint(pos):
                        pygame.mixer.stop()
                        self.audio.stop()
                        if self.return_to_settings:
                            return "settings"
                        else:
                            return

            self.draw_gradient()

            # Haupticon
            if self.icon:
                rect = self.icon.get_rect(
                    center=(self.width // 2, int(self.height * design.get_spacing("volume_icon_y")))
                )
                self.screen.blit(self.icon, rect)

            #Slider
            self.draw_slider()

            #Knöpfe
            is_test_highlighted = False
            is_continue_highlighted = False
            if self.use_navigation and nav.active:
                is_test_highlighted = (nav.get_highlighted_item() == "test")
                is_continue_highlighted = (nav.get_highlighted_item() == "continue")
            
            self.scale_test = self.draw_button(
                self.test_rect,
                lang.t("test"),
                hover_test,
                self.scale_test,
                is_test_highlighted
            )

            self.scale_continue = self.draw_button(
                self.continue_rect,
                lang.t("continue"),
                hover_continue,
                self.scale_continue,
                is_continue_highlighted
            )




          
            if self.clicked and self.click_time is not None:
                if pygame.time.get_ticks() - self.click_time > design.get_animation("click_feedback_duration"):
                    if self.use_navigation:
                        nav.active = True
                    self.clicked = False
                    self.click_time = None
                    if self.choice:
                        return self.choice

            pygame.display.flip()
            self.clock.tick(60)


