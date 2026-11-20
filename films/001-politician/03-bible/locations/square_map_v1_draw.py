import math, numpy as np, sys
from PIL import Image, ImageDraw, ImageFont
X0,X1,Y0,Y1=-62.0,-14.0,-16.0,27.0; S=22  # px per m
W=int((X1-X0)*S)+40; H=int((Y1-Y0)*S)+40
img=Image.new('RGB',(W,H+150),'#F4EFE6'); d=ImageDraw.Draw(img)
F=lambda s: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',s)
FB=lambda s: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',s)
def P(x,y): return (20+(x-X0)*S, 20+(Y1-y)*S)   # north up, west left
def rect(x0,x1,y0,y1,fill,outline=None):
    a=P(x0,y1); b=P(x1,y0); d.rectangle([a,b],fill=fill,outline=outline)
# ground
rect(X0,X1,Y0,Y1,'#E3D6C0')
# buildings
for b in [(X0,-43.5,Y0,-10.5),(X0,-43.5,10.5,Y1)]: rect(*b,'#9C8B74','#5E5244')
# sidewalks
for b in [(X0,-43.5,-10.5,-7.0),(X0,-43.5,7.0,10.5),(-43.5,-35.5,-10.5,-7.0)]: rect(*b,'#CFC2AA','#A89A82')
d.text(P(-61,-12.5),'SW BLOCK: the wall of S06 (facade facing the square\nalong x=-43.5, and facing the street along y=-10.5)',fill='#FFFFFF',font=F(13))
d.text(P(-61,25),'NW BLOCK',fill='#FFFFFF',font=F(14))
d.text(P(-61,1.4),'WEST STREET  (road 14 m, sidewalks)  >>> 160 m to the crossroads, his car',fill='#3B3127',font=FB(14))
d.text(P(-38,25.5),'THE SQUARE  (open, about 87 x 63 m, continues east and north)',fill='#3B3127',font=FB(14))
def dot(x,y,r,c,label=None,off=(8,-8),fs=13):
    a=P(x,y); d.ellipse([a[0]-r,a[1]-r,a[0]+r,a[1]+r],fill=c,outline='#222')
    if label: d.text((a[0]+off[0],a[1]+off[1]),label,fill='#222',font=F(fs))
# camera frusta for SH110
cam=np.array((-28.3,0.6)); tgt=np.array((-50.0,-3.5)); f=(tgt-cam)/np.linalg.norm(tgt-cam)
def ray(ang,L):
    a=math.radians(ang); r=np.array((f[0]*math.cos(a)-f[1]*math.sin(a), f[0]*math.sin(a)+f[1]*math.cos(a))); return cam+r*L
for half,col,lab in ((32.7,'#C9A227','28 mm (animatic d11)'),(19.8,'#B0451E','50 mm'),(13.5,'#6B2A8C','75 mm')):
    for s in (-1,1):
        e=ray(s*half,40); d.line([P(*cam),P(*e)],fill=col,width=2)
    e=ray(half,17+half*0.25); d.text(P(*e),lab,fill=col,font=FB(12))
