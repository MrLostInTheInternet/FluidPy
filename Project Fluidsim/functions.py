import argparse
import matplotlib.pyplot as plt
import numpy as np
import PySimpleGUI as sg
import os
import string
import textwrap
import time
from collections import deque
from textwrap import fill, wrap
from queue import Empty

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
#function blocks to individue the blocks and create the groups
def define_groups(group, limit_switch_string):
    l = group.count('//')
    groups = [[] for _ in range(l+1)]
    limit_switches = [[] for _ in range(l+1)]
    i = 0
    j = 0
    finish = False
    while not finish:
        if '//' not in group[i]:
            groups[j].append(group[i])
            limit_switches[j].append(limit_switch_string[i])
            i += 1
        else:
            j += 1
            i += 1
        if i == len(group):
            finish = True
    return groups, limit_switches

#function to separate groups by //
def separate_groups(sequence_list, limit_switch_list):
    seen = []
    group = ''
    limit_switch_string = ''
    finish = False
    i = 0
    while not finish:
        stroke = sequence_list[i][0]
        if stroke not in seen:
            seen.append(stroke)
            group += sequence_list[i]
            limit_switch_string += limit_switch_list[i]
            i += 1
        else:
            group += '//'
            limit_switch_string += '//'
            seen.clear()
        if i == len(sequence_list):
            finish = True
    group = wrap(group, 2)
    limit_switch_string = wrap(limit_switch_string, 2)
    return define_groups(group, limit_switch_string)

#ask to insert the correct stroke if the check returns false
def insert_correct_stroke():
    stroke = input(fill(bcolors.OKBLUE + '[x] Insert the correct stroke: ' + bcolors.ENDC))
    return stroke

#check if there are pistons in loop
def check_for_loops(s):
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

#number of pistons in the sequence, return number of pistons, sequence of limit switches and piston's name list
def total_pistons(sequence_list):
    all_names_list = []
    sequence_list = [words.replace("-", "") for words in sequence_list]
    sequence_list = [words.replace("+", "") for words in sequence_list]
    total_number_of_pistons = len(set(sequence_list))
    for stroke in sequence_list:
        if stroke not in all_names_list:
            all_names_list.append(stroke)
    piston_name_list = sequence_list
    return total_number_of_pistons, all_names_list, piston_name_list

#diagram's fases
def draw_diagrams(sequence_list, limit_switches):
    all_names_list = []
    total_number_of_pistons, all_names_list, piston_name_list= total_pistons(sequence_list)
    cell_text = [limit_switches]
    columns= sequence_list

    fig, axs = plt.subplots(nrows = total_number_of_pistons, ncols = 1)
    plt.get_current_fig_manager().set_window_title("Diagram's fases")
    colors = plt.rcParams["axes.prop_cycle"]()

    x = list(range(len(sequence_list)+1))
    y = [[] for _ in range(total_number_of_pistons)]

    for j in range(len(all_names_list)):

        stroke = all_names_list[j]
        piston_index = piston_name_list.index(stroke)
        if sequence_list[piston_index][1] == '+':
            y[j].append(0)
            v = 0
        else:
            y[j].append(0.99)
            v = 0.99
        for i in range(len(sequence_list)):
            if stroke == sequence_list[i][0]:
                if sequence_list[i][1] == '+':
                    y[j].append(0.99)
                    v = 0.99
                else:
                    y[j].append(0)
                    v = 0
            else:
                y[j].append(v)
    if len(sequence_list) == 2 or len(set(sequence_list)) == 2:
        c = next(colors)["color"]
        axs.set_ylabel(str(all_names_list[0]), rotation = 0, color = c)
        axs.set_ylim([0, 1.0])
        axs.set_yticks(range(0,2,1))
        axs.set_xlim([0, len(sequence_list)])
        axs.sharex(axs)
        axs.plot(x,y[0], 'o-', color = c)
    else:
        for i, ax in enumerate(axs.flat):
            c = next(colors)["color"]
            ax.set_ylabel(str(all_names_list[i]), rotation = 0, color = c)
            ax.set_ylim([0, 1.0])
            ax.set_yticks(range(0,2,1))
            ax.set_xlim([0, len(sequence_list)])
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

    plt.subplots_adjust(left=0.190, bottom=0.210, right=0.900, top=0.970, wspace=None, hspace=1.000)
    dir = os.path.dirname('diagram_fases.png') + 'diagram_fases.png'
    plt.savefig(dir)

#function to create list of limit switches
def limit_switches(limit_switches_list):
    new_s = []
    limit_switches_list = [words.replace("+", "1")
                          for words in limit_switches_list]
    limit_switches_list = [words.replace("-", "0")
                          for words in limit_switches_list]
    for i, each in enumerate(limit_switches_list):
        new_s.append(limit_switches_list[i - 1])
    limit_switches_list = new_s
    return limit_switches_list

#read sequence from file
def read_file(sequence_list):
    dir = os.path.dirname('sequence.txt') + 'sequence.txt'
    with open(dir) as f:
        line = f.readlines()
    s = [x.replace("/","") for x in line]
    s = ''.join(s)
    sequence_list = wrap(s, 2)
    return sequence_list

