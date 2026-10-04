This conversion program asks for a file name 
and checks for a .mid or .csv extension.
It automatically tries to convert  based on the extension.

Currently, it supports MIDI notes many other MIDI events.
MIDI 1.0 standard only. 
Automatically skps sequencer specific messages.

I'm working on MIDI timing issues between relative and absolute time.
Issues encountered so far are based on the mido library I'm using.
I'm considering writing my own functions to read and parse the MIDI data.
