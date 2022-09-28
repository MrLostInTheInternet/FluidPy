import PySimpleGUI as sg
import fluid
from functions import *
from fluid import *
import os

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
    data_tab = fluid.data_table()
    groups = data_tab.groups
    relay_k_name = data_tab.relay_k_name
    limit_switch_list_bool = data_tab.limit_switch_list_bool
    limit_switch_list = data_tab.limit_switch_list
    data = [['']*6 for _ in range(len(limit_switch_list))]
    num_blocks = len(groups) - 1
    data[0].insert(0,num_blocks)
    for i in range(len(groups)):
        data[i].insert(1 ,groups[i])
    num_mem = len(relay_k_name)
    data[0].insert(2, num_mem)
    for i in range(num_mem):
        data[i].insert(3, relay_k_name[i])
    for i in range(len(limit_switch_list_bool)):
        if limit_switch_list_bool[i] == 'TRUE':
            data[i].insert(4, limit_switch_list[i])
        else:
            data[i].insert(5, limit_switch_list[i])
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
                dir1 = os.path.dirname('plc_txt') + 'plc.txt'
                with open(dir1, 'r') as p:
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
        dir2 = os.path.dirname('diagram_fases.png') + 'diagram_fases.png'
        im = dir2
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