#check piston position, if the piston is already in the position of the new stroke, then ask again for the correct stroke
def check_piston_position(stroke, s, correct_stroke):
    s = [x.upper() for x in s]
    stroke = stroke.upper()
    correct_stroke = True
    for i in reversed(range(len(s))):
        if s[i][0] == stroke[0]:
            last_position = i
            if s[last_position] == stroke:
                print(fill(bcolors.WARNING + "[!] Error. The piston is already in that position.\n" + bcolors.ENDC))
                correct_stroke = False
                break
            else:
                correct_stroke = True
                break

    return correct_stroke

#check the sequence, if it is not completed it asks to finish it.
def check_sequence(sequence_list):
    sequence_list = [x.upper() for x in sequence_list]
    l = total_pistons(sequence_list)[0]
    if len(sequence_list) != (l*2):
        s = total_pistons(sequence_list)[2]
        loop = check_for_loops(s)
        if loop == True:
            correct_stroke = True
        else:
            print(fill(bcolors.WARNING + "[!] Error. The sequence isn't completed.\n" + bcolors.ENDC))
            correct_stroke = False
    else:
        correct_stroke = True
    return correct_stroke

#check the input from the user
def check_stroke(stroke, sequence_list):
    correct_stroke = False
    while not correct_stroke:
        if len(stroke) > 2:     #limit input buffer
            print(fill(bcolors.WARNING + '[!] Error. Too many arguments.\n' + bcolors.ENDC))
            correct_stroke = False
            break
        elif len(stroke) == 0:
            print(fill(bcolors.WARNING + '[!] Error. No stroke submitted\n' + bcolors.ENDC))
            correct_stroke = False
            break
        elif stroke[0] in string.ascii_lowercase or stroke[0] in string.ascii_uppercase:        #the name of the piston is the first letter to check
            if len(stroke) > 1:
                if stroke[1] == '+' or stroke[1] == '-':                                            #the stroke can only be positive or negative
                    correct_stroke = check_piston_position(stroke, sequence_list, correct_stroke)
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
                correct_stroke = check_sequence(sequence_list)
                if correct_stroke == False:
                    break
                else:
                    print(fill(bcolors.OKGREEN + '[+] The sequence is terminated\n' + bcolors.ENDC))
        else:
            print(fill(bcolors.WARNING + '[!] Error. \n' + bcolors.ENDC))
            correct_stroke = False
            break

    return correct_stroke

#def write sequence to the file sequence.txt
def write_file(sequence_list):
    dir = os.path.dirname('sequence.txt') + 'sequence.txt'
    with open(dir, 'w') as f:
        f.write(''.join(sequence_list))

#function that ask the user to insert the strokes, if the stroke is correct, add it to the sequence array
def insert_stroke(sequence_list):
    stroke = input(fill(bcolors.OKGREEN + '[ ] Insert stroke: ' + bcolors.ENDC))
    continue_insert = False
    while not continue_insert:
        correct_stroke = check_stroke(stroke, sequence_list)
        if correct_stroke != True:
            stroke = insert_correct_stroke()
        else:
            if '/' in stroke:
                print(fill(bcolors.OKGREEN + '[+] Proceeding with the analysis\n' + bcolors.ENDC))
                continue_insert = False
                break
            else:
                continue_insert = True

    sequence_list.append(stroke)
    return stroke, sequence_list

#---------------------------------------------------------------------------
def algorithm_limit_switches(limit_switch_list, sequence_list):
    #limit_switch_list normal array 'letter+number'
    seen = []
    loop_stroke = []
    limit_switch_list_bool = []
    s = total_pistons(sequence_list)[2]
    s = [x.lower() for x in s]
    sequence_list = [x.lower() for x in sequence_list]
    loop = check_for_loops(s)
    if loop == True:
        for i in range(len(limit_switch_list) - 1):
            rep = s.count(limit_switch_list[i][0])
            if rep > 2 and limit_switch_list[i][0] not in loop_stroke:
                loop_stroke.append(limit_switch_list[i][0])
                a = limit_switch_list.index(limit_switch_list[i])
                break
            else:
                continue
        for i in range(1, len(sequence_list)):
            if limit_switch_list[i][0] in loop_stroke and limit_switch_list[a][1] == '1':
                if limit_switch_list[i][1] == '0':
                    limit_switch_list_bool.append('TRUE')
                else:
                    limit_switch_list_bool.append('FALSE')
            elif limit_switch_list[i][0] in loop_stroke and limit_switch_list[a][1] == '0':
                if limit_switch_list[i][1] == '1':
                    limit_switch_list_bool.append('TRUE')
                else:
                    limit_switch_list_bool.append('FALSE')
            elif limit_switch_list[i][0] not in loop_stroke and limit_switch_list[i][0] not in seen:
                seen.append(limit_switch_list[i][0])
                limit_switch_list_bool.append('FALSE')
            elif limit_switch_list[i][0] not in loop_stroke and limit_switch_list[i][0] in seen:
                limit_switch_list_bool.append('TRUE')
        limit_switch_list_bool.insert(0, "TRUE")
    else:
        for i in range(1, len(limit_switch_list)):
            if limit_switch_list[i][0] not in seen:
                seen.append(limit_switch_list[i][0])
                limit_switch_list_bool.append('FALSE')
            else:
                limit_switch_list_bool.append('TRUE')
        limit_switch_list_bool.insert(0, "TRUE")
    return limit_switch_list_bool

def merge_groups(groups):
    seen = []
    merge = False
    for i in range(len(groups[-1])):
        seen.append(groups[-1][i][0])
    for j in range(len(groups[0])):
        stroke = groups[0][j][0]
        if stroke in seen:
            merge = False
            break
        else:
            merge = True
    return merge
