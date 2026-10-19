
import pygame


class ButtonNavigation:
    
    
    def __init__(self):
        #Aktuelle Auswahl
        self.current_index = 0
        self.selected_item = None
        self.highlighted_item = None
        
        #TastenStatus
        self.left_pressed = False
        self.right_pressed = False
        self.select_triggered = False
        
        
        self.last_action_time = 0
        self.action_cooldown = 200  # ms
        
        #callbacks
        self.on_navigate = None
        self.on_select = None
        self.on_back = None
        self.on_enter_menu = None
        
        #Menü Items
        self.menu_stack = ["main"]
        self.menu_items = {}
        self.current_menu = "main"
        
        # Navigation aktiv ja nein?
        self.active = False
        



        self.select_pending = False
        self.select_timer = 0
        self.select_timeout = 300  # ms
    
    
    
    def setup_menus(self):
        
        self.set_menu_items("main", ["profile", "settings", "start"])
        self.set_menu_items("settings", ["language", "volume", "duration", "exercise", "evaluation", "back"])
        self.set_menu_items("language", ["confirm"])
        #self.set_menu_items("profile", ["create", "load", "delete", "back"])
        self.set_menu_items("profile", ["profile_list", "input_field", "create", "load", "delete", "back"])
        self.set_menu_items("volume", ["test", "continue", "back"])    #"slider",
        self.set_menu_items("exercise", ["left", "middle", "right", "custom", "back"])
        #self.set_menu_items("evaluation", ["on", "off", "back"])
        self.set_menu_items("evaluation", [])
        self.set_menu_items("duration", ["1min", "3min", "5min", "back"])
    
    
      
    def set_menu_items(self, menu_id, items): #Menü Einträge setzen
        self.menu_items[menu_id] = items
    


    def enter_menu(self, menu_id):
        #wenn man in ein Untermenü geht
        if menu_id in self.menu_items:
            self.menu_stack.append(menu_id)
            self.current_menu = menu_id
            self.current_index = 0
            self.selected_item = None
            self.highlighted_item = None
            if self.on_enter_menu:
                self.on_enter_menu(menu_id)
            return True
        return False
      

    
    def go_back(self): #Menü zurück
        if len(self.menu_stack) > 1:
            self.menu_stack.pop()
            self.current_menu = self.menu_stack[-1]
            self.current_index = 0
            self.selected_item = None
            self.highlighted_item = None
            if self.on_back:
                self.on_back(self.current_menu)
            return True
        return False
    
    def get_current_items(self): #aktuelle items
        return self.menu_items.get(self.current_menu, [])
    
    def get_selected_item(self): #gewähltes item
        items = self.get_current_items()
        if items and 0 <= self.current_index < len(items):
            return items[self.current_index]
        return None
    
    def get_highlighted_item(self):
        return self.highlighted_item
    
    def get_highlighted_index(self):
        return self.current_index



    #Tasten Steuerung
    def set_left(self, pressed):
        #status linke Taste
        current_time = pygame.time.get_ticks()
        
        if pressed:
            self.left_pressed = True
            # Prüfe ob rechte Taste auch gedrückt ist 
            if self.right_pressed:
                self._trigger_select()
            else:
                # Starte Timer für Kombination
                self.select_pending = True
                self.select_timer = current_time
        else:
            self.left_pressed = False
            # Wenn keine Kombination erkannt wurde und linke Taste losgelassen wird
            if not self.select_triggered and not self.right_pressed:
                self.select_pending = False
                self._handle_left()
            self.select_triggered = False
    
    def set_right(self, pressed):
        #selbe mit rechts
        current_time = pygame.time.get_ticks()
        
        if pressed:
            self.right_pressed = True
            if self.left_pressed:
                self._trigger_select()
            else:
                
                self.select_pending = True
                self.select_timer = current_time
                

        else:
            self.right_pressed = False
            
            if not self.select_triggered and not self.left_pressed:
                self.select_pending = False
                self._handle_right()
            self.select_triggered = False
    
    def _trigger_select(self): #Auswahl
        if not self._can_act():
            return
        self.select_triggered = True
        self.select_pending = False
        self._handle_select()
    
    def update(self): #jedes Frame aufgerufen schaut ob Event passiert ist
        if not self.select_pending:
            return
        
        current_time = pygame.time.get_ticks()
        
        # Wenn der Timer abgelaufen und Taste noch gedrückt 
        if current_time - self.select_timer > self.select_timeout:
            if self.left_pressed and not self.right_pressed:
                self.select_pending = False
                self._handle_left()
            elif self.right_pressed and not self.left_pressed:
                self.select_pending = False
                self._handle_right()
            elif self.left_pressed and self.right_pressed:
                self.select_pending = False
                self._trigger_select()
    
    def _handle_left(self):
        #geht in Liste von items rückwärts
        if not self._can_act():
            return
        items = self.get_current_items()
        if items:
            self.current_index = (self.current_index - 1) % len(items)
            self.selected_item = self.get_selected_item()
            self.highlighted_item = self.selected_item
            self.last_action_time = pygame.time.get_ticks()
            if self.on_navigate:
                self.on_navigate(self.selected_item, self.current_index)
    
    def _handle_right(self):
        #geht in Liste Items vorwärts
        if not self._can_act():
            return
        items = self.get_current_items()
        if items:
            self.current_index = (self.current_index + 1) % len(items)
            self.selected_item = self.get_selected_item()
            self.highlighted_item = self.selected_item
            self.last_action_time = pygame.time.get_ticks()
            if self.on_navigate:
                self.on_navigate(self.selected_item, self.current_index)
    
    def _handle_select(self):
        #wenn beide Tasten Auswahl Item
        if not self._can_act():
            return
        selected = self.get_selected_item()
        self.last_action_time = pygame.time.get_ticks()
        self.select_pending = False
        self.select_triggered = False
        if self.on_select:
            self.on_select(selected)
    
    def _can_act(self):

        current_time = pygame.time.get_ticks()
        return current_time - self.last_action_time >= self.action_cooldown
    


    #callbacks
    def set_on_navigate(self, callback):
        self.on_navigate = callback
    
    def set_on_select(self, callback):
        self.on_select = callback
    
    def set_on_back(self, callback):
        self.on_back = callback
    
    def set_on_enter_menu(self, callback):
        self.on_enter_menu = callback
    
 
 
    #jeweliger Status
    def reset(self):
        self.menu_stack = ["main"]
        self.current_menu = "main"
        self.current_index = 0
        self.selected_item = None
        self.highlighted_item = None
        self.left_pressed = False
        self.right_pressed = False
        self.select_triggered = False
        self.select_pending = False
        self.last_action_time = 0
    
    def activate(self, active=True):
        self.active = active
        if active:
            self.reset()
            
            
    def on_button_event(action): #bei jedem Button Event aufgerufen
        print(f"Button Event: {action}")
        if action == "left":
            nav.button_pressed("left")
        elif action == "right":
            nav.button_pressed("right")
        elif action == "select":
            nav.button_pressed("select")
    



class NavigationHelper:
    
    def __init__(self, nav):
        self.nav = nav
        self.current_menu = "main"
    
    def setup_ui(self, menu_id):
        self.current_menu = menu_id
        self.nav.current_menu = menu_id
        self.nav.current_index = 0
        self.nav.highlighted_item = None
    
    def get_items(self):
        return self.nav.get_current_items()
    
    def get_highlighted(self):
        return self.nav.get_highlighted_item()
    
    def get_highlighted_index(self):
        return self.nav.get_highlighted_index()
    
    def is_item_highlighted(self, item):
        return item == self.nav.get_highlighted_item()
    
    def set_items(self, items):
        self.nav.set_menu_items(self.current_menu, items)
        

    
    def navigate_to(self, menu_id):
        return self.nav.enter_menu(menu_id)
    
    def go_back(self):
        return self.nav.go_back()
    
    def reset(self):
        self.nav.reset()
    
    def activate(self, active=True):
        self.nav.activate(active)
