# NEFFY3-Programm
Enthält alle Dateien, die für die Installation und Ausführung des Neffy3 Programms benötigt werden.

Die Übersichten erklären, welche Module derzeit vorhanden sind und wie sie miteinander verbunden sind.

Systemübersicht komplett
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

<img width="4771" height="6769" alt="Systemübersicht" src="https://github.com/user-attachments/assets/957fe589-c3ec-4cb6-907b-34c262cbeeea" />

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------


NEFFY Standard:
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

<img width="3846" height="1809" alt="SystemStandard" src="https://github.com/user-attachments/assets/e2629fd2-5172-49df-836e-6e1da52c8f4b" />


NEFFY Atemerkennung:
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

<img width="3846" height="1862" alt="SystemAtemerkennung" src="https://github.com/user-attachments/assets/95251486-68be-4d62-b48d-cb3c3a9eaa9d" />

NEFFY Profile:
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

<img width="2736" height="3431" alt="SystemProfile" src="https://github.com/user-attachments/assets/4ea21897-3a01-4503-9fa1-4bc009d98d9a" />


Nützliche Werkzeuge bei der Enwicklung
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
RaspberryPi (Download Imager): https://www.raspberrypi.com/
#
RealVNC Viewer (Remote über Laptop auf Raspberry Pi Arbeiten): https://www.realvnc.com/en/connect/download/viewer/?lai_sr=0-4&lai_sl=l
#
WinSCP (Transfer größerer Dateien): https://winscp.net/eng/download.php
#
Audacity (Soundeditor): https://www.audacityteam.org/download/
#
Krita (Animationen/Icons): https://krita.org/de/
#
Hilfreiche Werkzeuge für den Bericht:
#
draw.io (Erstellen Diagramme): https://www.drawio.com/
#
latex (Erstellen Bericht): https://www.latex-project.org/

Setup der Systeme 
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
(steht auch in ```READMEFIRST.txt``` in den einzelnen Systemordnern)
#
1: Im Terminal in den Projektordner des jeweiligen Systems navigieren.

<img width="1746" height="898" alt="setup3" src="https://github.com/user-attachments/assets/1ad22130-523d-4e7e-8bbc-d1fc9243b158" />

2: Die Befehle für die Installation auf dem jeweiligen Betriebssystem aus der ```READMEFIRST.txt``` Datei kopieren und im Terminal ausführen.

<img width="1748" height="862" alt="setup5" src="https://github.com/user-attachments/assets/f67834a4-0c50-4a64-82dd-2707ed6dce70" />

3: ```venv``` Ordner wird im Projektordner des jeweiligen Projektordners erstellt.
#
4: Der Befehl ```python src/main.py``` startet das Programm (venv muss aktiviert sein)

Installation des Programms in Windows
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Python muss vorhanden sein. 
#
In den jeweiligen Projektordner des Systems welches man Installieren möchte wechseln: 

```
NEFFY STANDARD: NEFFY
----------------------------------------
NEFFY ATEMERKENNUNG: Atemerkennung/NEFFY
----------------------------------------
NEFFY PROFILE: NEFFYPROFILES
```

#
Mit ```cd``` kann man im Terminal durch die Ordner navigieren. 
Installation wird identisch auch in ```READMEFIRST.txt``` in jedem Projektordner erklärt.

#
1:
Erstelle venv im Projektordner: ```py -m venv venv```
#
2:
Aktiviere venv in PowerShell: ```.\venv\Scripts\Activate.ps1```
Aktiviere venv in CMD: ```venv\Scripts\activate.bat```
#
3:
Installiere requirements: ```python -m pip install -r requirements.txt```
#
4:
Starte Programm: ```python src/main.py```
Verlasse Programm: ```Escape``` in Auswahl der Übung drücken
#
5:
Deaktiviere venv: ```deactivate```
#

6: In die Datei ```MotorC.py``` gehen und gegebenenfalls den Portnamen anpassen. ```COM3``` zum Beispiel in Windows und ```/dev/serial0``` auf dem Raspberry Pi. Wenn der falsche Port gesetzt wird, funktioniert das gesamte System nicht, selbst wenn kein Motor oder Board angeschlossen ist. 
 
<img width="793" height="52" alt="Portname" src="https://github.com/user-attachments/assets/1e6ac2f8-6ed1-4304-b4c0-a575c1c6032f" />


# 
Kompletter Befehl zur Ausführung in CMD:
```
py -m venv venv
venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```

