## first attempt: using SoundAnalyse ##

import numpy
import wave
import analyse
import struct

sound_file = wave.open('supermarche_mono.wav', 'r')		# open sound file

frames = sound_file.getnframes()
# print frames

for i in range(0, frames, 1024):
	# print "i = ", i
	# sound_file.setpos(i)
	raw_samp = sound_file.readframes(1024)		# read frames as string of bytes

	# print "position: ", sound_file.tell()
	# print "raw_samp = ", str(raw_samp)
	
	# chunk = struct.unpack(<)

	# Convert to NumPy array
	chunk = numpy.fromstring(raw_samp, dtype=numpy.int16)

	# print "chunk = ", chunk

	# Show pitch
	print analyse.detect_pitch(chunk, min_frequency=75, max_frequency=500,
		ratio=3.0, sens=0.0)



## second attempt: using praatinterface ##

# from praatinterface import PraatLoader
# from os import path

# praatpath = path.abspath('Praat.app')

# pl = PraatLoader(praatpath=praatpath)

# audio_file = 'test.wav'

# text = pl.run_script('pitch.praat', audio_file, 5, 5500)

# pitch = pl.read_praat_out(text)



## third attempt: using intonation lib ##

# import intonation




















