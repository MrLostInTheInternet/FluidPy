#!/usr/bin/env python3

import argparse
from xml.etree.ElementInclude import include
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import math
import numpy as np
import sys
import string
import textwrap
import time
from matplotlib.widgets import Slider
from matplotlib.backends.backend_qt5agg  import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5 import QtWidgets
from textwrap import fill, wrap  
from queue import Empty



#---------------------------------------------------------------------------
#function blocks to individue the blocks and create the groups
def create_groups(group, l_sw):
    l = group.count('//')
    groups = [[] for _ in range(l+1)]
    limit_switches = [[] for _ in range(l+1)]
    i = 0
    j = 0
    finish = False
    while not finish:
        if '//' not in group[i]:
            groups[j].append(group[i])
            limit_switches[j].append(l_sw[i])
            i += 1
        else:
            j += 1
            i += 1
        if i == len(group):
            finish = True
    compatible = False
    for z in range(len(groups[-1])):
        if groups[-1][z] not in groups[0]:
            compatible = True
        else:
            compatible = False
            print('Not compatible.')
            break
    if compatible == True:
        arr1 = ''.join(groups[-1])
        arr2 = ''.join(groups[0])
        arr = arr1 + arr2
        arr = wrap(arr, 2)
        groups[0] = [arr]
        del groups[-1]

    return groups, limit_switches

def find_blocks(sequence, l_s):
    seen = []
    group = ''
    l_sw = ''
    finish = False
    i = 0
    while not finish:
        stroke = sequence[i][0]
        if stroke not in seen:
            seen.append(stroke)
            group += sequence[i]
            l_sw += l_s[i]
            i += 1
        else:
            group += '//'
            l_sw += '//'
            seen.clear()
        if i == len(sequence):
            finish = True
    group = wrap(group, 2)
    l_sw = wrap(l_sw, 2)
    return create_groups(group, l_sw)
        
#ask to insert the correct stroke if the check returns false
def insert_correct_stroke():
    stroke = input("Error. Insert the correct stroke: ")
    return stroke

#check if there are pistons in loop 
def check_loop(s):
    stroke_signed = []
    for i in range(len(s)):
        stroke = s[i]
        rep = s.count(stroke)
        if stroke not in stroke_signed:    
            if rep > 2:
                stroke_signed.append(stroke)
                loop = True
                break
            else:
                loop = False
        else:
            loop = True
            break
    return loop

#number of pistons in the sequence
def limit(sequence):
    s = []
    sequence = [words.replace("-", "") for words in sequence]
    sequence = [words.replace("+", "") for words in sequence]
    limit = len(set(sequence))
    for stroke in sequence:
        if stroke not in s:
            s.append(stroke)
    index_sequence = sequence
    return limit, s, index_sequence

#diagram's fases 
def diagrams(sequence, limit_switches):
    s = []
    l, s, index_sequence= limit(sequence)
    cell_text = [limit_switches]
    columns= sequence
    

    fig, axs = plt.subplots(nrows = l, ncols = 1)
    plt.get_current_fig_manager().set_window_title("Diagram's fases")
    #plt.rcParams["figure.figsize"] = [20, 20]
    #plt.rcParams["figure.autolayout"] = True
    colors = plt.rcParams["axes.prop_cycle"]()

    x = list(range(len(sequence)+1))
    y = [[] for _ in range(l)]

    for j in range(len(s)):

        stroke = s[j]
        index = index_sequence.index(stroke)
        if sequence[index][1] == '+':
            y[j].append(0)
            v = 0
        else:
            y[j].append(0.99)
            v = 0.99
        for i in range(len(sequence)):
            if stroke == sequence[i][0]:
                if sequence[i][1] == '+':
                    y[j].append(0.99)
                    v = 0.99
                else:
                    y[j].append(0)
                    v = 0
            else:
                y[j].append(v)
    for i, ax in enumerate(axs.flat):
        c = next(colors)["color"]
        ax.set_ylabel(str(s[i]), rotation = 0, color = c)
        ax.set_ylim([0, 1.0])
        ax.set_yticks(range(0,2,1))
        ax.set_xlim([0, len(sequence)])
        ax.sharex(ax)
        ax.plot(x,y[i], 'o-', color = c)
        
    diagram = fig.add_subplot()
    diagram.table(cellText = cell_text,
                rowLabels = ['limit switches'],
                colLabels = columns,
                loc = 'bottom',
                bbox =[0.0, -0.25, 1, 0.12])
    diagram.axis('off')
    diagram.axis('off')

    #figManager = plt.get_current_fig_manager()
    #figManager.window.showMaximized()
    #plt.tight_layout()
    plt.subplots_adjust(left=0.190, bottom=0.210, right=0.900, top=0.970, wspace=None, hspace=1.000)
    plt.show()
   
