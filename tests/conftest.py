from pathlib import Path
import pytest

TEST_ROOT = Path(__file__).parent
FIXTURES_ROOT = TEST_ROOT.parent / "fixtures"

@pytest.fixture
def fixtures_path() -> Path:
    return FIXTURES_ROOT 
