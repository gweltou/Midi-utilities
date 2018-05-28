### source: https://eli.thegreenplace.net/2011/12/27/python-threads-communication-and-stopping

import mido
import time
import threading


DEBUG = True


class PlayOnce(threading.Thread):
    def __init__(self, rec, outport):
        super(PlayOnce, self).__init__()
        self.rec = rec
        self.outport = outport
        if DEBUG: print "New PlayOnce Thread"
    
    def run(self):
        print "notes in thread", self.rec
        for msg in self.rec:
            time.sleep(msg.time)
            self.outport.send(msg)
        print "note played", msg
    


class MidiLooper:
    def __init__(self, inport, outport):
        self.inport = inport
        self.outport = outport
        self.recording = False
        self.playing = True
        self.recs = []
        
        self.get_first_rec()
        self.main_loop()
    
    
    def is_start_rec(self, msg):
        return msg.type == 'control_change' \
           and msg.control == 64 \
           and msg.value == 127
    
    
    def is_stop_rec(self, msg):
        return msg.type == 'control_change' \
           and msg.control == 64 \
           and msg.value == 0
    
    
    def is_delete(self, msg):
        return msg.type == 'control_change' \
           and msg.control == 67 \
           and msg.value == 127
    
    
    def get_first_rec(self):
        new_rec = []
        first_note = 0
        
        while True:
            for msg in self.inport.iter_pending():
                print msg
                if self.is_start_rec(msg):
                    self.recording = True
                    if DEBUG: print "First recording started"
                elif self.is_stop_rec(msg):
                    self.recording = False
                    if DEBUG: print "First recording stopped"
                    self.maxlen = time.time() - first_note
                    if len(new_rec) > 0:
                        self.recs.append(new_rec)
                        if DEBUG: print new_rec 
                        return
                else:
                    if self.recording:
                        if first_note == 0:
                            first_note = time.time()
                            last_note = first_note
                        new_rec.append(msg.copy(time=time.time()-last_note))
                        last_note = time.time()
    
    
    def main_loop(self):
        if DEBUG: print "Entering main loop..."
        
        last_delete = 0
        
        while self.playing and len(self.recs)>0:
            for r in self.recs:
                PlayOnce(r, self.outport).start()
            
            new_rec = []
            start = time.time()
            last_note = start
        
            while (time.time()-start < self.maxlen):
                for msg in self.inport.iter_pending():
                    if self.is_start_rec(msg):
                        self.recording = True
                    elif self.is_stop_rec(msg):
                        self.recording = False
                    elif self.is_delete(msg):
                        if len(self.recs)>0: del self.recs[-1]
                    else:
                        if self.recording:
                            new_rec.append(msg.copy(time=time.time()-last_note))
                            last_note = time.time()
                time.sleep(0.01)
            
            if len(new_rec) > 0:
                self.recs.append(new_rec)
      


if __name__ == "__main__":
    mido.set_backend('mido.backends.portmidi')
    indev = None
    outdev = None
    
    inport = mido.open_input(indev)
    outport = mido.open_output(outdev, autoreset=True)
    
    MidiLooper(inport, outport)
    