#s_l_s = sequence_limit_switches
def limit_switches(s_l_s):
    new_s = []
    s_l_s = [words.replace("+", "1")
                          for words in s_l_s]
    s_l_s = [words.replace("-", "0")
                          for words in s_l_s]
    for i, each in enumerate(s_l_s):
        new_s.append(s_l_s[i - 1])
    s_l_s = new_s
    return s_l_s

#read sequence from file
def read_file(sequence):
    with open('VisualSCProjects\Project Fluidsim\sequence.txt') as f:
        line = f.readlines()
    s = [x.replace("/","") for x in line]
    s = ''.join(s)
    sequence = wrap(s, 2)
    return sequence

#check piston position, if the piston is already in the position of the new stroke, then ask again for the correct stroke   
def check_piston_position(stroke, s, correct_stroke):
    s = [x.upper() for x in s]
    stroke = stroke.upper()
    correct_stroke = True
    for i in reversed(range(len(s))):
        if s[i][0] == stroke[0]:
            last_position = i 
            if s[last_position] == stroke:
                print("The piston is already in that position.")
                correct_stroke = False
                break
            else:
                correct_stroke = True
                break
    
    return correct_stroke

#check the sequence, if it is not completed it asks to finish it.
def check_sequence(sequence):
    sequence = [x.upper() for x in sequence]
    l = limit(sequence)[0]
    if len(sequence) != (l*2):
        s = limit(sequence)[2]
        loop = check_loop(s)
        if loop == True:
            correct_stroke = True
        else:
            print("The sequence isn't completed")
            correct_stroke = False
    else:
        correct_stroke = True
    return correct_stroke

#check the input from the user
def check_stroke(stroke, sequence):                                                                  
    correct_stroke = False
    while not correct_stroke:                                                                          
        if len(stroke) > 2:     #limit input buffer                                         
            print("Too many arguments. ")
            correct_stroke = False
            break
        elif stroke[0] in string.ascii_lowercase or stroke[0] in string.ascii_uppercase:        #the name of the piston is the first letter to check      
            if len(stroke) > 1:
                if stroke[1] == '+' or stroke[1] == '-':                                            #the stroke can only be positive or negative
                    correct_stroke = check_piston_position(stroke, sequence, correct_stroke)
                    if correct_stroke == False:
                        break
                else:
                    correct_stroke = False                                                                  
                    break
            else:
                correct_stroke = False
                break
        elif '/' in stroke[0]:
            if len(stroke) > 1:
                correct_stroke = False
                break
            else:
                correct_stroke = check_sequence(sequence)
                if correct_stroke == False:
                    break
                else:
                    print("The sequence is terminated.\n")
        else:
            print("A letter must be the name of the actuator")
            correct_stroke = False
            break
        
    return correct_stroke

#def write sequence to the file sequence.txt
def write_file(sequence):
    with open('VisualSCProjects\Project Fluidsim\sequence.txt', 'w') as f:
        f.write(''.join(sequence))

