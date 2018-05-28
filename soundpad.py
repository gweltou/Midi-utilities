#! /usr/bin/env python
# -*- coding: utf-8 -*-


import pyo
import os


MIDI_NOTE_ZERO = 60
MIDI_MAX_NOTE = 16

s = pyo.Server()
s.setMidiInputDevice(99)
s.boot()



class SoundPad:
    def __init__(self):
        self.tables = []
        self.readers = []
        self.filenames = []
        
        self.loadFiles()
    
    
    def loadFiles(self):
        dir = os.getcwd()
        
        for path, dirs, files in os.walk(dir):
            # ignore directories whose name starts with '_'
            for d in dirs:
                if d.startswith('_'): dirs.remove(d)
            for f in files:
                if len(self.filenames) >= MIDI_MAX_NOTE:
                    break
                if os.path.splitext(f)[1].lower() in ['.wav', '.aif', '.aiff', '.flac']:
                    print f, u"ajouté"
                    self.filenames.append(os.path.join(path, f))
        
        self.filenames.sort()
        for f in self.filenames:
            self.tables.append(pyo.SndTable(f))
            self.readers.append(pyo.TableRead(table=self.tables[-1], freq=self.tables[-1].getRate()))
    
    
    def midi_handle(self, status, data1, data2):
        if status == 144:	# NoteIn
            padnum = data1 - MIDI_NOTE_ZERO
            if data2 and padnum>=0 and padnum<len(self.tables):
                print self.filenames[padnum]
                self.readers[padnum].setMul(data2/128.)
                self.readers[padnum].play()
                self.readers[padnum].out()



if __name__ == "__main__":
    s.start()
    sp = SoundPad()
    midi = pyo.RawMidi(sp.midi_handle)
    
    s.gui(locals())