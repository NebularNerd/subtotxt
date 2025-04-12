"""Subtitle to plain Text converter: Handles  .srt, .vtt, .ssa, .ass files."""

# cSpell:disable
# SRT, ASS/SSA or WEBVTT to plain Text
# Author: NebularNerd
# Version: 2025-02-03
# https://github.com/NebularNerd/subtotxt
import sys
import os
import argparse
import subprocess
import re
from pathlib import Path


version = "2025-02-03"


def missing_modules_installer(required_modules):
    """Auto module installer, fairly clever, will run if it finds modules are missing."""
    import platform

    if float(platform.python_version().rsplit(".", 1)[0].strip()) < 3.12:  # pkg_resources method
        import pkg_resources

        installed = {pkg.key for pkg in pkg_resources.working_set}
    if float(platform.python_version().rsplit(".", 1)[0].strip()) >= 3.12:  # importlib.metadata method
        import importlib.metadata

        distributions = importlib.metadata.distributions()
        installed = set()
        for dist in distributions:
            installed.add(dist.metadata["Name"].lower())
    missing = required_modules - installed
    if missing:
        y = ""
        for x in missing:
            y += f"{x.lower()}, "
        print(f"Installing missing modules\n{y[:-2]}\nplease wait a few moments.")
        python = sys.executable
        subprocess.check_call([python, "-m", "pip", "install", *missing], stdout=subprocess.DEVNULL)
        print("Done, thanks for waiting")


# Install send2trash and charset_normalizer if missing.
# https://pypi.org/project/Send2Trash/
# https://github.com/Ousret/charset_normalizer


while True:
    try:
        from send2trash import send2trash
        from charset_normalizer import from_path

        break
    except ModuleNotFoundError:
        missing_modules_installer({"send2trash", "charset-normalizer"})


# 8888888b.  8888888888 8888888888 .d8888b.
# 888  "Y88b 888        888       d88P  Y88b
# 888    888 888        888       Y88b.
# 888    888 8888888    8888888    "Y888b.
# 888    888 888        888           "Y88b.
# 888    888 888        888             "888
# 888  .d88P 888        888       Y88b  d88P
# 8888888P"  8888888888 888        "Y8888P"


class file_handler:
    """Get the file ready for action."""

    def __init__(self):
        """Variables have the following purposes."""
        self.i = None  # Input file
        self.o = None  # Output file
        self.c = None  # Copy file
        self.overw = None  # Overwrite

    def set_file(self, i):
        """Set file input, then create output names."""
        i = Path(i)
        if i.is_file():
            self.i = i
            self.o = i.with_suffix(".txt")
            self.c = i.with_stem(f"{Path(i).stem}-copy")
            print(f"Input file: {i}")
        else:
            raise FileNotFoundError(f"File '{i}' not found.")

    def set_over(self, x):
        """Overwrite existing output file without asking."""
        self.overw = x


class encoding:
    """Figure out what encoding the subtitle has, override output encoding if desired."""

    def __init__(self):
        """Variables have the following purposes."""
        self.res = None  # Check encoding
        self.enc = None  # Detected encoding
        self.out = None  # Output encoding

    def check_encoding(self):
        """charset_normalizer guess encoding."""
        self.res = from_path(file.i).best()
        self.enc = self.res.encoding
        if self.res is not None and self.enc == "utf_8" and self.res.bom:
            self.enc += "_sig"  # adds sig for utf_8_sig/bom files
        print(f"Detected Character Encoding: {self.enc}")
        print(f"Confidence of encoding: {int((1.0 - self.res.chaos) * 100)}%")

    def force_utf8(self, x):
        """Force UTF8 output regardless of input encoding."""
        print("Output encoding forced to UTF-8" if x else "Output will use input encoding")
        self.out = "utf_8" if x else self.enc


