

import pygame
import sys
import os
from language_manager import lang
from design_system import design
from navigation import NavigationHelper


class Übungsauswahl:  
    def __init__(self, screen, clock, audio): #initalisieriung des Programms und worauf wir zugreifen also screen, audio, clock um Pausen zu steuern
        self.screen = screen     
        self.clock = clock
        self.audio = audio
 
        pygame.display.set_caption("Decision")
        self.width, self.height = self.screen.get_size()   #Es wird festgelegt welche Breite und Höhe wir verwenden in dem wir schauen welche Maße unser Bildschirm hat 
        
        self.ref_height = 1080     
        self.scale = self.height / self.ref_height  
        
        self.font = design.get_font("title", self.scale)  #Schriftart, Größe
        self.info_font = design.get_font("small", self.scale)
        
        self.choice = None   
        self.clicked = False
        self.click_time = None
        
        self.scale_values = {}
        self.icons = {} #nicht benötigt
        


        panel_width = self.width // 5  #Zahl gibt Menge an Paneln an wenn wir 5 wollen würden müsste man das ändern und self.panels erweitern
        panel_height = self.height // 2 
        
        self.panels = {
            "left": pygame.Rect(0, 0, panel_width, self.height),  #müsste x , y , breite, höhe sein also auf Position x=0 der höhe y=0 beginnt Panel 1 mit einer breite von 
            "middle": pygame.Rect(panel_width, 0, panel_width, self.height),
            "right": pygame.Rect(panel_width * 2, 0, panel_width, self.height),
            "custom": pygame.Rect(panel_width * 4, 0, panel_width, self.height),
            "Dankbarkeitsübung": pygame.Rect(panel_width * 3, 0, panel_width, self.height)
        }
        
        #im Prinzip sehr leicht ergänzbar sollten mehr Übungen folgen
        
        """
        self.panels = {
            "left": pygame.Rect(0, 0, panel_width, panel_height),  #müsste x , y , breite, höhe sein also auf Position x=0 der höhe y=0 beginnt Panel 1 mit einer breite von 
            "middle": pygame.Rect(panel_width, 0, panel_width, panel_height),
            "right": pygame.Rect(panel_width * 2, 0, panel_width, panel_height),
            "custom": pygame.Rect(panel_width * 3, 0, panel_width, panel_height),
            "1": pygame.Rect(0, panel_height, panel_width, panel_height),  #müsste x , y , breite, höhe sein also auf Position x=0 der höhe y=0 beginnt Panel 1 mit einer breite von 
            "2": pygame.Rect(panel_width, panel_height, panel_width, panel_height),
            "3": pygame.Rect(panel_width * 2, panel_height, panel_width, panel_height),
            "4": pygame.Rect(panel_width * 3, panel_height, panel_width, panel_height)
        }
        """
        
        self.gradient_surface = design.create_gradient_surface(   #laden die Werte aus der design Datei mit der wir das Design generalisiert halten
            self.width, self.height, "decision"    #breite, höhe, Spezifikation welcher Programmteil aus der Design config.json
        )
        
        self.border_radius = design.get_border_radius("panel") 
        #        self.load_icons()    #not requiered anymore
        for key in self.panels:
            self.scale_values[key] = 1.0 
         

        
        self.nav_helper = None
        self.use_navigation = False
        self.nav = None
        

        self.nav_items = ["left", "middle", "right", "Dankbarkeitsübung", "custom"]  #wodurch wir Navigieren können alle Einträge einer Ui müssen hier drin stehen 
                                                                                     #es seiden es ist eine bewusste Entscheidung wie bei Slidern
                                                                                     #Reihenfolge spielt eine Rolle


    #kann entfernt werden außer es werden noch Icons für die Übungen erstellt
    """
    def load_icons(self):   #kann rausgenommen werden
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
            print("?? Icons konnten nicht geladen werden")
            for key in self.panels:
                dummy_surface = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
                dummy_surface.fill((150, 150, 150))
                self.icons[key] = dummy_surface"""
                
                
    
    def draw_gradient(self):
        self.screen.blit(self.gradient_surface, (0, 0))  #blit ist Pygame Funktion die Bild auf ein anderes überträgt wir legen den Gradienten über das initale Bild (blit=Block Image Transfer)
                                                         #wir greifen auf screen zu mit den gradient surface das mit der Funktion 
                                                         #create_gradient_surface in der design_system datei erstellt wird. (0,0) ist dann die Position von der aus wir starten
                                                         #Wenn es nicht anders definiert ist steht 0,0 für die Ecke links oben je nachdem wo man etwas positionieren will kann man dann die Werte anpassen
                                                         #100,0 verschiebt es nach rechts 0,100 verschiebt es nach unten
        
    def _wrap_text(self, text, font, max_width):  #Hilfsfunktion die man vielleicht in die designdatei verschieben sollte wenn wir sie anwenden brauchen wir einen entsprechenden Text, Schriftart
                                                  #und eine definierte Breite
        words = text.split(' ') #split teilt Text in Liste von Wörtern auf ("So","sieht","es","aus")
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
    
    def draw_panel(self, name, rect, is_highlighted=False):   #Definition aller Elemente die wir später in run aufrufen und zeichnen lassen
        mouse = pygame.mouse.get_pos() 
        hovered = rect.collidepoint(mouse) 
        
        target_scale = design.get_animation("hover_scale") if (hovered or is_highlighted) else 1.0 #wie groß Hover Effekt sein soll
        self.scale_values[name] += (target_scale - self.scale_values[name]) * design.get_animation("animation_speed")
        scale = self.scale_values[name]
        
        scaled_width = int(rect.width * scale)
        scaled_height = int(rect.height * scale)
        
        if name == "custom": #logik wie wir die Farben festlegen wollen nicht ganz einheitlich über alle Auswahlen hinweg
            color_name = "info" if not hovered and not is_highlighted else "info_hover"
        else:
            color_name = "primary" if not hovered and not is_highlighted else "primary_hover"
        
        alpha = design.get_ui("alpha_hover") if (hovered or is_highlighted) else design.get_ui("alpha_normal")
        
        draw_rect = pygame.Rect(0, 0, scaled_width, scaled_height) #zeichnet Rechtecke basierend auf ihren Bezeichnungen und je nachdem ob sie gehovered werden oder nicht
        draw_rect.center = rect.center  #draw_rect die definierten Positionen für x y aus Panel entnehmen und dann die Saklaierungen für die definierten 
                                        #höhen und breiten anwenden.
                                        #center definiert einen Punkt in der Mitte des Rechtecks oder objekts das gezeichnet wird 
        
        design.draw_rounded_rect(     #Hilfsfunktion aus Design für abgerundete Panel
            self.screen, #Objekt in dem wir arbeiten
            design.get_color(color_name),  #Farben wieder entnommen aus der config.json für einheitliche Färbung /einfach Kontrolle
            draw_rect,  #Rechteck x=  y= Werte je anch Panel, breite höhe skaliert auf jeweiliges Panel
            self.border_radius, 
            alpha
        )
        
        #Rahmen zur besseren Auswahl über Tasten
        if is_highlighted:    
            
            border_rect = draw_rect.inflate(15, 15) #intiales Rechteck wird vergrößert um 15 15
            design.draw_rounded_rect(
                self.screen,
                design.get_color("accent"), #definierte Farbe für den Rahmen
                border_rect,  #Rechteck das vergrößert wird
                self.border_radius, #größe der 
                0,     #Durchsichtigkeit 150 bereits sehr durchsichtig 255 wäre komplett
                width=3  #Breite des Rahmens nehme ich an vielleicht auch nochmal erklären
            )
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
        
        display_text = lang.t(name) if hasattr(lang, 't') else name.upper() #upper wandelt alle Buchstaben in Großbuchstaben um
        text_surface = self.font.render(display_text.upper(), True, design.get_color("text"))
        text_offset_y = design.get_scaled_spacing("margin_small", self.scale) * -20.0  
        text_rect = text_surface.get_rect(
            center=(draw_rect.centerx, draw_rect.centery + text_offset_y)  
        )
        self.screen.blit(text_surface, text_rect)
        
        info_key = f"{name}_info"  #z.B. LEFT_info
        info_text = lang.t(info_key) if hasattr(lang, 't') and lang.t(info_key) != info_key else ""   #wendet die entsprechende Übersetzung an für den jeweiligen Panelnamen überüprüft ob der jeweilige Name
                                                                                                      #in dem langauge_manager vorhanden ist und ob der Name des gleich dem initalen Platzhalternamen ist wenn
                                                                                                      #es ungleich ist und beide Bedingungen erfüllt sind wird der Text angezeigt
            
        if info_text:   
            max_text_width = int(rect.width * 0.4) #0.4
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
        
        self.audio.play("ui")
        
        self.choice = None
        self.clicked = False
        self.click_time = None
        
        self.nav = nav
        self.use_navigation = (nav is not None and nav.active)  #Event handeling für die Tasten/Schulterplatten
        
         #Logik für die Navigation
         #Taste links wird gedrückt Befehl wird angenommen
         #schaut ob innerhalb definierten Zeitraums für Auswahl Taste rechts registriert wird (if current_time - self.last_right_time < self.combination_window:)
         #in main kommt "left" "right" "selected" an wird in on_button_event verarbeitet und entsprechend werden set_left und set_right in nav gesetzt was die weitere Logik in den Auswahlen steuert
         #nav wird dann an die Auswahlen übergeben wie hier die Übungsauswahlen 
         #mit set_items bestimmen wir welche Auswahlen gemacht werden können
         #wenn on_select oder on_navigate erhalten wird entweder das jeweilige Panel als self.choice gesetzt und das beenden der Auswahl getriggert oder weiter durch die Auswahl navigiert 
        
        if self.use_navigation:    
            self.nav_helper = NavigationHelper(nav)
            self.nav_helper.setup_ui("exercise") #müsste man auch rausnehmen können es sollte trotzdem funktionieren
            self.nav_helper.set_items(self.nav_items)  #hier left middle right custum 
            
            def on_navigate(item, index):
                pass
                

            
            def on_select(item):  
                print(f"DecisionUI SELECT: {item}")
                self.choice = item  #eins der items also entweder left middle right custum
                self.clicked = True
                self.click_time = pygame.time.get_ticks()
            
            nav.set_on_navigate(on_navigate)
            nav.set_on_select(on_select)
            
            #wo wir in der Naviagation starten
            if self.nav_items:  #
                nav.current_index = 0 #Panel
                nav.highlighted_item = self.nav_items[0] #welches Panel hervorgehoben wird 
        
        while True:   
            # Navigation update
            if self.use_navigation:
                nav.update()
            
            
            for event in pygame.event.get():  #welche Events wir haben und wie sie sich verhalten für alle Events die nicht die Schultern/Tasten sind
                if event.type == pygame.QUIT:
                    self.audio.stop()
                    pygame.quit()
                    sys.exit()   
                
                if event.type == pygame.KEYDOWN: #wenn Taste gedrückt wird 
                    if event.key == pygame.K_ESCAPE:
                        self.audio.stop()
                        pygame.quit()
                        sys.exit()
                    
                    if self.use_navigation and nav.active: 
                        if event.key == pygame.K_LEFT:  #wenn event.key K_l ankommt also die l Taste auf der Tastatur gedrückt wird wird für die l Taste von False auf True gestellt wenn dann die r 
                            nav.set_left(True)       #Taste auch als Event auftaucht in einem bestimmten Zeitraum wird es als Auswahl registriert 
                        elif event.key == pygame.K_RIGHT:
                            nav.set_right(True)
                
                if event.type == pygame.KEYUP:  #Wenn  Taste losgelassen
                    if self.use_navigation and nav.active:
                        if event.key == pygame.K_LEFT:      #umgekehrtes Verhalten um zu garantieren das die Tasten wieder auf False gereseted werden damit es nicht die ganze Zeit durch die Panel läuft
                            nav.set_left(False)
                        elif event.key == pygame.K_RIGHT: #K_r und K_l sind Tastaturtasten kann jede beliebige Tastaturtaste sein K_"Buchstabe oder Zahl"
                            nav.set_right(False)
                
                if event.type == pygame.MOUSEBUTTONDOWN and not self.clicked:
                    if self.use_navigation:
                        nav.active = False # sobald wir mit der Maus oder dem Finger einen Klick ausführen wird die Tastennavigation abgeschaltet 
                    
                    mouse = pygame.mouse.get_pos()  #registrieret die Mausposition
                    for name, rect in self.panels.items():
                        if rect.collidepoint(mouse): #registriert wenn Maus in einem Panel ist
                            self.choice = name
                            self.clicked = True
                            self.click_time = pygame.time.get_ticks()
                            break #bricht ab
            
            #
            #
            #
            #was wir auf dem Bildschirm alles zeichnen
            self.draw_gradient()   #gezeichnet wird immer von oben nach unten heißt erst wird Hintergrund gezeichnet dann die weiteren Elmente
            
            for name, rect in self.panels.items(): #schauen wie viele Panel wir definiert haben
                is_highlighted = False 
                if self.use_navigation and nav.active:
                    is_highlighted = (name == nav.get_highlighted_item()) #dafür müssen wir in der Naviagationsdatei nachsehen aber müsste eine Hilfsfunktion sein die hervorhebt was gerade in der Auswahl ist
                self.draw_panel(name, rect, is_highlighted)
            
            if self.clicked and self.click_time is not None:
                rect = self.panels[self.choice]
                design.draw_rounded_rect(        #zeichnet die Panels je nachdem wie viele wir definieren
                    self.screen,
                    design.get_color("text_muted"),  #alle Informationen dazu wie es gezeichnet werden soll design.get_color hier nur für Text Farbe
                    rect, #text_muted
                    self.border_radius,
                    design.get_ui("alpha_overlay")
                )
                if pygame.time.get_ticks() - self.click_time > design.get_animation("click_feedback_duration"): #wenn Auwahl entweder über tippen oder Tasten ausgewählt wurd
                    self.audio.stop()
                    if self.use_navigation:
                        nav.active = True
                    return self.choice #jeweilige Auswahl des Panels also Übung 4x6 die als Auswahl zurückgegeben wird
            
            pygame.display.flip() #aktualisiert ganzen Bildschirm
            self.clock.tick(60)



