# Original cue: groove + build modelled on the measured shape of 7 Minutes 0:34-1:06
# (75 BPM, ~10 s build with denser kicks and fills, then a loud syncopated groove whose accents move every bar).
# Own key (B minor), own chords and melody, own drum patterns. Every bar is different.
import sys, random, mido
random.seed(7)
out=sys.argv[1]; TPB=480; BPM=75
ev=[]
def note(ch,n,start,dur,vel): ev.append((start,'on',ch,n,vel)); ev.append((start+dur,'off',ch,n,0))
def B(b,beat=0.0): return (b-1)*4+beat
progs={0:48,1:43,2:38,3:61,4:44,5:56,6:47}
KICK,SN,LT,MT,HT,HH,OH,CR,RIDE=36,38,41,45,48,42,46,49,51
# --- build: bars 1-3 (0-9.6 s) ---
# bar 1: sparse low toms, strings swell on B
for p,v in ((0,70),(2.75,60)): note(9,LT,B(1,p),0.2,v)
note(4,47,B(1,0),4,50); note(4,54,B(1,0),4,45)
# bar 2: kicks enter syncopated, hats eighths quiet, strings rise
for p in (0,1.75,2.5): note(9,KICK,B(2,p),0.2,85)
for k in range(8): note(9,HH,B(2,k/2),0.1,40+k*3)
for p in (1,3): note(9,SN,B(2,p),0.2,70)
note(4,50,B(2,0),2,65); note(4,55,B(2,2),2,70)
note(1,35,B(2,0),4,80)
# bar 3: fill, density rising every beat, tom run, crescendo strings
fill=[(0,KICK),(0.5,LT),(0.75,LT),(1,KICK),(1.25,MT),(1.5,MT),(1.75,KICK),(2,HT),(2.25,MT),(2.5,LT),(2.75,KICK),(3,SN),(3.25,SN),(3.5,SN),(3.625,SN),(3.75,SN),(3.875,SN)]
for i,(p,n) in enumerate(fill): note(9,n,B(3,p),0.15,70+i*3)
for k in range(16): note(9,HH,B(3,k/4),0.08,50+k*2)
note(4,57,B(3,0),4,80); note(4,61,B(3,0),4,80)
note(1,33,B(3,0),2,90); note(1,34,B(3,2),2,95)
# --- groove: bars 4-9 (9.6-28.8 s), loud, accents move every bar ---
chords={4:[35,47,50,54],5:[36,48,52,55],6:[31,43,47,50],7:[28,40,43,47],8:[30,42,46,49],9:[35,47,50,54]}  # Bm, C, G, Em, F#, Bm
kick_opts=[[0,0.75,1.5,2.75],[0,1.25,2,3.5],[0,0.5,1.75,2.5,3.25],[0,1,1.75,3,3.75],[0,0.75,2.25,2.75],[0,1.5,2,3.25,3.5]]
sn_opts=[[1,3,3.75],[1,2.75,3],[1,3,1.75],[1.25,3],[1,3,3.25,3.5],[1,2.5,3]]
melody={4:[(0,71,1),(1,73,0.5),(1.5,74,1.5),(3,76,1)],5:[(0,79,0.75),(0.75,76,0.75),(1.5,72,2.5)],6:[(0,74,0.5),(0.5,71,0.5),(1,67,1),(2,69,2)],
        7:[(0,71,1.5),(1.5,72,0.5),(2,76,2)],8:[(0,78,1),(1,73,1),(2,70,1),(3,66,1)],9:[(0,71,4)]}
for i,b in enumerate(range(4,10)):
    note(9,CR,B(b,0),1,110 if b in (4,9) else 85)
    for p in kick_opts[i]: note(9,KICK,B(b,p),0.15,115)
    for p in sn_opts[i]: note(9,SN if p in (1,3) else MT,B(b,p),0.15,118 if p in (1,3) else 95)
    for k in range(16):
        acc=random.choice([0,0,1]); note(9,OH if (k%8==7 and random.random()<0.4) else HH,B(b,k/4),0.08,70+acc*35)
    c=chords[b]
    # low strings + synth bass: driving 8ths with a different accent pattern per bar
    for k in range(8):
        v=95 if (k in kick_opts[i] or k/2 in kick_opts[i]) else 75
        note(1,c[0],B(b,k/2),0.45,v); note(2,c[0]+12,B(b,k/2),0.3,v)
    # tremolo upper strings on the chord, brass stabs on syncopations
    for n in c[1:]: note(4,n+12,B(b,0),4,85)
    for p in (0,kick_opts[i][-1]): 
        for n in c[1:]: note(3,n,B(b,p),0.3,105)
    for p,n,d in melody[b]: note(5,n,B(b,p),d,105); note(0,n-12,B(b,p),d,95)
    if b>=7:
        for p in (0,2): note(6,c[0]+12,B(b,p),0.5,110)
# final: bar 10 beat 1 hit, cut at 30.0 s (bar 10 starts at 28.8 s)
for n in (35,47,50,54,59,62,66): note(3,n,B(10,0),1,127)
note(9,CR,B(10,0),1,127); note(9,KICK,B(10,0),0.2,127); note(6,47,B(10,0),1,127)
mid=mido.MidiFile(ticks_per_beat=TPB); tr=mido.MidiTrack(); mid.tracks.append(tr)
tr.append(mido.MetaMessage('set_tempo',tempo=mido.bpm2tempo(BPM)))
for ch,p in progs.items(): tr.append(mido.Message('program_change',channel=ch,program=p,time=0))
last=0
for beat,k,ch,a,v in sorted(ev,key=lambda e:(e[0],0 if e[1]=='off' else 1)):
    tk=int(round(beat*TPB)); dt=tk-last; last=tk
    tr.append(mido.Message('note_on' if k=='on' else 'note_off',channel=ch,note=a,velocity=v if k=='on' else 0,time=dt))
mid.save(out); print('saved',round(mid.length,2),'s')
