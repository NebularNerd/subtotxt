# cSpell:disable
# SRT or WEBVTT to plain Text
# Author: NebularNerd
# Version: 2025-01-31
# https://github.com/NebularNerd/subtotxt
import sys
import os
import argparse
import subprocess
import re
from pathlib import Path


def missing_modules_installer(required_modules):
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
    def __init__(self, i):
        if i.is_file():
            self.i = i
            self.o = i.with_suffix(".txt")
            self.c = i.with_stem(f"{Path(i).stem}-copy")
            print(f"Input file: {i}")
        else:
            raise Exception(f"File {i} not found.")


class encoding:
    def __init__(self, i):
        self.res = from_path(i).best()  # charset_normalizer guess encoding
        self.enc = self.res.encoding
        self.out = "utf_8" if args.utf8 else self.enc
        if self.res is not None and self.enc == "utf_8" and self.res.bom:
            self.enc += "_sig"  # adds sig for utf_8_sig/bom files
        print(f"Detected Character Encoding: {self.enc}")
        print(f"Confidence of encoding: {int((1.0 - self.res.chaos) * 100)}%")
        print("Output encoding forced to UTF-8" if args.utf8 else "Output will use input encoding")


class subtitle:
    def __init__(self):
        self.format = self.testsub()  # Which subtitle format
        self.text = ""  # The output text
        self.text_finished = ""  # The output text after a final check
        self.prev = ""  # Previously read line, prevents duplicates
        self.junk = self.junklist()

    def testsub(self):
        with open(file.i, "r", encoding=enc.enc) as ts:
            for line in ts:
                if "WEBVTT" in line:
                    return "vtt"
                if line.strip("\n") == "1" and re.search("(.*:.*:.*-->.*:.*:.*)", next(ts)):
                    return "srt"

    def junklist(self):
        # This list will grow
        # Escaping and r(raw) tag needed for special characters
        return ["<.*?>", r"\{\\an8\}", r"^-\s", r"\[.*\]", r"\(.*\)", "^.*?:"]


def cls():  # Clear screen win/*nix friendly
    os.system("cls" if os.name == "nt" else "clear")


def yn(yn):  # Simple Y/N selector, use yn(text_for_choice)
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
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Quickly convert SRT or WEBVTT subtitles into plain text file.",
        epilog="Visit https://github.com/NebularNerd/subtotxt for more information.",
    )
    parser.add_argument(
        "--file", "-f", type=str, required=True, help="Path to .srt or .vtt file, enclose in quotes if path has spaces"
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
    return parser.parse_args()


def overwrite(f):
    if f.is_file():
        if (not args.overwrite and yn("Output file already exists, delete and make a new one?")) or args.overwrite:
            print("Overwriting old file")
            send2trash(f)
        else:
            raise Exception("Output file already exists.")


def copy():
    overwrite(file.c)
    with open(file.i, "r", encoding=enc.enc) as original, open(file.c, "w", encoding=enc.out) as new:
        for line in original:
            if args.screen:
                print(line, end="")
            new.write(line)
    print(f"Output file: {file.c}")


def junk_strip(line):
    # Based on PR#4 by eMPee584
    # Looping is terrible, but, a required evil it seems
    for junk in sub.junk:
        try:
            line = re.sub(rf"{junk}", "", line)
        except Exception:  # Line may become blank if we remove Closed Captions
            pass
    return line


def process_line(line):
    # Strip formatting junk from line
    # We do this before checking for duplicates
    line = junk_strip(line)
    # Process line if it's not a duplicate of the previous one, or empty.
    # Based on PR#4 by eMPee584
    line = line.strip()
    if not line == sub.prev and line != "":
        # One liners based on PR#2 by adam-sierakowski
        if args.oneliners:
            if line[-1] in [".", "?", "!", "…"]:
                ln = f"{line}\n"
                sub.text += ln
            else:
                ln = f"{line} "
                sub.text += ln
        else:
            ln = f"{line}\n"
            sub.text += ln

        if args.screen:
            print(ln, end="")
        sub.prev = ln


def do_srt():
    # SubRip subtitle file .srt
    # https://en.wikipedia.org/wiki/SubRip
    # Format has a line number followed by a timecode on the next line, then text.
    with open(file.i, "r", encoding=enc.enc) as original:
        subnum = 1
        for line in original:  # Ignore SRT Subtitle # and Timecode lines
            if line.strip("\n") == str(subnum) and re.search("(.*:.*:.*-->.*:.*:.*)", next(original)):
                subnum += 1
            elif not line.strip("\n") == "":
                process_line(line)
    write_to_file()


def do_vtt():
    # WebVTT (Web Video Text Tracks) subtitle file .vtt
    # https://en.wikipedia.org/wiki/WebVTT
    # https://www.checksub.com/blog/guide-use-webvtt-subtitles-format
    # This format has a few differing 'standards', you have:
    # Metadata, notes, styles, timceodes with optional hours, and optional line numbers,
    # almost none of which are actually used it seems. But we need to handle them
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


def write_to_file():
    with open(file.o, "w", encoding=enc.out) as new:
        # We check for junk again because it can gets split over two lines and we can't find it until now.
        for line in sub.text.splitlines():
            sub.text_finished += f"{junk_strip(line)}\n"
        new.write(sub.text_finished)


def do_work():
    overwrite(file.o)
    if sub.format == "srt":
        do_srt()
    elif sub.format == "vtt":
        do_vtt()
    else:
        raise Exception("Unable to determine Subtitle format.")


if __name__ == "__main__":
    args = arguments()
    cls()
    try:
        print(f"SUB to TXT v2025-01-31\n{'-' * 22}")
        file = file_handler(Path(args.file))
        enc = encoding(file.i)
        if args.pause and not yn("Ready to start?"):
            raise Exception("User exited at pause before start")
        if args.copy:
            copy()
        else:
            sub = subtitle()
            do_work()
        print("\nFinished!\n")
    except Exception as error:
        print(f"Script execution stopped because:\n{error}")
