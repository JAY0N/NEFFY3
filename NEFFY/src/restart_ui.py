
import pygame
import sys
from language_manager import lang
from design_system import design
from navigation import NavigationHelper


class Restart:  
    def __init__(self, screen, clock, audio):
        self.screen = screen
        self.clock = clock
        self.audio = audio

        self.width, self.height = self.screen.get_size()
        
        
        self.ref_height = 1080
        self.scale = self.height / self.ref_height

        #Font
        #font_size = int(100 * self.scale)
        #self.font = pygame.font.SysFont("Arial", font_size, bold=True)
        self.font = design.get_font("title", self.scale) 

        self.choice = None
        self.clicked = False
        self.click_time = None

        # Animation
        self.scale_values = {}

        panel_width = self.width // 2



        
        self.panels = {
            "again": pygame.Rect(0, 0, panel_width, self.height),  #gleiches verhalten wie in Übungsauswahl
            "exit": pygame.Rect(panel_width, 0, panel_width, self.height) 
        }
        
        


  
        self.gradient_surface = design.create_gradient_surface(  #spezifischen Werte aus der config.json entnommen
            self.width, self.height, "restart"  #derzeit werden alle Gradienten mit den selben Werten gezeichnet man könnte also auch nur ein generellen Verwenden aber es ist imPrinzip Variation möglich    
        )

        self.border_radius = design.get_border_radius("panel") #für die abgerundeten Ecken

        for key in self.panels:
            self.scale_values[key] = 1.0
        



        self.nav_helper = None
        self.use_navigation = False
        self.nav = None


        self.nav_items = ["again", "exit"]



    def draw_gradient(self):
        self.screen.blit(self.gradient_surface, (0, 0))

    def draw_panel(self, key, rect, is_highlighted=False):
        mouse = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse)

        target_scale = design.get_animation("hover_scale") if (hovered or is_highlighted) else 1.0
        self.scale_values[key] += (target_scale - self.scale_values[key]) * design.get_animation("animation_speed")
        scale = self.scale_values[key]

        scaled_width = int(rect.width * scale)
        scaled_height = int(rect.height * scale)
        
 

        if key == "again": 
            color_name = "primary" if not hovered and not is_highlighted else "text_muted"  
        elif key == "exit":
            color_name = "primary" if not hovered and not is_highlighted else "text_muted"   
        
        else:
            color_name = "primary" if not hovered and not is_highlighted else "text_muted" #primary_hover
        
        alpha = design.get_ui("alpha_hover") if (hovered or is_highlighted) else design.get_ui("alpha_normal")

        draw_rect = pygame.Rect(0, 0, scaled_width, scaled_height)
        draw_rect.center = rect.center

        design.draw_rounded_rect(
            self.screen,
            design.get_color(color_name),  
            #color,
            draw_rect,
            self.border_radius,   #15,
            alpha
        )
        
        
        if is_highlighted:  
            border_rect = draw_rect.inflate(15, 15)
            design.draw_rounded_rect(
                self.screen,
                design.get_color("accent"),
                border_rect,
                self.border_radius,   #15,
                150,
                width=3
            )


    
        
        display_text = lang.t(key) if hasattr(lang, 't') else name.upper() #upper wandelt alle Buchstaben in Großbuchstaben um
        text_surface = self.font.render(display_text.upper(), True, design.get_color("text"))
        text_rect = text_surface.get_rect(center=draw_rect.center)
        self.screen.blit(text_surface, text_rect)
        

    def run(self, nav=None):
        self.audio.play("restart")
        
        self.choice = None
        self.clicked = False
        self.click_time = None
        
        self.nav = nav
        self.use_navigation = (nav is not None and nav.active)
        
        if self.use_navigation: #separiert man könnte auch alles in der Hauptschleife behalten
            self.nav_helper = NavigationHelper(nav)
            self.nav_helper.setup_ui("restart")
            self.nav_helper.set_items(self.nav_items)
            
            def on_navigate(item, index):
                pass
            
            def on_select(item):
                print(f"RestartUI SELECT: {item}")
                self.choice = item   #panel_key
                self.clicked = True
                self.click_time = pygame.time.get_ticks()
            
            nav.set_on_navigate(on_navigate)
            nav.set_on_select(on_select)
            
            # Initiale Hervorhebung
            if self.nav_items:
                nav.current_index = 0
                nav.highlighted_item = self.nav_items[0]

        while True: #Hauptschleife
            # Navigation update
            if self.use_navigation:
                nav.update()

            for event in pygame.event.get(): #generelles Setup für die Events -> für alle events in pygame.event enthalten -> KEYDOWN, MOUSEBUTTONDOWN etc. jeweiliges Verhalten Tastaturtasten werden
                                             #mit pygame.K_jeweiliger Buchstabe oder Zahl definiert
                if event.type == pygame.QUIT:
                    self.audio.stop()
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN: #verhalten wenn wir Taste runterdrücken also 
                    if event.key == pygame.K_ESCAPE: 
                        self.audio.stop()
                        pygame.quit()
                        sys.exit()
                    
                    if self.use_navigation and nav.active:
                        if event.key == pygame.K_LEFT:
                            nav.set_left(True)
                        elif event.key == pygame.K_RIGHT: #K_SPACE == Leertaste, K_DOWN== Pfeiltaste UNTEN , K_UP == Pfeiltaste HOCH, K_LEFT == Pfeiltaste LINKS , K_RECHTS == Pfeiltaste RECHTS
                            nav.set_right(True)
                            


                if event.type == pygame.KEYUP: #wenn losgelassen navigation und die Auswahlen nach links und rechts werde gestoppt
                    if self.use_navigation and nav.active:
                        if event.key == pygame.K_LEFT:
                            nav.set_left(False)
                        elif event.key == pygame.K_RIGHT: 
                            nav.set_right(False)

                if event.type == pygame.MOUSEBUTTONDOWN and not self.clicked: #Logik für Mausklich
                    if self.use_navigation:
                        nav.active = False
                    
                    mouse = pygame.mouse.get_pos()
                    for key, rect in self.panels.items(): #wenn key also exit oder restart in self-panel items und es wird registriert das es in einem Panel ist 
                        if rect.collidepoint(mouse):   
                            self.choice = key    #entsprechende Auswahl
                            self.clicked = True   #wurde geklickt
                            self.click_time = pygame.time.get_ticks()
                            break #scließt

            self.draw_gradient()

            for key, rect in self.panels.items():

                is_highlighted = False 
                if self.use_navigation and nav.active:
                    is_highlighted = (key == nav.get_highlighted_item()) #dafür müssen wir in der Naviagationsdatei nachsehen aber müsste eine Hilfsfunktion sein die hervorhebt was gerade in der Auswahl ist
                self.draw_panel(key, rect, is_highlighted)


            if self.clicked and self.click_time is not None:
                rect = self.panels[self.choice]
                design.draw_rounded_rect(        #zeichnet die Panels je nachdem wie viele wir definieren
                    self.screen,
                    design.get_color("primary"),  #alle Informationen dazu wie es gezeichnet werden soll design.get_color hier nur für Text Farbe
                    rect, #text_muted
                    self.border_radius,
                    design.get_ui("alpha_overlay")
                )

                if pygame.time.get_ticks() - self.click_time > design.get_animation("click_feedback_duration"):
                    self.audio.stop()
                    if self.use_navigation:
                        nav.active = True
                    return self.choice   #jeweilige Key Auswahl wird zurückgegeben? wenn exit Programm geschlossen wenn restart wieder in Übungsauswahl zurückschicken

            pygame.display.flip()
            self.clock.tick(60)

