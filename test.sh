#!/bin/bash -e

# uncompress test.wav if not already done so
if [ ! -f test.wav ] ; then
  bunzip2 test.wav.bz2
fi
   
# this should yield: packet: 2019-05-31 13:49    sysDiff +0.025
python3 MSF60decoder.py test.wav

exit 0
