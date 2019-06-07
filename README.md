# MSF-60 decoder

A simple software decoder for the 60kHz NPL time signal (aka MSF) accurate to a few tens of milliseconds.

The UK radio time signal is broadcast on 60kHz from Anthorn, Cumbria, UK (see [Time from NPL](https://en.wikipedia.org/wiki/Time_from_NPL_(MSF)))

There are many ways to decode this signal already out there but all seem to involve significant hardware (e.g. [current search](https://www.google.com/search?q=msf+decoder)).  This project uses just a bit of wire into a soundcard and does all the hard work in software.   I'm about 250 miles away from the transmitter and I put about 4 meters of wire out of an upstairs window and attached it to a tree.  Others suggest that a small loop antenna or a few turns around a ferrite rod would do the trick as well.  Whatever antenna is used, there is no radio frequency hardware (e.g. demodulator), everything is done by sampling and software.

## Testing install

test.sh just calls MSF60decoder.py on a standard file, test.wav (after uncompressing it if that hasn't already been done).   You should see: packet: 2019-05-31 13:49    sysDiff +0.025

This is the decoded packet formatted as a date and time plus a rough guess at the difference between radio time and system time.

## Recording audio

I have a [Intel DX58SO motherboard](https://ark.intel.com/content/www/us/en/ark/products/36888/intel-desktop-board-dx58so.html) (from 2008!) which has a 82801JI HD Audio Controller, but anything that samples at 192kHz will probably do.  If you haven't got 32bit input you may have a "20dB boost".  You'll probably have to fiddle with both the sox recording line and boosting the kernal prioities of the recording process.  MSF60decoder.sh contains a 'good enough' solution for me, and also has links to documentation.  MSF60decoder.sh also calls MSF60decoder.py, so once you've got everything set up you can call this and decode the time from MSF-60.

## Signal processing

So how does MSF60decoder.py work?  Lines marked with ## can be uncommented to show the signal processing steps.  If you do this don't forget to add a 'plt.show()' line so that the plot is displayed.   The plots below come from the supplied test.wav file.

So what does the recorded waveform look like?  Here are the first few samples:

![waveform](https://github.com/drtonyr/MSF60decoder/raw/master/img/wave.png)

Well, there's certaily something happening there.  The low frequnecy is almost certainly 50Hz mains noise, and there's a lot more happening at other frequencies. so let's look at the waveform in the frequency domain:

![FFT of waveform](https://github.com/drtonyr/MSF60decoder/raw/master/img/fft.png)

Good, there is a peak at 60kHz, that's the signal we are after.

Now let's construct a filter to pick out that signal, here is the filter called swindow which is a windowed sine wave:

![swindow](https://github.com/drtonyr/MSF60decoder/raw/master/img/swindow.png)

That's a lot of points, too many to see the sine wave, just its envelope.   So let's look at the firt 64 points:

![swindow64](https://github.com/drtonyr/MSF60decoder/raw/master/img/swindow64.png)

That doesn't look much like a sine wave because it's at 60kHz and the maximum frequency we can represent is 96 kHz, but it is a sine wave and because it repeats so many times it's good at filtering out all the other frequencies present.   So now we can demodulate our original waveform and we get:

![demod](https://github.com/drtonyr/MSF60decoder/raw/master/img/demod.png)

There's defintely some structure there, let's look at the first part:

![demod](https://github.com/drtonyr/MSF60decoder/raw/master/img/demod512.png)

And there we have it, our time signal.  All we need to do now is get the exact timing of the signal (as we have oversampled) and then we can digitise and get all the bits out.

## sysDiff

The final field of a packet decode is systemTime (computed from the mtime of the file) minus radioTime (computed from the radio time signal).  Many file systems only store times to a second, in which case you can't expect any better accuracy than a second.  However, if you are running ext4 then you are in luck and you should get the time to at least 0.1s.

## Extensions

* Filter the input signal so as to remove all the low frequecny power, which should improve the SNR and hence error rate.  A simple y(t) = x(t) - x(t-1) is probably all that is needed.

* Mearure the SNR more accurately:  At the moment approxSNR is reported prior to decoding the signal.  After decoding we know what all the bits are, so we can measure it exactly: SNR = 10 log10(meanPowerCarrierOn / meanPowerCarrierOff).

* Achieve better SNR using long term coherance:  As things stand the phase of the 60kHz carrier is estimated for each symbol.  This makes the code smaller, but is an approximation as the carrier is accurate to 2 parts in 10^12 (much better than a soundcard clock!).   This extension would track the carrier exactly, even when not transmitting, and so maintain coherance over all the symbols.

* Achieve Low SNR decoding using minute repeats:  Almost the same signal is transmitted every minute, the lowest bit of the minute and the parity bit always changes and on average about one more does as well.  That's only one unpredictable bit in 600 slots, it is possible to use this redundancy to improve the error rate in low SNR conditions.  At simplest the templates may be averaged and a full blown solution would have a probility for each bit, a grammar for allowable minite to minute changes and a Viterbi decoder.

* Get better time resolution: Each on/off transition occurs on a 10ms boundary these can all be measured more accurately and aggregated for higher precisionn (e.g. after decoding search around the known carrier on/off points, compute a likelihood of carrier on and average modulo 10ms).

* Extend to decoding of the [DCF77 signal from Mainflingen, Germany](https://en.wikipedia.org/wiki/DCF77) and/or the [WWVB signal from Fort Collins, Colorado, USA](https://en.wikipedia.org/wiki/WWVB).

* Investigate antenna design.  With hardware some people like a horizontal wire perpendicular to the direction of the transmitter, some vertical, some loop antenna and some ferrite coil.   The code will give you a SNR figure so designs may be tried and optimised.

* Do any existing recordings reach as far as 60kHz?  It would be fun if the time code could be pulled from old 8 track analog...

* What is the furthest away the MSF-60 signal can be reliably decoded with (a) the standard release or (b) any mod you like?
