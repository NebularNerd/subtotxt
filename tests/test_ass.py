# cSpell: disable
# Test SubStation Alpha Subtitles 4.00+
import tempfile
from pathlib import Path
from subtotxt import check_it_works
import binascii
import pytest


class test_values:
    """Set file name and options to parse."""

    def __init__(self):
        """
        Variables have the following purposes.

        loca: Maps basedir to location of this file.
        file: Input file, we use a string as it will become a Path again later.
        utf8: If True, Force UTF8 encoding for output.
        name: If True, Strip names from lines, e.g.: `Blackadder: You're name is Bob?`.
        sort: If True, Disables sorting .ass subs into timecode order.
        onel: If True, Trys to join split sentences into one line.
        outf: Temp output file to override normal output location.
        """
        self.loca = Path(__file__).parent.absolute()
        self.file = str(f"{self.loca}/resources/SSA_Example_400plus.ass")
        self.utf8 = False
        self.name = False
        self.sort = False
        self.onel = False
        self.outf = tempfile.NamedTemporaryFile()


use_this = test_values()


def compare_files():
    """If both approved output and tested output match, all is good."""
    a = CRC32_from_file(Path(f"{use_this.loca}/resources/outputs/SSA_Example_400plus.txt"))
    b = CRC32_from_file(Path(use_this.outf.name))
    if a != b:
        return "CRC32 does not match sample output"
    else:
        return


def CRC32_from_file(filename):
    """Quick and easy CRC32 checker, nothing fancy."""
    buf = open(filename, "rb").read()
    buf = binascii.crc32(buf) & 0xFFFFFFFF
    return "%08X" % buf


@pytest.fixture
def in_file():
    """Set variables to pass through to tester in main script."""
    return {
        "test_file": use_this.file,
        "test_force": use_this.utf8,
        "test_names": use_this.name,
        "test_sort": use_this.sort,
        "test_onel": use_this.onel,
        "test_outf": Path(use_this.outf.name),
    }


def test_ass(in_file):
    """
    Tests using default options.

    Temp file should match CRC32 of know good output.
    Not the most comprehensive test but it's a start.
    """
    results = check_it_works(in_file)
    assert results is None

    crc = compare_files()
    assert crc is None
