#!/usr/bin/env python3

import argparse
from tkinter import Y

import matplotlib.pyplot as plt
import numpy as np
import sys
import string
import textwrap
from types import new_class             

#ask to insert the correct stroke if the check returns false
def insert_correct_stroke():
    stroke = input("Error. Insert the correct stroke: ")
    return stroke

#def assign_blocks(sequence):
    with sequence as s:
        get_index = s.index(stroke)

def check_loop(s):
    for i in range(len(s)):
        stroke = s[i]
        rep = s.count(stroke)
        if rep > 2:
            print("There is a loop with the piston %s\n" %stroke)
        else:
            continue

def limit(sequence):
    s = []
    sequence = [words.replace("-", "") for words in sequence]
    sequence = [words.replace("+", "") for words in sequence]
    limit = len(set(sequence))
    for stroke in sequence:
        if stroke not in s:
            s.append(stroke)
    return limit, s

def diagrams(sequence, limit_switches):
    s = []
    l, s = limit(sequence)
    fig, axs = plt.subplots(nrows = l, ncols = 1)
    
    x1 = [0, len(sequence)]
    x2 = [-x for x in x1]

    y = x1
    for i, ax in enumerate(axs.flat):
        ax.set_title(f'Piston ' + str(s[i]))
        ax.set_ylim([0, 1])
        for stroke in range(len(sequence)):
            if sequence[stroke][1] == '+':
                z = x1
            else:
                z = x2
            ax.plot(x1, z, 'b')
    plt.tight_layout()
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

#def pistons_plots(sequence, l_s):


#check piston position, if the piston is already in the position of the new stroke, then ask again for the correct stroke   
def check_piston_position(stroke, s, correct_stroke):
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

#check the input from the user

def check_stroke(stroke, sequence):                                                                  
    correct_stroke = False
    while not correct_stroke:                                                                          
        if len(stroke) > 2:     #limit input buffer                                         
            print("Too many arguments. ")
            correct_stroke = False
            break
        elif stroke[0] in string.ascii_lowercase or stroke[0] in string.ascii_uppercase:        #the name of the piston is the first letter to check      
            if stroke[1] == '+' or stroke[1] == '-':                                            #the stroke can only be positive or negative
                correct_stroke = check_piston_position(stroke, sequence, correct_stroke)
                if correct_stroke == False:
                    break
            else:
                correct_stroke = False                                                                  
                break
        elif '/' in stroke[0]:                                                             
            correct_stroke = True
            print("The sequence is terminated.\n")

        else:
            print("A letter must be the name of the actuator")
            correct_stroke = False
            break
        
    return correct_stroke

#function that ask the user to insert the strokes, if the stroke is correct, add it to the sequence array
def insert_stroke(sequence):
    stroke = input("Insert stroke: ")
    continue_insert = False
    while not continue_insert:
        correct_stroke = check_stroke(stroke, sequence)
        if correct_stroke != True:
            if '/' not in stroke:
                stroke = insert_correct_stroke()
            else:
                print("We can proceed with the analysis")
        else:
            continue_insert = True

    sequence.append(stroke)
    return stroke, sequence

class FluidPy:
    def __init__(self, args):
        self.args = args
    def run(self):
        if self.args.loop:
            self.loop()
        #elif self.args.file():
        #    self.file()
        else:
            self.normal()
    
    def analysis(self, sequence):
        s_loop = check_loop(sequence)
        #s_blocks = assign_blocks(sequence)
        s_l_s = limit_switches(sequence)
        s_upper = [stroke.upper() for stroke in sequence]
        diagrams(s_upper, s_l_s)
        #pistons_plots(sequence, l_s)

    def normal(self):
        sequence = []
        stop_sequence = False
        try:
            while not stop_sequence:
                stroke, sequence = insert_stroke(sequence)

                if '/' in stroke:
                    del sequence[-1]
                    stop_sequence = True
                    self.analysis(sequence)
                else:
                    stop_sequence = False
    


        except KeyboardInterrupt:
            print("\nUser has terminated the sequence.\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description='FluidPy Tool',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=textwrap.dedent('''Example:
    fluid.py -f=mysequence.txt #lettura sequenza da file
    fluid.py -l -f=mysequence.txt #lettura sequenza con loop da file
    '''))
    parser.add_argument('-f', '--file', type=argparse.FileType('r'))
    parser.add_argument('-l','--loop',help='sequence with loop in it')
    args = parser.parse_args()
    #print(args.file.readlines())
    fp = FluidPy(args)
    fp.run()
