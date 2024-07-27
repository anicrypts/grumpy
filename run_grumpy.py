#!/usr/bin/env python3
from pathlib import Path
import os
from grumpy.rhythm_calculator import RhythmCalculator, Offsets
import grumpy.input_output as io
from grumpy.filtration import *

OUTPUT_DIR = os.path.join(os.getcwd(), 'output')
SESSION_DIR = os.path.join(os.getcwd(), 'sessions')

MAIN_MENU_MSG = 'Select one of the following options:\n' + \
                '\t1. Start a new session\n' + \
                '\t2. Exit the program\n'
SESSION_MSG =   'Select one of the following options:\n' + \
                '\t1. Save session output to CSV\n' + \
                '\t2. Save session output to JSON\n' + \
                '\t3. Save session output to MusicXML\n' + \
                '\t4. Add a new filter to the session\n' + \
                '\t5. Save filter output to CSV\n' + \
                '\t6. Save filter output to JSON\n' + \
                '\t7. Save filter output to MusicXML\n' + \
                '\t8. Return to the previous menu. This erases the current session.\n'
INT_INPUT_INVALID_MSG = 'Input invalid. Please provide an integer number.'
FILTER_TYPE_MSG = 'Create an AND or OR filter? (and/or)\n'
RHYTHM_FILTER_MSG = "Rhythm filters take the following format:\n" + \
                    "\t- They are of the same length as the rhythms they will be matched to.\n" + \
                    "\t- They consist of any of the four characters '1', '0', 'X', or '_'\n" + \
                    "\t- Include a 1 or 0 at positions you want to exactly match to that character.\n" + \
                    "\t- Include an underscore (_) between every beat.\n" + \
                    "\t- Include an X at any position that may be either a 1 or 0.\n"
GET_RHYTHM_FILTER_MSG = "Provide the pattern matching string for this rhythm filter.\n" + \
                        "Note that it will not be checked for validity.\n"
CALC_FILTER_MSG =   'A calculation filter applies to one computational model.\n' + \
                    'It has a minimum value and maximum value.'

def filter_selection_is_valid(sel:str, session:io.GrumpySession):
    sel_is_valid = False
    if sel.isdigit():
        sel = int(sel)
        sel_is_valid = sel >= 0 and sel < len(session.filters)
    return sel_is_valid

def get_filter_selection(session:io.GrumpySession):
    print('This session contains the following filters:\n')
    session.list_filters()
    sel = input('Enter the number corresponding to the filter of choice.\n')
    while not filter_selection_is_valid(sel, session):
        print('Invalid input.')
        sel = input('Enter the number corresponding to the filter of choice.\n')
    return int(sel)
 
def save_session_csv(session:io.GrumpySession):
    filename = input('Saving in CSV format. Please enter a name for the file.\n')
    filename = os.path.join(OUTPUT_DIR, filename)
    filename = Path(filename).with_suffix('.csv')
    io.write_rhythms_csv(session.rhythm_calculator, filename)
    print(f'File {filename} written in output directory.')

def save_session_json(session:io.GrumpySession):
    filename = input('Saving in JSON format. Please enter a name for the file.\n')
    filename = os.path.join(OUTPUT_DIR, filename)
    filename = Path(filename).with_suffix('.json')
    io.write_rhythms_json(session.rhythm_calculator, filename)
    print(f'File {filename} written in output directory.')

def save_session_musicxml(session:io.GrumpySession):
    filename = input('Saving in MusicXML format. Please enter a name for the file.\n')
    filename = os.path.join(OUTPUT_DIR, filename)
    filename = Path(filename).with_suffix('.xml')
    print('Writing... this may take a few minutes.')
    io.write_rhythms_musicxml(session.rhythm_calculator, filename)
    print(f'File {filename} written in output directory.')

def save_filter_result_csv(session:io.GrumpySession):
    f_idx = get_filter_selection(session)
    result = session.rhythm_calculator.get_filter_result(session.filters[f_idx]) 
    filename = input('Saving in CSV format. Please enter a name for the file.\n')
    filename = os.path.join(OUTPUT_DIR, filename)
    filename = Path(filename).with_suffix('.csv')
    io.write_rhythms_csv(session.rhythm_calculator, filename, rhythms=result)
    print(f'File {filename} written in output directory.')

def save_filter_result_json(session:io.GrumpySession):
    f_idx = get_filter_selection(session)
    result = session.rhythm_calculator.get_filter_result(session.filters[f_idx]) 
    filename = input('Saving in JSON format. Please enter a name for the file.]n')
    filename = os.path.join(OUTPUT_DIR, filename)
    filename = Path(filename).with_suffix('.json')
    io.write_rhythms_json(session.rhythm_calculator, filename, rhythms=result)
    print(f'File {filename} written in output directory.')

