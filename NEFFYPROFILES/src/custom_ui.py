
#limitiert auf 0 bis 10 Sekunden bei Pausen, 3 bis 10 für hoch runterfahren 06.07   kein 0-10 für Motoren damit es zu keinen Konflikt kommt zwischen was Motor schaffen kann und was ausgewä
import pygame
import sys
import os
from language_manager import lang
from design_system import design


class PygameCustomUI:
    def __init__(self, screen, clock, audio):
        self.screen = screen
        self.clock = clock
        self.audio = audio
        self.width, self.height = self.screen.get_size()
        
        self.ref_height = 1080
        self.scale = self.height / self.ref_height
        
    
        title_font_size = int(60 * self.scale)        
        label_font_size = int(40 * self.scale)
        value_font_size = int(50 * self.scale)
        small_font_size = int(30 * self.scale)
        
        self.title_font = pygame.font.SysFont("Arial", title_font_size, bold=True)
        self.label_font = pygame.font.SysFont("Arial", label_font_size)
        self.value_font = pygame.font.SysFont("Arial", value_font_size, bold=True)
        self.small_font = pygame.font.SysFont("Arial", small_font_size)
        
        # Slider Parameter
        self.slider_height = int(20 * self.scale)
        self.slider_width = int(500 * self.scale)
        self.handle_radius = int(25 * self.scale)
        

        # 3-10 Sekunden minimu für Motorbewegung damit Bewegungen realisitsch sind
        self.move_min = 3
        self.move_max = 10
        
        #0 -10 Sekunden 0 wenn keine Pause Animation wird automatisch nur die relevanten Animationeabschnitte abspielen
        self.pause_min = 0
        self.pause_max = 10
        
        #mit diesen Werten wird jedes mal geladen
        self.move_up_time = 4
        self.pause_top_time = 2
        self.move_down_time = 4
        self.pause_bottom_time = 2
        
        
        self.sliders = {
            "move_up": (self.move_up_time - self.move_min) / (self.move_max - self.move_min),
            "pause_top": (self.pause_top_time - self.pause_min) / (self.pause_max - self.pause_min),
            "move_down": (self.move_down_time - self.move_min) / (self.move_max - self.move_min),
            "pause_bottom": (self.pause_bottom_time - self.pause_min) / (self.pause_max - self.pause_min)
        }
        
        self.slider_rects = {}
        self.handle_rects = {}
        
        # Audio Auswahl
        self.audio_folder = "assets_mp3/audio"
        self.available_audios = []
        self.selected_audio_index = 0
        self.selected_audio = None
        self.audio_list_open = False
        self.audio_preview_playing = False
        self.preview_stop_time = 0
        
        # Audio Panel für Auswahl
        audio_panel_width = int(600 * self.scale)
        audio_panel_height = int(700 * self.scale)
        self.audio_panel_rect = pygame.Rect(
            self.width - audio_panel_width - int(50 * self.scale),
            int(150 * self.scale),
            audio_panel_width,
            audio_panel_height
        )


        
        #Audioliste scrollbar aber nicht ideal
        self.scroll_offset = 0
        self.audio_item_height = int(50 * self.scale)
        self.visible_items = audio_panel_height // self.audio_item_height
        
        # Preview Button
        preview_button_width = int(300 * self.scale)
        preview_button_height = int(100 * self.scale)
        self.preview_button_rect = pygame.Rect(
            self.audio_panel_rect.x + (audio_panel_width - preview_button_width) // 2,
            self.height - int(150 * self.scale),
            #self.audio_panel_rect.y + audio_panel_height - preview_button_height - int(-150 * self.scale),
            preview_button_width,
            preview_button_height
        )
        
        # Lade verfügbare Audios
        self._load_available_audios()
        
        # Aktuell gezogener Slider
        self.dragging = None
        
        #Start Zurück Knöpfe
        button_width = int(300 * self.scale)
        button_height = int(100 * self.scale)
        button_spacing = int(150 * self.scale)
        total_width = button_width * 2 + button_spacing
        start_x = (self.width - total_width) // 4
        
        self.start_button = pygame.Rect(
            start_x,
            self.height - int(150 * self.scale),
            button_width,
            button_height
        )
        self.back_button = pygame.Rect(
            start_x + button_width + button_spacing,
            self.height - int(150 * self.scale),
            button_width,
            button_height
        )
        
        self.choice = None
        self.clicked = False
        

        
        self.gradient_surface = design.create_gradient_surface(   #laden die Werte aus der design Datei mit der wir das Design generalisiert halten
            self.width, self.height, "decision")    #breite, höhe, Spezifikation welcher Programmteil aus der Design config.json
        


    
    def _load_available_audios(self):
        self.available_audios = []
        if os.path.exists(self.audio_folder):
            for file in os.listdir(self.audio_folder):
                if file.endswith(".mp3"):
                    display_name = file.replace(".mp3", "")
                    self.available_audios.append({
                        "file": os.path.join(self.audio_folder, file),
                        "name": display_name
                    })
        
        self.available_audios.sort(key=lambda x: x["name"])


        
        for i, audio in enumerate(self.available_audios):
            if "middle" in audio["name"].lower():
                self.selected_audio_index = i
                self.selected_audio = audio["file"]
                break
        else:
            if self.available_audios:
                self.selected_audio_index = 0
                self.selected_audio = self.available_audios[0]["file"]
    
    def _value_from_position(self, x, slider_x, min_val, max_val):
        relative_x = max(0, min(x - slider_x, self.slider_width))
        t = relative_x / self.slider_width
        return min_val + t * (max_val - min_val)
    
    def _position_from_value(self, value, slider_x, min_val, max_val):
        t = (value - min_val) / (max_val - min_val)
        return slider_x + t * self.slider_width
    
    def _update_slider_rects(self):
        start_y = int(280 * self.scale)
        slider_spacing = int(150 * self.scale)
        slider_x = int(450 * self.scale) #450
        
        sliders_order = ["move_up", "pause_top", "move_down", "pause_bottom"]
        
        for i, key in enumerate(sliders_order):
            y = start_y + i * slider_spacing
            self.slider_rects[key] = pygame.Rect(slider_x, y, self.slider_width, self.slider_height)
            
            value = self._get_value_for_slider(key)
            min_val, max_val = self._get_range_for_slider(key)
            
            handle_x = self._position_from_value(value, slider_x, min_val, max_val)
            self.handle_rects[key] = pygame.Rect(
                handle_x - self.handle_radius,
                y - self.handle_radius + self.slider_height // 2,
                self.handle_radius * 2,
                self.handle_radius * 2
            )
    
    def _get_range_for_slider(self, slider_key):
        if "pause" in slider_key:
            return (self.pause_min, self.pause_max)
        else:
            return (self.move_min, self.move_max)
    
    def _get_value_for_slider(self, slider_key):
        values = {
            "move_up": self.move_up_time,
            "pause_top": self.pause_top_time,
            "move_down": self.move_down_time,
            "pause_bottom": self.pause_bottom_time
        }
        return values[slider_key]
    
    def _set_value_for_slider(self, slider_key, value):
        if "pause" in slider_key:
            min_val, max_val = self.pause_min, self.pause_max
        else:
            min_val, max_val = self.move_min, self.move_max
        
        value = max(min_val, min(max_val, value))
        
        if slider_key == "move_up":
            self.move_up_time = value
        elif slider_key == "pause_top":
            self.pause_top_time = value
        elif slider_key == "move_down":
            self.move_down_time = value
        elif slider_key == "pause_bottom":
            self.pause_bottom_time = value
    
    def _update_slider_value_from_position(self, slider_key, mouse_x):
        slider_rect = self.slider_rects[slider_key]
        min_val, max_val = self._get_range_for_slider(slider_key)
        value = self._value_from_position(mouse_x, slider_rect.x, min_val, max_val)
        self._set_value_for_slider(slider_key, value)
        
        handle_x = self._position_from_value(value, slider_rect.x, min_val, max_val)
        self.handle_rects[slider_key].centerx = handle_x


    

    def _get_clean_params(self):
        params = {
            "move_up": self.move_up_time,
            "pause_top": self.pause_top_time if self.pause_top_time >= 1 else 0,
            "move_down": self.move_down_time,
            "pause_bottom": self.pause_bottom_time if self.pause_bottom_time >= 1 else 0,
            "audio": self.selected_audio
        }
        print(f"Clean params: {params}")
        return params
    
    def draw_gradient(self):
        self.screen.blit(self.gradient_surface, (0, 0))
    
    def draw_slider(self, key, label):
        rect = self.slider_rects[key]
        handle_rect = self.handle_rects[key]
        
        #Slider Text
        label_text = lang.t(label) if hasattr(lang, 't') else label
        label_surface = self.label_font.render(label_text, True, design.get_color("text"))
        label_rect = label_surface.get_rect(
            midright=(rect.x - int(50 * self.scale), rect.centery)  #20
        )
        self.screen.blit(label_surface, label_rect)
        
        # Slider Hintergrund
        pygame.draw.rect(self.screen, design.get_color("slider_bg"), rect, border_radius=design.get_border_radius("slider"))
        
        #Slider Bereich in dem Auswahl gerade ist 0.3 für 30% z.B.
        filled_width = handle_rect.centerx - rect.x
        if filled_width > 0:
            filled_rect = pygame.Rect(rect.x, rect.y, filled_width, rect.height)
            pygame.draw.rect(self.screen, design.get_color("slider_fill"), filled_rect, border_radius=design.get_border_radius("slider"))
        
        # Handle
        pygame.draw.circle(self.screen, design.get_color("slider_handle"), handle_rect.center, self.handle_radius)
        pygame.draw.circle(self.screen, design.get_color("slider_handle_inner"), handle_rect.center, self.handle_radius - int(5 * self.scale))
        
        
        value = self._get_value_for_slider(key)
        value_text = f"{value:.1f} s"
        value_surface = self.value_font.render(value_text, True, design.get_color("accent"))
        value_rect = value_surface.get_rect(
            midleft=(rect.x + self.slider_width + int(20 * self.scale), rect.centery)
        )
        self.screen.blit(value_surface, value_rect)
    
    def draw_audio_panel(self):
        #Panel Hintergrund
        pygame.draw.rect(self.screen, design.get_color("panel_bg"), self.audio_panel_rect, border_radius=design.get_border_radius("panel"))
        pygame.draw.rect(self.screen, design.get_color("panel_border"), self.audio_panel_rect, int(3 * self.scale), border_radius=design.get_border_radius("panel"))
        
        #Titel
        title_text = lang.t("audio_selection")
        title_surface = self.label_font.render(title_text, True, design.get_color("accent"))
        title_rect = title_surface.get_rect(center=(self.audio_panel_rect.centerx, self.audio_panel_rect.y + int(30 * self.scale)))
        self.screen.blit(title_surface, title_rect)
        


        
        #aktuelle Auswahl
        if self.selected_audio:
            current_prefix = lang.t("current")
            current_text = f"{current_prefix}: {os.path.basename(self.selected_audio).replace('.mp3', '')}"
            current_surface = self.small_font.render(current_text, True, design.get_color("text_muted"))
            current_rect = current_surface.get_rect(center=(self.audio_panel_rect.centerx, self.audio_panel_rect.y + int(75 * self.scale)))
            self.screen.blit(current_surface, current_rect)
        
        # Audio Liste wenn angetippt
        if self.audio_list_open:
            list_rect = pygame.Rect(
                self.audio_panel_rect.x + int(10 * self.scale),
                self.audio_panel_rect.y + int(90 * self.scale),
                self.audio_panel_rect.width - int(20 * self.scale),
                self.audio_panel_rect.height - int(160 * self.scale)
            )
            pygame.draw.rect(self.screen, design.get_color("list_bg"), list_rect, border_radius=design.get_border_radius("list_item"))
            
            mouse = pygame.mouse.get_pos()
            start_y = list_rect.y + int(5 * self.scale)
            
            total_items = len(self.available_audios)
            max_scroll = max(0, total_items - self.visible_items)
            self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))
            
            for i in range(self.visible_items):
                item_idx = i + self.scroll_offset
                if item_idx >= total_items:
                    break
                
                audio = self.available_audios[item_idx]
                item_rect = pygame.Rect(
                    list_rect.x + int(5 * self.scale),
                    start_y + i * self.audio_item_height,
                    list_rect.width - int(10 * self.scale),
                    self.audio_item_height - int(2 * self.scale)
                )
                
                if item_rect.collidepoint(mouse):
                    pygame.draw.rect(self.screen, design.get_color("list_hover"), item_rect, border_radius=design.get_border_radius("list_item"))
                
                if item_idx == self.selected_audio_index:
                    pygame.draw.rect(self.screen, design.get_color("list_selected"), item_rect, border_radius=design.get_border_radius("list_item"))
                
                name_surface = self.small_font.render(audio["name"], True, design.get_color("text"))
                name_rect = name_surface.get_rect(center=item_rect.center)
                self.screen.blit(name_surface, name_rect)
            
            if total_items > self.visible_items:
                scroll_height = list_rect.height * (self.visible_items / total_items)
                scroll_pos = list_rect.y + (list_rect.height - scroll_height) * (self.scroll_offset / max_scroll)
                scroll_rect = pygame.Rect(
                    list_rect.right - int(8 * self.scale),
                    scroll_pos,
                    int(5 * self.scale),
                    scroll_height
                )
                pygame.draw.rect(self.screen, design.get_color("scroll_bar"), scroll_rect, border_radius=3)
        
        
        hint_text = lang.t("click_to_open")
        hint_surface = self.small_font.render(hint_text, True, design.get_color("text_muted"))
        hint_rect = hint_surface.get_rect(center=(self.audio_panel_rect.centerx, self.audio_panel_rect.bottom - int(25 * self.scale)))
        self.screen.blit(hint_surface, hint_rect)


    
    def draw_preview_button(self):
        mouse = pygame.mouse.get_pos()
        hovered = self.preview_button_rect.collidepoint(mouse)
        
        color = design.get_color("button_preview_hover") if hovered else design.get_color("button_preview")
        pygame.draw.rect(self.screen, color, self.preview_button_rect, border_radius=design.get_border_radius("button"))
        
        preview_text = lang.t("preview")
        preview_surface = self.label_font.render(preview_text, True, design.get_color("text"))
        preview_rect = preview_surface.get_rect(center=self.preview_button_rect.center)
        self.screen.blit(preview_surface, preview_rect)
    
    def draw_buttons(self):
        mouse = pygame.mouse.get_pos()
        
        #Start Knopf
        hovered_start = self.start_button.collidepoint(mouse)
        color = design.get_color("button_start_hover") if hovered_start else design.get_color("button_start")
        pygame.draw.rect(self.screen, color, self.start_button, border_radius=design.get_border_radius("button"))
        start_text = lang.t("startcustum")
        start_surface = self.label_font.render(start_text, True, design.get_color("text"))
        start_rect = start_surface.get_rect(center=self.start_button.center)
        self.screen.blit(start_surface, start_rect)
        
        #Zurück Knopf 
        hovered_back = self.back_button.collidepoint(mouse)
        color = design.get_color("button_back_hover") if hovered_back else design.get_color("button_back")
        pygame.draw.rect(self.screen, color, self.back_button, border_radius=design.get_border_radius("button"))
        back_text = lang.t("back")
        back_surface = self.label_font.render(back_text, True, design.get_color("text"))
        back_rect = back_surface.get_rect(center=self.back_button.center)
        self.screen.blit(back_surface, back_rect)
    
    

    
    def play_preview(self):
        if self.selected_audio and os.path.exists(self.selected_audio):
            if pygame.mixer.get_init():
                pygame.mixer.stop()
            try:
                pygame.mixer.music.load(self.selected_audio)
                pygame.mixer.music.play()
                self.audio_preview_playing = True
                self.preview_stop_time = pygame.time.get_ticks() + 7000
                print(f"Preview gestartet: {self.selected_audio}")
            except Exception as e:
                print(f"Fehler beim Abspielen der Vorschau: {e}")
    
    def update(self):
        if self.audio_preview_playing:
            if pygame.time.get_ticks() >= self.preview_stop_time:
                pygame.mixer.music.stop()
                self.audio_preview_playing = False
                print("Preview beendet")
        

    
    def handle_audio_panel_click(self, pos):
        if not self.audio_panel_rect.collidepoint(pos):
            return False
        
        if self.audio_list_open:
            list_rect = pygame.Rect(
                self.audio_panel_rect.x + int(10 * self.scale),
                self.audio_panel_rect.y + int(90 * self.scale),
                self.audio_panel_rect.width - int(20 * self.scale),
                self.audio_panel_rect.height - int(160 * self.scale)
            )
            
            if list_rect.collidepoint(pos):
                relative_y = pos[1] - (list_rect.y + int(5 * self.scale))
                item_index = relative_y // self.audio_item_height + self.scroll_offset
                
                if 0 <= item_index < len(self.available_audios):
                    self.selected_audio_index = item_index
                    self.selected_audio = self.available_audios[item_index]["file"]
                    self.audio_list_open = False
                    return True
            
            self.audio_list_open = False
            return True
        else:
            self.audio_list_open = True
            return True
        
        return False
    
    def handle_scroll(self, y_offset):
        if self.audio_list_open:
            self.scroll_offset -= y_offset
            max_scroll = max(0, len(self.available_audios) - self.visible_items)
            self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))
            return True
        return False
    
    def run(self):
        self.audio.play("custom")
        self._update_slider_rects()
        click_time = None
        
        clock = pygame.time.Clock()
        
        while True:
            self.update()
            
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
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.preview_button_rect.collidepoint(event.pos):
                            self.play_preview()
                            continue


                        
                        if self.handle_audio_panel_click(event.pos):
                            continue
                        
                        for key, rect in self.handle_rects.items():
                            if rect.collidepoint(event.pos):
                                self.dragging = key
                                break
                        
                        if self.dragging is None:
                            if self.start_button.collidepoint(event.pos) and not self.clicked:
                                # Bereinigte Parameter verwenden
                                self.choice = self._get_clean_params()
                                self.clicked = True
                                click_time = pygame.time.get_ticks()
                            elif self.back_button.collidepoint(event.pos) and not self.clicked:
                                self.choice = None
                                self.clicked = True
                                click_time = pygame.time.get_ticks()
                    
                    elif event.button == 4:
                        self.handle_scroll(1)
                    elif event.button == 5:
                        self.handle_scroll(-1)
                
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.dragging = None
                
                if event.type == pygame.MOUSEMOTION:
                    if self.dragging is not None:
                        self._update_slider_value_from_position(self.dragging, event.pos[0])
            
            self.draw_gradient()
            #self.draw_title()
            
            sliders_order = ["move_up", "pause_top", "move_down", "pause_bottom"]
            labels = {
                "move_up": "move_up",
                "pause_top": "pause_top",
                "move_down": "move_down",
                "pause_bottom": "pause_bottom"
            }
            
            for key in sliders_order:
                self.draw_slider(key, labels[key])
            
            self.draw_audio_panel()
            self.draw_preview_button()
            self.draw_buttons()
            

            
            if self.clicked:
                if pygame.time.get_ticks() - click_time > 200:
                    self.audio.stop()
                    return self.choice
            
            pygame.display.flip()
            clock.tick(60)
