#! /usr/bin/env python
# -*- coding: utf-8 -*-

import Tkinter as tk
import mido
import threading

DEBUG = True


def get_chords_dict(path):
    with open(path, 'r') as f:
        lines = f.readlines()
    
    d = dict()
    for l in lines:
        if l.startswith('#') or not l.strip():
            continue
        l = l.split()
        d[l[0]] = filter(str.isdigit, l)
    
    return d


class devicePickerGui:
    def __init__(self, top):
        self.top = top
        self.top.title("Midi ports")
        frame = tk.Frame(top)
        frame.pack()
        
        self.buttons = []
        
        for d in mido.get_input_names():
            self.buttons.append(tk.Button(frame, text=d, command=lambda dev=d: self.openPort(dev)))
            self.buttons[-1].pack()
        
    def openPort(self, device):
        global midi_port
        midi_port = mido.open_input(device, autoreset=True)
        top.destroy()


class ChordsGui:
    def __init__(self, top, inport, outport, chords):
        self.top = top
        self.top.protocol("WM_DELETE_WINDOW", self.quit)
        self.running = True
        self.inport = inport
        self.outport = outport
        self.chords = chords
        self.chord_set = False
        self.buttons = []
        
        for i, k in enumerate(self.chords.keys()):
            self.buttons.append(tk.Button(self.top,
                text=k, command=lambda chord=k: self.set_chord(chord)))
            self.buttons[-1].grid(row=i//2, column=i%2)
        
        self.thread = threading.Thread(target=self.midi_recieve_thread)
        self.thread.start()
        
    def set_chord(self, chordname):
        self.chord = self.chords[chordname]
        self.chord_set = True
        print(chordname, self.chord)
    
    def quit(self):
        print("quit")
        self.running = False
        self.thread.join()
        self.top.destroy()
    
    def midi_recieve_thread(self):
        played = list()
        for msg in self.inport:
            if DEBUG: print msg
            if not self.running:
                print("quitting thread")
                break
            if not self.chord_set:
                continue
            if msg.type == 'note_on' and msg.velocity>0:
                   c = [msg.note]
                   for interval in self.chord[1:]:
                       self.outport.send(msg.copy(note=msg.note+int(interval)))
                       c.append(msg.note+int(interval))
                   played.append(c)
            elif msg.type == 'note_on' and msg.velocity==0:
                rem = None
                for c in played:
                    if c[0] == msg.note:
                        rem = c
                        break
                for n in rem[1:]:
                    self.outport.send(msg.copy(note=n))
                played.remove(rem)
        print("quitting midi_recieve_thread")


if __name__ == '__main__':
    mido.set_backend('mido.backends.portmidi')
    
    indev = None
    outdev = None
    
    inport = mido.open_input(indev)
    outport = mido.open_output(outdev, autoreset=True)
    
    top = tk.Tk()
    ChordsGui(top, inport, outport, get_chords_dict("chords.txt"))
    top.mainloop()