#function that ask the user to insert the strokes, if the stroke is correct, add it to the sequence array
def insert_stroke(sequence):
    stroke = input("Insert stroke: ")
    continue_insert = False
    while not continue_insert:
        correct_stroke = check_stroke(stroke, sequence)
        if correct_stroke != True:
            stroke = insert_correct_stroke()
        else:
            if '/' in stroke:
                print("We can proceed with the analysis")
                continue_insert = False
                break
            else:
                continue_insert = True

    sequence.append(stroke)
    return stroke, sequence
    
#class bcolors for colored output
class bcolors:    
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#---------------------------------------------------------------------------
def algorithm_limit_switches(l_s, sequence):
    #l_s normal array 'letter+number'
    seen = []
    loop_stroke = []
    l_s_bool = []
    s = limit(sequence)[2]
    s = [x.lower() for x in s]
    sequence = [x.lower() for x in sequence]
    loop = check_loop(s)
    if loop == True:
        for i in range(len(l_s) - 1):
            rep = s.count(l_s[i][0])
            if rep > 2 and l_s[i][0] not in loop_stroke:
                loop_stroke.append(l_s[i][0])
                a = l_s.index(l_s[i])
            else:
                continue
        for i in range(1, len(sequence)):
            if l_s[i][0] in loop_stroke and l_s[a][1] == '1':
                if l_s[i][1] == '0':
                    l_s_bool.append('TRUE')
                else:
                    l_s_bool.append('FALSE')
            elif l_s[i][0] in loop_stroke and l_s[a][1] == '0':
                if l_s[i][1] == '1':
                    l_s_bool.append('TRUE')
                else:
                    l_s_bool.append('FALSE')
            elif l_s[i][0] not in loop_stroke and l_s[i][0] not in seen:
                seen.append(l_s[i][0])
                l_s_bool.append('FALSE')
            elif l_s[i][0] not in loop_stroke and l_s[i][0] in seen:
                l_s_bool.append('TRUE')
        l_s_bool.insert(0, "TRUE")
    else:
        for i in range(1, len(l_s)):
            if l_s[i][0] not in seen:
                seen.append(l_s[i][0])
                l_s_bool.append('FALSE')
            else:
                l_s_bool.append('TRUE')
        l_s_bool.insert(0, "TRUE")
    return l_s_bool

#PLC Structured text
class plc():
    def __init__(self, sequence, limit_switches, groups, l_s):
        self.run(sequence, limit_switches, groups, l_s)
    def run(self, sequence, limit_switches, groups, l_s):
        self.assignIO(sequence, limit_switches, groups, l_s)
    def assignIO(self, sequence, limit_switches, groups, l_s):
        l = len(sequence)
        g = len(groups)
        solenoids = sequence
        lenght__ = len(limit_switches)
        num_mem = math.ceil((lenght__)/2)
        relay_mem = [[] for _ in range(num_mem)]
        #print(groups)
        #print(limit_switches)
        z = 1
        j = 0
        all_blocks = False
        while not all_blocks:
            relay_mem[j].append(limit_switches[z][0])           #limit switch that activates the relay memory K*
            if z < len(limit_switches) - 1:    
                z += 1
                if len(relay_mem[j]) == 2:
                    j += 1
            else:
                if num_mem > 1 and len(relay_mem[j]) == 2:
                    relay_mem[j+1].append(limit_switches[0][0])
                else:
                    relay_mem[j].append(limit_switches[0][0])
                all_blocks = True
        #print(relay_mem)

        with open('VisualSCProjects\Project Fluidsim\plc.txt','w') as f:
            for i in range(l):
                f.write(f'{solenoids[i]} AT %Q* : BOOL;')
                f.write('\n')
            for i in range(l):
                f.write(f'{l_s[i]} AT %I* : BOOL;')
                f.write('\n')
            f.write('\n//-----------------------------------------------------\n')
            f.write('// -----VARIABLES-----\n')
            f.write('// -----SOLENOIDS-----\n')
            for i in range(l):
                f.write(f'{solenoids[i]} := FALSE;')
                f.write('\n')
            l_s_bool = algorithm_limit_switches(l_s, sequence)
            f.write('// -----LIMIT SWITCHES-----\n')
            for i in range(l):
                f.write(f'{l_s[i]} := {l_s_bool[i]};')
                f.write('\n')
