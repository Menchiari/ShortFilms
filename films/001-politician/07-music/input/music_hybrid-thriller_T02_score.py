import sys, mido
out=sys.argv[1]
TPB=480; BPM=80
mid=mido.MidiFile(ticks_per_beat=TPB)
events=[]  # (beat, kind, ch, note/val, vel/ctrl)
def note(ch,n,start,dur,vel):
    events.append((start,'on',ch,n,vel)); events.append((start+dur,'off',ch,n,0))
def bar(b,beat=0): return (b-1)*4+beat
progs={0:42,1:43,2:38,3:45,4:57,5:40,6:59,7:60,8:95,10:44,11:56,12:48,13:47}
# cello drone G3 bars1-10 to beat 4 of bar10
note(0,55,bar(1),bar(10,3)-bar(1),55)
# electronic tick (hi-hat 42) in 32nds: 8 per beat
for b in range(1,11):
    if b in (5,6): continue
    vel={1:22,2:26,3:30,4:45,7:62,8:64,9:66,10:0}[b]
    if not vel: continue
    for k in range(32):
        note(9,42,bar(b,k/8),0.06,vel)
# bass contrabass
note(1,32,bar(2,0),2,80); note(1,31,bar(2,2),2,80)
note(1,30,bar(3,0),4,85)
note(1,29,bar(4,0),3,85); note(1,28,bar(4,3),1,85)
note(1,28,bar(7,0),4,95); note(1,27,bar(8,0),4,95)
note(1,26,bar(9,0),2,100); note(1,25,bar(9,2),2,100)
note(1,25,bar(10,0),2.9,110); note(1,25,bar(10,3),0.5,120)
# synth bass syncopated 16ths bars 7-9
pat=[0,3,6,8,11,14]
for b,ns in ((7,[28]),(8,[27]),(9,[26,25])):
    for p in pat:
        n=ns[0] if (len(ns)==1 or p<8) else ns[1]
        note(2,n+12,bar(b,p/4),0.2,100)
# violas pizz bar2
note(3,61,bar(2,0),0.5,90); note(3,64,bar(2,1),0.5,90); note(3,61,bar(2,2.5),0.5,90)
# trombone stab bar3
note(4,42,bar(3,0),0.3,115)
# solo violin bar3
note(5,75,bar(3,0),0.5,90); note(5,87,bar(3,0.5),1.5,95); note(5,82,bar(3,2),2,85)
# percussion
for t in (bar(3,0),bar(3,2.5)): note(9,41,t,0.2,110)
note(9,55,bar(4,1.5),0.5,100)
for b in (5,6):
    for bt in (0,2): note(9,36,bar(b,bt),0.2,75)
for bt in (0,1.5,3): note(9,45,bar(7,bt),0.2,110)
for bt in (0.75,1.5,2.25,3.5): note(9,43,bar(8,bt),0.2,112)
for bt in (0,1.25,2,3,3.5): note(9,45,bar(9,bt),0.2,118)
note(9,49,bar(10,0),1,127); note(9,49,bar(10,3),0.5,127)
# muted trumpet bar5
note(6,71,bar(5,0),1,75); note(6,72,bar(5,1),1,75); note(6,74,bar(5,2),2,78)
# horn bar6 long E with crescendo (expression CC11)
note(7,64,bar(6,0),4,90)
for i in range(16): events.append((bar(6,i*0.25),'cc',7,11,30+i*6))
events.append((bar(7,0),'cc',7,11,110))
for i,n in enumerate((56,57,59,61)): note(7,n,bar(7,i),1,100)
# glitch pad bar6
note(8,52,bar(6,0),4,55)
# violins tremolo cluster bar8
for n in (73,74,75): note(10,n,bar(8,0),4,100)
# trumpets + strings octave bar9
for i,n in enumerate((64,66,67,68)):
    note(11,n,bar(9,i),1,112); note(12,n+12,bar(9,i),1,112)
# bar10 tutti chord C# minor + final hit
for n in (49,52,56): note(11,n,bar(10,0),2.9,120)
for n in (61,64,68,73): note(12,n,bar(10,0),2.9,120)
for n in (49,52,56): note(11,n,bar(10,3),0.4,127)
for n in (61,64,68): note(12,n,bar(10,3),0.4,127)
note(13,37,bar(10,0),1,127); note(13,37,bar(10,3),0.5,127)
tr=mido.MidiTrack(); mid.tracks.append(tr)
tr.append(mido.MetaMessage('set_tempo',tempo=mido.bpm2tempo(BPM)))
for ch,p in progs.items(): tr.append(mido.Message('program_change',channel=ch,program=p,time=0))
for ch in range(16): tr.append(mido.Message('control_change',channel=ch,control=11,value=110,time=0))
evs=sorted(events,key=lambda e:(e[0],0 if e[1]=='off' else 1))
last=0
for beat,kind,ch,a,v in evs:
    tk=int(round(beat*TPB)); dt=tk-last; last=tk
    if kind=='on': tr.append(mido.Message('note_on',channel=ch,note=a,velocity=v,time=dt))
    elif kind=='off': tr.append(mido.Message('note_off',channel=ch,note=a,velocity=0,time=dt))
    else: tr.append(mido.Message('control_change',channel=ch,control=a,value=v,time=dt))
mid.save(out); print('saved', mid.length,'s')
