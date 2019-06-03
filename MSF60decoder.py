#!/usr/bin/python3

# Extract the MSF time code from a WAV (RIFF WAVE) file
# Reference: https://en.wikipedia.org/wiki/Time_from_NPL_(MSF)

# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import os
import sys
import datetime
import numpy as np
import scipy.io.wavfile
import scipy.signal
import matplotlib.pyplot as plt
## plt.figure(figsize=(10,3))

# fundamental parameters
symbolTime = 0.1  # this is the duration of a symbol (one bit) in seconds
overSample = 8    # we oversample so as to locate the start of every second

# rough check of format (ignores fixed A and B values)
def formatCheck(frames):
  check = (frames[0] == [True, True, True, True, True, False, False, False, False, False])
  if check:
    for frame in frames[1:]:
      check = check and frame[0]
      for posn in range(3, 10):
        check = check and not frame[posn]

  return check

# check a block of frames against its CRC value
def crcCheck(frames, crc):
  parity = True

  for frame in frames:
   parity ^= frame[1]

  return parity == crc[2]
   
# decode a set of BCD frames and report the number of bit errors 
def BCDdecode(frames):
  data = 0
  mult = 1
  for frame in reversed(frames):
    if frame[1]:
      data += mult
    mult *= 2
    if mult == 16:
      mult = 10
  return data

# check args
if len(sys.argv) != 2:
  exit('Symtax: %s file.wav' % (sys.argv[0]))

sampleRate, wavdata = scipy.io.wavfile.read(sys.argv[1])
data = wavdata.astype(float)
## plt.plot(data[0:512])
## plt.semilogy(abs(np.fft.fft(data[0:sampleRate])[0:int(sampleRate/2)]))

windowLen = int(round(sampleRate * symbolTime))
rfreq = 2 * np.pi * 60000 / sampleRate

# set up the filters to demodulate and downsample
window  = scipy.signal.hamming(windowLen) # maybe rect is better!
swindow = np.empty(windowLen)
cwindow = np.empty(windowLen)

for i in range(windowLen):
  swindow[i] = window[i] * np.sin(rfreq * i)
  cwindow[i] = window[i] * np.cos(rfreq * i)
## plt.plot(swindow[0:64])

# compute the demodulated waveform
demod = []
for init in range(0, len(data) - windowLen, int(windowLen/overSample)):
  ssum = np.dot(swindow, data[init:init+windowLen])
  csum = np.dot(cwindow, data[init:init+windowLen])
  demod.append(np.sqrt(ssum * ssum + csum * csum))
## plt.plot(demod)

# the carrier is on at least 50% of the time, use top half
hiValue = np.mean(sorted(demod, reverse = True)[0:int(0.5 * len(demod))])
# and there is always one in 10 that is low, so use bottom 10%
loValue = np.mean(sorted(demod)[0:int(0.1 * len(demod))])

# this really should be calculated after the decode
## print("approxSNR: %.0f dB" % (20 * np.log10(hiValue / loValue)))

# now we have a sensible threshold to convert demod into bits
threshold = 0.5 * (loValue + hiValue)

# find the start of the second which is always high to low
period = int(overSample / symbolTime)
acc = [0] * period  
for i in range(1, len(demod)):
  if demod[i - 1] > threshold and demod[i] < threshold:
    acc[i % period] += 1
offset = acc.index(max(acc))

# decode all the bits
bout = []
minit = -1
for init in range(offset, len(demod) - period, period):
  frame = []
  for i in range(0, period, overSample):
    frame.append(demod[init + i] < threshold)
  bout.append(frame)

# search for complete frames and format the bits as a date string
for i in range(0, len(bout) - 60):
  dout = bout[i:i+60]

  if formatCheck(dout) and \
     crcCheck(dout[17:25], dout[54]) and crcCheck(dout[25:36], dout[55]) and \
     crcCheck(dout[36:39], dout[56]) and crcCheck(dout[39:52], dout[57]):
    year   = BCDdecode(dout[17:25]) + 2000
    month  = BCDdecode(dout[25:30])
    dayOM  = BCDdecode(dout[30:36])
    dayOW  = BCDdecode(dout[36:39])
    hour   = BCDdecode(dout[39:45])
    minute = BCDdecode(dout[45:52])
    if dout[58][2]:
      TZ = 'BST'
    else:
      TZ = 'GMT'
      
    # we could compute the true SNR here as now we know all the bits

    radioTime = datetime.datetime(year, month, dayOM, hour=hour, minute=minute).timestamp()
    systemTime = os.path.getmtime(sys.argv[1]) + i + 60 - 0.59 - len(bout)
    
    print("packet: %4d-%02d-%02d %02d:%02d    sysDiff %+0.2f" % (year, month, dayOM, hour, minute, systemTime - radioTime))
