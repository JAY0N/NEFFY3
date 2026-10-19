

import serial
import struct
import threading
import time

START_OF_FRAME = 0xFA  #muss vor jeden command stehen

CMD_MOVE_BODY_IN_TIME = 0x04  #was wir an den Motor/board schicken
CMD_MOVE_HEAD_IN_TIME = 0x05  #könntefür sleep/aufwachen verwendet werden
CMD_MOVE_BODY_HEAD_IN_TIME = 0x06  #primär verwendet
CMD_DISABLE_MOTORS = 0x07

# BBefehle die ans Raspberry Pi geschickt werden man könnte noch Logik einbauen das nächste Befehle erst geschickt werden wenn Position mit einem response bestätigt wurden
TASTE_LINKS = 0x08   # Linke Schulterplatte gepresst
TASTE_RECHTS = 0x0B  # Rechte Schulterplatte gepresst
CMD_SENSOR = 0x03        # Abstand Bewegungssensor?




class MotorController:
    def __init__(self, port="COM3", baudrate=115200):  #"COM3" - Windows  , "/dev/serial0" - RaspberryPi
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.1
        )
        self.lock = threading.Lock() #sorgt dafür das nur eine Nachricht geschrieben werden kann und nicht zwei threads gleichzeitig Nachrichten schicken damit sich Nachrichten nicht vermixen können
        
        #Navigation Callback
        self.nav_callback = None #jeweilige Navigationsnachricht die über main an die Auswahlen geschickt wird
        

        self.sensor_callback = None  #was dann über main an die sleep datei geschickt wird und das Auwachen triggert
        
        #
        #
        #
        #self.body_done_event = threading.Event()  #für die Antwort vom Board ob der Motor seine Zielposition erreicht hat 
        #self.head_done_event = threading.Event()
        #
        #
        #
        #wenn auch nur eine Antwort verloren geht funktioniert gesammtes System nicht mehr also vielleicht doch eher über time.sleep alles steuern  
        #es wird wieder über time.sleep geregelt ansosnten ganze response Befehl schicken funktioniert nicht zuverlässig da es zwei Befehl sind die ankommen wenn einer fehlt versucht es kontinuierlich in seine
        #Position zu fahren zum Beispiel 0 0 wodurch die Motoren es kontinuierlich ausführen und es funktioniert nicht mehr

        
        self.last_left_time = 0
        self.last_right_time = 0
        self.combination_window = 400 #200
        self.left_triggered = False
        self.right_triggered = False
        
        #Resonse zuhören
        self.listening = True
        self.response_thread = threading.Thread(target=self._listen_responses, daemon=True)  #Threading ermöglicht das man mehrere Funktionen parallel laufen lassen kann 
        self.response_thread.start()                                                         #hier sagen wir das response_thread in einem neuen Thread laufen soll der dann permanent schaut ob Commands ankommen
                                                                                             #response_thread.start startet dann den thread
                                                                                             #daemon=True stellt sicher das der thread nur solange läuft wie das Programm auch wirklich ausgeführt wird
                                                                                             #andernfalls würde _listen_responses weiter laufen
        
        print(f"Connected to {port} @ {baudrate} baud")
        print(f"Button-Listener gestartet (Links=0x{TASTE_LINKS:02X}, Rechts=0x{TASTE_RECHTS:02X})")
        print(f"Sensor-Listener gestartet (Sensor=0x{CMD_SENSOR:02X})")

    def _listen_responses(self):
        while self.listening:
            if not self.ser or not self.ser.is_open:  #schaut ob serial port etwas auffängt schläft und überprüft wieder
                time.sleep(0.1)
                continue
            
            try:
                if self.ser.in_waiting > 0:
                    byte = self.ser.read(1) #wir schauen was im serial port geliefert wird 
                    if not byte:
                        continue
                    
                    if byte[0] == START_OF_FRAME: #prüft ob erstes byte 0xFA entspricht
                        cmd = self.ser.read(1) #read liest immer das nächste noch ungelesene byte aus
                                               #Heißt wir schauen erst ist es ein byte wenn ja -> ist das byte == START_OF_FRAME wenn ja -> read schaut sich das nächste noch ungelesene byte an
                                               #das ist im Ablauf die Command_id welche wir vergleichen können mit allen Commands die verwendet werden -> das nächste read(1) liest dann die länge aus 
                                               #ist irelevant für TASTE_LINKS, TASTE_RECHTS und ABSTANDSSENSOR da diese bloß die Command_id brauchen
                                               #spielt eine Rolle wenn wir response auslesen ob der Motor seine Position erreicht hat
                        if not cmd:            
                            continue
                        
                        length = self.ser.read(1)     
                        if not length:
                            continue
                        
          
                        #Sensor annehmen als es noch nur über einen Wert gelaufen ist hätte exakt gleich funktioniert 
                        """
                        if cmd[0] == CMD_SENSOR:   

                            if self.sensor_callback:
                                self.sensor_callback(True)   """


                        if cmd[0] == CMD_SENSOR:
                        
                            payload = b""
                            if length[0] > 0:
                                payload = self.ser.read(length[0])
                                if len(payload) != length[0]:
                                    continue
                        
                            payload_value = payload[0] if len(payload) > 0 else 0
                            #print(f" SENSOR: Payload={payload_value}")
                        
                            if self.sensor_callback:
                                self.sensor_callback(payload_value)




                        
                        
                        #Events wenn die Schulterplatte gedrückt wird
                        elif cmd[0] == TASTE_LINKS:
                            print("Linke Taste")
                            self._handle_left_button() #für Navigation erst in main verarbeitet dann in der Navigation und dann an die entsprechende Auswahl
                        
                        elif cmd[0] == TASTE_RECHTS:
                            print("Rechte Taste")
                            self._handle_right_button()
                        
                        
                    
                    
                    
                    

                  #kann prinzipiell rausgenommen werden time.sleep für jeden Befehl zu nehmen ist nicht ideal aber erheblich einfacher und stabiler
                        # Body-Besttigung (0x04)   #Besätigung von Board das Motorposition erreicht wurde
                        """
                        elif cmd[0] == CMD_MOVE_BODY_IN_TIME:
                            if length[0] > 0:
                                payload = self.ser.read(length[0])
                                if len(payload) != length[0]:
                                    continue
                                status = payload[0] if len(payload) > 0 else 0x00
                                print(f"ESPONSE BODY: CMD=0x{cmd[0]:02X}, Status=0x{status:02X}")
                                self.body_done_event.set()
                            else:
                                print(f"RESPONSE BODY: CMD=0x{cmd[0]:02X}")
                        
                        # Head-Besttigung (0x05)
                        elif cmd[0] == CMD_MOVE_HEAD_IN_TIME:
                            if length[0] > 0:
                                payload = self.ser.read(length[0])
                                if len(payload) != length[0]:
                                    continue
                                status = payload[0] if len(payload) > 0 else 0x00
                                print(f"RESPONSE HEAD: CMD=0x{cmd[0]:02X}, Status=0x{status:02X}")
                                self.head_done_event.set()
                            else:
                                print(f"RESPONSE HEAD: CMD=0x{cmd[0]:02X}")
                        
                        # MOVE_BODY_HEAD_IN_TIME (0x06)  keine Besttigung, nur loggen
                        elif cmd[0] == CMD_MOVE_BODY_HEAD_IN_TIME:
                            print(f"RESPONSE: CMD=0x{cmd[0]:02X} (kein Acknowledge definiert)")"""

                        
                    else:
                        # Unerwartete Bytes ignorieren
                        pass
                        
            except Exception as e:
                print(f"Kommunikation fehlerhaft")
                print(e)
                time.sleep(0.1)


  # Logik für die Annahme von Befehlen 
  #kann theoretisch rausgenommen werden weil wieder über time.sleep
    """
    def wait_for_move_done(self, timeout): #wird an Steuerung übergeben
        
        #Wartet darauf das BEIDE Events body und head gesetzt sind
        #Gibt True zurück wenn beide innerhalb Timeouts eintreffen
        
        # Zuerst beide Events zurcksetzen
        self.body_done_event.clear()
        self.head_done_event.clear()
    
        # Warte auf beide
        body_ok = self.body_done_event.wait()
        head_ok = self.head_done_event.wait()
    
        if body_ok and head_ok:
            return True
        else:
            print(f"Timeout: body={body_ok}, head={head_ok}")
            return False"""




    def _handle_left_button(self):
        current_time = time.time() * 1000
        self.left_triggered = True
        self.last_left_time = current_time
        
        if current_time - self.last_right_time < self.combination_window:
            self._trigger_combination()
            return
        
        def delayed_action():
            time.sleep(self.combination_window / 1000.0)
            if self.left_triggered and not self.right_triggered:
                self.left_triggered = False
                if self.nav_callback:
                    self.nav_callback("left")
                    

        threading.Thread(target=delayed_action, daemon=True).start() 
        

    def _handle_right_button(self):
        current_time = time.time() * 1000
        self.right_triggered = True
        self.last_right_time = current_time
        
        if current_time - self.last_left_time < self.combination_window:  #Auswahllogik für rechts und links identisch
            self._trigger_combination()
            return
        
        def delayed_action():
            time.sleep(self.combination_window / 1000.0)
            if self.right_triggered and not self.left_triggered: #zurücksetzen damit wir nicht nach einem Tastendruck nur nach rechts oder links navigieren
                self.right_triggered = False
                if self.nav_callback:        
                    self.nav_callback("right")
         
        threading.Thread(target=delayed_action, daemon=True).start()


    def _trigger_combination(self): #Auswahl getroffen
        
        self.left_triggered = False #trigger links und rechts zurückgesetzt
        self.right_triggered = False
        if self.nav_callback:
            self.nav_callback("select")

  
        #Was wir in der main aufrufen und verarbeiten enthält die jeweilige Nachricht also right left oder halt der Sensor 
    def set_nav_callback(self, callback):
        self.nav_callback = callback
        print("Navigation Callback gesetzt")

    def set_sensor_callback(self, callback):
        self.sensor_callback = callback
        print("Sensor Callback gesetzt")



    def send_message(self, command, payload):
        message = bytearray()   
        message.append(START_OF_FRAME)    #START_OF_FRAME_IDENTIfIER =0xFA 
        message.append(command)        #jeweiliger Befehl wenn wir move_body_in_time aufrufen dann verpacken wir erst die Nachricht die wir senden wollen
                                       #also die Zielposition, die Zeit in der die Zielposition erreicht werden soll in eine Payload schicken diese mit der Command_id an send_message
                                       #was dann die message aneinanderreiht erst START_OF_FRAME_IDENTIFIER, Befehl und dann die Payload
        message.append(len(payload))
        message.extend(payload)

        with self.lock:
            self.ser.write(message)
            self.ser.flush() #flush sorgt dafür das die ganze Nachricht abgeschickt wurde bevor der Code weitermacht könnte man auch rausnehmen

        print(f"SEND: {message.hex(' ')}")

    def _pack_uint16(self, value):  #wandelt Dezimalzahl in Hexa Dezimal Zahl um
        return struct.pack(">H", int(value))

    def move_body_in_time(self, target_position_deg, move_time_ms):
        scaled_position = int(target_position_deg * 10)    #*10 damit wir keine float Nummer haben
        payload = bytearray()                               
        payload.extend(self._pack_uint16(scaled_position))  
        payload.extend(self._pack_uint16(move_time_ms))        
        self.send_message(CMD_MOVE_BODY_IN_TIME, payload)

    def move_head_in_time(self, target_position_deg, move_time_ms):
        scaled_position = int(target_position_deg * 10)
        payload = bytearray()
        payload.extend(self._pack_uint16(scaled_position))
        payload.extend(self._pack_uint16(move_time_ms))
        self.send_message(CMD_MOVE_HEAD_IN_TIME, payload)

    def move_body_head_in_time(self, body_target_deg, body_time_ms, head_target_deg, head_time_ms):
        body_scaled = int(body_target_deg * 10)
        head_scaled = int(head_target_deg * 10)



        payload = bytearray()
        payload.extend(self._pack_uint16(body_scaled))
        payload.extend(self._pack_uint16(body_time_ms))
        payload.extend(self._pack_uint16(head_scaled))
        payload.extend(self._pack_uint16(head_time_ms))

        self.send_message(CMD_MOVE_BODY_HEAD_IN_TIME, payload)

    def disable_motors(self):
        payload = bytearray([0x01])
        self.send_message(CMD_DISABLE_MOTORS, payload)

    def close(self):
        self.listening = False
        if self.response_thread:
            self.response_thread.join(timeout=1)
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Verbindung geschlossen")