class subtitle:
    """Wrangle and mangle to file into nice readable text."""

    def __init__(self):
        """Variables have the following purposes."""
        self.format = None  # Which subtitle format
        self.text = ""  # The output text
        self.text_finished = ""  # The output text after a final check
        self.prev = ""  # Previously read line, prevents duplicates
        self.junk = None  # Junk remover list, set below
        self.no_names = False  # If True removes names from subtitles
        self.nosrt = False  # If True leaves subs in file order, not timecode order
        self.scr = False  # If True outputs to screen as each line processed
        self.oneline = False  # If True attempts to join longer lines

    def testsub(self):
        """
        Opens subtitle file and attempts to detect encoding used.

        Notes:
        A file may appear as `UTF8` in some programs but be detects as `ascii` here,
        this is not a bug. `ascii` just means there are no characters in the file beyond the
        standard character set.

        Chinese and near neighbours/dialects have many many encodings, sometimes the wrong one may
        be choosen but it should not affect output.
        """
        with open(file.i, "r", encoding=enc.enc) as ts:
            for line in ts:
                if "WEBVTT" in line:
                    self.format = "vtt"
                if line.strip("\n") == "1" and re.search("(.*:.*:.*-->.*:.*:.*)", next(ts)):
                    self.format = "srt"
                if any(s in line for s in ["!:", "Timer:", "Style:", "Comment:", "Dialogue:", "ScriptType:"]):
                    self.format = "ass"

    def junklist(self):
        """
        List of junk strings, characters, control codes we wish to remove.

        This list will grow/adapt over time.
        Escaping and r(raw) tag needed for special characters
        """
        j = ["<.*?>", r"\{.*?\}", r"\[.*\]", r"\(.*\)", r"^-\s"]
        if self.no_names:
            j.append("^.*?:")
        return j

    def set_no_names(self, x):
        """If True: Strip names from lines, e.g.: `Blackadder: You're name is Bob?`."""
        self.no_names = x
        self.junk = self.junklist()

    def set_no_sort(self, x):
        """If True: Prevents .ass/.ssa subs from being sorted by timecode."""
        self.nosrt = x

    def screen_output(self, x):
        """If True: Outputs processed content to screen/console."""
        self.scr = x

    def one_line(self, x):
        """If True: Sets one line function, attempts to join split sentences."""
        self.oneline = x


def cls():
    """Clear screen win/*nix friendly."""
    os.system("cls" if os.name == "nt" else "clear")


def yn(yn):
    """
    Yes/No selector, returns True for yes.

    Usage: yn(text_for_choice)
    """
    while True:
        print(f"{yn} [Y/N]")
        choice = input().lower()
        if choice in {"yes", "y"}:
            return True
        elif choice in {"no", "n"}:
            return False
        else:
            print("Please respond with 'yes' or 'no'")


def arguments():
    """Everyone loves arguments, here's a list of them."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Quickly convert SRT, SSA or WEBVTT subtitles into plain text file.",
        epilog="Visit https://github.com/NebularNerd/subtotxt for more information.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--file",
        "-f",
        type=str,
        required=False,
        help="Path to .srt/.vtt/.ass/.ssa file, enclose in quotes if path has spaces",
    )
    group.add_argument(
        "--dir",
        "-d",
        type=str,
        required=False,
        help="Path to folder containing subtitle files, process all files in folder",
    )
    parser.add_argument(
        "--utf8",
        "-8",
        default=False,
        action="store_true",
        required=False,
        help="Force output file to use UTF-8 instead of input encoding",
    )
    parser.add_argument(
        "--pause",
        "-p",
        default=False,
        action="store_true",
        required=False,
        help="Pauses at info step to allow viewing info before continuing",
    )
    parser.add_argument(
        "--screen",
        "-s",
        default=False,
        action="store_true",
        required=False,
        help="Prints the output to the console",
    )
    parser.add_argument(
        "--copy",
        "-c",
        default=False,
        action="store_true",
        required=False,
        help="Copies input to output without change, appends -copy to filename",
    )
    parser.add_argument(
        "--overwrite",
        "-o",
        default=False,
        action="store_true",
        required=False,
        help="Skips asking for permission to overwrite, will auto-delete old file and create a new one",
    )
    parser.add_argument(
        "--oneliners",
        "-1",
        default=False,
        action="store_true",
        required=False,
        help="Write all sentences in one line, even if the original divides it into many lines or subtitles.",
    )
    parser.add_argument(
        "--nonames",
        "-nn",
        default=False,
        action="store_true",
        required=False,
        help="Removes character names if present (.ssa/.ass), attempts this for other formats.",
    )
    parser.add_argument(
        "--nosort",
        "-ns",
        default=False,
        action="store_true",
        required=False,
        help="For SubStation Alpha (.ssa/.ass), do not sort by timecode.",
    )
    parser.add_argument(
        "--debug",
        "-db",
        default=False,
        action="store_true",
        required=False,
        help="Give Traceback output if the script fails",
    )
    return parser.parse_args()


def overwrite_old_file(f):
    """Politely check if there is an exiting file before moving forward."""
    if f.is_file():
        if (not file.overw and yn("Output file already exists, delete and make a new one?")) or file.overw:
            print("Overwriting old file")
            send2trash(f)
        else:
            raise Exception("Output file already exists.")


def copy():
    """For testing encoding errors, copies file line by line but does not process the subtitles."""
    overwrite_old_file(file.c)
    with open(file.i, "r", encoding=enc.enc) as original, open(file.c, "w", encoding=enc.out) as new:
        for line in original:
            if args.screen:
                print(line, end="")
            new.write(line)
    print(f"Output file: {file.c}")


def junk_strip(line):
    """Based on PR #4 by eMPee584. Looping is terrible, but, a required evil it seems."""
    if sub.junk:
        for junk in sub.junk:
            try:
                line = re.sub(rf"{junk}", "", line)
            except Exception:  # Line may become blank if we remove Closed Captions
                pass
    return line


