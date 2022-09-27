#!/usr/bin/env python3
from tkinter import scrolledtext
import PySimpleGUI as sg
import fluid
from fluid import *
from PIL import Image
import matplotlib.image as img

sg.theme('DefaultNoMoreNagging')

def insert_stroke_gui(sequence, value):
    stroke = value
    continue_insert = False
    while not continue_insert:
        correct_stroke = check_stroke(stroke, sequence)
        if correct_stroke != True:
            sg.PopupQuickMessage('Error. The stroke is not correct.', background_color='Red')
            break
        else:
            if '/' in stroke:
                sg.PopupQuickMessage("To terminate the sequence press 'Finish'.", background_color='Red')
                break
            else:
                sequence.append(stroke)
                continue_insert = True
    return stroke, sequence

def collapse(layout, key, visible):
    return sg.pin(sg.Column(layout, key=key, visible=visible))\

section = [[sg.Multiline(expand_x = True, horizontal_scroll=True, size = (45, 19), key = 'plc_code')]]

image_viewer_column = [
    [sg.Image(key="-IMAGE-", visible = False)],
]

layout_data = [[sg.Text('Sequence:', size = (11, 2)), sg.Text(key = 'text', expand_x = True, size = (35, 2), text_color = 'Black')],
            [sg.Text('Insert stroke: ', size = (11, 2)), sg.Input(key = 'input', size = (6, 2), text_color='Black')],
            [sg.Button('Finish', size =(10, 2)), sg.Button('Clear', size = (10, 2)), sg.Button("Display Diagram's fases", expand_x = True, expand_y = True)],
            [sg.Checkbox('Show PLC ST code', enable_events=True, key = 'checkbox_key')],
            [sg.Canvas(key = 'canvas')],
            [collapse(section, 'plc', False)]
        ]

layout = [
    [
        sg.Column(layout_data, vertical_alignment= 'top'),
        sg.VSeperator(),
        sg.Column(image_viewer_column),
    ]
]

sequence = []


window = sg.Window('GUI', layout, finalize = True)
window['input'].bind("<Return>", "_Enter")

toggle_bool = False
Text = ''
bool_toggle2 = False

while True:
    event, values = window.read()
    if event is None:
        break
    if event == 'input' + '_Enter':
        stroke = values['input']
        stroke, sequence = insert_stroke_gui(sequence, stroke)
        sequence = [x.upper() for x in sequence]
        window['text'].update(sequence)
        window['input'].update('')
    if event == 'Finish':
        if len(sequence) == 0:
            sg.PopupQuickMessage('No sequence submitted.')
        else:
            check = check_sequence(sequence)
            if check is False:
                sg.PopupQuickMessage("The sequence isn't completed.", background_color='Red')
                continue
            else:
                args = ''
                f = fluid.FluidPy(args)
                f.analysis(sequence)
                with open('VisualSCProjects/Project Fluidsim/plc.txt', 'r') as p:
                    Text = p.readlines()
                    Text = ''.join(line for line in Text)
                window['plc_code'].update(Text)
    if event == 'Clear':
        sequence = []
        window['text'].update('')
        bool_toggle2 = False
        window['-IMAGE-'].update(visible = False)
        window['plc_code'].update('')
    if event == "Display Diagram's fases":
        bool_toggle2 = not bool_toggle2
        im = "VisualSCProjects/Project Fluidsim/diagram_fases.png"
        window['-IMAGE-'].update(im, visible = bool_toggle2)
    if event == 'checkbox_key':
        toggle_bool = not toggle_bool
        window['plc'].update(visible=toggle_bool)
        window['plc_code'].update(Text)

window.close()