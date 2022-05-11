# subtotxt
Quickly convert a SubRip .srt or WEBVTT .vtt subtitle file to plain text, removes timestamps and .srt subtitle line numbers. 
This was a quick project thrown together for my girlfriend, she's still learning English and wanted to be able to read subtitles more like a transcript for some of the tricker bit.
## Usage: 
Pop the python file somewhere you can reach it and from a command line use  
```python C:\Python\subtotxt.py -f subtitle.srt```  
or  
```python C:\Python\subtotxt.py -f subtitle.vtt```  
The script will check which format the subtitle file if (in case of incorrect file extension), then write out a .txt file with the same name as your input. If the output file already exists it will ask for permission to delete and create a new one.  
The scripts makes use of the most excellent [Send2Trash](https://pypi.org/project/Send2Trash/) Python module to safely delete the file on both Win and \*nix based systems. If your system does not have Send2Trash installed, it will auto install on first use.  
## Features:
- Nice and fast
- Should be cross platform friendly thanks to PathLib
- Handles SRT to TXT or WEBVTT to TXT
- Handles multi line subtitles and subtitle lines with just numbers (does not confuse them with SRT line numbers)
## Future plans:
- Possibly handle more formats, for now you can use something like [SubtitleEdit](https://github.com/SubtitleEdit/subtitleedit) to convert other formats to .srt or .vtt. If you have a format you are using heavily contact me to see if I can add support.
- GUI option for simple drag and drop usage.
## License:
Released as CC0, use it how you wish. If you do use it elsewhere, please be awesome and tag me as the original author 🙂.
