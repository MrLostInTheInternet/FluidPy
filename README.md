# FluidPy
A script that helps Students like me to use and create their own FluidSim circuit

                
                   ________                 _               _______         __     
                  /   ____/ __     __   __ |_|   _____     /  __   \ __    / /     
                 /  /___   / /    / /  / / __   / ___  \  /  / /   | \ \  / /      
                /  ____/  / /    / /  / / / /  / /   \  | /  /_/  |   \ \/ /       
               /  /      / /    / /  / / / /  / /   |  |  /  ____/     \  /        
              /  /      / /__  / /__/ / / /  / /___/  /  /  /          / /         
             /__/      /____/ /______/ /_/  /_______/   /__/          /_/   []     
                
                      Developed by MrLostInTheInternet
                
Welcome to FluidPy, an automation tool to analyze the creation of a FluidSim circuit, 
even without the actual Software Festo FluidSim.

FluidPy will create 3 other files to help you create your FluidSim circuit: "diagram's fases",
"plc.txt" and "sequence.txt".

This 3 files contain the Diagram's Fases which will help to
undestand the motions of the desired actuators in the sequence, the Sequence that you submitted
and the PLC Structured-Text code of the sequence.

The program can be used as GUI or in terminal mode.

The PLC ST code will be saved in a file apart called "plc.txt", it can be copied and
pasted onto any ST software like CODESYS and others.

The code will be improved and still updating.

REQUIREMENTS

Install python and pip on your pc:

-Linux:

sudo apt install python3 python3-pip

-Windows:

download and install python from the website https://www.python.org

add it to your PATH

Install PySimpleGUI, matplotlib, tk, numpy:

pip install PySimpleGUI
pip install matplotlib
pip install tk
pip install numpy

HOW TO USE IT

Git clone the files in a folder:

git clone https://github.com/MrLostInTheInternet/FluidPy.git

cd FluidPy

cd Project Fluidsim

TERMINAL MODE

python fluid.py --help

GUI MODE

python main.py




~MrLostInTheInternet