#
Kompletter Befehl zur Ausführung in Powershell: 
```
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Installation des Programms auf einem Raspberry Pi
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Python muss vorhanden sein. 
#
In den jeweiligen Projektordner des Systems welches man Installieren möchte wechseln: 

```
NEFFY STANDARD: NEFFY
----------------------------------------
NEFFY ATEMERKENNUNG: Atemerkennung/NEFFY
----------------------------------------
NEFFY PROFILE: NEFFYPROFILES
```

#

Mit ```cd``` kann man im Terminal durch die Ordner navigieren. 
Installation wird identisch auch in ```READMEFIRST.txt``` in jedem Projektordner erklärt.
#
1:
Erstelle venv im Projektordner: ```python -m venv venv```
#
2:
Aktiviere venv: ```source venv/bin/activate```
#
3:
Installiere requirements: ```python -m pip install -r requirements.txt```
#
4:
Starte Programm: ```python src/main.py```
Verlasse Programm: ```Escape``` in Auswahl der Übung drücken
#
5:
Deaktiviere venv: ```deactivate```
#
6: In die Datei ```MotorC.py``` gehen und gegebenenfalls den Portnamen anpassen. ```COM3``` zum Beispiel in Windows und ```/dev/serial0``` auf dem Raspberry Pi. Wenn der falsche Port gesetzt wird, funktioniert das gesamte System nicht, selbst wenn kein Motor oder Board angeschlossen ist. 

<img width="793" height="52" alt="Portname" src="https://github.com/user-attachments/assets/1e6ac2f8-6ed1-4304-b4c0-a575c1c6032f" />

#
Alle drei Zeilen für vollständige Installation zum kopieren:
```
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```
Beispiel Installation Raspberry Pi
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------


https://github.com/user-attachments/assets/cc4148de-f3cc-40a1-a074-8410ae8a1b80



Service erstellen 
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Auch beschrieben in ```ServiceSetupCommands.txt```.

Der Service führt eine Datei bei dem Start des Raspberry Pis aus. Hier ist das die ```Start.py``` Datei, damit sofort das jeweilige Programm ausgewählt werden kann.


Setup:
#
1:
Erstelle den Service: ```sudo nano /etc/systemd/system/start.service```
#

2:
Kopiere den Inhalt in das Terminal Feld. Je nachdem, in welchem Ordner das Programm abgelegt ist, muss möglicherweise der Pfad angepasst werden.
#
```
[Unit]
Description=NEFFY Start Script
Wants=sound.target
After=sound.target

[Service]
Type=idle
Environment=XDG_RUNTIME_DIR=/run/user/1000
Environment=SDL_AUDIODRIVER=pulse
SupplementaryGroups=audio
ExecStartPre=/bin/sleep 15
ExecStart=/usr/bin/python3 /home/neffy3/Neffy3/Start.py
WorkingDirectory=/home/neffy3/Neffy3
User=neffy3
Restart=always
RestartSec=5
StartLimitIntervalSec=0


[Install]
WantedBy=multi-user.target

