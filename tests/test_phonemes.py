from lapa_ng.phonemes import PhonemeList

def test_phoneme_extractor():

    result = PhonemeList.default().split_phonemes("9ytg#zOnd#rt")
    phonemes = [phoneme.sampa for phoneme in result]

    assert phonemes == ["9y", "t", "g", "#", "z", "O", "n", "d", "#", "r", "t"]
