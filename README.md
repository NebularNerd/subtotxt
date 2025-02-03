# subtotxt
Quickly convert a [SubRip](https://en.wikipedia.org/wiki/SubRip) .srt, [SubStation Alpha](https://wiki.multimedia.cx/index.php?title=SubStation_Alpha) .ssa/.ass  or [WEBVTT](https://en.wikipedia.org/wiki/WebVTT) .vtt subtitle file to plain text. Removes timestamps and .srt/.vtt subtitle line numbers. 
This was a quick project thrown together for my girlfriend, she's still learning English and wanted to be able to read subtitles more like a transcript for some trickier language issues (and to understand the jokes in Friends by discussing them with me).  
  
With a spot of feature creep and some encoding detection needs, it evolved into being able to detect character encoding, along with being able to understand both .srt and .vtt formats to save some pre-processing work.
## Usage: 
Pop the python file somewhere you can reach it and from a command line use:  
```python C:\Python\subtotxt.py -f subtitle.srt```  
or  
```python C:\Python\subtotxt.py -f subtitle.vtt```  
The script will check which format the subtitle file is (incase of incorrect file extensions), detect the character encoding used then write out a .txt file with the same name as your input. If the output file already exists it will ask for permission to delete and create a new one.
## Advanced Usage:
The script has more advanced arguments you can parse:  
- **--dir** or **-d**: Multiple file mode, use this **instead** of `-f` and point it at a folder containing your subtitles. It will run through and process them all, the files must have `.srt`, `.vtt`, `.ssa` or `.ass` extensions. Path can be a full path e.g. `C:\mysubs` or a relative path `.\`.
- **--noname** or **-nn**: For SubStation Alpha this prevents prepending the subtitle line with the character name given in the file, if present. A line with a character might appear as `Blackadder: Your name is Bob?`. I highly recommend this setting if using `oneliners` below. For other formats we attempt to remove `NAME:` from the beginning of the subtitle line.
- **--nosort** or **-ns**: Specifically for SubStation Alpha files, one aspect of these files is that the subtitles can be placed in any order, when the file is processed it works out when a line will appear. I imagine the main reason for this is you could split the dialogue into one block, and labels for signs, books, etc... in another. By default we sort and most examples I've seen have everything in one large block.
- **--utf8** or **-8**: Forces the output file to use [UTF-8](https://en.wikipedia.org/wiki/UTF-8) encoding. This may eliminate character encoding issues if you cannot view the output file. In practice, if you can read the contents of the input subtitle file successfully the output should work without the need to change the encoding.  
- **--pause** or **-p**: Pause the script at the sanity check stage to let you check some stats before continuing, handy if the output is not working.  
- **--screen** or **-s**: Prints the output to the console while writing to the file, may help with debugging failed outputs.  
- **--copy** or **-c**: Copies input to output without change, appends *-copy* to filename *e.g.: subtitle-copy.srt*, handy to use with *--utf8* to quickly change encoding. Might be useful if your video player app cannot understand your original subtitle file encoding.
- **--overwrite** or **-o**: Skips asking `Output file already exists, delete and make a new one? [y/n]` and simply deletes the existing output file to create a new one. Ideal for batch processing.
- **--oneliners** or **-1**: Writes all sentences in one line, even if the original file divides some sentences into many lines or subtitles.
- **--help** or **-h**: Shows above information.
## Required External Modules:  
- [Send2Trash](https://pypi.org/project/Send2Trash/) Python module to safely delete the old output file on both Win and \*nix based systems.
- ~~[cchardet](https://pypi.org/project/cchardet/) Python module to detect your subtitle file encoding~~ (Removed for v2.0+ release due to issues with Python 3.10.x installs, still used in v1.0 and will work on Python 3.9.x installs).  
- [charset_normalizer](https://github.com/Ousret/charset_normalizer) Python module to detect your subtitle file encoding (v2.0 and YYYY-MM-DD versions, supports Python 3.9.x and above).   

If your system does not these installed, it will auto install them on first use (or if you install a new version of Python later). If you prefer you can install them either manually, or by using the `requirements.txt`
## Features:
- Fast (aside from initial missing modules install on slow net connections)
- Process a single file or point at a folder to process all supported files.
- Input files character encoding formats are autodetected (if supported by [cchardet](https://pypi.org/project/cchardet/) [v1.0] or [charset_normalizer](https://github.com/Ousret/charset_normalizer) [v2.0+]). For most languages it should be fine, for Chinese and near neighbour languages it can be tricky, a subtitle may contain valid characters for Mandarin or Cantonese (or other dialects) and be in  potentially the wrong encoding. This can result in some wonky detection but it should not affect the overall output.
- Output files are wrote in the same encoding as the input or can be forced to UTF8
- Should be cross platform friendly thanks to PathLib and Send2Trash
- Handles UNC style ```\\myserver\myshare\mysub.srt``` paths thanks to PathLib
- Handles SRT to TXT or WEBVTT to TXT
- Handles multi line subtitles and subtitle lines with just numbers (does not confuse them with SRT line numbers)
- Strips formatting tags, and rogue `{\an8}` tags you sometimes find in poorly converted subtitles
- WEBVTT: Removes 'WEBVTT', headers, metadata, notes, styles and timestamps from output
- SRT: Removes subtitle line #'s and Timestamps, will not work if first subtitle is not 1 or if duplicated line numbers are present (rare cases but possible), use [SubtitleEdit](https://github.com/SubtitleEdit/subtitleedit) to renumber lines for now if this happens. 
- SSA/ASS: Removes all non dialogue lines, detects script version, removes positional {xxx} tags from text.
## Examples:
WEBVTT Input:
```  
WEBVTT
Kind: captions
Language: en

00:00:18.590 --> 00:00:21.389
you'll hear a telephone conversation

00:00:21.389 --> 00:00:23.310
now you have some time to look at

00:00:23.310 --> 00:00:27.589
questions one to six
```  
or SRT Input:  
```  
1
00:00:18,590 --> 00:00:21,389
you'll hear a telephone conversation

2
00:00:21,389 --> 00:00:23,310
now you have some time to look at

3
00:00:23,310 --> 00:00:27,589
questions one to six
```
Output:
```  
you'll hear a telephone conversation
now you have some time to look at
questions one to six
```  
  
### Examples with non latin characters:
These are random examples take from an SRT website. cchardet detects the encoding as UTF-8-SIG, Notepad++ detects as UTF-8-BOM, these are technically the same thing. 
  
Arabic SRT in UTF-8-BOM / UTF-8-SIG encoding:
```  
1
00:00:02,425 --> 00:00:20,776
تـرجـمـة وتـعـديـل
الدكتور علي طلال 

2
00:00:58,425 --> 00:00:59,776
مادلين)؟)

