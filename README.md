# subtotxt
Quickly convert a [SubRip](https://en.wikipedia.org/wiki/SubRip) .srt or [WEBVTT](https://en.wikipedia.org/wiki/WebVTT) .vtt subtitle file to plain text. Removes timestamps and .srt subtitle line numbers. 
This was a quick project thrown together for my girlfriend, she's still learning English and wanted to be able to read subtitles more like a transcript for some trickier language issues (and to understand the jokes in Friends by discussing them with me).  
  
With a spot of feature creep and some encoding detection needs, it evolved into being able to detect character encoding, along with being able to understand both .srt and .vtt formats to save some pre-processing work.
## Usage: 
Pop the python file somewhere you can reach it and from a command line use:  
```python C:\Python\subtotxt.py -f subtitle.srt```  
or  
```python C:\Python\subtotxt.py -f subtitle.vtt```  
The script will check which format the subtitle file is (incase of incorrect file extensions), detect the character encoding used then write out a .txt file with the same name as your input. If the output file already exists it will ask for permission to delete and create a new one.
## Advanced Usage:
The script has six more arguments you can parse:  
- *--utf8* or *-8*  
Forces the output file to use [UTF-8](https://en.wikipedia.org/wiki/UTF-8) encoding. This may eliminate character encoding issues if you cannot view the output file. In practice, if you can read the contents of the input subtitle file successfully the output should work without the need to change the encoding.  
- *--pause* or *-p*  
Pause the script at the sanity check stage to let you check some stats before continuing, handy if the output is not working.  
- *--screen* or *-s*  
Prints the output to the console while writing to the file, may help with debugging failed outputs.  
- *--copy* or *-c*  
Copies input to output without change, appends *-copy* to filename *e.g.: subtitle-copy.srt*, handy to use with *--utf8* to quickly change encoding. Might be useful if your video player app cannot understand your original subtitle file encoding.
- *--overwrite* or *-o*  
Skips asking ```Output file already exists, delete and make a new one? [y/n]``` and simply deletes the existing output file to create a new one. Ideal for batch processing.
- *--help* or *-h*   
Shows above information.
## Required External Modules  
- [Send2Trash](https://pypi.org/project/Send2Trash/) Python module to safely delete the old output file on both Win and \*nix based systems.
- [cchardet](https://pypi.org/project/cchardet/) Python module to detect your subtitle file encoding.  
If your system does not these installed, it will auto install them on first use.  
## Features:
- Fast (aside from initial missing modules install on slow net connections)
- Input files character encoding formats are autodetected (if supported by [cchardet](https://pypi.org/project/cchardet/))  
- Output files are wrote in the same encoding as the input or can be forced to UTF8
- Should be cross platform friendly thanks to PathLib and Send2Trash
- Handles UNC style ```\\myserver\myshare\mysub.srt``` paths thanks to PathLib
- Handles SRT to TXT or WEBVTT to TXT
- Handles multi line subtitles and subtitle lines with just numbers (does not confuse them with SRT line numbers)
- WEBVTT: Removes 'WEBVTT', 'Kind: xxxx', 'Language: xxx' headers and Timestamps from output
- SRT: Removes subtitle line #'s and Timestamps, will not work if first subtitle is not 1 or if duplicated line numbers are present (rare cases but possible), use [SubtitleEdit](https://github.com/SubtitleEdit/subtitleedit) to renumber lines for now if this happens. 
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
  
Examples with non latin characters:
These are random examples take from an SRT website. cchardet calls them UTF-8-SIG, Notepad++ calls them UTF-8-BOM. 
  
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
## Future plans:
- Possibly handle more formats (.ssa Sub Station Alpha would be the other major one I could think of), for now you can use something like [SubtitleEdit](https://github.com/SubtitleEdit/subtitleedit) to convert other exotic formats to .srt or .vtt. If you have a format you would like to convert to txt, contact me or raise an issue to see if I can add support.
- GUI option for simple drag and drop usage.
- Figure out a checking method for misnumbered or duplicate numbered SRT line numbers.
- Handle stripping out SRT formatting tags for bold, italic etc...
## License:
Released as CC0, use it how you wish. If you do use it elsewhere, please be awesome and tag me as the original author 🙂.
