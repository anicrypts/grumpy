SP_FILL = ' ' * 4

class RhythmFilter:
    """ 
    A RhythmFilter is a string consisting of any of the four characters '1',
    '0', 'X', or '_'. To match a RhythmFilter, a rhythm (in its string
    representation) must:
        - Exactly match any 1's or 0's.
        - Exactly match any underscores. These correspond to the subdivision of
        the measure, and rhythms should only be matched to filters of the
        corresponding time signature and subdivision.
        - Be of the same length.
        - Contain either a 1 or 0 in place of an X.

    Attributes:
        pattern (str): The beat pattern to be matched for this filter.
    """
    def __init__(self, pattern:str):
        self.pattern = pattern

    @classmethod
    def from_json(cls, as_json):
        """Initialize frorm JSON-formatted data."""
        rf = cls(as_json)
        return rf

    def get_serializable(self):
        """Return a serializable (for JSON) form of this instance."""
        return self.pattern
    
    def matches(self, rhythm:str):
        """Return True if param rhythm matches self's beat pattern."""
        if (len(rhythm) != len(self.pattern)):
            return False
        matches = True
        for (c1, c2) in zip(rhythm, self.pattern):
            matches = matches and ((c1 == c2) or (c2 == 'X'))
            pass
        return matches
    
    def get_name(self):
        """Return a pretty name for this filter."""
        return f'RHYTHM:{self.pattern}'

class CalculationFilter:
    """
    Attributes:
        offset_name (str): The calculation to which this filter applies
        offset_val (int): The offset of the calculation this filter applies to
        min (int): Minimum value of calculation (inclusive)
        max (int): Maximum value of calculation (inclusive)
    """
    def __init__(self, offset_name:str, offset_val:int, mini:int, maxi:int):
        self.offset_name = offset_name
        self.offset_val = offset_val
        self.min = mini
        self.max = maxi
    
    @classmethod
    def from_json(cls, as_json):
        """Initialize from JSON-formatted data."""
        cf = cls(as_json['offset_name'], as_json['offset_val'], as_json['min'],
                 as_json['max'])
        return cf

    def get_serializable(self):
        """Return a serializable (for JSON) form of this instance."""
        self_dict = {'offset_name': self.offset_name,
                     'offset_val': self.offset_val,
                     'min': self.min,
                     'max': self.max}
        return self_dict

    def matches(self, calculation:int):
        """Return True if param calculation matches self's filter."""
        return (calculation >= self.min and calculation <= self.max)
    
    def get_name(self):
        """Return a pretty name for this filter."""
        return f'CALCULATION:{self.offset_name}_min{self.min}_max{self.max}'


class AndFilter:
    """
    An AndFilter consists of:
        - At most, one RhythmFilter.
        - At most, one CalculationFilter per calculation as defined in Offsets.

    Attributes:
        rhythm_filter (None | RhythmFilter)
        calc_filters (list[CalculationFilter])
    """
    def __init__(self):
        """Initialize empty AndFilter."""
        self.calc_filters = []
    
    @classmethod
    def from_rfilter(cls, rf:RhythmFilter):
        """Initialize with a RhythmFilter."""
        andfilter = cls()
        andfilter.rhythm_filter = rf
        return andfilter

    @classmethod
    def from_json(cls, as_json):
        """Initialize from JSON-formatted data."""
        andfilter = cls()
        if 'rhythm_filter' in as_json:
            andfilter.update_rhythm_filter(RhythmFilter.from_json(as_json['rhythm_filter']))
        if 'calc_filters' in as_json:
            andfilter.calc_filters = [CalculationFilter.from_json(cf)
                                      for cf in as_json['calc_filters']]
        return andfilter

    def get_serializable(self):
        """Return a serializable (for JSON) form of this instance."""
        self_dict = {}
        if hasattr(self, 'rhythm_filter'):
            self_dict['rhythm_filter'] = self.rhythm_filter.get_serializable()
        if self.calc_filters:
            self_dict['calc_filters'] = [cf.get_serializable() for cf in 
                                         self.calc_filters]
        return self_dict

    def update_rhythm_filter(self, rf:RhythmFilter):
        """Assign a new rhythm filter to this instance."""
        self.rhythm_filter = rf
        
    def add_calculation_filter(self, cf:CalculationFilter):
        self.calc_filters.append(cf)

    def matches(self, rhythm:str, calculations:list):
        """
        Return True if the given rhythm, and its calculations, match all of
        self's filters.

        Arguments:
            rhythm (str): The string representation of a rhythm
            calculations (list[int]): The calculated values associated with the
                passed rhythm.
        """
        matches = True
        if hasattr(self, 'rhythm_filter'):
            matches = matches and self.rhythm_filter.matches(rhythm)
        if hasattr(self, 'calc_filters'):
            for cf in self.calc_filters:
                matches = matches and cf.matches(calculations[cf.offset_val])
        return matches
    
    def get_name(self, spaces_off=0):
        """Return a pretty name for this filter."""
        spfill = SP_FILL * 2
        name = 'AND:'
        if hasattr(self, 'rhythm_filter'):
            name = f'{name}\n{' ' * spaces_off}{spfill}{self.rhythm_filter.get_name()}'
        if hasattr(self, 'calc_filters'):
            for cf in self.calc_filters:
                name = f'{name}\n{' ' * spaces_off}{spfill}{cf.get_name()}'
        return name
        

class OrFilter:
    """ An OrFilter consists of at least one AndFilter.
    
    Attributes:
        andfilters (list[AndFilter])
    """
    def __init__(self):
        """Initialize empty OrFilter."""
        self.andfilters = []

    @classmethod
    def from_andfilters(cls, andfilters:list[AndFilter]):
        orfilter = cls()
        orfilter.andfilters = andfilters

    
    @classmethod
    def from_json(cls, as_json):
        """Initialize from JSON-formatted data."""
        orfilter = cls()
        orfilter.andfilters = [AndFilter.from_json(af) for af in as_json]
        return orfilter
    
    def get_serializable(self):
        """Return a serializable (for JSON) form of this instance."""
        return [af.get_serializable() for af in self.andfilters]

    def add_filter(self, f:AndFilter):
        self.andfilters.append(f)

    def matches(self, rhythm:str, calculations:list):
        matches = True
        for f in self.andfilters:
            matches = matches and f.matches(rhythm, calculations)
        return matches

    def get_name(self, sp_off=0):
        """Return a pretty name for this filter."""
        name = 'OR:'
        for f in self.andfilters:
            name = f'{name}\n{' ' * sp_off}{SP_FILL}{f.get_name(sp_off)}'
        return name