def save_filter_result_musicxml(session:io.GrumpySession):
    f_idx = get_filter_selection(session)
    result = session.rhythm_calculator.get_filter_result(session.filters[f_idx]) 
    if len(result) == 0:
        print('Result of filter contains no rhythms. MusicXML write cancelled.')
    else:
        filename = input('Saving in MusicXML format. Please enter a name for the file.\n')
        filename = os.path.join(OUTPUT_DIR, filename)
        filename = Path(filename).with_suffix('.xml')
        print('Writing... this may take a few minutes.')
        io.write_rhythms_musicxml(session.rhythm_calculator, filename,
                                  rhythms=result)
        print(f'File {filename} written in output directory.')

def menu_int_selection_valid(sel:str, hi:int):
    selection_valid = False
    if sel.isdigit():
        sel = int(sel)
        if (sel >= 1 and sel <= hi):
            selection_valid = True
    return selection_valid

def offset_is_valid(offset:str):
    return offset in Offsets.__members__

def get_offset_for_filter():
    print("The following computational models are available:\n")
    for i, name in enumerate(Offsets.__members__):
        print(f'\t{i}. {name}')
    offset = input("\nWhich computational model does this filter apply to? Provide a case-sensitive name.\n")
    while not offset_is_valid(offset):
        print("Input invalid. Specify the name of the computational model, e.g., nPVI\n")
        offset = input("Which computational model does this filter apply to? Provide a case-sensitive name.\n")
    offset_val = Offsets[offset].value
    return (offset, offset_val)

def get_max_for_filter():
    maxi = input("What is the maximum value for this filter?\n")
    while not maxi.isnumeric():
        print("Invalid input: please specify a number.")
        maxi = input("What is the maximum value for this filter?\n")
    return int(maxi)

def get_min_for_filter():
    mini = input("What is the minimum value for this filter?\n")
    while not mini.isnumeric():
        print("Invalid input: please specify a number.")
        mini = input("What is the minimum value for this filter?\n")
    return int(mini)

def create_calc_filter():
    print('Creating a calculation filter.\n')
    print(CALC_FILTER_MSG)
    offset_name, offset_val = get_offset_for_filter() 
    mini = get_min_for_filter()
    maxi = get_max_for_filter()
    cfilter = CalculationFilter(offset_name, offset_val, mini, maxi)
    print(f'Calculation filter created: offset {offset_name} min {mini} max {maxi}\n')
    return cfilter

def create_rhythm_filter():
    print('Creating a rhythm filter.')
    print(RHYTHM_FILTER_MSG)
    do_try = True
    while do_try:
        pattern = input(GET_RHYTHM_FILTER_MSG)
        retry = input(f"You entered: {pattern}\n Is this the pattern you want? (y/n)]\n")
        while retry.casefold() != 'y' and retry.casefold() != 'n':
            print("Invalid input.")
            retry = input(f"You entered: {pattern}\n Is this the pattern you want? (y/n)]\n")
        if retry.casefold() == 'n':
            pass # do nothing
        else:
            do_try = False
    rfilter = RhythmFilter(pattern)
    print(f"Rhythm filter created with pattern {pattern}\n")
    return rfilter

def create_or_filter():
    print('Creating an OR filter. An OR filter consists of at least one AND filter.')
    orfilter = OrFilter()
    add_another_filter = True
    while add_another_filter:
        print('Adding an AND filter to this OR filter.')
        andfilter = create_and_filter()
        orfilter.add_filter(andfilter)
        cont = input('AND filter added. Add another AND filter to this OR filter? (y/n)\n')
        while not (cont.casefold() == 'y' or cont.casefold() == 'n'):
            cont = input('Input invalid. Please specify y or n.')
        if cont.casefold() == 'y':
            pass
        else:
            add_another_filter = False
    print(f'OR filter created:\n{orfilter.get_name()}\n')
    return orfilter

def create_and_filter():
    print('Creating an AND filter.')
    andfilter = AndFilter()
    add_another_filter = True
    while add_another_filter:
        ftype = input('Which type of filter do you want to add? (Calculation/Rhythm)\n')
        while not (ftype.casefold() == 'calculation' or
                   ftype.casefold() == 'rhythm'):
            ftype = input("Input invalid. Please specify calculation or rhythm:\n")
        if ftype.casefold() == 'rhythm':
            print('If this filter already has a rhythm filter, the existing one will be replaced.')
            f = create_rhythm_filter()
            andfilter.update_rhythm_filter(f)
        else:
            f = create_calc_filter()
            andfilter.add_calculation_filter(f)
        cont = input('Filter added. Add another filter to this AND filter? (y/n)\n')
        while not (cont.casefold() == 'y' or cont.casefold() == 'n'):
            cont = input('Input invalid. Please specify y or n.\n')
        if cont.casefold() == 'y':
            pass
        else:
            add_another_filter = False
    print(f'AND filter created:\n{andfilter.get_name()}\n')
    return andfilter

def ftype_sel_is_valid(sel:str):
    return (sel.casefold() == 'and' or sel.casefold() == 'or')