3
00:01:01,705 --> 00:01:03,462
هل تريدين أنّ تأكلين مجددًا؟
```  
Output with forced UTF-8 encoding:
```  
تـرجـمـة وتـعـديـل
الدكتور علي طلال 
مادلين)؟)
هل تريدين أنّ تأكلين مجددًا؟
```  
Chinese (Simplified) SRT in UTF-8-BOM / UTF-8-SIG encoding:  
```  
1
00:00:58,016 --> 00:00:59,476
瑪德琳？

2
00:01:01,270 --> 00:01:03,272
（妳又想吃飯了？）

3
00:01:04,313 --> 00:01:07,276
（妳心情不好才會吃這麼多）

4
00:01:09,528 --> 00:01:10,612
瑪德琳！
```  
Output file in original UTF-8-BOM / UTF-8-SIG encoding:
```  
瑪德琳？
（妳又想吃飯了？）
（妳心情不好才會吃這麼多）
瑪德琳！
```
## Oneliner flag example:
With the oneliner flag on, the program checks if a line ends in one of those symbols: `. ? ! …`, then it writes a space and continues to write in the same line.
Input:
```  
1
00:02:07,240 --> 00:02:09,680
Vine aquí a mediados
del mes de julio

2
00:02:09,720 --> 00:02:11,600
en busca de luz y de calma.

3
00:02:12,200 --> 00:02:14,880
Fue estupendo.
```
Output:
```
    Vine aquí a mediados del mes de julio en busca de luz y de calma.
    Fue estupendo.
```
## Future plans:
- Possibly handle more formats, for now you can use something like [SubtitleEdit](https://github.com/SubtitleEdit/subtitleedit) to convert most other formats to .srt or .vtt. If you have a format you would like to convert to txt, contact me or raise an issue to see if I can add support.
- GUI option for simple drag and drop usage.
- Figure out a checking method for misnumbered or duplicate numbered SRT line numbers.
## License:
Released as CC0, use it how you wish. If you do use it elsewhere, please be awesome and tag me as the original author. 🙂
