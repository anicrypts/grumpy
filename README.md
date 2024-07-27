# GRuMPy: The Generator of Rhythms und Metrics
GRuMPy is a Python program for generating rhythms and applying rhythmic characteristic models to those rhythms.
## Features
### Generation and Calculation
The user defines a measure of music in terms of meter, beat subdivision, and subdivision organization. GRuMPy generates every possible combination of rhythmic events in the given measure.

For all generated rhythms, the following calculations are performed:
- Density (number of notes in a measure)
- Durational variability, using nPVI (Grabe & Low, 2002)
- LHL (Longuet-Higgins & Lee, 1984)
- PRS (Pressing, 1997)
- TMC, 'Metric Complexity' (Toussaint, 2002)
- TOB, 'Off-beatness' (Toussaint, 2005)

### Filtration
The user may filter generated rhythms on the basis of:
- Any of the calculated rhythmic values, for a single value or range.
- Specific rhythmic characteristics; for example, an event on every other beat.

Multiple filters can be applied inclusively or exclusively.

### Input/output
- Generated rhythms and their accompanying calculations can be output in CSV and JSON format.
- Generated rhythms, before or after filtering, can be output in the MusicXML format. 

### Considerations
- GRuMPy doesn’t consider accented notes, dynamics, or note duration, so it’s not compatible with syncopation models that rely on these characteristics.

## How to use GRuMPy
### 1. Set up a virtual environment
I recommend running GRuMPy in a virtual environment for best practice installing the musicscore and NumPy libraries that GRuMPy depends on. 
Here is one way to do so if you're not familiar with setting one up:
1. From a command line (e.g., Terminal on macOS, PowerShell on Windows) navigate to the **parent** grumpy directory on your computer.
2. Install the virtual environment:
- `python3 -m venv .venv`
3. Activate the virtual environment:
- On MacOS/Linux: `source .venv/bin/activate`
- On Windows: `.venv\Scripts\activate`
- You will know the virtual environment is active if `(.venv)` appears at the front of your command-line prompt.
4. Install dependencies:
- `pip install -r requirements.txt`
5. When you're done, deactivate the virtual environment with `deactivate`. Activate the virtual environment (step 3) each time you use GRuMPy. You don't need to reinstall the virtual environment or dependencies.

### 2a. Run GRuMPy from the command line
From a command line prompt, navigate to the **parent** grumpy directory. Execute an interactive interface to GRuMPy with the command: `./run_grumpy`

### 2b. Use a script
```
import grumpy.rhythm_calculator as rc
import grumpy.input_output as io

# RhythmCalculator objects perform generation and calculation on instantiation
four_four_eighths = rc.RhythmCalculator(8, [2, 2, 2, 2], (4, 4))

# Write rhythms & calculations in CSV format
io.write_rhythms_csv(four_four_eighths, 'output/grumpy_448.csv')

# Write rhythms & calculations in JSON format 
io.write_rhythms_json(four_four_eighths, 'output/grumpy_448.json')

# Write rhythms in MusicXML format
io.write_rhythms_musicxml(four_four_eighths, 'output/grumpy_448.xml')
```
## Acknowledgements
- Sincere thanks to Dr. Leigh VanHandel for supporting this project. Check out the VanLab here: https://blogs.ubc.ca/drvan/theoryandcognition/
- GRuMPy utilises the SynPy program for syncopation calculations.
    - https://code.soundsoftware.ac.uk/projects/syncopation-dataset
    - GRuMPy uses a subset of the SynPy program, converted for Python 3.