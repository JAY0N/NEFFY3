

#für die erweiterte Darstellung der Statistik
import json
import os
import datetime
import uuid


class DataLogger:

    def __init__(self, base_path="logs"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

        self.session_file = os.path.join(base_path, "session_log.json")
        self.evaluation_file = os.path.join(base_path, "evaluation_log.json")

        self.current_session_id = None

    def start_session(self):
        self.current_session_id = str(uuid.uuid4()) # erzeugt zufällige UUID (Universally Unique Identifier) der in string umgewandelt wird innerhalb des loops in dem die Übungen stattfindenausgeführt
        return self.current_session_id              #damit eine individuelle Id erstellt wird


    """
    def _timestamp(self):
        return datetime.datetime.now().isoformat() #gibt Zeitpunkt wandelt in einen ISO-8601-String um """

    def _write(self, path, data):
        if os.path.exists(path):  
            with open(path, "r", encoding="utf-8") as f:
                try:
                    content = json.load(f)
                except:
                    content = []
        else:
            content = []

        content.append(data) #hängt neuen data Eintrag unten an 

        with open(path, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=4) #schreibt Liste zurück in json indent bestimmt die Formatierung in der json

    def log_pre_evaluation(self, choice, duration, stress_before=None): #Evaluation des Stresslevels vor der Übung
        data = {
            "session_id": self.current_session_id,
            #"time": self._timestamp(),
            "choice": choice,
            "duration": duration,
            "stress_before": stress_before 
        }
        self._write(self.session_file, data)

    def log_evaluation(self, selected): #Evaluation nach Übung
        data = {
            "session_id": self.current_session_id,
            #"time": self._timestamp(),
            "stress_after": selected
        }
        self._write(self.evaluation_file, data)
