
#     Logik für Sortierung und Synchronisierung der Befehle die in der Übung stattfinden. Also das Dauer der Übung eingehalten wird und wie sich die Übungen zusammensetzen

#Steuerung sendet die Befehle an über den Motorcontroller an das Board

import time
import threading


class Steuerung: 
    def __init__(self, controller):
        self.mc = controller
        self.current_animation_batch = 0
        self.batch_lock = threading.Lock()  

    def set_animation_batch(self, batch):
        with self.batch_lock:
            self.current_animation_batch = batch
            print(f"ANIMATION BATCH SET: {batch}")

    def get_animation_batch(self): #was der Animationplayer sieht wenn er über logic auf Steuerung zugreift
        with self.batch_lock:
            return self.current_animation_batch 



    #body_head für left und um in die Startposition zu fahren 
    def body_head(self, body_top, body_bottom, head_top, head_bottom,
                  move_up_time, move_down_time,
                  total_runtime, stop_event=None):

        start_time = time.time()
        iteration = 0

        print("=" * 60)
        print("START body_head (ohne Pausen)")
        print(f"Body: {body_top} -> {body_bottom}")
        print(f"Head: {head_top} -> {head_bottom}")
        print(f"Times: up={move_up_time}s, down={move_down_time}s")
        print("=" * 60)

        try:
            while True:
                if stop_event and stop_event.is_set():
                    print("Stop event set")
                    break

                elapsed = time.time() - start_time    #schauen ob die Zeit - Startzeit größer oder kleiner als die Dauer der Übung ist 
                if elapsed >= total_runtime:
                    print(f"Total runtime done ({total_runtime}s)")
                    break

                iteration += 1   #ansonsten wird eine iteration weiter gegangen
                print(f"\nIteration {iteration}")

                #Batch 1 erst wenn set_animation_batch gesetzt wird werden die Befehle an das Board gesended damit Animation und die ensprechende Bewegung des Körpers/Kopes einheitlich und zueinander
                #passend ablaufen
                
                print(f"MOVE UP: Body->{body_top}, Head->{head_top}, {move_up_time}s")
                
                self.set_animation_batch(0)             #Motor steuert auch wie die Animationen ablaufen heißt wir steuern nicht Animationen und Motorbewegung seperat sondern binden beides aneinander damit
                self.mc.move_body_head_in_time(         #Animation und Motor nicht über grobe zeiten miteinander in Einklang gebracht werden müssen 
                    body_top, int(move_up_time * 10),    
                    head_top, int(move_up_time * 10)     
                )
                time.sleep(move_up_time + 0.3) #da wir erstmal ohne response vom Motor arbeiten gehen wir davon aus das der Motor zu diesem Zeitpunkt sein Ziel erreicht hat unelegant aber funktioniert 
                                               

                if stop_event and stop_event.is_set():
                    break

                #Batch 2  
                if move_down_time > 0:
                    print(f"MOVE DOWN: Body->{body_bottom}, Head->{head_bottom}, {move_down_time}s")
                    
                    self.set_animation_batch(1) #vom Index her muss es immer 0 1 sein für die Batches da wir mit 2 Animationen pro Batch arbeiten
                    self.mc.move_body_head_in_time(
                        body_bottom, int(move_down_time * 10),  
                        head_bottom, int(move_down_time * 10)    
                    )
                    time.sleep(move_down_time + 0.3)

                if stop_event and stop_event.is_set():
                    break

        except Exception as e:
            print(f"Error in body_head: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.mc.disable_motors()   #wenn Dauer erreicht wurde wird der Motor gestoppt
            print("Motor stopped")





    #Mit Pausen also middle, custum identischer Aufbau nur das time.sleep Pausen gesetzt werden wenn die Werte die in MotorFunktionen stehen größer als 0 sind
    def body_head_pause(self, body_top, body_bottom, head_top, head_bottom,
                        move_up_time, pause_top, move_down_time, pause_bottom,
                        total_runtime, stop_event=None):

        start_time = time.time()
        iteration = 0



        print("=" * 60)
        print("START body_head_pause (mit Pausen)")
        print(f"Body: {body_top} -> {body_bottom}")
        print(f"Head: {head_top} -> {head_bottom}")
        print(f"Times: up={move_up_time}s, pause_top={pause_top}s, down={move_down_time}s, pause_bottom={pause_bottom}s")
        print("=" * 60)

        try:
            while True:
                if stop_event and stop_event.is_set():
                    print("Stop event set")
                    break

                elapsed = time.time() - start_time
                if elapsed >= total_runtime:
                    print(f"Total runtime done ({total_runtime}s)")
                    break

                iteration += 1
                print(f"\nIteration {iteration}")

                
                
                #Batch1
                print(f"MOVE UP: Body->{body_top}, Head->{head_top}, {move_up_time}s")
                
                self.set_animation_batch(0)
                self.mc.move_body_head_in_time(
                    body_top, int(move_up_time * 10),
                    head_top, int(move_up_time * 10)
                )
                time.sleep(move_up_time + 0.3)

                if stop_event and stop_event.is_set():
                    break

                
                #Pause set_animation_batch wird neu gesetzt damit Animation stattfinden kann auch wenn kein Befehl geschickt wird
                if pause_top > 0:
                    print(f"PAUSE TOP: {pause_top}s")
                    self.set_animation_batch(1)
                    time.sleep(pause_top)

                if stop_event and stop_event.is_set():
                    break

                    
                #Bewegung nach unten
                if move_down_time > 0:
                    print(f"MOVE DOWN: Body->{body_bottom}, Head->{head_bottom}, {move_down_time}s")
                    
                    self.set_animation_batch(2)
                    self.mc.move_body_head_in_time(
                        body_bottom, int(move_down_time * 10),
                        head_bottom, int(move_down_time * 10)
                    )
                    time.sleep(move_down_time + 0.3)

                if stop_event and stop_event.is_set():
                    break

                
                #Pause unten
                if pause_bottom > 0:
                    print(f"PAUSE BOTTOM: {pause_bottom}s")
                    self.set_animation_batch(3)
                    time.sleep(pause_bottom)

        except Exception as e:
            print(f"Error in body_head_pause: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.mc.disable_motors()
            print("Motor stopped")




    #asynchrone Übung 
    def execute_sequence(self, sequence, total_runtime, stop_event=None):
        
        start_time = time.time()
        

        print("=" * 60)
        print("START execute_sequence")
        print(f"Total runtime: {total_runtime}s")
        print(f"Steps: {len(sequence)}")
        print("=" * 60)

        try:
            while True:
                if stop_event and stop_event.is_set():
                    print("Stop event set")
                    break

                elapsed = time.time() - start_time
                if elapsed >= total_runtime:
                    print(f"Total runtime done ({total_runtime}s)")
                    break



                #For loop geht durch die definierte Liste in Sequence die jeweils die WerteKataloge für die unterschiedlichen Abbschnitte enthält heißt erst Katalog 1 dann Katalog2... der while loop
                #wiederholt den for loop bis die gewählte duration erreicht wurde
                for i, step_data in enumerate(sequence): 
                    if stop_event and stop_event.is_set(): 
                        break                              
                        
                        

                    elapsed = time.time() - start_time
                    if elapsed >= total_runtime:
                        break

                     #wir geben im Prinzip Werte an die durchlaufen werden sollen 
                    batch = step_data.get("batch", 0) 
                    body_pos = step_data.get("body_pos", 0)  
                    head_pos = step_data.get("head_pos", 0)  
                    move_time = step_data.get("move_time", 1)
                    pause_after = step_data.get("pause_after", 0)
                    

                
                    print(f"  Body: {body_pos}, Head: {head_pos}")
                    print(f"  Move time: {move_time}s, Pause: {pause_after}s")
                    print(f"  Animation Batch: {batch}")

                    #wir setzen wieder den Animationsbatch so das Animation und Motor angepasst aneinander laufen
                    self.set_animation_batch(batch) #definierter Batch in MotorFunktionen stellt sicher das der korrekte AnimationBatch gesetzt wird

                    # Motor-Befehl senden (nur wenn move_time > 0)
                    if move_time > 0:
                        self.mc.move_body_head_in_time(
                            body_pos, int(move_time * 10),
                            head_pos, int(move_time * 10)
                        )
                        time.sleep(move_time + 0.3)

                    # Pause nach Bewegung
                    if pause_after > 0:
                        print(f"  Pause: {pause_after}s")
                        time.sleep(pause_after)



                # Wenn alle Schritte durchlaufen wurden, wieder von vorne
                print("\nSequence complete, restarting...")
                if time.time() - start_time < total_runtime:
                    continue   #beginnt wieder mit den ersten definierten Werten so kann man komplexere Übungen entsprechend realisieren
                else:
                    break

        except Exception as e:
            print(f"Error in execute_sequence: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.mc.disable_motors()
            print("Motor stopped")



#Mit Response leider funktioniert es nicht wie es sollte
#
"""
#wartet auf Response Board das Motoren in Positionen angekommen sind
import time
import threading


class Steuerung: #MotionPattern:
    def __init__(self, controller):
        self.mc = controller
        self.current_animation_batch = 0
        self.batch_lock = threading.Lock()  

    def set_animation_batch(self, batch):
        with self.batch_lock:
            self.current_animation_batch = batch
            print(f"ANIMATION BATCH SET: {batch}")

    def get_animation_batch(self): #was der Animationplayer sieht wenn er über logic auf Steuerung zugreift
        with self.batch_lock:
            return self.current_animation_batch 



#body_head für left und um in die Startposition zu fahren 
    def body_head(self, body_top, body_bottom, head_top, head_bottom,
                  move_up_time, move_down_time,
                  total_runtime, stop_event=None):
    
        start_time = time.time()
        iteration = 0
    
        print("=" * 60)
        print("START body_head (mit Event-Sync)")
        print("=" * 60)
    
        try:
            while True:
                if stop_event and stop_event.is_set():
                    break
    
                elapsed = time.time() - start_time  #schauen ob die Zeit - Startzeit größer oder kleiner als die Dauer der Übung ist 
                if elapsed >= total_runtime:
                    break
    
                iteration += 1   #ansonsten wird eine iteration weiter gegangen
                print(f"\nIteration {iteration}")
    
                
                print(f"MOVE UP: Body->{body_top}, Head->{head_top}, {move_up_time}s")
    
    
                self.mc.body_done_event.clear()  #Events dafür das Kopf und Körper in der Posiition angekommen sind wird zurückgesetzt
                self.mc.head_done_event.clear()
    

                

                #Batch 1 erst wenn set_animation_batch gesetzt wird werden die Befehle an das Board gesended damit Animation und die ensprechende Bewegung des Körpers/Kopes einheitlich und zueinander
                #passend ablaufen
                
                print(f"MOVE UP: Body->{body_top}, Head->{head_top}, {move_up_time}s")
                #up
                self.set_animation_batch(0)             #Motor steuert auch wie die Animationen ablaufen heißt wir steuern nicht Animationen und Motorbewegung seperat sondern binden beides aneinander damit
                self.mc.move_body_head_in_time(         #Animation und Motor nicht über grobe zeiten miteinander in Einklang gebracht werden müssen 
                    body_top, int(move_up_time * 10),    
                    head_top, int(move_up_time * 10)     
                )
                
                
                

                body_ok = self.mc.body_done_event.wait()  #Wenn Bestätigung das Kopf Körper Position erreicht wurden wird nächster Befehl geschickt
                head_ok = self.mc.head_done_event.wait()
    
                if not (body_ok and head_ok):
                    print(f"? Timeout beim Move-Up (body={body_ok}, head={head_ok})")
    
                if stop_event and stop_event.is_set():
                    break
    
                # Dpwn
                if move_down_time > 0:
                    print(f"MOVE DOWN: Body->{body_bottom}, Head->{head_bottom}, {move_down_time}s")
    
                    self.mc.body_done_event.clear()
                    self.mc.head_done_event.clear()
    
                    self.set_animation_batch(1)
                    self.mc.move_body_head_in_time(
                        body_bottom, int(move_down_time * 10),
                        head_bottom, int(move_down_time * 10)
                    )
    
                    body_ok = self.mc.body_done_event.wait()
                    head_ok = self.mc.head_done_event.wait()
    
                    if not (body_ok and head_ok):
                        print(f"? Timeout beim Move-Down (body={body_ok}, head={head_ok})")
    
                if stop_event and stop_event.is_set():
                    break
    
        except Exception as e:
            print(f"Error in body_head: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.mc.disable_motors()  #wenn Dauer erreicht wurde wird der Motor gestoppt
            print("Motor stopped")






    def body_head_pause(self, body_top, body_bottom, head_top, head_bottom,
                        move_up_time, pause_top, move_down_time, pause_bottom,
                        total_runtime, stop_event=None):
    
        start_time = time.time()
        iteration = 0
    
        try:
            while True:
                if stop_event and stop_event.is_set():
                    break
    
                elapsed = time.time() - start_time
                if elapsed >= total_runtime:
                    break
    
                iteration += 1
                print(f"\nIteration {iteration}")
    
                # --- MOVE UP ---
                self.mc.body_done_event.clear()
                self.mc.head_done_event.clear()
    
                self.set_animation_batch(0)
                self.mc.move_body_head_in_time(
                    body_top, int(move_up_time * 10),
                    head_top, int(move_up_time * 10)
                )
    
      
                body_ok = self.mc.body_done_event.wait()
                head_ok = self.mc.head_done_event.wait()
                if not (body_ok and head_ok):
                    print(f"? Timeout Move-Up (body={body_ok}, head={head_ok})")
    
                if stop_event and stop_event.is_set():
                    break
    
                #PauseTop
                if pause_top > 0:                 #Pause set_animation_batch wird neu gesetzt damit Animation stattfinden kann auch wenn kein Befehl geschickt wird
                    self.set_animation_batch(1)
        
                    time.sleep(pause_top)
    
                if stop_event and stop_event.is_set():
                    break
  
                    #Down
                if move_down_time > 0:
                    self.mc.body_done_event.clear() #selbe Logik wie auch für body head movement
                    self.mc.head_done_event.clear()
    
                    self.set_animation_batch(2)
                    self.mc.move_body_head_in_time(
                        body_bottom, int(move_down_time * 10),
                        head_bottom, int(move_down_time * 10)
                    )
    
                    body_ok = self.mc.body_done_event.wait()
                    head_ok = self.mc.head_done_event.wait()
                    if not (body_ok and head_ok):
                        print(f"? Timeout Move-Down (body={body_ok}, head={head_ok})")
    
                if stop_event and stop_event.is_set():
                    break
    
                # --- PAUSE BOTTOM ---
                if pause_bottom > 0:
                    self.set_animation_batch(3)
                    time.sleep(pause_bottom)
    
        except Exception as e:
            print(f"Error in body_head_pause: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.mc.disable_motors()
            print("Motor stopped")





    def execute_sequence(self, sequence, total_runtime, stop_event=None): #lassen sich komplexere Übungen bauen reicht aus die Sequenzen in MotorFunktionen zu definieren und die entsprechenden 
        #Animationen an die in den Sequenzen definierten Batches anzupassen danach sollte über logic die Übung aufrufbar sein..
        start_time = time.time()
    
        try:
            while True:
                if stop_event and stop_event.is_set():
                    break
    
                elapsed = time.time() - start_time
                if elapsed >= total_runtime:
                    break




                #For loop geht durch die definierte Liste in Sequence die jeweils die WerteKataloge für die unterschiedlichen Abbschnitte enthält heißt erst Katalog 1 dann Katalog2... der while loop
                #wiederholt den for loop bis die gewählte duration erreicht wurde
                for i, step_data in enumerate(sequence):
                    if stop_event and stop_event.is_set():
                        break
    
                    elapsed = time.time() - start_time
                    if elapsed >= total_runtime:
                        break
 
                      #wir geben Werte in Sequenzen an die durchlaufen werden sollen so könenn komplexere Übung erstellt werden die nicht aus hoch runter und Pause bestehen sonder 2 Hoch 2 runter zum Beispiel
                    batch = step_data.get("batch", 0)
                    body_pos = step_data.get("body_pos", 0)
                    head_pos = step_data.get("head_pos", 0)
                    move_time = step_data.get("move_time", 1)
                    pause_after = step_data.get("pause_after", 0)
    
                    self.set_animation_batch(batch)  #definierter Batch der in MotorFunktionen für die jeweilige Sequenz gesetzt wird stellt sicher das der korrekte AnimationBatch abgespielt wird
    
                    if move_time > 0:
                        self.mc.body_done_event.clear()
                        self.mc.head_done_event.clear()
    
                        self.mc.move_body_head_in_time(
                            body_pos, int(move_time * 10),
                            head_pos, int(move_time * 10)
                        )
    
 
                        body_ok = self.mc.body_done_event.wait()
                        head_ok = self.mc.head_done_event.wait()
                        if not (body_ok and head_ok):
                            print(f"? Timeout Step {i} (body={body_ok}, head={head_ok})")
    
                    if pause_after > 0:
                        time.sleep(pause_after)
    
                if time.time() - start_time < total_runtime: 
                    continue #beginnt wieder mit den ersten definierten Werten so kann man komplexere Übungen entsprechend realisieren
                else:
                    break
    
        except Exception as e:
            print(f"Error in execute_sequence: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.mc.disable_motors()
            print("Motor stopped")
"""

