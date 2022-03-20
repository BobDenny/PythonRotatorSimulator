ASCOM Alpaca Rotator Simulator in Python
----------------------------------------

Version: 0.9 (December 2021)
By: Bob Denny <rdenny@dc3.com>

This ASCOM Alpaca Standard Rotator simulator will run on Python 3.7 or later (and probably some earlier Python 3s, I won't comment on Python 2.x)

Installation and Test
---------------------

(1) PRE-REQUISITES - The file requirements.txt lists the required Python packages and their versions.

So on the target device (raspberry Pi), use PIP3 to install the packages listed in requirements.txt. Your toolset may be able to create a virtual environment from requirements.txt and if so that's excellent.

* Flask
* Flask-RESTX
* WTForms (plural)
* Flask-WTF
* gevent (this is huge, and is for the production web server WSGIServer)

After doing these, look and see what else you might need to complete the packages in requirements.txt. 

(2) Create the Python Rotator Simulator application in a folder: 

    (a) Create a folder Rotator somewhere like your ~ or Desktop directory
    (b) Copy the contents of Rotator folder inside the ZIP file into that folder. There  will be 'static' and 'templates' subfolders.

(3) Edit Rotator/app.py. Scroll to "Network Connection" area (about line 76) and change the IP address 192.168.0.40 to whatever IP address your lightweight device (Raspberry Pi or whatever) is on. Maybe you'll want to change the port 5555 to something else. The assumption is that you are going to run the simator Pi on the same LAN as your windows system with the Conform tool and a Rotator client such as Software Bisque TheSky's FOVI rotation feature.

(5) Now start the simulator:

cd wherever/Rotator
python3 app.py

This should result in something like (ignore the warning for now)

	* Simulator accessible via Alpaca at 192.168.0.40:5555
	  For management home page http://192.168.0.40:5555/
	* Serving Flask app "app" (lazy loading)
	* Environment: production
	  WARNING: This is a development server. Do not use it in a production deploymet.
	  Use a production WSGI server instead.
	* Debug mode: off 

 (6) If you get this far without errors (missing Python dependencies, old versions of Python 3, etc.) you are ready to play with the simulator. Open a web browser on a system that is on the same LAN, and navigate to the Alpaca Rotator Simulator home page at
 
     http://192.168.0.40:5555/
	 
Along the top you should see links to the Server Setup and Device (Rotator) Setup pages. There are four Rotators implemented as shipped but you can edit the sources to change this. Using the dropdown list and the Rotator Setup link you can change the characteristics of each of the four rotators. In the body of the home page are links to see the Swagger self-documentation/testing user interfaces. Exercise the simulator using the Rotator API Swagger UI as well as the Management API. Don't forget that you have to set Connected to True on the Rotator before doing anything else ha ha.

At this point you should be able to use the Windows Conform tool to validate the correctness of the simulator. In Conform, set it for Rotator conformation then in the ASCOM Chooser enable ALpaca if needed and if you are on the same LAN segment recommended), let it discover this Rotator Simulator, then select it in the device list as the chosen device. Click Properties as usual, and if you didn't use discovery enter the IP address and port of the Pi. Close both windows. Now try to do a Conform check. 

Feel free to connect to this from TheSky X on Windows and play with TheSky's Field of View Indicator. First, pick a FOVI and make certain (edit FOVI) that there is no East/West offset on the angle and that it is for the Center of the Chart. The setup is tricky as the rotator is part of the Camera setup. Set TheSky's Rotator for ASCOM Rotator. Do the ASCOM device setup in TheSky to get the ASCOM Rotator chooser again. making sure that it is still connected to the rotator simulator on the Pi. Connect the Rotator in TheSky and if all went well you'll see TheSky pollng the Rotator at a high rate. Play with it now. Use the Swagger API pages on the simulator as a way to move the rotator (moveabsolute) and watch it turn in TheSky, etc. NO MODIFICATIONS to TheSky needed!!

KEEP IN MIND THAT THESE TESTS USE WINDOWS ONLY BECAUSE THERE ARE NOT YET ANY ALPACA ROTATOR CLIENTS so you're using the Platform 6.5's automatic Alpaca Dynamic Driver feature to reach out beyond Windows to your Linux device. ALPACA AND THE ROTATOR SIMULATOR ARE NOT DEPENDENT ON WINDOWS!!!

Working with this in Visual Studio Code
---------------------------------------
Right-click the Rotator folder and select Visual Studio Code to open the project. Start with the Python 3.7 or later master environment. I suggest you create a virtual environment using Requirements.txt 

$ python3 -m venv .venv
--  exit and restart terminal and see that is using .venv --
$ pip install -r requirements.txt

The main program (as usual) is app.py. Run it from the Python command or the VSCode debugger. Try testing with the new ConformU or from the old Windows Conform via an Alpaca dynamic driver.. You should get a valid test. 
 
Working with this in Visual Studio 2019
---------------------------------------
Included with this package is a Visual Studio 2019  Solution file RotatorDemo.sln. It assumes that the rest of the files are in a subfolder Rotator below the solution file and requirements.txt. Assuming you already have installed Python 3 support, requirements.txt is enough to have VS2019 build you a Python3 virtual environment under which you can not only run, but also develop, test, and debug with the Python visual debugger. You can add an environment (VS command in the Python Environments pane) and use Requirements.txt as the list of packages you need. I hope you're somewhat familiar with this.

The objective, though, is to have this Alpaca Rotator run on a Raspberry Pi or other lightweight platform that supports Python 3.6 or later. ALWAYS USE PYTHON3 and PIP3 unless you're SURE your system won't take you to Python 2.x with python or pip.

(1) Make sure app.py is set as the startup project.
(2) In app.py change the HOST to 127.0.0.1.
(3) In the Start selector of VS2019, select Web Server and in the sub-menu choose the browser of your choice. I use Chrome or Firefox. 
(4) Start the simulator using the Web Server (xxx) button and the browser will open to the simulator's home page.

PLEASE NOTE
-----------
I'm no Linux expert, no Python expert, and no Flask expert. This whole project was one big "just in time learning" exercise. What I know is that it is easy to get the Python packages into a screwed up state, mix up Python 2 vs 3, and other issues. If you get errors "module not found" on the Raspberry Pi after starting app.py with pip3, you can be sure you didn't install some or all module(s) with the pip3  (as opposed to pip) command. If your Pi installation can support "virtual environments" then that's good. Use requirements.txt as a guide. I had no problems at all, but I have run into problems in the past on other projects with package versions and dependencies. Your chances of success are very high though. What I cannot do is help you solve problems with the Python stuff, nor Linux things like directory permissions, paths, strange ENVVAR side-effects, etc. Under the right conditions this rotator simulator will work. 

  Bob Denny - 23-Jan-2021
  
