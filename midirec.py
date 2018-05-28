#! /usr/bin/env python
# -*- coding: utf-8 -*-

import Tkinter as tk
import mido
import time
import datetime
import threading
import Queue
import sys


TRACK_INTERVAL_TIME = 3	# in seconds


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



class recGui:
    def __init__(self, top, port):
        self.port = port
        self.tempo = mido.bpm2tempo(120)
        self.lasttime = 0
        
        self.top = top
        self.top.title("MidiRec")
        self.top.geometry('52x52')
        self.top.protocol("WM_DELETE_WINDOW", self.quit)
        frame = tk.Frame(top)
        frame.pack()
        
        self.midiLedCanvas = tk.Canvas(frame, width=50, height=50)
        self.midiLedCanvas.pack(expand=tk.YES, fill=tk.BOTH)
        
        self.queue = Queue.Queue()
        self.thread = threading.Thread(target=self.midiRecieveThread)
        self.thread.start()
        
        self.newMidiFile()
        self.processNewMsg()
    
    
    def newMidiFile(self):
        self.mid = mido.MidiFile()
        self.track = mido.MidiTrack()
        self.mid.tracks.append(self.track)
    
    
    def saveMidiFile(self):
        datestr = datetime.datetime.now().strftime("%y%m%d%H%M%S")
        path = "midi_{}.mid".format(datestr)
        self.mid.save(path)
        print "File {} saved ({} messages)".format(path, len(self.track))
    
    
    def midiRecieveThread(self):
        for msg in self.port:
            dt = time.time() - self.lasttime
            if dt > TRACK_INTERVAL_TIME:
                self.queue.put(1)	# send a "new track" message
                dt = 0
            ticks = mido.second2tick(dt, ticks_per_beat=480, tempo=self.tempo)
            self.queue.put(msg.copy(time=int(ticks)))
            self.lasttime = time.time()            
    
    
    def processNewMsg(self):
        self.midiLedCanvas.delete(tk.ALL)
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                if type(msg) == int:	# "new track" message
                    if len(self.track) > 1:
                        self.saveMidiFile()
                    self.newMidiFile()
                else:
                    print msg
                    self.track.append(msg)
                    self.midiLedCanvas.create_oval(0, 0, 50, 50, width=0, fill='green')
            except Queue.Empty:
                pass
        
        self.top.after(100, self.processNewMsg)
    
    
    def quit(self):
        print "Quitting..."
        if len(self.track) > 1:
            self.saveMidiFile()
        self.port.close()
        ###self.thread.join()
        self.top.destroy()


if __name__ == '__main__':
    mido.set_backend('mido.backends.portmidi')
    
    midi_port = None
    top = tk.Tk()
    devicePickerGui(top)
    top.mainloop()
    
    if midi_port:
        top = tk.Tk()
        recGui(top, midi_port)
        top.mainloop()