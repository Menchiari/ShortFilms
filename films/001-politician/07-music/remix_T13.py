import subprocess,numpy as np,sys
SR=44100
T='/home/user/ShortFilms/films/001-politician/07-music/takes/'
def load(name):
    raw=subprocess.run(['ffmpeg','-nostdin','-v','error','-i',T+name,'-ac','2','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
    return np.frombuffer(raw,np.float32).reshape(-1,2).astype(np.float64)
def seg(x,a,b): return x[int(round(a*SR)):int(round(b*SR))].copy()
def db(v): return 10**(v/20)
def ltas(x,n=4096):
    m=x.mean(1);fr=np.lib.stride_tricks.sliding_window_view(m,n)[::n//2]*np.hanning(n)
    return np.sqrt((np.abs(np.fft.rfft(fr,axis=1))**2).mean(0))
def match_eq(x,target,n=4096,maxdb=6):
    src=ltas(x,n);r=target/(src+1e-9)
    k=np.ones(31)/31;r=np.convolve(r,k,'same')  # smooth
    r=np.clip(r,db(-maxdb),db(maxdb))
    h=np.fft.irfft(r);h=np.roll(h,n//2)*np.hanning(n)
    out=np.stack([np.convolve(x[:,c],h,'same') if False else fftconv(x[:,c],h) for c in range(2)],1)
    return out
def fftconv(a,h):
    N=len(a)+len(h)-1;L=1<<int(np.ceil(np.log2(N)))
    y=np.fft.irfft(np.fft.rfft(a,L)*np.fft.rfft(h,L),L)[:N]
    o=len(h)//2;return y[o:o+len(a)]
def rms(x): return np.sqrt((x**2).mean())
def lowpass(x,fc):
    n=len(x);L=1<<int(np.ceil(np.log2(n)));F=np.fft.rfftfreq(L,1/SR)
    g=1/np.sqrt(1+(F/fc)**8)
    return np.stack([np.fft.irfft(np.fft.rfft(x[:,c],L)*g,L)[:n] for c in range(2)],1)
def ramp(n,a,b,shape='lin'):
    t=np.linspace(0,1,n)
    if shape=='eqp': return np.sin(t*np.pi/2) if b>a else np.cos(t*np.pi/2)
    return a+(b-a)*t
out=np.zeros((int(40*SR),2))
def place(x,at,gain=1.0):
    i=int(round(at*SR));out[i:i+len(x)]+=x*gain

t02=load('music_80s-action-synth_T02_end.wav');drums=load('music_80s-action-synth_T09_eleven_drums.wav')
v5=load('music_80s-action-synth_T10_eleven_body_v5.wav');v9=load('music_80s-action-synth_T10_eleven_body_v9.wav')
v7=load('music_80s-action-synth_T10_eleven_body_v7.wav');v10=load('music_80s-action-synth_T10_eleven_body_v10.wav')
chord=load('music_80s-action-synth_T09_eleven_chord.wav')
X=0.375  # crossfade length (one eighth note), ends on the downbeat
HIT=10.98
# 1. T02 0-10.98, dips 5 dB over the last two bars so the drum build rises out of it, short fade at the hit
a=seg(t02,0,HIT);n=len(a);g=np.ones(n);i0=int(4.98*SR);g[i0:]=ramp(n-i0,1,db(-5));g[-int(0.02*SR):]*=np.linspace(1,0,int(0.02*SR))
place(a*g[:,None],0)
# 2. drum build 4.98-10.98 (drums 0-5.98 placed at 4.96), rising from -12 dB to 0 dB, no own final hit
d=seg(drums,0,5.98);n=len(d);g=ramp(n,db(-12),1.0);g[-int(0.03*SR):]*=np.linspace(1,0,int(0.03*SR))
place(d*g[:,None]*db(-3),4.96)
# 3. band: v5 bars 1-2 (its 0.03-6.03), v9 bars (9.03-15.03), v7 last two bars (18.03-24.03); EQ-matched to v5, equal-power crossfades ending on each downbeat
target=ltas(seg(v5,0.03,6.03))
parts=[(v5,0.03,6.03),(v9,9.03,15.03),(v7,18.03,24.03)]
at=HIT
lv=None
for k,(src,a0,b0) in enumerate(parts):
    pre=X if k>0 else 0.0
    post=X if k<len(parts)-1 else 0.0
    s=seg(src,a0-pre,b0+(0 if k==len(parts)-1 else 0))
    s=match_eq(s,target)
    if lv is None: lv=rms(s)
    else: s*=lv/rms(s)
    n=len(s);g=np.ones(n)
    if pre>0: m=int(pre*SR);g[:m]=ramp(m,0,1,'eqp')
    # outgoing fade: last X before the next downbeat
    if k<len(parts)-1:
        m=int(X*SR);g[-m:]=ramp(m,1,0,'eqp')
    else:
        g[-int(0.015*SR):]*=np.linspace(1,0,int(0.015*SR))
    place(s*g[:,None],at-pre)
    at+=b0-a0
END=at
# 4. v10 bass layer under the first 12 s of the band, low-passed, fading out over the last bar
b=lowpass(seg(v10,0.03,12.03),140);n=len(b);g=np.ones(n);m=int(3*SR);g[-m:]=ramp(m,1,0)
b*=lv/rms(b)*db(-9)
place(b*g[:,None],HIT)
# 5. final guitar chord on the next downbeat
c=chord*(lv/rms(seg(chord,0,1.0)))*db(1)
place(c,END-0.026)
out=out[:int((END+8)*SR)]
out.astype(np.float32).tofile(sys.argv[1])
print('band end / chord at',round(END,3),'peak',round(20*np.log10(np.abs(out).max()),1))
