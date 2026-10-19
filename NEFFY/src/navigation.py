
#vermutlich kann man in dieser Datei noch eine Menge Sachen löschen. Zum Zeil noch üerbleibsel aus dem Profilsystem
import pygame


class ButtonNavigation:
    #Navigation über 2 Tasten nicht zu hundert Prozent zuverlässig man könnte versuchen das Triggern von Selection in MotorC anpassen
    
    def __init__(self):
        # Aktuelle Auswahl
        self.current_index = 0
        self.selected_item = None
        self.highlighted_item = None
        
        # Tasten Status
        self.left_pressed = False
        self.right_pressed = False
        self.select_triggered = False
        
        #Aktionscooldown
        self.last_action_time = 0
        self.action_cooldown = 200  # ms
        
        # Callbacks
        self.on_navigate = None
        self.on_select = None
        #self.on_back = None
        #self.on_enter_menu = None
        
        # Menue-Stack und -Items  kann glaube ich auch raus wichtig im anderen Programm
        
        self.menu_stack = ["main"]
        self.menu_items = {}
        self.current_menu = "main"
        
        # Navigation aktiv?
        self.active = False
        

        self.select_pending = False
        self.select_timer = 0
        self.select_timeout = 300  # ms
    

    

       #kann raus 
    """
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
        
        
        """
        
    
    def set_menu_items(self, menu_id, items):  #Navigation bekommt von den Auswahlen alle Items durch die es Navigieren kann
        self.menu_items[menu_id] = items
    
    
    #kann raus
    """
    def enter_menu(self, menu_id):
        
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
      

    
    def go_back(self):
        
        if len(self.menu_stack) > 1:
            self.menu_stack.pop()
            self.current_menu = self.menu_stack[-1]
            self.current_index = 0
            self.selected_item = None
            self.highlighted_item = None
            if self.on_back:
                self.on_back(self.current_menu)
            return True
        return False"""
    
    def get_current_items(self):
        return self.menu_items.get(self.current_menu, [])
    
    def get_selected_item(self):
        #aktueller Eintrag
        items = self.get_current_items()
        if items and 0 <= self.current_index < len(items):
            return items[self.current_index]
        return None
    
    def get_highlighted_item(self):
        #hervorgehobenes item
        return self.highlighted_item
    
    def get_highlighted_index(self):

        return self.current_index
    


    #Tasten Steuerung links
    def set_left(self, pressed):
        
        current_time = pygame.time.get_ticks()
        
        if pressed:
            self.left_pressed = True
            #rechte Taste auch gedrückt?
            if self.right_pressed:
                self._trigger_select()
            else:
                # Starte Timer Kombination
                self.select_pending = True
                self.select_timer = current_time
        else:
            self.left_pressed = False
            # Wenn keine Kombination erkannt wurde und linke Taste losgelassen wird
            if not self.select_triggered and not self.right_pressed:
                self.select_pending = False
                self._handle_left()
            self.select_triggered = False
    
    
    
    def set_right(self, pressed): #Taste rechts
        
        current_time = pygame.time.get_ticks()
        
        if pressed:
            self.right_pressed = True
            #linke Taste auch gedrückt?
            if self.left_pressed:
                self._trigger_select()
            else:
                # Starte Timer Kombination
                self.select_pending = True
                self.select_timer = current_time
                

        else:
            self.right_pressed = False
            # Wenn keine Kombination erkannt wurde und rechte Taste losgelassen wird
            if not self.select_triggered and not self.left_pressed:
                self.select_pending = False
                self._handle_right()
            self.select_triggered = False
    
    def _trigger_select(self): #Auswahl getroffen
        if not self._can_act():
            return
        self.select_triggered = True
        self.select_pending = False
        self._handle_select()
    
    def update(self):
        #prüft auf Timeout und Selection
        if not self.select_pending:
            return
        
        current_time = pygame.time.get_ticks()
        
        # Wenn der Timer abgelaufen ist und die Taste noch gedrückt ist
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
    
    def _handle_left(self): #wir gehen Rückwärts in der Liste
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
    
    def _handle_right(self):  #wir gehen vorwärts in der Liste
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
    
    def _handle_select(self): #Selection
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
    

    #Callbacks
    def set_on_navigate(self, callback):
        self.on_navigate = callback
    
    def set_on_select(self, callback):
        self.on_select = callback
    
    def set_on_back(self, callback):
        self.on_back = callback
    
    def set_on_enter_menu(self, callback):
        self.on_enter_menu = callback
    

     #Status aller möglichen Aktionen 
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
            
            
    def on_button_event(action):
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