#---------------------------------------------------------------------
#-----Algorithm for limit_switches-----------------------------------


#class FluidPy to read the input arguments and elaborate all the functions
class FluidPy:
    def __init__(self, args):
        self.args = args
    def run(self):
        if self.args.file:
            self.file()
        else:
            self.normal()
            
    def welcome(self):
        print('      ________                 _               _______         __ ')
        print('     /  _____/ __     __   __ |_|   _____     /  __   \ __    / / ')
        print('    /  /___   / /    / /  / / __   / ___  \  /  / /   | \ \  / /  ')
        print('   /  ____/  / /    / /  / / / /  / /   \  | /  /_/  |   \ \/ /   ')
        print('  /  /      / /    / /  / / / /  / /   |  |  /  ____/     \  /    ')
        print(' /  /      / /__  / /__/ / / /  / /___/  /  /  /          / /     ')
        print('/__/      /____/ /______/ /_/  /_______/   /__/          /_/   [] ')
        print('\n')
        print(bcolors.OKGREEN + '                Developed by MrLostInTheInternet              ' + bcolors.ENDC)
        print(fill(bcolors.HEADER + '**Welcome to FluidPy, a script that will help you create your Fluidsim circuit !**' + bcolors.ENDC))
        print('')
        time.sleep(0.5)
        print(fill(bcolors.HEADER + 'This python script will guide you throught all you need, for creating your circuit' + bcolors.ENDC))
        print('')
        time.sleep(0.5)
        print(fill(bcolors.HEADER + 'First of all, enter your sequence you\'ll be working with:\n' + bcolors.ENDC))
        print('')
        if self.args.file:
            return
        else:
            time.sleep(1)
            print(fill(bcolors.HEADER + '**Enter ' + bcolors.WARNING + '"/"' + bcolors.HEADER + ' when you want to finish the sequence ...\n' + bcolors.ENDC))

    def analysis(self, sequence):
        groups = []
        l_sw = []
        s = limit(sequence)[2]
        s_l_s = limit_switches(sequence)
        s_l_s = [l.lower() for l in s_l_s]              #limit switches labels are lowercase
        s_upper = [stroke.upper() for stroke in sequence]
        groups, l_sw = find_blocks(s_upper, s_l_s)
        diagrams(s_upper, s_l_s)
        self.structured_text(s_upper, l_sw, groups, s_l_s)

    def normal(self):
        self.welcome()
        sequence = []
        stop_sequence = False
        try:
            while not stop_sequence:
                stroke, sequence = insert_stroke(sequence)

                if '/' in stroke:
                    del sequence[-1]
                    stop_sequence = True
                    write_file(sequence)
                    self.analysis(sequence)
                else:
                    stop_sequence = False

        except KeyboardInterrupt:
            print("\nUser has terminated the sequence.\n")
    
    def file(self):
        self.welcome()
        sequence = []
        sequence = read_file(sequence)
        if sequence is not Empty:
            self.analysis(sequence)
        else:
            print("The sequence is empty.")

    def structured_text(self, sequence, limit_switches, groups, l_s):
        plc(sequence, limit_switches, groups, l_s)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description='FluidPy Tool',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=textwrap.dedent('''Example:
    fluid.py -f=mysequence.txt #read the sequence from file.txt
    '''))
    parser.add_argument('-f', '--file', type=argparse.FileType('r'))
    args = parser.parse_args()
    fp = FluidPy(args)
    fp.run()