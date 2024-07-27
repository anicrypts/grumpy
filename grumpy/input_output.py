import csv, json
from musicscore import *
from musicxml.xmlelement.xmlelement import *
from .rhythm_calculator import RhythmCalculator, Offsets
from .filtration import OrFilter

# For write_rhythms_musicxml
partno = 0

########## CSV ##########
def get_csv_header():
    csv_header = [name for name in Offsets.__members__]
    csv_header.insert(0, 'Rhythm')
    return csv_header

def write_rhythms_csv(rc:RhythmCalculator, filename:str, rhythms=None):
    """
    In string form and with their calculated values, write rhythms in CSV
    format to the provided file in the output directory, creating it if it 
    doesn't exist and overwriting it if it does.

    Args:
        rc (RhythmCalculator)
        filename (str): The file to write to.
        rhythms (None | list[int]): Optional subset of rc.rhythms; if included,
            only these rhythms and their values are written.
    """
    # outfile = get_file_path(filename, OUTPUT_DIR)
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        header = get_csv_header()
        writer.writerow(header)
        if rhythms == None:
            rhythms_to_write = rc.rhythms
        else:
            rhythms_to_write = rhythms
        for rhythm in rhythms_to_write:
            row = list(rc.metrics[rhythm])
            rhythm_as_string = RhythmCalculator.rhythm_to_string(rhythm,
                                                                 rc.num_divs,
                                                                 rc.time_map)
            row.insert(0, rhythm_as_string)
            writer.writerow(row)

########## JSON ##########
def get_rhythm_dict(values:list):
    """
    Given a list of a rhythm and its calculated metrics, return a dictionary
    mapping the name of each metric to its value.
    """
    keys = [name for name in Offsets.__members__]
    keys.insert(0, 'Rhythm')
    rhythm_dict = {}
    for (key, val) in zip(keys, values):
        rhythm_dict[key] = val
    return rhythm_dict

def write_rhythms_json(rc:RhythmCalculator, filename:str, rhythms=None):
    """
    In string form and with their calculated values, write rhythms in JSON
    format to the provided file in the output directory, creating it if it 
    doesn't exist and overwriting it if it does.

    Args:
        rc (RhythmCalculator):
        filename (str): The file to write to.
        rhythms (None | list[int]): Optional subset of rc.rhythms; if included,
            only these rhythms and their values are written.
    """
    with open(filename, 'w') as jsonfile:
        json_objects = []
        if rhythms == None:
            rhythms_to_write = rc.rhythms
        else:
            rhythms_to_write = rhythms
        for rhythm in rhythms_to_write:
            json_object = list(rc.metrics[rhythm])
            rhythm_as_string = RhythmCalculator.rhythm_to_string(rhythm,
                                                                 rc.num_divs,
                                                                 rc.time_map)
            json_object.insert(0, rhythm_as_string)
            json_object = get_rhythm_dict(json_object)
            json_objects.append(json_object)
        json.dump(json_objects, jsonfile, indent=4)

########## MusicXML ##########
def write_rhythms_musicxml(rc:RhythmCalculator, filename:str, rhythms=None):
    """
    Write rhythms in MusicXML format to the given file in the output directory,
    creating it if it doesn't exist and overwriting it if it does.
    
    Args:
        rc (RhythmCalculator)
        filename (str): The file to write to. A .xml extension must be present
            for the file write to succeed.
        rhythms (None | list[int]): Optional subset of rc.rhythms; if included,
            only these rhythms are written. This function expects len(rhythms)
            > 0.
    """
    score = Score()
    #part names must be unique within the run of a program
    part = score.add_child(Part(f'p{partno}')) 
    partno += 1

    time = Time()
    time.signatures = [rc.get_num_beats(), rc.get_beat_type()]
    qd = 4/(rc.get_beat_type()*(rc.num_divs/rc.get_num_beats()))

    if rhythms == None:
        rhythms_to_write = rc.rhythms
    else:
        rhythms_to_write = rhythms

    for rhythm in rhythms_to_write:
        # Set up the measure
        measure = part.add_child(Measure(number=rhythm, time=time))
        clef = Clef(sign='percussion')
        staff = Staff(number=1, clef=clef)
        measure.add_child(staff)
        voice = staff.add_child(Voice(number=1))

        # Single-line staff
        stafflines = XMLStaffLines(value_=1)
        staff_details = XMLStaffDetails()
        staff_details.add_child(stafflines)
        attributes_l = measure.xml_object.get_children_of_type(XMLAttributes)
        attributes = attributes_l[0] # should only be one attribute
        attributes.add_child(staff_details)

        # Add the rhythm to the measure
        rhythm_as_str = RhythmCalculator.get_undelimited_bin(rhythm, rc.num_divs)
        events = [char for char in rhythm_as_str]

        for event in events:
            beat = voice.add_child(Beat(quarter_duration=qd))
            if (event == '0'):
                chord = Chord(0, qd)
                beat.add_child(chord) 
            else:
                chord = Chord(77, qd)
                beat.add_child(chord)

    score.export_xml(filename)

########## Session persistence ##########
class GrumpySession:
    """
    A GRuMPy user session, defined by a type of measure (RhythmCalculator)
    and filters.

    Attributes:
        rhythmCalculator (RhythmCalculator)
        filters (list[OrFilter])
    """
    def __init__(self, rc:RhythmCalculator):
        self.rhythm_calculator = rc
        self.filters = []

    @classmethod
    def from_file(cls, filename:str):
        """Initialize from a session saved in the specified file."""
        with open(filename, 'r') as savefile:
            as_json = json.load(savefile)
            session = cls(RhythmCalculator.from_json(as_json['rhythm_calculator']))
            session.filters = [OrFilter.from_json(f) for f in as_json['filters']]
            return session

    def get_serializable(self):
        """Return a serializable (for JSON) form of this instance."""
        self_dict = {}
        self_dict['rhythm_calculator'] = self.rhythm_calculator.get_serializable()
        self_dict['filters'] = [f.get_serializable() for f in self.filters]
        return self_dict

    def add_filter(self, f:OrFilter):
        """Add a filter to this session."""
        self.filters.append(f)

    def list_filters(self, spaces_off=0):
        """List the filters of this session in a human-friendly format."""
        for i, f in enumerate(self.filters):
            print(f'{i}. {f.get_name(spaces_off)}')
    
    def write_session(self, filename:str):
        """
        Write this session to the specified file, creating the file if it 
        doesn't exist and overwriting it if it does.
        """
        with open(filename, 'w') as savefile:
            json.dump(self.get_serializable(), savefile, indent=4)