def process_line(line):
    """Process each line, remove formatting junk, check for duplicates, store for writing later."""
    # Strip formatting junk from line
    # We do this before checking for duplicates
    line = junk_strip(line).strip()
    # Process line if it's not a duplicate of the previous one, or empty.
    # Based on PR #4 by eMPee584
    # Fix for live translations giving duplicates from Issue #9 by rajibando
    if line.strip() and line.strip() != sub.prev.strip():
        # One liners based on PR #2 by adam-sierakowski
        if sub.oneline:
            if line[-1] in [".", "?", "!", "…"]:
                ln = f"{line}\n"
                sub.text += ln
            else:
                ln = f"{line} "
                sub.text += ln
        else:
            ln = f"{line}\n"
            sub.text += ln

        if sub.scr:
            print(ln, end="")
        sub.prev = ln


def do_srt():
    """
    Format: .srt SubRip.

    https://en.wikipedia.org/wiki/SubRip
    Format has a line number followed by a timecode on the next line, then text.
    """
    print("Processing file as SubRip subtitles [.srt]")
    with open(file.i, "r", encoding=enc.enc) as original:
        subnum = 1
        for line in original:  # Ignore SRT Subtitle # and Timecode lines
            if line.strip("\n") == str(subnum) and re.search("(.*:.*:.*-->.*:.*:.*)", next(original)):
                subnum += 1
            elif not line.strip("\n") == "":
                print(line)
                process_line(line)
    write_to_file()


def do_vtt():
    """
    Format: .vtt WebVTT (Web Video Text Tracks).

    https://en.wikipedia.org/wiki/WebVTT
    https://www.checksub.com/blog/guide-use-webvtt-subtitles-format
    This format has a few differing `standards`, you have:
    Metadata, notes, styles, timceodes with optional hours, and optional line numbers,
    almost none of which are actually used it seems. But we need to handle them.
    """
    print("Processing file as WebVTT (Web Video Text Tracks) [.vtt]")
    with open(file.i, "r", encoding=enc.enc) as original:
        subnum = 1
        head = 1  # Try and skip over everything until we reach the subtitles.
        for line in original:
            # Line number and timecode format
            if line.strip("\n") == str(subnum) and re.search("(.*:.*-->.*:.*)", next(original)):
                subnum += 1
                head = 0
            # Timecode only format
            elif re.search("(.*:.*-->.*:.*)", line):
                head = 0
            elif not line.strip("\n") == "" and head == 0:
                process_line(line)
    write_to_file()


