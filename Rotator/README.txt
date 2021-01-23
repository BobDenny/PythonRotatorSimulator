ASCOM Alpaca Rotator Simulator in Python
----------------------------------------

Version: 0.8 (23-Jan-2021)
By: Bob Denny <rdenny@dc3.com>

This ASCOM Alpaca Standard Rotator simulator will run on Python 3.5 or later (and probably some earlier Python 3s and probably on Python 2.7 as well). 

Installation and Test
---------------------

(1) PRE-REQUISITES - The file requirements.txt lists the required Python packages and their versions. If you are on Windows and are using Visual Studio 2019 (or 2017) with Python support, requirements.txt is enough to have VS2019 build you a Python3 virtual environment under which you can not only run, but also develop, test, and debug with the Python visual debugger. The objective, though, is to have this Alpaca Rotator run on a Raspberry Pi or other lightweight platform that supports Python 3 or, if you must, try Python 2.7. ON THE PI USE PIP3 IF YOU ARE GOING TO RUN PYTHON3 (recommended). 

So on the target device, use PIP3 to install the packages listed in requirements.txt. Some of them are dependencies so you may only need to install

* Flask
* Flask-RESTX
* WTForms (plural)
* Flask-WTF
* gevent (this is huge, and is for the production web server WSGIServer)

After doing these, look and see what else you might need to complete the packages in requirements.txt. Note that the file requirements.txt is not needed in production. It can be  used in Visual Studio 2019 with Python to create a nice virtual environment with the required packages.

(2) Create the Python application in a folder: Create a folder (e.g.) Rotator. Then copy the contents of the ZIP file (except requirements.txt and README.txt) into that folder. There  will be 'static' and 'templates' subfolders.

(3) Edit app.py. Scroll to "Network Connection" area (about line 70) and change the IP address 192.168.0.40 to whatever IP address your lightweight device (Raspberry Pi or whatever) is on. Maybe you'll want to change the port 5555 to something else. 

(4) If needed open the firewall on your system to accept inbound connections on port 5555

(5) Now start the simulator:

cd wherever/Rotator
python3 app.py

This should result in something like

 * Running on Raspberry Pi Linux 192.168.0.40 
 * Serving Flask app "app" (lazy loading)
 * Environment: production
   WARNING: Do not use the development server in a production environment.
   Use a production WSGI server instead.
 * Debug mode: off 
 
 (6) If you get this far without errors (missing Python dependencies, old versions of Python 3, etc.) you are ready to play with the simulator. Open a web browser and navigate to the Alpaca Rotator Simulator home page at
 
     http://192.168.0.40:5555/
	 
You should see links to see the Swagger self-documentation/testing user interfaces. Exercise the simulator using the Rotator API Swagger UI as well as the Management API. Don't forget that you have to set Connected to True on the Rotator before doing anything else ha ha.

At this point you should be able to use the Windows Conform tool to validate the correctness of the simulator. In Conform, set it for Rotator conformation then in the ASCOM Chooser select ASCOM Remote 1. Click Properties as usual, and enter the IP address and port of the Pi. and close both windows. Now try to do a Conform check. 

Feel free to connect to this from TheSky X on Windows and play with TheSky's Field of View Indicator. Set TheSky's Rotator for ASCOM Rotator. Do the ASCOM device setup in TheSky to get the ASCOM Rotator chooser again, and again fill out the IP and Port. Connect in TheSky and if all went well you'll see TheSky pollng the Rotator at a high rate. Play with it now.

KEEP IN MIND THAT THESE TESTS USE WINDOWS ONLY BECAUSE THERE ARE NOT YET ANY ALPACA ROTATOR CLIENTS so you're using ASCOM Remote to reach out beyond Windows to your Linux device. ALPACA AND THE ROTATOR SIMULATOR ARE NOT DEPENDENT ON WINDOWS!!!

SETUP FORM
----------
If you browse to the instance endpoint http://192.168.0.40:5555/api/v1/rotator/0/setup you'll see a crude sample Setup form that will allow you to set the Reverse, Step Size, and Steps Per Second. These settings are not persistent, so they will revert to the default settings each time the simulator is started. However you can change them once it is running. This form uses WTForms and Flask-WTF. By using those facilities, the form is fully protected for Cross-Site Request Forgery (CSRF) see https://www.owasp.org/index.php/Cross-Site_Request_Forgery_(CSRF). The purpose of my including this was to show how easy it is to serve a setup form with Model-View-Controller (MVC) architecture. For simplicity I didn't include any CSS but I did assign class names to the elements. Feel free to style and extend it.

PLEASE NOTE
-----------
I'm no Linux expert, no Python expert, and no Flask expert. This whole project was one big "just in time learning" exercise. What I know is that it is easy to get the Python packages into a screwed up state, mix up Python 2 vs 3, and other issues. If you get errors "module not found" on the Raspberry Pi after starting app.py with pip3, you can be sure you didn't install some or all module(s) with the pip3 command. If your installation can support "virtual environments" then that's good. Use requirements.txt as a guide. I had no problems at all, but I have run into problems in the past on other projects with package versions and dependencies. Your chances of success are very high though. What I cannot do is help you solve problems with the Python stuff, nor Linux things like directory permissions, paths, strange ENVVAR side-effects, etc. Under the right conditions this rotator simulator will work. 

  Bob Denny - 23-Jan-2021
  
