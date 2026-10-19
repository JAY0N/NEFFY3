
#jetzt richtig mit Navigation 
import pygame
import sys
import os
from language_manager import lang
from design_system import design
from navigation import NavigationHelper
import math
import subprocess

class Volume: 
    def __init__(self, screen, clock, audio):  
        self.screen = screen
        self.clock = clock
        self.audio = audio
       

        self.width, self.height = self.screen.get_size()

      
        self.ref_height = 1080
        self.scale = self.height / self.ref_height


        
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        
        self.icon = None
        self.icon_low = None
        self.icon_high = None

        # Test Sound
        self.test_sound = pygame.mixer.Sound("assets_mp3/Test.mp3")  #test 
        #self.audio_available = True
 


       
        self.volume = 50 #sollte Volumen am Anfang immer auf 50 setzen. 50 ist aber nur Refernzwert wenn wir die intiale Lautstärke auf dem Pi auf max stellen verändert sich auch wie laut
                        #und leise wir werden können


        #self.scale_test = 1.0
        #self.scale_continue = 1.0
        self.confirm_scale = 1


        self.button_radius = design.get_border_radius("button")
        self.slider_radius = design.get_border_radius("slider")
        self.icon_radius = design.get_border_radius("icon_frame")

        #Slider Layout
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

        # Anfangslautstaerke setzen
        self.apply_volume()


        self.nav_helper = None
        self.use_navigation = False
        self.nav = None
        
        # Menü Einträge kein Slider zu umständlich)
        self.nav_items = ["test", "continue"]



    def load_icon(self):
        
        icon_width = design.get_scaled_size("volume_icon_width", self.scale) 
        icon_height = design.get_scaled_size("volume_icon_height", self.scale)
        
        self.icon = design._load_rounded_image(   #            self.icon = self._load_rounded_image( das funktioniert wenn man _load_rounded_image hier hat
            "assets/volume_icons/chart.png",
            size=(icon_width, icon_height),
            radius=self.icon_radius 
        )


    def load_volume_icons(self):
        
        icon_size = design.get_scaled_size("volume_small_icon_width", self.scale)

        self.icon_low = design._load_rounded_image(   #self._load_rounded_image(
            "assets/volume_icons/low.jpeg",
            size=(icon_size, icon_size),
            radius=self.icon_radius
        )

        self.icon_high = design._load_rounded_image(     #self._load_rounded_image(
            "assets/volume_icons/high.jpeg",
            size=(icon_size, icon_size),
            radius=self.icon_radius
        )

        


    def apply_volume(self):
 
        volume_float = self.anpassung(self.volume)
        
        self.audio.set_volume(volume_float)
        
        self.test_sound.set_volume(1.0)

        pygame.mixer.music.set_volume(volume_float)
        
    
    def anpassung(self, slider_value):
        angepasst = max(0.0, min(1.0, slider_value / 100.0))
        # menschliches Gehör funktioniert logarithmus nicht linear 
        return angepasst ** 2    #quadratische Funktion kann man vermutlich noch besser machen aber sollte eine besseres Verhalten haben als linear 

    
    def set_volume(self, value):
        self.volume = max(0, min(100, value))
        self.apply_volume()


    def draw_gradient(self):
        self.screen.blit(self.gradient_surface, (0, 0))
        


    def draw_slider(self):
        
        design.draw_rounded_rect(  #Slider
            self.screen,
            design.get_color("slider_track"),
            self.slider_rect, #definierte Größe
            self.slider_radius
        )

        # Fill
        fill_width = int(self.slider_rect.width * (self.volume / 100))
        fill_rect = pygame.Rect(
            self.slider_rect.x, #Position
            self.slider_rect.y,
            fill_width,      #Lautstärke Balken je nach Einstellung
            self.slider_rect.height #höhe Slider
        )

        design.draw_rounded_rect(
            self.screen,
            design.get_color("slider_fill_volume"),
            fill_rect,
            self.slider_radius
        )



        
        if self.icon_low:  #niedrige Lautstärke
            icon_offset = design.get_scaled_spacing("volume_icon_offset", self.scale)
            rect = self.icon_low.get_rect(
                center=(
                    self.slider_rect.left - icon_offset,
                    self.slider_rect.centery
                )
            )
            self.screen.blit(self.icon_low, rect)

        
        if self.icon_high:
            icon_offset = design.get_scaled_spacing("volume_icon_offset", self.scale)
            rect = self.icon_high.get_rect(
                center=(
                    self.slider_rect.right + icon_offset,
                    self.slider_rect.centery
                )
            )
            self.screen.blit(self.icon_high, rect)
            
            

        
    def draw_button(self, rect, text, is_highlighted=False):
        target_scale = design.get_animation("hover_scale") if is_highlighted else 1.0
        #scale_value += (target_scale - scale_value) * design.get_animation("animation_speed")
        self.confirm_scale += (target_scale - self.confirm_scale) * design.get_animation("animation_speed")
        scale = self.confirm_scale

        draw_width = int(rect.width * scale) #
        draw_height = int(rect.height * scale)

        draw_rect = pygame.Rect(0, 0, draw_width, draw_height)
        draw_rect.center = rect.center

        color_name = "button_test_hover" if is_highlighted else "button_test"
        
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

        text_surface = self.font.render(text.upper(), True, design.get_color("text")) #(inhalt, Alising True or False, Farbe)
        text_rect = text_surface.get_rect(center=draw_rect.center)
        self.screen.blit(text_surface, text_rect)



    def run(self, nav=None):
        self.audio.play("volume") #Erklärung im audio_manager
        
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
            
            def on_select(item): #Event Unterscheidung da es nicht nur um Weitergabe von Werten geht
                print(f"VolumeUI SELECT: {item}")
                if item == "test":
                    pygame.mixer.stop()
                    self.test_sound.play()
                    
                    #if self.audio_available:
                    #    pygame.mixer.stop()
                    #    self.test_sound.play()
                elif item == "continue":
                    pygame.mixer.stop()
                    self.audio.stop()
                    self.choice = item 
                    self.clicked = True
                    self.click_time = pygame.time.get_ticks()
            
            nav.set_on_navigate(on_navigate)
            nav.set_on_select(on_select)
            
            #in welchem Panel es startet
            if self.nav_items:
                nav.current_index = 0
                nav.highlighted_item = self.nav_items[0]

        pygame.event.clear()
        pygame.time.wait(80)
        pygame.event.clear()

        while True: 
            
            if self.use_navigation:
                nav.update()
            
            mouse = pygame.mouse.get_pos()

            hover_test = self.test_rect.collidepoint(mouse)
            hover_continue = self.continue_rect.collidepoint(mouse)

            for event in pygame.event.get():  #Events die nicht über die Navigation laufen
                if event.type == pygame.QUIT:
                    return None

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    
                    if self.use_navigation and nav.active:
                        if event.key == pygame.K_LEFT:
                            nav.set_left(True)
                        elif event.key == pygame.K_RIGHT:
                            nav.set_right(True)

                if event.type == pygame.KEYUP:
                    if self.use_navigation and nav.active:
                        if event.key == pygame.K_LEFT:
                            nav.set_left(False)
                        elif event.key == pygame.K_RIGHT:
                            nav.set_right(False)

                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                    if self.use_navigation:
                        nav.active = True #False
                    
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


                    elif self.test_rect.collidepoint(pos):
                        pygame.mixer.stop()
                        # Test-Sound ber denselben Channel wie UI-Sounds abspielen
                        self.audio.channel.set_volume(self.volume / 100.0)
                        self.audio.channel.play(self.test_sound)
                


                     #"Continue" Knopf
                    elif self.continue_rect.collidepoint(pos):
                        pygame.mixer.stop()
                        self.audio.stop()
                        return    


            #alle Objekte die gezeichnet werden
            self.draw_gradient()

            
            if self.icon:
                rect = self.icon.get_rect(
                    center=(self.width // 2, int(self.height * design.get_spacing("volume_icon_y")))
                )
                self.screen.blit(self.icon, rect)

 
            self.draw_slider()

            
            is_test_highlighted = False
            is_continue_highlighted = False
            if self.use_navigation and nav.active:
                is_test_highlighted = (nav.get_highlighted_item() == "test")
                is_continue_highlighted = (nav.get_highlighted_item() == "continue")
            


            self.scale_test = self.draw_button(
                self.test_rect,
                lang.t("test"),
                is_test_highlighted
            )

            self.scale_continue = self.draw_button(
                self.continue_rect,
                lang.t("continue"),
                is_continue_highlighted
            )

            #Beenden der Auswahl
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
