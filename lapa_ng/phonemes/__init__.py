import csv
import dataclasses
from typing import Iterator
from pathlib import Path

__all__ = ["Phoneme", "PhonemeList"]

DEFAULT_PHONEME_FILE = Path(__file__).parent / "default.csv"

@dataclasses.dataclass
class Phoneme:
    sampa: str
    ipa: str
    example: str
    notes: str


class PhonemeList:

    def __init__(self, phoneme_list: list[Phoneme]):
        # It's important that we test the longest phonemes first
        self.phoneme_list = sorted(phoneme_list, key=lambda x: len(x.sampa), reverse=True)
 
    def get_first(self, word: str) -> Phoneme | None:
        """
        Returns the first phoneme that matches the start of the word.
        """
        for phoneme in self.phoneme_list:
            if word.startswith(phoneme.sampa):
                return phoneme
        return None

    def split_phonemes(self, word: str, ignore_errors: bool = False) -> tuple[Phoneme, ...]:
        """
        Splits "compound" phonemes into their constituent phonemes. 
        Basically, if we have a phoneme like "CH" and we see "CHI" in the word, we split it into "CH" and "I".
        """
        phonemes = []
        while word:
            phoneme = self.get_first(word)
            if phoneme:
                phonemes.append(phoneme)
                word = word[len(phoneme.sampa):]
            else:
                if not ignore_errors:
                    raise ValueError(f"No phoneme found for word: {word}")
                else:
                    word = word[1:]
        return tuple(phonemes)
    
    def __getitem__(self, key: int | str) -> Phoneme:
        if isinstance(key, str):
            for phoneme in self.phoneme_list:
                if phoneme.sampa == key:
                    return phoneme
            raise AttributeError(f"No phoneme found for {key}")
        return self.phoneme_list[key]
    
    def __len__(self) -> int:
        return len(self.phoneme_list)
    
    def __iter__(self) -> Iterator[Phoneme]:
        return iter(self.phoneme_list)
    
    @classmethod
    def from_csv(cls, file_path: str) -> "PhonemeList":
        with open(file_path, "r") as f:
            reader = csv.reader(f)
            _ = next(reader) # Skip the header row
            phonemes = [Phoneme(*row) for row in reader]
        return cls(phonemes)
    
    @classmethod
    def default(self) -> "PhonemeList":
        return self.from_csv(DEFAULT_PHONEME_FILE)

