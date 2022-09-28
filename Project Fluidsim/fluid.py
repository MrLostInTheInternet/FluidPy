from functions import *

global groups_global, relay_k_name_global, relay_memories_global, limit_switch_list_bool_global, limit_switch_list_global

groups_global = []
relay_k_name_global = []
relay_memories_global = []
limit_switch_list_bool_global = []
limit_switch_list_global = []

#PLC Structured text
class plc():
    def __init__(self, sequence_list, limit_switch_groups, groups, limit_switch_list):
        self.run(sequence_list, limit_switch_groups, groups, limit_switch_list)
    def run(self, sequence_list, limit_switch_groups, groups, limit_switch_list):
        self.assignIO(sequence_list, limit_switch_groups, groups, limit_switch_list)
    def assignIO(self, sequence_list, limit_switch_groups, groups, limit_switch_list):
        l = len(sequence_list)
        g = len(groups)
        solenoids = sequence_list
        len_switches = len(limit_switch_groups)
        all_names = total_pistons(sequence_list)[2]
        all_names = [x.lower() for x in all_names]
        loop = check_for_loops(all_names)
        if loop == True:
            loop_index = 0
            for i in range(len(all_names)):
                loop_piston = all_names.count(all_names[i])
                if loop_piston > 2:
                    loop_index = i
                else:
                    continue
            loop_index -= 1
            limit_switch_list_loop = limit_switch_list[loop_index]
        # if last group compatible with the first group, then we can merge them together
        merge__ = merge_groups(groups)
        if merge__ == True:
            g -= 1
        else:
            g = g
        # if merge is true then we have to proceed with a different method then before
        #-----------------------------------------------------------------------------

        # (number of memories = groups - 1)
        num_mem = g - 1
        relay_memories = [[] for _ in range(num_mem)]
        switches_index = 1
        # the following loop is to assign the switches to the relays contacts. IT WORKS
        for i in range(num_mem):
            relay_memories[i].append(limit_switch_groups[switches_index][0])
            if i == (num_mem - 1):
                if merge__ == True:
                    relay_memories[i].append(limit_switch_groups[switches_index+1][0])
                elif merge__ == False:
                    relay_memories[i].append(limit_switch_groups[0][0])
            else:
                relay_memories[i].append(limit_switch_groups[switches_index+1][0])
            switches_index += 1
        #-------------------------------------------------------------------------------
        # for loop to assign names to the memories
        relay_k_name = []
        for i in range(num_mem):
            relay_k_name.append('K'+ str(i))
        #-------------------------------------------------------------------------------


        #Open the file that we want to write on the plc structured text
        dir = os.path.dirname('plc_txt') + 'plc.txt'
        with open(dir,'w') as f:
            #relays variables ----------------------------------------------------
            f.write('PROGRAM FluidsimSequence\n')
            f.write('VAR\n')
            for i in range(num_mem):
                f.write(f'#{relay_k_name[i]} AT %Q : BOOL;\n')
            #solenoids variables -------------------------------------------------
            for i in range(l):
                f.write(f'#{solenoids[i]} AT %Q* : BOOL;\n')
            #limit switches variables --------------------------------------------
            for i in range(l):
                f.write(f'#{limit_switch_list[i]} AT %I* : BOOL;\n')
            f.write('END_VAR\n')
            f.write('\n//-----------------------------------------------------\n')
            f.write('// -----VARIABLES-----\n')
            f.write('// -----RELAY MEMORIES-----\n')
            for i in range(num_mem):
                f.write(f'#{relay_k_name[i]} := FALSE;\n')
            f.write('// -----SOLENOIDS-----\n')
            for i in range(l):
                f.write(f'#{solenoids[i]} := FALSE;\n')
            limit_switch_list_bool = algorithm_limit_switches(limit_switch_list, sequence_list)
            f.write('// -----LIMIT SWITCHES-----\n')
            for i in range(l):
                f.write(f'#{limit_switch_list[i]} := {limit_switch_list_bool[i]};\n')
            f.write('\n//-----------------------------------------------------\n')
            f.write('// -----CONDITIONS-----\n')
            for j in range(num_mem):
                #first conditions for the first relay
                #activation switch
                f.write(f'\nIF #{relay_memories[j][0]} = True THEN\n\t')
                f.write(f'#{relay_k_name[j]} := TRUE;\n')
                f.write('END_IF;\n')
                #deactivation switch
                f.write(f'\nIF #{relay_memories[j][1]} = True THEN\n\t')
                f.write(f'#{relay_k_name[j]} := FALSE;\n')
                f.write('END_IF;\n')
                #------------------------------------
            #first relay-------------------------------------
            f.write(f'\nIF #{relay_k_name[0]} = True THEN\n')
            if merge__ == True:
                merged_groups = []
                merged_groups = groups[0] + groups[-1]
                for k in range(len(groups[0]) + len(groups[-1])):
                    f.write(f'\t#{merged_groups[k]} := FALSE;\n')
                f.write('END_IF;\n')
            elif merge__ == False:
                for k in range(len(groups[0])):
                    f.write(f'\t#{groups[0][k]} := FALSE;\n')
                f.write('END_IF;\n')
            f.write(f'\nIF #{relay_k_name[0]} = False THEN\n')
            for k in range(len(groups[1])):
                f.write(f'\t#{groups[1][k]} := FALSE;\n')
            f.write('END_IF;\n')

            #update data table with global variables
            global groups_global, relay_k_name_global, relay_memories_global, limit_switch_list_bool_global, limit_switch_list_global
            groups_global = groups
            relay_k_name_global = relay_k_name
            relay_memories_global = relay_memories
            limit_switch_list_bool_global = limit_switch_list_bool
            limit_switch_list_global = limit_switch_list

            #------------------------------------------------
            #next relays-------------------------------------
            for j in range(1, num_mem):
                f.write(f'IF #{relay_k_name[j]} = False THEN\n')
                for k in range(len(groups[j+1])):
                    f.write(f'\t#{groups[j+1][k]} := FALSE;\n')
                f.write('END_IF;\n')

            #------------------------------------------------
            #conditions for the circuit to start and activate the first solenoid
            # we need to have the limit_switches sequence list shifted by one element
            limit_switch_list = deque(limit_switch_list)
            limit_switch_list.rotate(-1)
            limit_switch_list = list(limit_switch_list)
            #print(l_s)
            #------------------------------------------------------------------------
            #---------------FIRST GROUP-----------------------
            #------------------START--------------------------
            f.write(f'IF #START = True AND #{limit_switch_list[-1]} = True AND #{relay_k_name[0]} = False ')
            for i in range(1, num_mem):
                f.write(f'AND #{relay_k_name[i]} = False ')
            f.write('THEN\n\t')
            f.write(f'#{solenoids[0]} := TRUE;\n\t')
            f.write(f'IF #{solenoids[0]} = True THEN\n\t\t')
            #if group 0 ins't just one stroke then
            if len(groups[0]) > 1:
                f.write(f'#{limit_switch_list[0]} := TRUE;\n\t')
                convert_on_off = limit_switch_list[0][0]
                for on_off in range(1,len(limit_switch_list)):
                    if convert_on_off == limit_switch_list[on_off][0]:
                        f.write(f'\t#{limit_switch_list[on_off]} := FALSE;\n\t')
                        break
                    else:
                        continue
                f.write('END_IF;\n\t')
                finish_group = 1
                _index_ = 1
                while finish_group < len(groups[0]):
                    f.write(f'IF #{limit_switch_list[_index_ - 1]} = True THEN\n\t\t')
                    f.write(f'#{solenoids[_index_]} := TRUE;\n\t')
                    f.write('END_IF;\n\t')
                    f.write(f'IF #{solenoids[_index_]} = True THEN\n\t\t')
                    f.write(f'#{limit_switch_list[_index_]} := TRUE;\n\t')
                    convert_on_off = limit_switch_list[_index_][0]
                    for on_off in range(_index_ + 1,len(limit_switch_list)):
                        if convert_on_off == limit_switch_list[on_off][0]:
                            f.write(f'\t#{limit_switch_list[on_off]} := FALSE;\n\t')
                            break
                        else:
                            continue
                    f.write('END_IF;\n\t')
                    _index_ += 1
                    finish_group += 1
                f.write('\nEND_IF;\n')
            else:
                _index_ = 0
                f.write(f'#{limit_switch_list[_index_]} := TRUE;\n\t')
                convert_on_off = limit_switch_list[_index_][0]
                for on_off in range(1,len(limit_switch_list)):
                    if convert_on_off == limit_switch_list[on_off][0]:
                        f.write(f'\t#{limit_switch_list[on_off]} := FALSE;\n\t')
                        break
                    else:
                        continue
                f.write('END_IF;\nEND_IF;\n')
                _index_ += 1
            for j in range(num_mem):
                finish_group = 0
                f.write(f'IF #{limit_switch_list[_index_ - 1]} = True AND #{relay_k_name[j]} = True THEN\n')
                while finish_group < len(groups[j + 1]):
                    f.write(f'\t#{solenoids[_index_]} := TRUE;\n')
                    if finish_group != 0:
                        f.write('\tEND_IF;\n')
                    f.write(f'\tIF #{solenoids[_index_]} = True THEN\n\t')
                    f.write(f'\t#{limit_switch_list[_index_]} := TRUE;\n')
                    convert_on_off = limit_switch_list[_index_][0]
                    for on_off in range(_index_ + 1,len(limit_switch_list)):
                        if convert_on_off == limit_switch_list[on_off][0]:
                            f.write(f'\t\t#{limit_switch_list[on_off]} := FALSE;\n')
                            break
                        else:
                            continue
                    if loop == True and limit_switch_list[on_off][0] != limit_switch_list[loop_index][0]:
                        for on_off in range(_index_):
                            if convert_on_off == limit_switch_list[on_off][0]:
                                f.write(f'\t\t#{limit_switch_list[on_off]} := FALSE;\n')
                                break
                            else:
                                continue
                    f.write('\tEND_IF;\n')
                    if finish_group != (len(groups[j+1]) - 1):
                        f.write(f'\tIF #{limit_switch_list[_index_]} = True THEN\n\t')
                    _index_ += 1
                    finish_group += 1
                f.write('END_IF;\n')
            if merge__ == True:
                f.write(f'IF #{limit_switch_list[_index_ - 1]} = True AND #{relay_k_name[0]} = False ')
                if len(groups[-1]) > 1:
                    for i in range(1, num_mem):
                        f.write(f'AND #{relay_k_name[i]} = False ')
                    f.write('THEN\n')
                    finish_group = 0
                    while finish_group < len(groups[-1]):
                        f.write(f'\t#{solenoids[_index_]} := TRUE;\n')
                        f.write(f'\tIF #{solenoids[_index_]} = True THEN\n\t')
                        f.write(f'\t#{limit_switch_list[_index_]} := TRUE;\n')
                        convert_on_off = limit_switch_list[_index_][0]
                        for on_off in range(_index_ + 1,len(limit_switch_list)):
                            if convert_on_off == limit_switch_list[on_off][0]:
                                f.write(f'\t\t#{limit_switch_list[on_off]} := FALSE;\n')
                                break
                            else:
                                continue
                        for on_off in range(_index_):
                            if convert_on_off == limit_switch_list[on_off][0]:
                                f.write(f'\t\t#{limit_switch_list[on_off]} := FALSE;\n')
                                break
                            else:
                                continue
                        f.write('\tEND_IF;\n')
                        if finish_group != (len(groups[-1]) - 1):
                            f.write(f'\tIF #{limit_switch_list[_index_]} = True THEN\n\t')
                        _index_ += 1
                        finish_group += 1
                    f.write('END_IF;\n')
                else:
                    for i in range(1, num_mem):
                        f.write(f'AND #{relay_k_name[i]} = False ')
                    f.write('THEN\n')
                    f.write(f'\t#{solenoids[_index_]} := TRUE;\n')
                    f.write(f'\tIF #{solenoids[_index_]} = True THEN\n\t\t')
                    f.write(f'#{limit_switch_list[_index_]} := TRUE;\n\t')
                    convert_on_off = limit_switch_list[_index_][0]
                    for on_off in range(_index_ + 1,len(limit_switch_list)):
                        if convert_on_off == limit_switch_list[on_off][0]:
                            f.write(f'\t#{limit_switch_list[on_off]} := FALSE;\n\t')
                            break
                        else:
                            continue
                    for on_off in range(_index_):
                        if convert_on_off == limit_switch_list[on_off][0]:
                            f.write(f'\t#{limit_switch_list[on_off]} := FALSE;\n\t')
                            break
                        else:
                            continue
                    f.write('END_IF;\nEND_IF;\n')
            f.close()
            return groups_global, relay_k_name_global, relay_memories_global, limit_switch_list_bool_global, limit_switch_list_global

