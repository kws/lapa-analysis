# LAPA: Language Pattern Analyser

A Digital Tool for the Analysis of Patterns in Spelled Language Sounds in Historical Dutch Theatre Plays.

LAPA allows for converting digitised early modern Dutch theatre plays into (presumed) phonetic script (SAMPA). To achieve this, a ruleset has been created that codifies the transliteration to SAMPA. This codebase contains parsers for the rule sets (xls format), parsers for the digitised texts (naf xml) and logic to perform counts and correlations.

The motivation for this project can be found in the following publication:

Smitskamp, Fieke. (2024). From Ah! to Little Z: Clustering Spelled Language Sounds in Early Modern Dutch Theatre Plays (1570-1800). BMGN - Low Countries Historical Review, 139, 7-31. https://doi.org/10.51769/bmgn-lchr.13868

## Installation

This project uses [Poetry](https://python-poetry.org/) for dependency management. To get started:

1. Install Poetry (if you haven't already):

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Clone the repository and install dependencies:

   ```bash
   git clone <repository-url>
   cd lapa-analysis
   poetry install
   ```

3. Activate the virtual environment:

   ```bash
   poetry shell
   ```

Alternatively, you can run commands directly using `poetry run`:

```bash
poetry run python -m lapa_classic --help
```

## File Structure

```bash
.
├── fixtures/             # Sample files for testing and CLI runs
├── lapa_classic/         # Core business logic for parsing and processing
│   ├── counter.py        # Classes to count emotions and sampa characters
│   ├── sampify.py        # Classes to parse and load the sampa transliteration dictionary
│   ├── naf.py            # Classes to parse the naf xml file
│   ├── _cli.py           # Command-line interface
│   ├── __init__.py       # Package initialization
│   └── __main__.py       # Package entry point
│
├── tests/                # Test suite
│   └── test_classic.py   # Tests for lapa_classic functionality
│
└── lapa_ng/             # Next generation version of LAPA (under development)
```

## Code Documentation

The code documentation can be found in the `docs` directory or browsed on [https://kws.github.io/lapa-analysis/](https://kws.github.io/lapa-analysis/).

## Usage

The code provides two main commands through the CLI interface:

### Processing NAF files (sampify)

Process a NAF file using the specified rules to generate counts and translations:

```bash
python -m lapa_classic sampify -n '/path/to/naf.xml' -r '/path/to/rules.xls' -o '/path/to/output'
```

This will produce:

- An Excel file with counts per sampa sound
- A CSV file with translations
- Debug and warning log files

### Validating rules (validate)

Validate a rules file against a reference translation:

```bash
python -m lapa_classic validate -r '/path/to/rules.xls' -t '/path/to/test.txt' -o '/path/to/output'
```

This will generate a validation report showing any discrepancies between the rules and expected translations.

### Getting Help

You can get help for any command by adding `--help`:

```bash
python -m lapa_classic --help
python -m lapa_classic sampify --help
python -m lapa_classic validate --help
```

## Sample Files

Sample NAF XML and rules files are provided in the `fixtures` directory for testing and reference.