def do_ass():
    """
    Format: .ssa/.ass SubStation Alpha.

    https://wiki.multimedia.cx/index.php?title=SubStation_Alpha
    http://www.tcax.org/docs/ass-specs.htm Browser may complain as not https site.
    This format has different version, later ones include more metadata and sections,
    this should not be a big problem as the text is always on a `Dialog:` line.
    Two keys issues are; lines may not be in timecode order,
    text may be for labelling objects and not part of the script.
    """
    print("Processing file as SubStation Alpha subtitle [.ssa/.ass]")
    with open(file.i, "r", encoding=enc.enc) as original:
        # Try and get version
        fv = ""
        for line in original:
            if "ScriptType:" in line:
                fv = line.split(": ")[1].strip()
        print(f"SSA Version: {fv}" if fv != "" else "No version found, assuming v1.0")
        original.seek(0)
        d = {}
        for line in original:
            # Example Dialog line v1.0:
            # Dialogue: Marked=0,0:01:16.0,0:01:23.4,White Text,Usagi,0000,0000,0000,Pretty Soldier Sailor Moon
            # Example Dialog line v3+:
            # Dialogue: Marked=0,0:01:38.95,0:01:41.75,owari,Lupin,0000,0000,0000,,Yeah, love is wonderful.
            if "Dialogue:" in line:
                if fv == "":
                    x = re.findall(r"Dialogue:.*?,(.*?\.\d*),.*?\.\d*,.*?,(.*?),.*?,.*?,.*?,(.*)", line)  # v1.0
                else:
                    x = re.findall(r"Dialogue:.*?,(.*?\.\d*),.*?\.\d*,(.*?),.*?,.*?,.*?,.*?,.*?,(.*)", line)  # v 3.0+
                stc = x[0][0]  # Start timecode
                nom = x[0][1]  # Character speaking
                txt = x[0][2]  # Text
                text = txt if (sub.no_names or nom == "") else f"{nom}: {txt}"
                d.update({stc: {"dialog": text}})
        for t in [v["dialog"] for k, v in sorted(d.items())] if not sub.nosrt else [v["dialog"] for v in d.values()]:
            process_line(t.replace(r"\n", " ").replace(r"\N", " "))  # Fixes odd newline in .ass
    write_to_file()


def write_to_file():
    """Write completed text to a new file."""
    with open(file.o, "w", encoding=enc.out) as new:
        # We check for junk again because it can gets split over two lines and we can't find it until now.
        for line in sub.text.splitlines():
            sub.text_finished += f"{junk_strip(line)}\n"
        new.write(sub.text_finished)


def do_work():
    """Process file based on sub.format, additionally check if there is a file from a previous run."""
    overwrite_old_file(file.o)
    if sub.format == "srt":
        do_srt()
    elif sub.format == "vtt":
        do_vtt()
    elif sub.format == "ass":
        do_ass()
    else:
        raise Exception("Unable to determine Subtitle format.")


def check_it_works(in_file):  # Pytest runner
    """For pytest runs, sets variables."""
    try:
        file.set_file(in_file["test_file"])
        file.o = Path(in_file["test_outf"])  # Override normal output file
        file.set_over(True)  # Always overwrite (although unlikely when Pytesting)
        enc.check_encoding()
        enc.force_utf8(in_file["test_force"])  # True/False
        sub.set_no_names(in_file["test_names"])  # True/False
        sub.set_no_sort(in_file["test_sort"])
        sub.screen_output(False)  # Pytest never needs to output to screen
        sub.one_line(in_file["test_onel"])
        sub.testsub()
        do_work()
        return
    except Exception as error:
        return f"Testing failed: {error}"


# Init classes
file = file_handler()
enc = encoding()
sub = subtitle()

# Do things
if __name__ == "__main__":
    args = arguments()
    cls()
    try:
        print(f"SUB to TXT v{version}\n{'-' * 22}")
        if args.file or args.copy:
            file.set_file(args.file)
            file.set_over(args.overwrite)
            enc.check_encoding()
            enc.force_utf8(args.utf8)  # True/False
            sub.set_no_names(args.nonames)  # True/False
            sub.set_no_sort(args.nosort)  # True/False
            sub.screen_output(args.screen)  # True/False
            sub.one_line(args.oneliners)  # True/False
            sub.testsub()
            if args.pause and not yn("Ready to start?"):
                raise Exception("User exited at pause before start")
            if args.copy:
                copy()
            else:
                do_work()
        if args.dir:
            files = list(filter(lambda p: p.suffix in {".srt", ".vtt", ".ssa", ".ass"}, Path(args.dir).glob("*")))
            how_many = len(files)
            c = 0
            print(f"Multi file mode. Found {how_many} files. The files are:")
            for idx, f in enumerate(files):
                print(str(i) + ": " + files)
            print("-" * 22)
            for f in files:
                file.set_file(f)
                sub.testsub()
                enc.force_utf8(args.utf8)
                do_work()
                print("-" * 22)
                c += 1
            print(f"Processed {c}/{how_many} files.")
        print("\nFinished!\n")
    except Exception as error:
        print(f"Script execution stopped because:\n{error}")
        if args.debug:
            import traceback

            print(traceback.format_exc())
