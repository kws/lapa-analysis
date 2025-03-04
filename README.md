# LAPA: Language Pattern Analyser. A Digital Tool for the Analysis of Patterns in Spelled Language Sounds in Historical Dutch Theatre Plays 
## Title

LAPA allows for converting digitised early modern Dutch theatre plays into (presumed) phonetic script (SAMPA). To achieve this, a ruleset has been created that codifies the transliteration to SAMPA. This codebase contains parsers for the rule sets (xls format), parsers for the digitised texts (naf xml) and logic to perform counts and correlations.

## File structure
```bash
|__ classes:             all business logic related to parsing the dictionary and litterature text, 
|     |                  executing phoenetic translitteration (in SAMPA) and performing tallying across multiple
|     |                  dimensions.
|     |
|     |__ counter.py:    classes to count emotions and sampa characters. Consists of simple mappings, getters and 
|     |                  setters.
|     |__ sampify.py:    classes to parse (and load) the smapa translitteration dictionary (excel) and operate as
|     |                  a translitteration engine once rules are loaded.
|     |__ naf.py:        classes to parse the naf xml file. These classes are very specific for the file format;
|     |                  it assumes a fixed xml structure, including word, lemma and emotions. 
|     |                  Once the file is parsed, translation to sampa and tallying is executed.
|     |__ tests.py:      Tests tot assert all classes work as designed against real-life scenario
|     |__ test_static:   Files used in the tests
|
|__ validate_cli.py:     helper tool to validate the quality of a dictionary file. 
|                        Provided with a reference translation file, it will assert translations against expected 
|                        translation and generate a report file.
|__ sampify_cli.py:      cli tool to generate excel with counts, given naf.xml and rules.xls.

```

## Running the code
The following command will produce an excel output file with counts per sampa sound, as well as a set of debug and warning log files.

```bash
>> python3 sampify.py --naf '/path/to/naf.xml' --rules '/path/to/rules.xls' --output '/path/to/write/outputs'
```

## Sample files
A sample naf xml and rule excel are provided in the folder `sources`.
