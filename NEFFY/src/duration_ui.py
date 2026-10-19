
#jetzt mit Navigation aber nicht mehr der Selection
import pygame
import sys
import os
from design_system import design
from navigation import NavigationHelper


class Duration:
    def __init__(self, screen, clock, audio):  #, return_to_settings=True
        self.screen = screen
        self.clock = clock
        self.audio = audio
        #self.return_to_settings = return_to_settings #kann rausgenommen werden relevant in dem System welches Profile verwendet

        self.width, self.height = self.screen.get_size()
        

        self.ref_height = 1080
        self.scale = self.height / self.ref_height

        self.font = design.get_font("title", self.scale) #Schriftart, Größe etc. entbommen aus der config json

        self.choice = None
        self.clicked = False
        self.click_time = None

        
        self.scale_values = {}

    
        self.icons = {} 
        self.icon_size = design.get_scaled_size("icon_size", self.scale) #gab anfangs Probleme mit Icons mit zu hihen Pixelwerten die beim rendern zu einer starken Verlangsamung im System führten 




        panel_width = self.width // 3  #mehr Auswahlmöglichkeiten zum Beispiel 10 Minuten denkbar 

        self.panels = {
            "60": pygame.Rect(0, 0, panel_width, self.height),
            "180": pygame.Rect(panel_width, 0, panel_width, self.height),
            "300": pygame.Rect(panel_width * 2, 0, panel_width, self.height)
        }

        self.labels = {
            "60": "1 MIN",
            "180": "3 MIN",
            "300": "5 MIN"
        }

        self.panel_values = {
            "60": 60,
            "180": 180,
            "300": 300
        }

        self.panel_radius = design.get_border_radius("panel") #für die Abrundung
        self.button_radius = design.get_border_radius("button")



        self.gradient_surface = design.create_gradient_surface(  #spezifischen Werte aus der config.json entnommen
            self.width, self.height, "duration"
        )

        self.load_icons()

        for key in self.panels:
            self.scale_values[key] = 1.0
        


        #Navigation
        self.nav_helper = None
        self.use_navigation = False
        self.nav = None
        
        # Menue-Eintraege fuer Navigation
        self.nav_items = ["60", "180", "300"] #müsste man mit den höheren Zeiten ergänzen sollte man mehr Auswahlzeiten hinzufügen wollen

    def load_icons(self):
        base = "assets/duration_icons"
        try:
            self.icons = {
                "60": pygame.image.load(os.path.join(base, "60.png")).convert_alpha(),   #os.path.join(base, " ") verbindet einen Pfad mit einer Datei im Prinzip kann man auch assets/duration_icons/60.png
                "180": pygame.image.load(os.path.join(base, "180.png")).convert_alpha(), #schreiben
                "300": pygame.image.load(os.path.join(base, "300.png")).convert_alpha(), #image.load läd ein Bild in den Arbeitsspeicher
                                                                                         #convert_alpha wandelt image in pygame Format mit Trasnparenz um (sollte rendern beschleunigen un dbei durchsichtigen
                                                                                         #Hintergründen relevant sein
            }
        except:
            print("?? Duration Icons konnten nicht geladen werden")



    def draw_gradient(self):
        self.screen.blit(self.gradient_surface, (0, 0))  #ähnlicher Aufbau in allen Auswahlen wir initalisieren alle Werte die wir verwenden und welche Maße sie haben
                                                         #wir definieren den Hintergrund 
                                                         #wir definieren die Elemente die angeklickt
                                                         #wir ddefinieren welche Events passieren können und was übergeben wird
                                                         #wir zeichnen den Hintergrund und die Elemente bis die Eventkonditionen erfüllt sind und die Auswahl schließt

    def draw_panel(self, key, rect, is_highlighted=False):
        mouse = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse)


        target_scale = design.get_animation("hover_scale") if (hovered or is_highlighted) else 1.0
        self.scale_values[key] += (target_scale - self.scale_values[key]) * design.get_animation("animation_speed")
        scale = self.scale_values[key]

        scaled_width = int(rect.width * scale)
        scaled_height = int(rect.height * scale)

        # Farbe aus Design-System
        if hovered or is_highlighted:
            color = design.get_color("primary_hover")
            alpha = design.get_ui("alpha_hover")
        else:
            color = design.get_color("primary")
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
        
        #Rahmen für Navigation
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

        # Icon zeichnen
        if key in self.icons:
            icon = self.icons[key] #icon =self.icon Liste in der alle Panelnamen enthalten sind 
            icon_scaled = pygame.transform.smoothscale(icon, (self.icon_size, self.icon_size))   #smoothscale skaliert image auf definierte Größe müsste hier 120x120 sein
            icon_offset_y = design.get_scaled_spacing("padding_large", self.scale) * 2           #transform ändert die Größe eines Images
            icon_rect = icon_scaled.get_rect(
                center=(draw_rect.centerx, draw_rect.centery - icon_offset_y)
            )
            self.screen.blit(icon_scaled, icon_rect)

        # Text zeichnen keine Begrenzung des Textes notwendig
        text_surface = self.font.render(self.labels[key], True, design.get_color("text"))
        text_offset_y = design.get_scaled_spacing("margin_medium", self.scale) * 2
        text_rect = text_surface.get_rect(
            center=(draw_rect.centerx, draw_rect.centery + text_offset_y)
        )
        self.screen.blit(text_surface, text_rect)

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
                pass
            
            def on_select(item): 
                print(f"DurationUI SELECT: {item}")
                try:
                    value = int(item) #wandeln "60" über int in einen Zahlenwert 60 um für die Übungen
                    self.choice = value
                    self.clicked = True
                    self.click_time = pygame.time.get_ticks()
                except:
                    pass
            
            nav.set_on_navigate(on_navigate)
            nav.set_on_select(on_select)
            

            
            
            if self.nav_items:
                nav.current_index = 0
                nav.highlighted_item = self.nav_items[0]

        #Hauptschleife
        while True:
            #Navigation aktualisieren
            if self.use_navigation:
                nav.update()

            for event in pygame.event.get(): #Events werden verarbeitet je nachdem welcher Art sie sind also Tippen, Klicken oder Taste 
                if event.type == pygame.QUIT:  
                    self.audio.stop()
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:  #Taste wird gedrückt Navigation wird aktiviert 
                    if event.key == pygame.K_ESCAPE:
                        self.audio.stop()
                        return None
                        

                    
                    if self.use_navigation and nav.active:
                        if event.key == pygame.K_LEFT:  #für die Bewegung durch die Panel über Computer Tastatur
                            nav.set_left(True)
                        elif event.key == pygame.K_RIGHT:
                            nav.set_right(True)

                if event.type == pygame.KEYUP:  #Taste wird losgelassen Naviagation wird gestoppt (auf der normalen Tastatur
                    if self.use_navigation and nav.active:   
                        if event.key == pygame.K_LEFT:          
                            nav.set_left(False)
                        elif event.key == pygame.K_RIGHT:
                            nav.set_right(False)

                if event.type == pygame.MOUSEBUTTONDOWN and not self.clicked:  #Mausklick
                    if self.use_navigation:
                        nav.active = False
                    
                    mouse = pygame.mouse.get_pos()
                    for key, rect in self.panels.items():
                        if rect.collidepoint(mouse):
                            self.choice = self.panel_values[key]
                            self.clicked = True
                            self.click_time = pygame.time.get_ticks()
                            break
                            
                            
            
            self.draw_gradient() 

            
            for key, rect in self.panels.items():   #Panels werden gezeichnet je nachdem wie viele wir definiert haben
                is_highlighted = False
                if self.use_navigation and nav.active:
                    is_highlighted = (key == nav.get_highlighted_item())
                self.draw_panel(key, rect, is_highlighted)


            
            if self.clicked and self.click_time is not None: #wenn Auswahl getroffen
                selected_key = None
                for key, value in self.panel_values.items(): #60, 180, 300
                    if value == self.choice:
                        selected_key = key
                        break
                
                if selected_key: 
                    rect = self.panels[selected_key]
                    design.draw_rounded_rect(
                        self.screen,
                        design.get_color("accent"),
                        rect,
                        self.panel_radius,
                        design.get_ui("alpha_overlay")
                    )


                #Kondition für den Abbruch wenn Events stattfinden
                if pygame.time.get_ticks() - self.click_time > design.get_animation("click_feedback_duration"):
                    self.audio.stop()
                    if self.use_navigation:
                        nav.active = True

                        return self.choice   #hier wird der Wert zurückgegeben damit er in den Übungen als Duration verwendet werden kann

            pygame.display.flip()  #Bildschirm aktualisieren
            self.clock.tick(60) 




#Gleiches Verhalten wie bei der Übungsauswahl nur das anstatt eines strings ein integer als choice zurückgegeben wird und Icons gezeichnet werden
