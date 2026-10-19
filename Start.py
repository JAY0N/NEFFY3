#!/usr/bin/env python3



import pygame
import sys
import os
import subprocess
import time
import serial
import threading





START_OF_FRAME = 0xFA
CMD_MUTE = 0x01


class MuteController: #damit Kopfhörer Lautsprecher kontrolliert werden können
    

    def __init__(self, port="/dev/serial0", baudrate=115200):
        self.lock = threading.Lock()
        self.ser = None
        try:
            self.ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.1
            )

        except Exception as e:
            self.ser = None

    def send_mute(self, muted: bool):
        
        if self.ser is None or not self.ser.is_open:
            return False

        payload = bytearray([0x01 if muted else 0x00])
        message = bytearray()
        message.append(START_OF_FRAME)
        message.append(CMD_MUTE)
        message.append(len(payload))
        message.extend(payload)

        try:
            with self.lock:
                self.ser.write(message)
            print(f"MUTE gesendet: {'muted' if muted else 'sound on'} ({message.hex(' ')})")
            return True
        except Exception as e:
            print(f"MUTE senden fehlgeschlagen: {e}")
            return False

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()








WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (240, 240, 245)
GRAY = (200, 200, 210)
DARK_GRAY = (80, 80, 90)
BLUE = (50, 120, 220)
BLUE_HOVER = (70, 140, 240)
RED = (200, 50, 50)
RED_HOVER = (220, 70, 70)
GREEN = (50, 180, 80)
GREEN_HOVER = (70, 200, 100)
TEXT = (30, 30, 35)
TEXT_LIGHT = (100, 100, 110)
ORANGE = (220, 150, 40)
ORANGE_HOVER = (240, 170, 60)


#Password
class PasswordWindow:
    def __init__(self, screen, width, height):
        self.screen = screen

        self.width, self.height = self.screen.get_size()
        self.ref_height = 1080
        self.scale = self.height / self.ref_height
        

        #self.width = width
        #self.height = height
        self.font_large = pygame.font.Font(None, int(height * 0.06))
        self.font = pygame.font.Font(None, int(height * 0.04))
        self.small_font = pygame.font.Font(None, int(height * 0.025))
        
        self.max_length = 6
        self.correct_password = "1234"
        self.active = True
        self.feedback = ""
        self.feedback_color = BLACK
        self.exit_password = False
        
        self.reset()
        
        
        button_size = int(height * 0.15) #0.08 0.17
        spacing = int(height * 0.035)  #0.015
        start_x = (width - (3 * (button_size + spacing)) + spacing) // 2
        start_y = height // 2 - int(height * 0.4) #0.05   0.4
        
        self.digit_rects = []
        
        # Zahlen 1-9
        for i in range(9):
            row = i // 3
            col = i % 3
            x = start_x + col * (button_size + spacing)
            y = start_y + row * (button_size + spacing)
            rect = pygame.Rect(x, y, button_size, button_size)
            self.digit_rects.append((rect, str(i + 1)))
        
        #Zurück Knopf resetet Eingabe
        back_x = start_x + (button_size  + spacing)
        back_y = start_y + 3 * (button_size + spacing)
        self.back_rect = pygame.Rect(back_x, back_y, button_size * 2 + spacing, button_size)
        
        print(f"Passwort-Fenster initialisiert")
        print(f"Back-Button: {self.back_rect}")
    
    def reset(self):
        self.password = ""
        self.feedback = ""
        self.feedback_color = BLACK
        self.exit_password = False
        self.active = True
    

    def handle_event(self, event):
        if not self.active:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.active = False
                self.reset()
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.password = self.password[:-1]
                self.feedback = ""
                return True
            elif event.unicode.isdigit():
                if len(self.password) < self.max_length:
                    self.password += event.unicode
                    self.feedback = ""
                    if self.password == self.correct_password:
                        self.exit_password = True
                        self.feedback = ""
                        self.feedback_color = GREEN
                        return True
                return True
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            
            
            for rect, digit in self.digit_rects:
                if rect.collidepoint(pos):
                    if len(self.password) < self.max_length:
                        self.password += digit
                        self.feedback = ""
                        if self.password == self.correct_password:
                            self.exit_password = True
                            self.feedback = "Passwort korrekt!"
                            self.feedback_color = GREEN
                            return True
                    return True
            
            # Zurück Knopf
            if self.back_rect.collidepoint(pos):
                self.reset()
                self.active = False
                return True
        
        return False
    
    def draw(self):
        self.screen.fill(WHITE)
        

        
        # Zahlen Knöpfe
        for rect, digit in self.digit_rects:
            mouse = pygame.mouse.get_pos()
            hovered = rect.collidepoint(mouse)
            
            color = BLUE_HOVER if hovered else BLUE
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=10)
            
            text = self.font.render(digit, True, WHITE)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
        
        # Zurück Button
        mouse = pygame.mouse.get_pos()
        hovered = self.back_rect.collidepoint(mouse)
        color = ORANGE_HOVER if hovered else ORANGE
        pygame.draw.rect(self.screen, color, self.back_rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, self.back_rect, 2, border_radius=10)
        back_text = self.small_font.render("Zurück", True, WHITE)
        back_rect = back_text.get_rect(center=self.back_rect.center)
        self.screen.blit(back_text, back_rect)
        
        return self.active




