Windows
requires Python to be installed
virtual enviroment needs to be created in the project folder for "NEFFY STANDARD" this is "NEFFY"
You can move to the folder by using "cd" and then the path to the folder so "cd Neffy3\NEFFY" as an example
"cd .." moves you back one folder
Usually the folder that contains the "READMEFIRST.txt" file will be the folderpath in which the following
commands need to be executed.

Step 1:
create a virtual enviroment: py -m venv venv

Step 2:
activate the virtual enviroment PowerShell: .\venv\Scripts\Activate.ps1
activate the virtual enviroment CMD: venv\Scripts\activate.bat

Step 3:
install requirements: python -m pip install -r requirements.txt

Step 4:
start programm: python src/main.py
leave programm: use the "Escape" key in the exercise choice

Step 5:
deactivate the virtual enviroment: deactivate


Full command to create the initial venv in CMD if already in the project folder:
py -m venv venv
venv\Scripts\activate.bat
python -m pip install -r requirements.txt

Full command to create the initial venv in PowerShell:
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt


#
#
#
#
#


Raspberry Pi Setup should work identically on Linux
requires Python to be installed often preinstalled in linux distributions
virtual enviroment needs to be created in the project folder for "NEFFY STANDARD" this is "NEFFY"
You can move to the folder by using "cd" and then the path to the folder so "cd Neffy3/NEFFY" as an example
"cd .." moves you back one folder
Usually the folder that contains the "READMEFIRST.txt" file will be the folderpath in which the following
commands need to be executed.

Step 1:
creates a virtual enviroment: python -m venv venv

Step 2:
activate the virtual enviroment: source venv/bin/activate

Step 3:
install requirements: python -m pip install -r requirements.txt

Step 4:
start programm: python src/main.py
leave programm: use the "Escape" key in the exercise choice

Step 5:
deactive the virtual enviroment: deactivate



Full command to create the initial venv in the Terminal if already in the project folder:
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt


#
#
#
#
#


Additional information
Depending on if you are using Windows or are trying to install the programm on another Raspberry Pi you will need to edit the line:
     def __init__(self, port="COM3", baudrate=115200): #"/dev/serial0" 
This line can be found in file "MotorC" in line 22. 
In windows I used: port="COM3"
In the Raspberry Pi I used: port="/dev/serial0" 



On Windows you will not be able to use the "Start.py" to access the different systems.
The "Start.py" file has a defined command that starts the different system in their virtual enviroment using: source venv/bin/activate
Since this command doesnt work in Windows you can either edit the Start file or access the Systems through their respective folders.
Before you can use the Start file on the Raspberry Pi every System needs their virtual enviroment created and requirements installed.



The Service needs to be added manually. I would recommend only doing that on the Raspberry Pi. Information regarding the Service and the setup can be found in the 
"InhaltServicedatei.txt".



The Email Sender doesnt contain the information: image_path, sender_email, sender_password, recipient_email
image_path you will need to define dependent on where the analytics folder containing the "statistics.png" is located
In the Raspberry Pi that could be a path like this: "/home/neffy3/Neffy3/NEFFY/analytics/statistics.png"

sender_email = the email used for sending the png

sender_password: App Password can be found in the verified google Account under App Password for the sender_email

recipient_email: where the statistic.png is send 
in the Pi recipient and sender are the same accessing the email will allow to download the file  
To make the email sender usable you may need to access the google account from the Raspberry Pi once since Google has very strict security measurements

DO NOT SHARE OR UPLOAD THE SENDER PASSWORD there shouldnt be any information beyond the statistics images but the App Password is sensitiv information that can be used
to access the Google Account. Keep it out of Git-Repositorys and any documents. 



