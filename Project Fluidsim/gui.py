#!/usr/bin/env python3
import PySimpleGUI as sg
import fluid
import pandas
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
    return sg.pin(sg.Column(layout, key=key, visible=visible))

data = []
def __elaborate__():
    d = fluid.data_table()
    groups = d.groups
    relay__k = d.relay__k
    relay_mem = d.relay_mem
    l_s_bool = d.l_s_bool
    l_s = d.l_s
    num_rows = len(groups)
    data = [['']*6 for _ in range(len(l_s))]
    num_blocks = len(groups) - 1
    data[0].insert(0,num_blocks)
    for i in range(len(groups)):
        data[i].insert(1 ,groups[i])
    num_mem = len(relay__k)
    data[0].insert(2, num_mem)
    for i in range(num_mem):
        data[i].insert(3, relay__k[i])
    for i in range(len(l_s_bool)):
        if l_s_bool[i] == 'TRUE':
            data[i].insert(4, l_s[i])
        else:
            data[i].insert(5, l_s[i])
    return data



section = [[sg.Multiline(expand_x = True, horizontal_scroll=True, size = (50, 19), key = 'plc_code')]]

headings = ('Block S.','Groups', 'N. Memories','Relay Memories', 'L. S. Enabled', 'L. S. Disabled')

image_viewer_column = [
    [sg.Table(values = data , headings = headings, size = (10, 6), auto_size_columns=True, expand_x = True, visible = False, key = 'table')],
    [sg.Image(key="-IMAGE-", visible = False, expand_x = True)]
]


layout_data = [[sg.Text('Sequence:', size = (11, 2)), sg.Text(key = 'text', expand_x = True, size = (35, 2), text_color = 'Black')],
            [sg.Text('Insert stroke: ', size = (11, 2)), sg.Input(key = 'input', size = (6, 2), text_color='Black')],
            [sg.Button('Finish', size =(10, 1)), sg.Button('Clear', size = (10, 1)), sg.Button("Display Diagram's fases", expand_x = True, expand_y = True)],
            [sg.Checkbox('Show PLC ST code', enable_events=True, key = 'checkbox_key'), sg.Checkbox('Show Data', enable_events=True, key = 'data')],
            [collapse(section, 'plc', False)],
        ]

layout = [
    [
        sg.Column(layout_data, vertical_alignment= 'top'),
        sg.VSeperator(),
        sg.Column(image_viewer_column, visible = False, key = 'image_column'),
    ]
]

sequence = []

window = sg.Window('GUI', layout, finalize = True)
window['input'].bind("<Return>", "_Enter")

Text = ''
toggle_bool1 = False
toggle_bool2 = False
toggle_bool3 = False

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
                data = __elaborate__()
                with open('VisualSCProjects/Project Fluidsim/plc.txt', 'r') as p:
                    Text = p.readlines()
                    Text = ''.join(line for line in Text)
                window['plc_code'].update(Text)
    if event == 'Clear':
        sequence = []
        window['text'].update('')
        toggle_bool2 = False
        window['-IMAGE-'].update(visible = False)
        window['plc_code'].update('')
        window['table'].update('')
    if event == "Display Diagram's fases":
        toggle_bool2 = not toggle_bool2
        im = "VisualSCProjects/Project Fluidsim/diagram_fases.png"
        window['-IMAGE-'].update(im, visible = toggle_bool2)
        window['image_column'].update(visible = toggle_bool2)

    if event == 'checkbox_key':
        toggle_bool1 = not toggle_bool1
        window['plc'].update(visible=toggle_bool1)
        window['plc_code'].update(Text)
    if event == 'data':
        toggle_bool3 = not toggle_bool3
        window['table'].update(data, visible = toggle_bool3)
        window['image_column'].update(visible = toggle_bool3)
window.close()