class ProgramLauncher:
    def __init__(self):
        self.processes = []
        self.running_programs = []
        

        

        
        
        
    def send_data(self, folder_path):
        
        print(f"\n Sende Daten aus: {folder_path}")
    
        venv_python = os.path.join(folder_path, "venv", "bin", "python")
        email_script = os.path.join(folder_path, "src", "email_sender.py")
    
        # Fallback falls die Datei kleingeschrieben 
        if not os.path.exists(email_script):
            alt = os.path.join(folder_path, "src", "email_sender.py")
            if os.path.exists(alt):
                email_script = alt
    
        if not os.path.exists(venv_python):
            print(f"venv-Python nicht gefunden: {venv_python}")
            return False
    
        if not os.path.exists(email_script):
            print(f"Email-Skript nicht gefunden: {email_script}")
            return False
    
        try:
            process = subprocess.Popen(
                [venv_python, email_script],
                cwd=folder_path,                 
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True
            )
            self.processes.append(process)
            print(f"Email-Versand gestartet (PID: {process.pid})")
            return True
        except Exception as e:
            print(f"Fehler beim Senden: {e}")
            return False        
            
        
        
        
    
    def launch(self, folder_path):
        print(f"\nStarte Programm in: {folder_path}")
        
        venv_activate = os.path.join(folder_path, "venv", "bin", "activate")
        main_script = os.path.join(folder_path, "src", "main.py")
        
        if not os.path.exists(venv_activate):
            print(f"Fehler: venv nicht gefunden")
            return False
        
        if not os.path.exists(main_script):
            print(f"Fehler: main.py nicht gefunden")
            return False
        
        script_content = f"""#!/bin/bash
cd "{folder_path}"
source venv/bin/activate
python src/main.py &
"""
        
        script_path = "/tmp/neffy_launcher.sh"
        with open(script_path, "w") as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)


        
        try:
            process = subprocess.Popen(
                ["bash", script_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True
            )
            self.processes.append(process)
            self.running_programs.append(folder_path)
            
            print(f"Programm gestartet (PID: {process.pid})")
            return True
        except Exception as e:
            print(f"Fehler beim Starten: {e}")
            return False



class ProgramSelectorUI:
    def __init__(self):
        pygame.mixer.pre_init(
            frequency=44100,
            size=-16,
            channels=2,
            buffer=4096  # Von 2048 auf 4096 oder sogar 8192 erhht
        )
        
        pygame.init()


        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        clock = pygame.time.Clock()
        #screen_width, screen_height = screen.get_size()
        
        
        self.info = pygame.display.Info()

        self.screen = screen

        self.width, self.height = self.screen.get_size()
        self.ref_height = 1080
        self.scale = self.height / self.ref_height
        
        #self.width = self.info.current_w
        #self.height = self.info.current_h
        #self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
        pygame.display.set_caption("NEFFY - Programm Selector")
        self.clock = pygame.time.Clock()
        
        base_size = min(self.width, self.height) // 25
        self.font = pygame.font.Font(None, base_size)
        self.small_font = pygame.font.Font(None, int(base_size * 0.5))
        
        # Programme
        self.programs = [
            {"id": 0, "name": "NEFFY Profile", "folder": "/home/neffy3/Neffy3/NEFFYPROFILES", "color": BLUE},
            {"id": 1, "name": "NEFFY Standard", "folder": "/home/neffy3/Neffy3/NEFFY", "color": (50, 180, 120)},
            {"id": 2, "name": "NEFFY Atemerkennung", "folder": "/home/neffy3/Neffy3/Atemerkennung/NEFFY", "color": (50, 180, 120)},
            {
                "id": 3,
                "name": "Sende Daten NEFFY Profile",
                "folder": "/home/neffy3/Neffy3/NEFFYPROFILES",
                "color": (50, 120, 220),
                "action": "send_data"
            },
            {
                "id": 4,
                "name": "Sende Daten Neffy Standard",
                "folder": "/home/neffy3/Neffy3/NEFFY",
                "color": (50, 180, 120),
                "action": "send_data"
            },
            {
                "id": 5,
                "name": "Sende Daten Neffy Atemerkennung",
                "folder": "/home/neffy3/Neffy3/Atemerkennung/NEFFY",
                "color": (50, 180, 120),
                "action": "send_data"
            },            
            {"id": 6, "name": "Beenden", "folder": None, "color": RED, "is_password": True}
        ]
        
        #Panel
        self.panels = []
        panel_height = min(int(self.height * 0.09), 110)  #0.08   80
        panel_spacing = int(self.height * 0.03) #0.025
        total_height = len(self.programs) * (panel_height + panel_spacing) - panel_spacing
        start_y = (self.height - total_height) // 3 #2 
        panel_width = int(self.width * 0.5)
        start_x = (self.width - panel_width) // 2
        
        for i, program in enumerate(self.programs):
            y = start_y + i * (panel_height + panel_spacing)
            rect = pygame.Rect(start_x, y, panel_width, panel_height)
            self.panels.append({"rect": rect, "program": program, "hovered": False})
        
        self.launcher = ProgramLauncher()
        self.running = True
        self.password_window = None
        self.exit_program = False
        self.startup_message = ""
        self.message_timer = 0
        
        
        
        
        #Lausprecher stumm schalten
        self.mute_controller = MuteController()
        self.muted = False   #Default Lautsprecher an

        button_width = int(self.width * 0.19)
        button_height = int(self.height * 0.4)
        button_margin = int(self.width * 0.03)
        self.mute_rect = pygame.Rect(
            self.width - button_width - button_margin,
            self.height // 2 - button_height // 2,
            button_width,
            button_height
        )
  

    
    def draw_background(self):
        self.screen.fill(WHITE)
    
    def draw_panel(self, panel_data):
        rect = panel_data["rect"]
        program = panel_data["program"]
        
        mouse = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse)
        
        color = LIGHT_GRAY if hovered else WHITE
        pygame.draw.rect(self.screen, color, rect, border_radius=12)
        pygame.draw.rect(self.screen, GRAY, rect, 2, border_radius=12)
        
        name = program.get("name", "---")
        name_surface = self.font.render(name, True, TEXT)
        name_rect = name_surface.get_rect(center=rect.center)
        self.screen.blit(name_surface, name_rect)
        
        if hovered:
            color = program.get("color", BLUE)
            border_rect = rect.inflate(-4, -4)
            pygame.draw.rect(self.screen, color, border_rect, 3, border_radius=10)
        
        return hovered





    def draw_mute_button(self):
        mouse = pygame.mouse.get_pos()
        hovered = self.mute_rect.collidepoint(mouse)

        if self.muted:
            color = LIGHT_GRAY if hovered else WHITE 
            label = "Kopfhörermodus: AN"

        else:
            color = LIGHT_GRAY if hovered else WHITE 
            label = "Lautsprechermodus: AN"


        pygame.draw.rect(self.screen, color, self.mute_rect, border_radius=12)
        pygame.draw.rect(self.screen, GRAY, self.mute_rect, 3, border_radius=12)

        # Beschriftung
        label_surface = self.font.render(label, True, (0,0,0))
        label_rect = label_surface.get_rect(
            center=(self.mute_rect.centerx,
                    self.mute_rect.centery)
        )
        self.screen.blit(label_surface, label_rect)


        return hovered        

    
    def draw_message(self):
        if self.startup_message and pygame.time.get_ticks() - self.message_timer < 3000:
            msg_surface = self.small_font.render(self.startup_message, True, GREEN)
            msg_rect = msg_surface.get_rect(center=(self.width // 2, self.height - 50))
            self.screen.blit(msg_surface, msg_rect)
    




    def handle_click(self, pos):

        if self.mute_rect.collidepoint(pos):
            self.muted = not self.muted
            self.mute_controller.send_mute(self.muted)
            return
        
        
        
        for panel in self.panels:
            if panel["rect"].collidepoint(pos):
                program = panel["program"]
    
                if program.get("is_password"):
                    print("öffne Passwort-Fenster")
                    self.password_window = PasswordWindow(self.screen, self.width, self.height)
                    return
    
                folder = program.get("folder")
                action = program.get("action", "launch")
    
                if not folder:
                    self.startup_message = f" {program['name']} ist noch nicht konfiguriert"
                    self.message_timer = pygame.time.get_ticks()
                    return
    
               
                if action == "send_data":
                    success = self.launcher.send_data(folder)
                    if success:
                        self.startup_message = f"Daten von {program['name']} werden gesendet..."
                    else:
                        self.startup_message = f"Fehler beim Senden von {program['name']}"
                else:
                    success = self.launcher.launch(folder)
                    if success:
                        self.startup_message = f"{program['name']} gestartet!"
                    else:
                        self.startup_message = f"Fehler beim Starten von {program['name']}"
    
                self.message_timer = pygame.time.get_ticks()
                return



    
    def run(self):
        print("=" * 60)
        print("NEFFY PROGRAMM SELECTOR")
        print("=" * 60)
        print("")
        print("Programme:")
        for prog in self.programs:
            status = "" if prog.get("folder") else ""
            if prog.get("is_password"):
                status = ""
            print(f"  {status} {prog['name']}")
        print("")
        print("ESC = Beenden")
        print("=" * 60)
        print("")


        
        while self.running:
     
            if self.password_window is not None:
                # Events für Passwort verarbeiten
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    
                    # Handle Event wenn False zurückkommt zurück gedrückt
                    handled = self.password_window.handle_event(event)
                    
                    # Wenn Passwort korrekt -> Programm beenden
                    if self.password_window.exit_password:
                        self.exit_program = True
                        self.running = False
                        break
                    
                    # Wenn Fenster geschlossen wurde 
                    if not self.password_window.active:
                        print("Passwort-Fenster geschlossen")
                        self.password_window = None
                        break
                    
                    # ESC in der Hauptschleife
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.password_window = None
                        break
                
                # Zeichne Passwort-Fenster
                if self.password_window is not None and self.password_window.active:
                    self.password_window.draw()
                    pygame.display.flip()
                    self.clock.tick(60)
                    continue
                elif self.password_window is not None:
                    self.password_window = None
                    continue
            
             #normale Auswahl
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
            
            # Zeichnen
            self.draw_background()
            
            for panel in self.panels:
                hovered = self.draw_panel(panel)
                panel["hovered"] = hovered
                

            self.draw_mute_button()
            
            self.draw_message()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        
        
        if self.exit_program:
            print("\nProgramm mit Passwort beendet")

            try:
                self.mute_controller.close()
            except Exception:
                pass

            try:
                subprocess.run(
                    ["sudo", "/bin/systemctl", "stop", "start.service"],
                    check=False
                )
                print("Service gestoppt  System ist jetzt frei")
            except Exception as e:
                print(f"Service konnte nicht gestoppt werden: {e}")

            pygame.quit()
            sys.exit(0)
        else:
            try:
                self.mute_controller.close()
            except Exception:
                pass
            sys.exit(0)    

        




if __name__ == "__main__":
    ui = ProgramSelectorUI()
    ui.run()



