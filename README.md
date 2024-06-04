# LAPA. A Digital Tool for the Analysis of Language Sound Patterns in Historical Dutch Theater Plays 
## Title
How can we analyze sound patterns of historical Dutch theatre? What can we learn about early modern Dutch language and culture by looking at sound patterns? The research for which this tool, called LAPA (Language Patterns Analyzer), is designed, has a stylometric character. It aims to characterize historical Dutch theater plays (1570-1800) on the basis of sound analysis. The sounds of early modern theater were pre-eminently intended to splash out loud from a stage, at a time when important cultural developments took place in literary movements and in the way in which language was thought of.

By analyzing sound patterns using LAPA, I follow in the footsteps of research in the field of (computational) sound research, quantitative analysis of cultural trends, text mining, sound classification and stylometric identification of plays, publishers and authors.

The method can basically be divided into three phases: first the phonemes in the texts were distinguished from each other, then the sounds were counted, and finally the sound patterns were modeled via a path of operations so that they could eventually lead to specific sound profiles, also called fingerprints. LAPA is programmed to perform the first two phases to generate the raw dataset. LAPA was created in close collaboration with dr. Ruben Vosmeer, who took care of the programming and devised the most appropriate way to properly and transparently test the quality of LAPA's operation.

LAPA allows for converting digitized early modern Dutch plays into phonetic script (SAMPA). To achieve this, a ruleset has been created that codifies the transliteration to SAMPA. This codebase contains parsers for the rule sets (xls format), parsers for the digitized texts (naf xml) and logic to perform counts and correlations.

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