d.line([P(*cam),P(*(cam+f*36))],fill='#555',width=1)
# street light + arm
dot(-41.6,-8.6,6,'#222','street light (the hanging)',(9,4))
d.line([P(-41.6,-8.6),P(-39.62,-6.62)],fill='#222',width=3)
# bodies
K=[(2,(-51.5,-0.6)),(3,(-50.3,-8.8)),(4,(-44.8,-0.1)),(5,(-46.0,-6.3)),(6,(-44.0,-6.8)),(7,(-45.8,-3.9)),(8,(-42.8,-4.1))]
for n,(x,y) in K: dot(x,y,7,'#7A1F1F',f'{n}',(8,-9))
dot(-38.45,-6.35,8,'#7A1F1F','fat man + pipe',(9,-4))
dot(-35.2,-2.1,7,'#7A1F1F','second man',(9,-6))
# sniper zone
a=P(-44,6); b=P(-30,-6); d.rectangle([a,b],outline='#7A1F1F',width=1)
d.text((a[0]+4,a[1]+3),'S08 sniper: 3 dead somewhere in here\n(crowd sim, not computable here)',fill='#7A1F1F',font=F(11))
# case and papers
dot(-45.6,-4.0,6,'#2B2B2B','case (open)',(-90,8))
a=P(-50,3); b=P(-42,-8); d.rectangle([a,b],outline='#8A7A40',width=1)
d.text((a[0]+3,b[1]-16),'paper (animatic: 70 sheets)',fill='#6B5E20',font=F(11))
# helicopter
hx,hy=-24.0,0.5; a=P(hx-1.3,hy+1.3); b=P(hx+8.5,hy-1.3); d.rectangle([a,b],fill='#3D4436',outline='#111')
d.ellipse([P(hx+3.6-8,hy+8),P(hx+3.6+8,hy-8)],outline='#3D4436',width=1)
d.text(P(hx-2,hy-4.0),'HELICOPTER (door faces west)\nrotor wash blows outward',fill='#222',font=F(12))
dot(-28.0,0.6,5,'#1F4E8C','her',(6,-22))
dot(-28.95,0.55,4,'#8C5A1F')
# cameras of other shots
cams=[('SH110 her POV',(-28.3,0.6),(-50,-3.5),'#000',True,(-20,14)),('SH010 T02 (4)',(-39.4,8.4),(-39.2,-6.66),'#2E6B3A',False,(8,-6)),
      ('SH020 T03 (4)',(-47.4,-3.55),(-36,-4.5),'#2E6B3A',False,(-60,-24)),('SH040 (no 4 yet)',(-27,24),(-33,-0.5),'#777',False,(8,-6)),
      ('SH050 T02 (4), looks west',(-26.75,1.15),(-29.35,0.55),'#2E6B3A',False,(0,-44)),('SH060 T01 (4) / SH080 / SH100 / SH120, look east',(-29.38,1.2),(-28,0.6),'#2E6B3A',False,(-150,-62))]
for name,c,t,col,main,lo in cams:
    c=np.array(c); t=np.array(t); u=(t-c)/np.linalg.norm(t-c); e=c+u*2.6
    a=P(*c); b=P(*e); d.line([a,b],fill=col,width=4)
    n=np.array((-u[1],u[0])); d.polygon([b,P(*(e-u*0.9+n*0.6)),P(*(e-u*0.9-n*0.6))],fill=col)
    d.ellipse([a[0]-5,a[1]-5,a[0]+5,a[1]+5],fill=col)
    d.text((a[0]+lo[0],a[1]+lo[1]),name,fill=col,font=FB(12))
# scale and north
a=P(-60,-15); b=P(-50,-15); d.line([a,b],fill='#222',width=3); d.text((a[0],a[1]-18),'10 m',fill='#222',font=F(12))
d.text(P(-17,-13),'N ^\nW <  > E',fill='#222',font=FB(13))
# legend / notes
y=H+5
notes=["Top view of the square and the mouth of the west street. Coordinates from the d11 animatic code (stories/politician/animatic/src).",
"Dark red: the dead. 2-8 = his shots 2 to 8 in S06 (shot 1 went in the air). Positions = where the bullet stops them; the ragdoll moves each up to about 1 m.",
"Green triangles: cameras of S09 takes Leonard rated 4. Black: S09 SH110, her point of view, looking west down the street, slightly south.",
"From her eye: the corner and the street light at about 24 deg left, 16 m; the case at center, 18 m; most bodies 12 to 24 m, center and left;",
"second man 7 m; the street mouth 18 m; the dumpster 48 m, the burnt wreck 67 m, the crates 121 m; his car at the crossroads 179 m, 11 deg right."]
for n in notes: d.text((20,y),n,fill='#222',font=F(13)); y+=22
img.save(sys.argv[1]); print(img.size)