def add_filter_to_session(session:io.GrumpySession):
    print('Adding a new filter to the session.')
    ftype = input(FILTER_TYPE_MSG)
    while not ftype_sel_is_valid(ftype):
        print("Invalid input. Please specify 'and' or 'or'.")
        ftype = input(FILTER_TYPE_MSG)
    if (ftype.casefold() == 'and'):
        andfilter = create_and_filter()
        orfilter = OrFilter()
        orfilter.add_filter(andfilter)
        session.add_filter(orfilter)
    else:
        orfilter = create_or_filter()
        session.add_filter(orfilter)

def get_time_sig():
    time_sig_upper = input('What is the numerator of the time signature of the measure of interest?\n')
    while(not time_sig_upper.isdigit()):
        print(INT_INPUT_INVALID_MSG)
        time_sig_upper = input('What is the numerator of the time signature of the measure of interest?\n')

    time_sig_lower = input('What is the denominator of the time signature of the measure of interest?\n')
    while(not time_sig_lower.isdigit()):
        print(INT_INPUT_INVALID_MSG)
        time_sig_lower = input('What is the denominator of the time signature of the measure of interest?\n')
    
    time_sig_upper = int(time_sig_upper)
    time_sig_lower = int(time_sig_lower)
    return (time_sig_upper, time_sig_lower)

def get_num_divs():
    num_divs = input('How many subdivisions are in the measure? For example, a 3/4 ' + \
                     'measure with 8th note granularity has 6 subdivisions.\n')
    while (not num_divs.isdigit()):
        print(INT_INPUT_INVALID_MSG)
        num_divs = input('How many subdivisions are in the measure? For example, a 3/4 ' + \
                        'measure with 8th note granularity has 6 subdivisions.\n')
    return int(num_divs)

def get_unchecked_time_map(num_divs:int):
    total, i = 0, 1
    time_map = []

    # sd = input(f'How many subdivisions are in beat {i} of the measure?\n')
    # while (not sd.isdigit()):
    #     print(INT_INPUT_INVALID_MSG)
    #     sd = input('How many subdivisions are in the first beat of the measure?\n')
    # sd = int(sd)
    # time_map.append(sd)
    # total += sd
    # i += 1
    
    while total < num_divs:
        sd = input(f'How many subdivisions are in beat {i} of the measure?\n')
        while (int(sd) <= 0 if sd.isdigit() else True):
            print(INT_INPUT_INVALID_MSG)
            sd = input(f'How many subdivisions are in beat {i} of the measure?\n')
        sd = int(sd)
        time_map.append(sd)
        total += sd
        i += 1

    return (total, time_map)

def get_time_map(num_divs:int):
    total, time_map = get_unchecked_time_map(num_divs)
    while total > num_divs:
        print(f'Invalid input: sum does not equal total subdivions in the measure: \
              \n\tsum of input = {total}\n\tnumber of subdivisions = {num_divs}\n' + \
              'Restarting from first beat.')
        total, time_map = get_unchecked_time_map(num_divs)
    return time_map

def init_new_session():
    print('Initializing new session.')
    time_sig = get_time_sig()
    num_divs = get_num_divs()
    time_map = get_time_map(num_divs)
    print('Generating and calculating... this may take several minutes.')
    rc = RhythmCalculator(num_divs, time_map, time_sig)
    print('Done generating and calculating!')
    session = io.GrumpySession(rc)
    return session

def new_session():
    session = init_new_session()
    print('New session created.')
    exit_menu = False
    while not exit_menu:
        sel = input(SESSION_MSG)
        while not menu_int_selection_valid(sel, 8):
            print('Invalid input. Please specify a number from 1-8.')
            sel = input(SESSION_MSG)
        sel = int(sel)
        match sel:
            case 1:
                save_session_csv(session)
            case 2:
                save_session_json(session)
            case 3:
                save_session_musicxml(session)
            case 4:
                add_filter_to_session(session)
            case 5:
                save_filter_result_csv(session)
            case 6:
                save_filter_result_json(session)
            case 7:
                save_filter_result_musicxml(session)
            case 8:
                exit_menu = True
    main_menu()

def main_menu_selection_valid(sel:str):
    selection_valid = False
    if sel.isdigit():
        sel = int(sel)
        if (sel >= 1 and sel <= 2):
            selection_valid = True
    return selection_valid

def get_main_menu_selection():
    sel = input(MAIN_MENU_MSG)
    while not main_menu_selection_valid(sel):
        print('Invalid input. Please specify 1 or 2.')
        sel = input(MAIN_MENU_MSG)
    return int(sel)

def main_menu():
    # Set up output directory
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    
    exit_program = False
    while not exit_program:
        sel = get_main_menu_selection()
        if (sel == 1):
            new_session()
        else:
            exit_program = True
    print('Exiting program. Goodbye!')
    exit()

def main():
    print('Welcome to GRuMPy!\n')
    main_menu()

if __name__ == '__main__':
    main()