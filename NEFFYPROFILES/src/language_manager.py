
import json
import os


class LanguageManager:

    def __init__(self):

        self.language = None
        self.data = {}

    def load(self, lang):

        path = os.path.join("languages", f"{lang}.json")

        with open(path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        self.language = lang

    def t(self, key):

        return self.data.get(key, key)



lang = LanguageManager()#globale Instanz


#in der Sprachauswahl wird mit lang.load(self.selected) die ausgewählt Sprache geladen self.selected ist die jeweilige Sprache
#self.language ist die jeweilige Sprache Englisch beispielsweise
#self.data ist alles was in der jeweiligen Sprach.json enthalten ist
#hei0t wir laden den Pfad mit der jeweiligen Sprache laden dann den Inhalt der json in self.data 
#über t können wir dann bestimmte Wörter aus dem Wörterbuch laden "weiter" : "continue" zum Beispiel
#der linke Wert in der json ist wie der Wert in den Auswahlen verankert ist der rechte Wert ist die Entsprechnung der jeweiligen Sprache
#lang ist eine globale Instanz weshalb in allen Auswahlen das selbe Wörterbuch angewendet wird
