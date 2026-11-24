import sys, mido
out=sys.argv[1]
TPB=480; BPM=80
mid=mido.MidiFile(ticks_per_beat=TPB)
events=[]
def note(ch,n,start,dur,vel):
    events.append((start,'on',ch,n,vel)); events.append((start+dur,'off',ch,n,0))
def bar(b,beat=0): return (b-1)*4+beat
# 0 cellos ostinato, 1 basses, 2 violas+vln2 sustain, 3 vln1 tremolo, 4 horns, 5 trombones, 6 tuba, 7 timpani
progs={0:42,1:43,2:48,3:44,4:60,5:57,6:58,7:47}
# cello spiccato ostinato, eighths, every bar: C3 C3 G2 C3 Db3 C3 G2 C3 (bars 9-10 on G: G2 G2 D2 G2 Ab2 G2 D2 G2)
for b in range(1,11):
    pat=[48,48,43,48,49,48,43,48] if b<9 else [43,43,38,43,44,43,38,43]
    v=50+b*4
    for i,n in enumerate(pat): note(0,n,bar(b,i*0.5),0.3,v+(12 if i in (0,4) else 0))
# basses: C1/C2 pedal bars 1-8, G1 bars 9-10
note(1,36,bar(1),bar(9)-bar(1),70); note(1,31,bar(9),8,85)
# sustained strings, one chord per 2 bars
chords={1:[55,60,63],3:[56,60,63],5:[56,61,65],7:[59,63,67],9:[59,62,67]}
for b,ch in chords.items():
    for n in ch: note(2,n,bar(b),8,40+b*4)
# violins I high tremolo pp, from bar 3: G5, Ab5 bars 5-6, G5 7-8, Ab5 9-10
for b,n in ((3,79),(5,80),(7,79),(9,80)): note(3,n,bar(b),8,35+b*4)
# horns melody, unison, long notes, from bar 3
mel=[(3,0,60,4),(4,0,63,2),(4,2,62,2),(5,0,61,4),(6,0,60,2),(6,2,56,2),(7,0,59,4),(8,0,60,2),(8,2,62,2),(9,0,63,4),(10,0,62,4)]
for b,bt,n,d in mel: note(4,n,bar(b,bt),d,70+b*4)
# trombones long chords from bar 5, tuba pedal
for b,ch in ((5,[49,53]),(7,[47,51]),(9,[47,50])):
    for n in ch: note(5,n,bar(b),8,60+b*4)
note(6,36,bar(5),16,60); note(6,31,bar(9),8,75)
# timpani soft on downbeats from bar 5, C then G
for b in range(5,11): note(7,36 if b<9 else 43,bar(b),0.5,45+b*5)
tr=mido.MidiTrack(); mid.tracks.append(tr)
tr.append(mido.MetaMessage('set_tempo',tempo=mido.bpm2tempo(BPM)))
for ch,p in progs.items(): tr.append(mido.Message('program_change',channel=ch,program=p,time=0))
for ch in range(16): tr.append(mido.Message('control_change',channel=ch,control=11,value=110,time=0))
evs=sorted(events,key=lambda e:(e[0],0 if e[1]=='off' else 1))
last=0
for beat,kind,ch,a,v in evs:
    tk=int(round(beat*TPB)); dt=tk-last; last=tk
    tr.append(mido.Message('note_on' if kind=='on' else 'note_off',channel=ch,note=a,velocity=v,time=dt))
mid.save(out); print('saved', mid.length,'s')
