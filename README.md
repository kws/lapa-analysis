# LAPA: Language Pattern Analyser

A Digital Tool for the Analysis of Patterns in Spelled Language Sounds in Historical Dutch Theatre Plays.

LAPA allows for converting digitised early modern Dutch theatre plays into (presumed) phonetic script (SAMPA). To achieve this, a ruleset has been created that codifies the transliteration to SAMPA. This codebase contains parsers for the rule sets (xls format), parsers for the digitised texts (naf xml) and logic to perform counts and correlations.

The motivation for this project can be found in the following publication:

Smitskamp, Fieke. (2024). From Ah! to Little Z: Clustering Spelled Language Sounds in Early Modern Dutch Theatre Plays (1570-1800). BMGN - Low Countries Historical Review, 139, 7-31. https://doi.org/10.51769/bmgn-lchr.13868

To test the interactive notebooks, you can simply click the badge below:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/kws/lapa-analysis/HEAD?urlpath=lab/tree/notebooks/index.ipynb)

or open this URL in your browser:

https://mybinder.org/v2/gh/kws/lapa-analysis/HEAD?urlpath=lab/tree/notebooks/index.ipynb

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
poetry run lapa-ng --help
```

## File Structure

```bash
.
├── fixtures/             # Sample files for testing and CLI runs
├── lapa_classic/         # Core business logic for parsing and processing
│   ├── counter.py        # Classes to count emotions and sampa characters
│   ├── sampify.py        # Classes to parse and load the sampa transliteration dictionary
│   └── naf.py            # Classes to parse the naf xml file
│
├── tests/                # Test suite
│   └── test_classic.py   # Tests for lapa_classic functionality
│
└── lapa_ng/             # Next generation version of LAPA (under development)
```

## Code Documentation

The code documentation can be found in the `docs` directory or browsed on [https://kws.github.io/lapa-analysis/](https://kws.github.io/lapa-analysis/).

## Usage

LAPA-NG provides a command-line interface for common operations. The system uses a factory pattern to create different types of matchers based on a specification string.

### Matcher Specification

The matcher specification follows the format:

    [prefix:][filename[#sheet]][?options]

Where:
- `prefix`: Optional prefix indicating the type of matcher ('ng' or 'classic')
- `filename`: Path to the rules file (Excel or YAML)
- `sheet`: Optional sheet name for Excel files
- `options`: Optional query string parameters (e.g., ?sort=numeric)

Available options for the 'ng' prefix:
- `sort`: Rule sorting method ('numeric' or 'alpha')
  - `numeric`: Sort rules by numeric priority (default)
  - `alpha`: Sort rules alphabetically by letter and priority

Examples:
```bash
# Next-gen matcher with specific sheet and numeric sorting (default)
lapa-ng translate-words 'ng:rules.xlsx#RULES' word1 word2

# Next-gen matcher with alpha sorting
lapa-ng translate-words 'ng:rules.xlsx#RULES?sort=alpha' word1 word2

# Classic matcher, default sheet
lapa-ng translate-words 'classic:rules.xlsx' word1 word2

# Next-gen matcher (default prefix)
lapa-ng translate-words 'rules.xlsx#RULES' word1 word2
```

### Transcribing Words

Transcribe one or more words using the specified rules:

```bash
# Using numeric sorting (default)
lapa-ng translate-words 'rules.xlsx#RULES' word1 word2 word3

# Using alpha sorting
lapa-ng translate-words 'rules.xlsx#RULES?sort=alpha' word1 word2 word3
```

This will output the phonetic transcription in SAMPA format for each word.

### Processing NAF Files

Process text from NAF (NLP Annotation Framework) files:

```bash
# Using numeric sorting (default)
lapa-ng translate-naf 'rules.xlsx#RULES' input.naf

# Using alpha sorting
lapa-ng translate-naf 'rules.xlsx#RULES?sort=alpha' input.naf
```

This will:
1. Read the NAF file
2. Apply the specified rules
3. Output a CSV file with detailed transcription information

### Converting Rules

Convert Excel-based rules to YAML format:

```bash
lapa-ng convert-excel rules.xlsx rules.yaml --sheet RULES
```

### Getting Help

You can get help for any command by adding `--help`:

```bash
lapa-ng --help
lapa-ng translate-words --help
lapa-ng translate-naf --help
lapa-ng convert-excel --help
```

## Sample Files

Sample NAF XML and rules files are provided in the `fixtures` directory for testing and reference.
