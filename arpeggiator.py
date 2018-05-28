#! /usr/bin/env python
# -*- coding: utf-8 -*-

import Tkinter as tk
import mido
import time
import random
import sys

DEBUG = False

def main(inport, outport):
    measure = 1.0	# length of a measure in seconds
    time_delta = 0
    chord = set()
    note_idx = 0
    playing = False
    prev_note = None
    mode = 2
    
    while True:
        for msg in inport.iter_pending():
            print msg
            if msg.velocity > 0:
                if msg.note not in chord:
                    chord.add(msg.note)
            else:
                chord.remove(msg.note)
            
            if msg.type == 'note_off':
                chord.remove(msg.note)
        
        if len(chord) == 0:
            playing = False
        
        if len(chord) > 1 and not playing:
            playing = True
            note_idx = 0
            next_time = time.time()
        
        if playing and time.time() >= next_time:
            print sorted(chord), note_idx ###
            if note_idx >= len(chord):
                note_idx = note_idx%len(chord)
            
            note = sorted(chord)[note_idx]
            if prev_note:
                outport.send(mido.Message('note_on', note=prev_note, velocity=0))
            outport.send(mido.Message('note_on', note=note, velocity=20))
            prev_note = note
            
            if mode == 1:
                note_idx = (note_idx+1)%len(chord)
            if mode == 2:
                note_idx = (note_idx-1)%len(chord)
            if mode == 3:
                note_idx = (note_idx+1)%len(chord)
            if mode == 4:
                note_idx = random.randrange(len(chord))
            
            time_delta = measure/len(chord)
            next_time = time.time() + time_delta
    

if __name__ == '__main__':    
    device_n = 1
    mido.set_backend('mido.backends.portmidi')
    
    midi_in = mido.open_input("USB2.0-MIDI MIDI 1")
    midi_out = mido.open_output("USB2.0-MIDI MIDI 1", autoreset=True)
    
    main(midi_in, midi_out)