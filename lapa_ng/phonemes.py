"""
Phoneme handling for LAPA-NG.

This module provides functionality for working with phonemes, including
loading phoneme definitions from CSV files and splitting words into
their constituent phonemes.
"""

import csv
from pathlib import Path
from typing import Iterator

from lapa_ng.types import Phoneme

__all__ = ["PhonemeList"]

DEFAULT_PHONEME_FILE = Path(__file__).parent / "phonemes_default.csv"


class PhonemeList:
    """A collection of phonemes with methods for phoneme processing.

    This class provides functionality for working with a list of phonemes,
    including splitting words into phonemes and looking up phonemes by
    their SAMPA representation.
    """

    def __init__(self, phoneme_list: list[Phoneme]):
        """Initialize with a list of phonemes.

        Args:
            phoneme_list: List of phonemes to use, sorted by SAMPA length
        """
        # It's important that we test the longest phonemes first
        self.phoneme_list = sorted(
            phoneme_list, key=lambda x: len(x.sampa), reverse=True
        )

    def get_first(self, word: str) -> Phoneme | None:
        """Find the first phoneme that matches the start of a word.

        Args:
            word: The word to match against

        Returns:
            The matching phoneme, or None if no match is found
        """
        for phoneme in self.phoneme_list:
            if word.startswith(phoneme.sampa):
                return phoneme
        return None

    def split_phonemes(
        self, word: str, ignore_errors: bool = False
    ) -> tuple[Phoneme, ...]:
        """Split a word into its constituent phonemes.

        This method attempts to match the longest possible phonemes first,
        which is why the phoneme list is sorted by length in reverse order.

        Args:
            word: The word to split into phonemes
            ignore_errors: Whether to skip unknown characters instead of raising an error

        Returns:
            Tuple of phonemes that make up the word

        Raises:
            ValueError: If an unknown character is encountered and ignore_errors is False
        """
        phonemes = []
        while word:
            phoneme = self.get_first(word)
            if phoneme:
                phonemes.append(phoneme)
                word = word[len(phoneme.sampa) :]
            else:
                if not ignore_errors:
                    raise ValueError(f"No phoneme found for word: {word}")
                else:
                    word = word[1:]
        return tuple(phonemes)

    def __getitem__(self, key: int | str) -> Phoneme:
        """Get a phoneme by index or SAMPA representation.

        Args:
            key: Either an integer index or a SAMPA string

        Returns:
            The requested phoneme

        Raises:
            IndexError: If the index is out of range
            KeyError: If no phoneme is found for the given SAMPA string
        """
        if isinstance(key, str):
            for phoneme in self.phoneme_list:
                if phoneme.sampa == key:
                    return phoneme
            raise KeyError(f"No phoneme found for {key}")
        return self.phoneme_list[key]

    def __len__(self) -> int:
        """Return the number of phonemes in the list."""
        return len(self.phoneme_list)

    def __iter__(self) -> Iterator[Phoneme]:
        """Return an iterator over the phonemes."""
        return iter(self.phoneme_list)

    @classmethod
    def from_csv(cls, file_path: str) -> "PhonemeList":
        """Create a PhonemeList from a CSV file.

        The CSV file should have a header row followed by rows containing:
        SAMPA, IPA, example, notes

        Args:
            file_path: Path to the CSV file

        Returns:
            A new PhonemeList instance
        """
        with open(file_path, "r") as f:
            reader = csv.reader(f)
            _ = next(reader)  # Skip the header row
            phonemes = [Phoneme(*row) for row in reader]
        return cls(phonemes)

    @classmethod
    def default(self) -> "PhonemeList":
        """Create a PhonemeList using the default phoneme definitions.

        Returns:
            A new PhonemeList instance using the built-in phoneme definitions
        """
        return self.from_csv(DEFAULT_PHONEME_FILE)
