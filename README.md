# MSF-60 decoder

A software decoder for the 60kHz NPL time signal (aka MSF)

The UK radio time signal is broadcast on 60kHz from Anthorn, Cumbria, UK (see [Time from NPL](https://en.wikipedia.org/wiki/Time_from_NPL_(MSF)))

There are many ways to decode this signal already out there but all seem to involve significant hardware [e.g. from Google](https://www.google.com/search?q=msf+decoder).  This project uses just a bit of wire into a soundcard and does all the hard work in software.   I'm about 250 miles away from the transmitter and I put about 4 meters of wire out of an upstairs window and attached it to a tree.  Others suggest that a small loop antenna or a few turns around a ferrite rod would do the trick as well.  Whatever antenna is used, there is no radio frequency hardware (e.g. demodulator), everything is done by sampling and software.

I have a [Intel DX58SO motherboard](https://ark.intel.com/content/www/us/en/ark/products/36888/intel-desktop-board-dx58so.html) (from 2008!) which has a 82801JI HD Audio Controller, but anything that samples at 192kHz will probably do.  If you haven't got 32bit input you may have a "20dB boost", or if all else fails use a [TA7642](https://www.ebay.co.uk/itm/2x-TA7642-Replaces-MK484-ZN414-ZN484-Single-Chip-AM-Radio-UK-Seller/372434251928) amplifier.

A description of the signal processing and some pretty matplotlib.pyplot plots will go here soon...

## Extensions

* Better SNR using long term coherance:  As things stand the phase of the 60kHz carrier is estimated for each symbol.  This makes the code smaller, but is an approximation as the carrier is accurate to 2 parts in 10^12 (much better than a soundcard clock!).   This extension would track the carrier exactly, even when not transmitting, and so maintain coherance over all the symbols.

* Low SNR decoding using minute repeats:  Almost the same signal is transmitted every minute, the lowest bit of the minute and the parity bit always changes and on average about one more does as well.  That's only one unpredictable bit in 600 slots, it is possible to use this redundancy to improve the error rate in low SNR conditions.  At simplest the templates may be averaged and a full blown solution would have a probility for each bit, a grammar for allowable minite to minute changes and a Viterbi decoder.

* Better time resolution: Each on/off transition occurs on a 10ms boundary these can all be measured more accurately and aggregated for higher precisionn (e.g. after decoding search around the known carrier on/off points, compute a likelihood of carrier on and average modulo 10ms).

* Extend to decoding of the [DCF77 signal from Mainflingen, Germany](https://en.wikipedia.org/wiki/DCF77) and/or the [WWVB signal from Fort Collins, Colorado, USA](https://en.wikipedia.org/wiki/WWVB).

* Investigate antenna design.  With hardware some people like a horizontal wire perpendicular to the direction of the transmitter, some vertical, some loop antenna and some ferrite coil.   The code will give you a SNR figure so designs may be tried and optimised.

* Do any existing recordings reach as far as 60kHz?  It would be fun if the time code could be pulled from old 8 track analog...

* What is the furthest away the MSF-60 signal can be reliably decoded with (a) the standard release or (b) any mod you like?
