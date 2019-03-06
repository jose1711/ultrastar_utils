#!/usr/bin/env python
'''
 - download lyrics + mp3 file
 - adjust lyrics (fix typos, expand short forms, repeat refrain)
 - open both in composer (http://performous.org/composer)
 - sync lines (not words) to music (Play + Time phrase)
 - add TITLE and CREATOR information in Song properties
 - save to .lrc format in composer (File - Export - LRC)
 - run this script with a filename of .lrc as a parameter
 - redirect output to .txt file and open in yass
 - sync words and add pitch information

to download music & video from youtube:
  youtube-dl --recode-video mp4 $YT_LINK
  youtube-dl -x --audio-format mp3 $YT_LINK
  mencoder -ovc copy -nosound input.avi -o output.avi
'''
import sys
import re
import pyphen

dic = pyphen.Pyphen(lang='sk_SK')

beat = 0
bpm = 180
output = []

header = '''#ENCODING:UTF8
#BPM:{0}'''.format(bpm)

metadata_map = {'ti': 'TITLE',
                'ar': 'ARTIST',
                're': 'CREATOR'}

output.append(header)


def parse_header(data):
    '''Get title and author info from the file header'''
    k, v = re.match(r'^\[(..):([^]]*)\]', data).groups()
    if k in metadata_map:
        output.append('#{0}:{1}'.format(metadata_map[k], v))


def timestamp2beats(timestamp):
    '''convert lrc's timestamp to ultrastar's beats'''
    mins, secs = re.match(r'\[(..):(..\...)\]', timestamp).groups()
    secs = 60 * int(mins) + float(secs)
    beats = int(secs / (60 / bpm / 4))
    return beats


def split_into_syllables(line):
    '''split line into a list of syllables'''
    syllables = []
    for word in line.split():
        word = dic.inserted(word)
        for ix, syllable in enumerate(word.split('-')):
            if ix == 0:
                syllables.append(' ' + syllable)
            else:
                syllables.append(syllable)
    return syllables


syllables = []
old_timestamp = None

if len(sys.argv) != 2:
    print('Supply a single argument (lrc file)')
    sys.exit(1)

with open(sys.argv[1]) as f:
    while True:
        line = f.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        line_r = re.match(r'^(?P<time>\[[0-9][0-9]:[0-9][0-9]\.[0-9][0-9]\])(?P<lyrics>.*)', line)
        if not line_r:
            parse_header(line)
            continue
        timestamp, lyrics = line_r.groups()
        timestamp = timestamp2beats(timestamp)
        syllables.append(split_into_syllables(lyrics))
        if old_timestamp is not None:
            duration = timestamp - old_timestamp
            duration_per_syllable = int(duration / (len(syllables[-1]) + 1))
            for ix, syllable in enumerate(syllables[-2], start=1):
                output.append(': {0} 4 0 {1}'.format(old_timestamp + ix *
                                                     duration_per_syllable, syllable))
            output.append('- {0}'.format(old_timestamp + (ix + 1) * duration_per_syllable))
        old_timestamp = timestamp

    # do the last line of input
    duration_per_syllable = int(duration / (len(syllables[-1]) + 1))
    syllables.append(split_into_syllables(lyrics))
    for ix, syllable in enumerate(syllables[-2], start=1):
        output.append(': {0} 4 0 {1}'.format(old_timestamp + ix *
                                             duration_per_syllable, syllable))
    output.append('- {0}'.format(old_timestamp + (ix + 1) * duration_per_syllable))
output.append('E')

print('\n'.join(output))
