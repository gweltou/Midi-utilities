#! /usr/bin/env python
# -*- coding: utf-8 -*-

import Tkinter as tk
import pygame as pg
from pygame.locals import *
import mido
import sys

DEBUG = False


def main(port):
    screen = pg.display.set_mode((400,150))
    clock = pg.time.Clock()
    closing = False
    
    keys = [K_q, K_z, K_s, K_e, K_d, K_f, K_t, K_g, K_y, K_h, K_u, K_j, K_k, K_o, K_l, K_p, K_m]
    keyboard = pg.key.get_pressed()
    
    octave = 0
    octave_debounce = 0
    
    while True:
        clock.tick(60)
        
        if pg.key.get_focused():
            keyboard_prev = keyboard
            keyboard = pg.key.get_pressed()
            assert(keyboard_prev is not keyboard)
            
            for k in keys:
                if keyboard[k] and not keyboard_prev[k]:
                    # Note on
                    note = 12*octave + 60 + keys.index(k)
                    msg = mido.Message('note_on', note=note)
                    if DEBUG: print msg, midi2hz(note)
                    port.send(msg)
                elif not keyboard[k] and keyboard_prev[k]:
                    # Note off
                    note = 12*octave + 60 + keys.index(k)
                    msg = mido.Message('note_off', note=note)
                    if DEBUG: print msg
                    port.send(msg)
            
            if keyboard[K_ESCAPE]:
                closing = True
            
            if keyboard[K_UP] and pg.time.get_ticks()-octave_debounce > 200:
                octave += 1
                print "octave up", octave
                octave_debounce = pg.time.get_ticks()
            
            if keyboard[K_DOWN] and pg.time.get_ticks()-octave_debounce > 200:
                octave -= 1
                print "octave down", octave
                octave_debounce = pg.time.get_ticks()
            
            if sum(keyboard) > 0:
                screen.fill((255,0,0))
            else:
                screen.fill((0,0,0))
            
        for e in pg.event.get():
            if e.type==QUIT:
                closing = True
        
        pg.display.flip()
        
        if closing:
            print "Bye !"
            port.close()
            print "#port closed"
            pg.display.quit()
            print "#display closed"
            pg.quit()
            print "#PyGame quited"
            sys.exit(0)


def play_file(port, path):
    for msg in mido.MidiFile(path).play():
        #print msg
        port.send(msg)

def midi2hz(midi):
    a = float(440)
    return (a/32) * 2**((midi-9)/12.)


class devicePickerGui:
    def __init__(self, top):
        self.top = top
        self.top.title("Midi ports")
        frame = tk.Frame(top)
        frame.pack()
        
        self.buttons = []
        
        print mido.get_output_names()
        for d in mido.get_output_names():
            self.buttons.append(tk.Button(frame, text=d, command=lambda dev=d: self.openPort(dev)))
            self.buttons[-1].pack()
        
    def openPort(self, device):
        midi_port = mido.open_output(device, autoreset=True)
        top.destroy()
        main(midi_port)


class Gui():
    def __init__(self, top, port):
        self.top = top
        self.octave = 0
        
        btn_up = tk.Button(self.top, text ="Oct +", command=self.octave_up)
        btn_down = tk.Button(self.top, text="Oct -", command=self.octave_down)
        
        btn_up.pack()
        btn_down.pack()
        
        self.top.focus_set()
        top.bind("<KeyPress>", self.key_down)
        top.bind("<KeyRelease>", self.key_up)
    
    def key_down(self, event):
        key = event.keysym
        print key, "down"
    
    def key_up(self, event):
        key = event.keysym
        print key, "up"
       
    def octave_up(self):
        self.octave += 1
        
    def octave_down(self):
        self.octave -+ 1
    

if __name__ == '__main__':
    pg.init()
    
    device_n = 1
    mido.set_backend('mido.backends.portmidi')
    midi_port = None
    
    if len(sys.argv)>1:
        # Device number as first argument
        device_n = int(sys.argv[1])
        port_name = mido.get_output_names()[device_n]
        midi_port = mido.open_output(port_name, autoreset=True)
    
    if len(sys.argv) > 2:	# read midi file
        for path in sys.argv[2:]:
            print path
            play_file(midi_port, path)
    else:
        top = tk.Tk()
        devicePickerGui(top)
        top.mainloop()
        sys.exit()
    
    main(midi_port)