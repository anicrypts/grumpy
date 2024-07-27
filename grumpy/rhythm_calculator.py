import os, shutil
from enum import Enum, unique, auto
import numpy as np
from .synpy import *
from .filtration import OrFilter

SIG_DIGS = 3
BEAT_DELIMITER = '_'
RHY_DIR_PATH = os.path.join(os.path.curdir, 'rhy')
RHY_FILE_PATH = os.path.join(RHY_DIR_PATH, 'temp.rhy')

@unique
class Offsets(Enum):
    """
    Offsets defines all the calculations implemented in this program.
    
    Add new offsets with the statement:
    NewOffset = auto()
    """
    Density = 0
    nPVI = auto()
    LHL = auto()
    PRS = auto()
    TMC = auto()
    TOB = auto()
    # Add any new offsets here

class RhythmCalculator:
    """
    A RhythmCalculator instance is defined by its of measure, in terms of
    time signature and subdivision. 

    Attributes:
        num_divs (int): The number of possible events (i.e., subdivisions) in
            a measure. For example:
                4/4 time and 16th note subdivision -> num_divs = 16
                3/4 time and 8th note subdivision  -> num_divs = 6
                6/8 time and 8th note subdivision  -> num_divs = 6
        time_map (list[int]): A list of the number of subdivisions in each 
            consecutive beat of a measure. For example:
                4/4 time and 16th note subdivision: time_map = [4,4,4,4]
                6/8 time and 8th note subdivision:  time_map = [3,3] 
                7/8 time and 8th note subdivision:  time_map = [3,2,2]
        time_sig (tuple): The time signature of the measure.
        num_rhythms (int): The number of rhythms that exist for the given 
            number of subdivisons (num_divs). Rhythms are represented by the 
            binary form of an integer, where 1 indicates an event and 0 
            indicates no event.
        rhythms (list[int]): A list of all rhythms possible in a measure. 
            Rhythms are represented by the binary form of an integer, where 1 
            indicates an event and 0 indicates no event, read from most 
            significant bit to least significant bit.
        metrics (numpy.array): A 2D array of the calculated metrics for each 
            generated rhythm.
    """

    def __init__(self, num_divs:int, time_map:list, time_sig:tuple):
        self.num_divs = num_divs
        self.time_map = time_map
        self.time_sig = time_sig
        self.num_rhythms = 2**num_divs
        self.rhythms = list(range(self.num_rhythms))
        self.metrics = np.empty((self.num_rhythms, len(Offsets)), order='C')
        self.calc_metrics()

    @classmethod
    def from_json(cls, as_json):
        """Initialize from JSON-formatted data."""
        rc = cls(as_json['num_divs'], as_json['time_map'], as_json['time_sig'])
        return rc
    
    def get_serializable(self):
        """Return a serializable (for JSON) form of this instance."""
        return {'num_divs': self.num_divs, 'time_map': self.time_map,
                'time_sig': self.time_sig}
    
    def to_rhy(self, rhythm:int):
        """
        Return a .rhy (compatible with SynPy) representation of rhythm,
        including the time signature.
        """
        time_sig_str = 'T{' + str(self.time_sig[0]) + '/' + \
            str(self.time_sig[1]) + '}'

        rhythm_as_bin = RhythmCalculator.get_undelimited_bin(rhythm,
                                                             self.num_divs)
        bits = list(rhythm_as_bin)
        velocity_seq = 'V{'
        for bit in bits:
            velocity_seq = velocity_seq + bit + ','
        velocity_seq = velocity_seq[:-1] + '}'

        as_rhy_str = time_sig_str + '\n' + velocity_seq
        return as_rhy_str

    def get_density(self, rhythm:int):
        return rhythm.bit_count()

    def get_npvi(self, rhythm:int):
        # zero or one events in rhythm
        if (rhythm == 0 or (rhythm.bit_count() == 1)):
            return 0

        # strip leading zeroes
        s = bin(rhythm)
        s = s.lstrip('-0b')

        # put each bit as an element of a list of ints
        bits = list(s)
        bits = list(map(int, bits))

        # list of durations between notes
        durations = []
        duration = 1
        # we already know the first bit is 1 as we stripped leading 0s
        for bit in bits[1:]:
            # start of a new note
            if (bit == 1):
                durations.append(duration)
                duration = 1
            # bit is 0 - continuation of previous note
            else:
                duration += 1
        durations.append(duration) #the last duration

        # list of summing terms
        pv = []
        for (d0, d1) in zip(durations, durations[1:]):
            val = (abs(d0 - d1)/(d0 + d1))*200
            pv.append(val)

        npvi = sum(pv)/len(pv)
        return npvi

    def get_synpy_result(self, rhythm:int, model:str):
        output = syncopation.calculate_syncopation(model, RHY_FILE_PATH)
        return output['summed_syncopation']

    def get_lhl(self, rhythm:int):
        lhl = self.get_synpy_result(rhythm, LHL)
        # SynPy returns -1 for no syncopation - correct to 0
        if (lhl == -1):
            lhl = 0
        return lhl
    
    def get_prs(self, rhythm:int):
        return self.get_synpy_result(rhythm, PRS)
    
    def get_tmc(self, rhythm:int):
        return self.get_synpy_result(rhythm, TMC)
    
    def get_tob(self, rhythm:int):
        return self.get_synpy_result(rhythm, TOB)
    
    def calc_all(self, rhythm:int):
        """
        Calculate the value of each computational model, as defined in Offsets,
        for param rhythm, populating self.metrics
        """
        rhydata = self.to_rhy(rhythm)
        with open(RHY_FILE_PATH, 'w') as rhyfile:
            rhyfile.write(rhydata)
        self.metrics[rhythm][Offsets.Density.value] = self.get_density(rhythm)
        self.metrics[rhythm][Offsets.nPVI.value] = round(self.get_npvi(rhythm),
                                                         SIG_DIGS)
        self.metrics[rhythm][Offsets.LHL.value] = self.get_lhl(rhythm)
        self.metrics[rhythm][Offsets.PRS.value] = self.get_prs(rhythm)
        self.metrics[rhythm][Offsets.TMC.value] = self.get_tmc(rhythm)
        self.metrics[rhythm][Offsets.TOB.value] = self.get_tob(rhythm)

    def calc_metrics(self):
        """
        Calculate the value of each computational model, as defined in
        Offsets, for each rhythm of self, populating self.metrics
        """
        if not os.path.exists(RHY_DIR_PATH):
            os.mkdir(RHY_DIR_PATH)
        for rhythm in self.rhythms:
            self.calc_all(rhythm)
        shutil.rmtree(RHY_DIR_PATH)

    @staticmethod
    def get_undelimited_bin(rhythm:int, num_divs:int):
        """
        Return an undelimted string representation of the rhythm, e.g., 
        '101010'
        """
        #'016b' -> width 16, fill with 0s
        format_str = '0{}b'.format(num_divs) 
        #undelimited binary
        rhythm_as_str = format(rhythm,format_str) 
        return rhythm_as_str
        
    @staticmethod
    def rhythm_to_string(rhythm:int, num_divs:int, time_map:list[int]):
        """
        Return a string representation of the rhythm with delimited beats,
        e.g., '101_010'
        """
        rhythm_as_str = RhythmCalculator.get_undelimited_bin(rhythm, num_divs)

        if (len(time_map) > 1):
            lo, hi = 0, 0
            substrings = []
            for val in time_map:
                lo = hi
                hi = hi + val
                substrings.append(rhythm_as_str[lo:hi])
            rhythm_as_str = BEAT_DELIMITER.join(substrings)

        return rhythm_as_str

    def get_filter_result(self, f:OrFilter):
        """
        Return a list of rhythms, in integer form, that satisfy the given
        filter.
        """
        matching_rhythms = []
        for rhythm in self.rhythms:
            rhythm_as_str = RhythmCalculator.rhythm_to_string(rhythm,
                                                              self.num_divs,
                                                              self.time_map)
            matches = f.matches(rhythm_as_str, self.metrics[rhythm])
            if matches:
                matching_rhythms.append(rhythm)
        return matching_rhythms
    
    def get_num_beats(self):
        """Return the number of beats in this measure."""
        return self.time_sig[0]
    
    def get_beat_type(self):
        """Return the type of beat (beat subdivision) of this measure."""
        return self.time_sig[1]
