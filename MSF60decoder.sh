#!/bin/bash -e
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

# This sox line and it's chrt prefix will need tweaking for your hardware
# sox:  see http://sox.sourceforge.net/ - 2m00s is enough to get 1 timecode
# chrt: see https://www.alsa-project.org/wiki/Low_latency_howto 
# the loop ensures that we retry on "sox WARN alsa: over-run"
while sudo chrt --deadline --sched-runtime 5000000 --sched-deadline 10000000 --sched-period 16666666 0 sox --bits 32 --rate 192000 --type alsa hw:CARD=Intel,DEV=0 --buffer 96000000 --no-dither --clobber --no-show-progress MSF60decoder.wav trim 0 00:02:00 remix 2 2>&1 | egrep --quiet WARN ; do
  echo "sox failed - retrying"
done

python3 MSF60decoder.py MSF60decoder.wav

exit 0