class data_table():
    def __init__(self):
        global groups_global, relay_k_name_global, relay_memories_global, limit_switch_list_bool_global, limit_switch_list_global
        self.groups = groups_global
        self.relay_k_name = relay_k_name_global
        self.relay_memories = relay_memories_global
        self.limit_switch_list_bool = limit_switch_list_bool_global
        self.limit_switch_list = limit_switch_list_global

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

    def analysis(self, sequence_list):
        groups = []
        limit_switch_groups = []
        s = total_pistons(sequence_list)[2]
        limit_switches_list = limit_switches(sequence_list)
        limit_switches_list = [l.lower() for l in limit_switches_list]
        sequence_uppercase = [stroke.upper() for stroke in sequence_list]
        groups, limit_switch_groups = separate_groups(sequence_uppercase, limit_switches_list)
        self.structured_text(sequence_uppercase, limit_switch_groups, groups, limit_switches_list)
        draw_diagrams(sequence_uppercase, limit_switches_list)

    def normal(self):
        self.welcome()
        sequence_list = []
        stop_sequence = False
        try:
            while not stop_sequence:
                stroke, sequence_list = insert_stroke(sequence_list)
                if '/' in stroke:
                    del sequence_list[-1]
                    if len(sequence_list) == 0:
                        stop_sequence = False
                        break
                    stop_sequence = True
                    write_file(sequence_list)
                    self.analysis(sequence_list)
                else:
                    stop_sequence = False

        except KeyboardInterrupt:
            print(fill(bcolors.FAIL + "\n[!] User has terminated the script.\n" + bcolors.ENDC))

    def file(self):
        self.welcome()
        sequence_list = []
        sequence_list = read_file(sequence_list)
        if sequence_list is not Empty:
            self.analysis(sequence_list)
        else:
            print("The sequence is empty.")

    def structured_text(self, sequence_list, limit_switch_groups, groups, limit_switches_list):
        plc(sequence_list, limit_switch_groups, groups, limit_switches_list)
        data_table()

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