```


#
3: 
Wenn man über ```Exit die Startauswahl``` verlässt, wird der Service temporär gestoppt, damit Änderungen vorgenommen werden können und der Service nicht sofort wieder ausgeführt wird.
#
Zusätzliche Befehle:
#
Stop Service :  ```sudo systemctl stop start.service```

#

Disable Service: ```sudo systemctl disable start.service```
#
Restart Service: ```sudo systemctl restart start.service```
#
Reload Service: ```sudo systemctl daemon-reload```
#
Status prüfen: ```sudo systemctl status start.service```
#
Logs ansehen: ```sudo journalctl -u start.service -b```


Neue Übungen hinzufügen
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Dateien, die geöffnet werden müssen: ```logic.py```, ```MotorFunktionen.py```, ```main.py```.
#

1. Übung in ```MotorFunktionen.py``` definieren: also die Werte für Hochfahren, Herunterfahren, Pausen und in welcher Zeit die Position erreicht werden soll. Man muss darauf achten, dass die Werte für den Motor auch anfahrbar sind. Bei NEFFY 3 sind das ungefähr 0–20 mm. Die Angabe ist in mm. Es gibt drei verfügbare Muster: body_head, body_head_pause und execute_sequence. Diese Muster sind in ```Steuerung.py``` definiert. body_head ist für Übungen ohne Pausen, body_head_pause für Übungen mit Pausen (oben/unten möglich) und execute_sequence ist für Übungen gedacht, die beispielsweise direkt zwei Phasen des Hochfahrens haben (Hochfahren, Hochfahren, Herunterfahren). So kann man beliebige Übungen konstruieren. Man kann einfach eine der bereits bestehenden Übungen kopieren und nach Belieben anpassen.

<img width="1552" height="609" alt="neueÜbung1" src="https://github.com/user-attachments/assets/8248a307-d826-4c5b-810b-c2ae76f264b4" />

#
2. Übung in ```logic.py``` hinzufügen. Selbe Idee: Man kopiert eine der bestehenden Übungen und passt die Anordnung der Clips gegebenenfalls an. Man kann ein anderes Audio abspielen lassen. Die Audios werden geloopt. Ich würde empfehlen, keine großen Audiodateien zu wählen, da diese länger zum Laden benötigen.
In der letzten Zeile ```run_exercise(player, exercises.example, duration)``` muss statt ```example``` die jeweilige in ```MotorFunktionen.py``` definierte Übung referenziert werden.

<img width="484" height="619" alt="logic" src="https://github.com/user-attachments/assets/3f23792c-b99b-47a1-9f60-b3ca6f92ae44" />

#
3. In ```main.py``` muss in Zeile 392 (NEFFY Standard) die neue Übung zugewiesen werden. Wenn man die ```ui.py``` (Übungsauswahl) nicht erweitern möchte, muss man eine der fünf Auswahlen (Übungen) durch die neue Übung ersetzen. Dafür muss man nur die entsprechende handle Funktion ersetzen, wie in diesem Beispiel gezeigt. Man muss darauf achten, dass die Übung aus ```logic.py``` auch in den Imports auftaucht.

<img width="622" height="156" alt="Übungenmain" src="https://github.com/user-attachments/assets/58c384dc-2639-4b9b-8f2d-5c30efebd161" />

Danach müssen nur noch die JSON Dateien in den unterschiedlichen Sprachen angepasst werden, so das die Erklärung der Übung und der Übungsname korrekt gezeichnet wird und nicht der alte Übungsname verbleibt.


Neue Sprachen hinzufügen
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

1. Neue JSON mit dem Namen der jeweiligen Sprache erstellen und im languages Ordner ablegen. Der Name der Datei wird angezeigt, wenn sich das Programm in der language_ui befindet. Der Name sollte deshalb in der jeweiligen Sprache festgelegt sein, also „Deutsch", „english", „español" etc.

<img width="1059" height="139" alt="JSONName" src="https://github.com/user-attachments/assets/3fa14667-5cd4-48e9-a784-491aa12544ae" />

#
2: Den Inhalt einer der bestehenden Dateien kopieren und die rechte Seite in der jeweiligen Sprache übersetzen

<img width="550" height="538" alt="JSON" src="https://github.com/user-attachments/assets/488abd5e-05d1-4a32-a96e-389c7d1511b3" />

#
3: Im Ordner flags der im Ordner ```assets``` liegt, die entsprechende Flagge unter dem selben Namen ablegen. Die Flagge wird der entsprechenden Sprache automatisch über den Namen zugeordnet. 

<img width="645" height="154" alt="flags" src="https://github.com/user-attachments/assets/1d245253-5039-47bf-9ebd-cdb9b709547f" />

Sprache ist in der ```language_ui``` zur Auswahl verfügbar und wird sofort korrekt in allen Anwendungen gezeichnet. 



Audio für neue Sprache hinzufügen:
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

1: Neuen Ordner in ```assets_mp3/ui``` mit dem jeweiligen Namen der Sprache erstellen (muss identisch zu dem Filenamen der JSON und Flagge sein).

<img width="861" height="162" alt="languageeordner" src="https://github.com/user-attachments/assets/1edd4917-2060-4074-99d7-eb1b21762690" />
#

2: Audios in der neuen Sprache erstellen. Die Dateinamen der Audios müssen übereinstimmen, mit den Keys die in den Auswahlen stehen. 

<img width="697" height="334" alt="Audio" src="https://github.com/user-attachments/assets/e1395b9f-04f1-4f9c-95ac-1c74c9ab4428" />

#
3: Wenn jetzt Sprache in ```language_ui``` entschieden wird, wird der Pfad zu diesem Audioordner gesetzt und die entsprechenden Audios werden in den Auswahlen korrekt abgespielt. Wenn man sich die Ordner Deutsch und english einmal anhört, sollte man die Idee nachvollziehen können.


Design Anpassen
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Das Design kann mit einer Datei für das gesamte System angepasst werden.

<img width="5184" height="958" alt="designsystem" src="https://github.com/user-attachments/assets/6c690332-c72e-47b8-9a45-3bbdc60be1f8" />



1: Erstelle eine JSON im Ordner config. Kopiere den Inhalt einer der bereits vorhandenen Dateien und passe die Werte nach belieben an.

<img width="1041" height="255" alt="designjson" src="https://github.com/user-attachments/assets/149106e7-663a-4ed4-aecf-2933d7a76825" />

2: Ändere in ```design_system.py``` in Zeile 23 (NEFFY Standard) den Namen zur neuen Konfigurationsdatei. Speichern, und bei dem nächsten Programmstart werden die Konfigurationen sofort über das gesamte System hinweg angewendet.


Email Sender
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Der Email Sender muss mit den notwendigen Informationen ergänzt werden. Aus offensichtlichen Gründen sind diese Informationen hier nicht vorhanden. Für das Passwort kann nicht das reguläre Passwort verwendet werden, sondern es muss ein APP-Passwort ausgewählt oder erstellt werden. Andernfalls funktioniert das Senden der Email nicht. App Passwörter können nur mit verifizierten Accounts erstellt werden. Das APP-Passwort sollte nicht geteilt werden und nicht in Dokumentationen des Programms auftauchen.


<img width="789" height="202" alt="Emailsender" src="https://github.com/user-attachments/assets/afe5d22b-5a7d-4418-a221-4a3a3f414db7" />


Es kann sein, das sich einmal auf Seite des Raspberry Pis in die Email (die Sender und Recipient darstellt) eingeloggt werden muss, damit Google das Senden zulässt.


Passwort Start
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Das Passwort in ```Start.py``` das zum Verlassen der Startauswahl benötigt wird, muss gesetzt werden. Initial ist es auf ```1-2-3-4``` gesetzt. Wenn ```Start.py``` auch auf Windows verwendet werden soll, müssen möglicherweise der Portname und die Aktivierungsdaten angepasst werden.

<img width="441" height="111" alt="PW" src="https://github.com/user-attachments/assets/62f382d5-2973-4726-a145-db83cc9d8303" />


Abbildungen der Auswahlen
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Start Auswahl:

<img width="1738" height="966" alt="Start" src="https://github.com/user-attachments/assets/fce11c72-aecd-476b-959f-775fe9757ae0" />

#

System: NEFFY Standard
#

Schlafmodus: 

<img width="1738" height="960" alt="Schlafmodus" src="https://github.com/user-attachments/assets/66b5ebd7-68c4-4902-9568-6e52d6e92c9f" />

#

Intro:

<img width="1734" height="964" alt="setup7" src="https://github.com/user-attachments/assets/9974f6cc-4167-488b-a650-86967f884ba0" />

#

Sprachauswahl:

<img width="1738" height="966" alt="language" src="https://github.com/user-attachments/assets/53193062-263f-4f9b-acf2-43593fc44da7" />


#

Lautstärkeauswahl:

<img width="1734" height="964" alt="Volume" src="https://github.com/user-attachments/assets/89f7dd26-36b2-4f7b-ab69-a68857ca702a" />

#
Evaluation Stresslevel:

<img width="1736" height="966" alt="Evaluation" src="https://github.com/user-attachments/assets/a036f31d-2c31-44d8-a3ef-946e3731f1ec" />


#
Übungsauswahl:


<img width="1738" height="968" alt="Übungsauswahl" src="https://github.com/user-attachments/assets/5849df2d-b34e-4d67-83f4-51de03d63acf" />

#

Dauer:

<img width="1736" height="966" alt="duration" src="https://github.com/user-attachments/assets/2e72266c-5584-43c3-b5bf-90a6419df3d1" />

#

Erklärung Übungsablauf: 

<img width="1734" height="966" alt="Erklärung" src="https://github.com/user-attachments/assets/91bbbe24-2dc5-4704-b6ca-4be0da2a41ad" />

#
Übung startet



#

System: NEFFY Profile

#

Hauptmenü:

<img width="1742" height="972" alt="main_menu" src="https://github.com/user-attachments/assets/38473f82-fee9-49e6-b075-8b8c0484b807" />

#

Profil Erstellung: 

<img width="1738" height="962" alt="Profile" src="https://github.com/user-attachments/assets/043a3103-871d-4907-b6e9-c9605388dc64" />

#

Einstellungen: 

<img width="1740" height="966" alt="settings" src="https://github.com/user-attachments/assets/e0e49ed7-1a7a-40cb-aecc-ebafbe861b6c" />



System: NEFFY Atemerkennung

Hinweis zur Atemerkennung: 

<img width="1738" height="964" alt="Atemerkennung" src="https://github.com/user-attachments/assets/f3d5435b-2a6c-4d14-82f2-d973fb3e1f0f" />


Beispiel ganze Übung: NEFFY Standard 
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

https://github.com/user-attachments/assets/ffb3ea81-8e0b-451f-aadb-58c38fe90987
