#sollte jetzt alle Sprachen automatisch anwenden: 

import json
import os
import pygame


class DesignSystem:
    #Zentrales Design System für alle Auswahlen
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        #läd die config datei config 5 ist die Standardfarbe man kann andere configs 6 7 ... erstellen verändert Farben und Größen entsprechend
        possible_paths = [
            os.path.join("config", "design_config5.json"),  #5
            "design_config.json",
            "../config/design_config.json"
        ]
        #kann raus
        default_config = {
            "colors": {"primary": [100, 100, 100], "text": [255, 255, 255]},
            "border_radius": {"panel": 15, "button": 10, "slider": 10}
        }
        
        for config_path in possible_paths:
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
                print(f"? Design-System geladen von {config_path}")
                return
            except FileNotFoundError:
                continue
            except json.JSONDecodeError as e:
                print(f"? JSON-Fehler in {config_path}: {e}")
                continue
        
        print("?? Keine Design-Konfiguration gefunden, verwende Standardwerte")
        self._config = default_config
    
    
    
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
    
    
    
    
    def get_color(self, color_name):
        #Gibt eine Farbe zurück als RGB Wert 
        colors = self._config.get("colors", {})
        color = colors.get(color_name, [150, 150, 150])
        return tuple(color)
    
    def get_color_with_alpha(self, color_name, alpha=None):
        #Gibt eine Farbe mit Alpha zurück als RGBA-Tupel
        color = self.get_color(color_name)
        if alpha is None:
            return color
        return (*color, alpha)
    
    def get_border_radius(self, element_name):
        #Abrundungen
        border_radius = self._config.get("border_radius", {})
        return border_radius.get(element_name, 10)
    
    def get_gradient(self, gradient_name="default"):
        #ibt top_color, bottom_color zurück
        gradients = self._config.get("gradients", {})
        gradient = gradients.get(gradient_name, gradients.get("default", {}))
        top = tuple(gradient.get("top", [100, 100, 150]))
        bottom = tuple(gradient.get("bottom", [80, 80, 100]))
        return top, bottom
    
    def get_font_config(self, font_name):
        #gibt Font zurück
        fonts = self._config.get("fonts", {})
        return fonts.get(font_name, {"name": "DejaVu Sans" , "size_multiplier": 30, "bold": False})  #"Arial" return fonts.get(font_name, {"name": "Arial" , "size_multiplier": 30, "bold": False})
    
    def get_size(self, size_name):
        #Gibt größe zurück
        sizes = self._config.get("sizes", {})
        return sizes.get(size_name, 50)
    
    def get_spacing(self, spacing_name):
        spacing = self._config.get("spacing", {})
        return spacing.get(spacing_name, 20)
        
        
        

    def get_animation(self, anim_name):
        animation = self._config.get("animation", {})
        return animation.get(anim_name, 0.1)
    
    def get_ui(self, ui_name): #kann raus
        ui = self._config.get("ui", {})
        return ui.get(ui_name, 80)
    
    def get_audio(self, audio_name):
        audio = self._config.get("audio", {})
        return audio.get(audio_name, 5000)
    
    def create_gradient_surface(self, width, height, gradient_name="default"):
        #Erstellt gradient surface ist derzeit für alle Auswahlen gleich könnte aber anders gestaltet werden
        top, bottom = self.get_gradient(gradient_name)
        surface = pygame.Surface((width, height))
        
        for y in range(height):
            ratio = y / height
            r = int(top[0] * (1 - ratio) + bottom[0] * ratio)
            g = int(top[1] * (1 - ratio) + bottom[1] * ratio)
            b = int(top[2] * (1 - ratio) + bottom[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
        
        return surface
    




    def get_font(self, font_name, scale):

        config = self.get_font_config(font_name)
        font_name_from_config = config.get("name")
        font_size = int(config.get("size_multiplier", 30) * scale)
        bold = config.get("bold", False)
        
        #wenn kein Schriftnames
        if font_name_from_config is None:
            if bold:
                try:
                    
                    return pygame.font.SysFont(None, font_size, bold=True)
                except:
                    # Fallback
                    return pygame.font.Font(None, font_size)
            return pygame.font.Font(None, font_size)
        
        #wenn Schriftname ist ein String versuche SysFont
        try:
            return pygame.font.SysFont(font_name_from_config, font_size, bold=bold)
        except Exception as e:
            print(f"?? Schrift '{font_name_from_config}' nicht gefunden: {e}")

            if bold:
                try:
                    return pygame.font.SysFont(None, font_size, bold=True)
                except:
                    return pygame.font.Font(None, font_size)
            return pygame.font.Font(None, font_size)    

    
    
    def get_scaled_size(self, size_name, scale):
        return int(self.get_size(size_name) * scale)
    
    def get_scaled_spacing(self, spacing_name, scale):
        return int(self.get_spacing(spacing_name) * scale)
    
    def draw_rounded_rect(self, surface, color, rect, radius, alpha=None, width=0):
        #Rechteck abgerundete Ecken
        if radius <= 0:
            if alpha is not None:
                color = (*color, alpha)
                rect_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
                rect_surface.fill(color)
                surface.blit(rect_surface, rect)
            else:
                pygame.draw.rect(surface, color, rect, width)
            return
        
    
        rect_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        
        if width == 0:  
            pygame.draw.rect(rect_surface, (*color, alpha if alpha else 255), 
                           rect_surface.get_rect(), border_radius=radius)
        else:  
            pygame.draw.rect(rect_surface, (*color, alpha if alpha else 255), 
                           rect_surface.get_rect(), width, border_radius=radius)
        
        surface.blit(rect_surface, rect)
    
    def reload(self):

        self._load_config()


#Globale Instanz gilt in allen Auswahölen
design = DesignSystem()
