from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
import re

fred=instancer.instantiateVariableFont(TTFont('Fredoka-VF.ttf'),{'wght':700,'wdth':100},inplace=False)
sora_b=instancer.instantiateVariableFont(TTFont('Sora-VF.ttf'),{'wght':700},inplace=False)
sora_s=instancer.instantiateVariableFont(TTFont('Sora-VF.ttf'),{'wght':600},inplace=False)

def layout(font,text,size,tracking_em=0.0):
    """returns list of (glyphname, x_offset) and total width in user units"""
    gs=font.getGlyphSet(); cmap=font.getBestCmap(); upem=font['head'].unitsPerEm; sc=size/upem; hm=font['hmtx']
    adv=0; parts=[]
    for ch in text:
        g=cmap.get(ord(ch))
        if g is None: adv+=size*0.3; continue
        parts.append((g,adv)); adv+=hm[g][0]*sc+tracking_em*size
    return parts, adv-tracking_em*size, gs, sc
def text_path(font,text,size,tracking_em=0.0,x=0,y=0,align='center'):
    parts,total,gs,sc=layout(font,text,size,tracking_em)
    x0 = x-total/2 if align=='center' else (x-total if align=='right' else x)
    d=[]
    for g,off in parts:
        pen=SVGPathPen(gs); gs[g].draw(TransformPen(pen,(sc,0,0,-sc,x0+off,y))); p=pen.getCommands()
        if p: d.append(p)
    return ' '.join(d), x0, total
def glyph_bounds(font,ch):
    gs=font.getGlyphSet(); g=font.getBestCmap()[ord(ch)]; bp=BoundsPen(gs); gs[g].draw(bp); return bp.bounds, font['hmtx'][g][0]

ORANGE="#F26B1D"; INK="#15181C"; CREAM="#FFF7EF"; WHITE="#FFFFFF"; INK2="#4A4F55"; SHADOW="#C4CCD4"

def wordmark(color, ebar, x, y, size, align='center'):
    """'Zumee' in Fredoka Bold with an orange rounded bar over the last e's crossbar."""
    d,x0,total=text_path(fred,"Zumee",size,0.0,x,y,align)
    parts,_,gs,sc=layout(fred,"Zumee",size,0.0)
    (bx0,by0,bx1,by1),adv=glyph_bounds(fred,'e')
    gname,off=parts[-1]
    ex0=x0+off+bx0*sc; ex1=x0+off+bx1*sc; xh=(by1-by0)*sc
    cy=y-xh*0.55                      # crossbar centre (y grows downward)
    th=xh*0.20                        # bar thickness
    bar='<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="%s"/>' % (ex0+xh*0.24, cy-th/2, (ex1-ex0)-xh*0.40, th, th/2, ebar)
    return '<path d="%s" fill="%s"/>%s' % (d,color,bar), x0, total

def car(body, glass, panel, ptext, spark, rim, hub, shadow, x=0, y=0, s=1.0):
    """Coupe facing right in a 700x270 box (y from -40 for sparkles)."""
    d,_,_=text_path(fred,"Zumee",64,0.0,352,186,'center')
    return ('<g transform="translate(%s %s) scale(%s)">'
      '<rect x="70" y="252" width="560" height="7" rx="3.5" fill="%s"/>'
      '<path d="M22 208 L22 152 C22 136 34 128 52 124 L66 120 L70 108 L92 114 L160 108 C200 56 268 34 362 34 C446 34 506 48 566 92 L648 110 C680 117 694 132 696 154 L696 208 Z" fill="%s"/>'
      '<path d="M180 108 C212 66 270 52 360 52 C432 52 484 62 536 98 Z" fill="%s"/>'
      '<path d="M334 52 L350 52 L356 98 L338 98 Z" fill="%s"/>'
      '<path d="M652 128 L694 142 L694 156 L648 148 Z" fill="%s"/>'
      '<path d="M22 150 L52 148 L52 164 L22 164 Z" fill="%s"/>'
      '<path d="M258 124 L478 124 L470 208 L240 208 Z" fill="%s"/>'
      '<path d="%s" fill="%s"/>'
      '<g stroke="%s" stroke-width="13" stroke-linecap="round" fill="none"><path d="M590 6 L578 -26"/><path d="M632 4 L650 -24"/></g>'
      '<g><circle cx="150" cy="212" r="50" fill="%s"/><circle cx="150" cy="212" r="34" fill="none" stroke="%s" stroke-width="11"/><circle cx="150" cy="212" r="19" fill="%s"/></g>'
      '<g><circle cx="560" cy="212" r="50" fill="%s"/><circle cx="560" cy="212" r="34" fill="none" stroke="%s" stroke-width="11"/><circle cx="560" cy="212" r="19" fill="%s"/></g>'
      '</g>') % (x,y,s, shadow, body, glass, body, glass, spark, panel, d, ptext, spark, body,rim,hub, body,rim,hub)

def tagline(x,y,size,ink,accent,align='center'):
    parts=[("DRIVE ",ink),("&",accent),(" EARN",ink)]
    widths=[layout(sora_b,t,size,0.28)[1] for t,_ in parts]
    total=sum(widths)+0.28*size*2
    x0 = x-total/2 if align=='center' else x
    out=[]; cur=x0
    for (t,c),w in zip(parts,widths):
        d,_,_=text_path(sora_b,t,size,0.28,cur,y,'left'); out.append('<path d="%s" fill="%s"/>'%(d,c)); cur+=w+0.28*size
    dash=lambda a,b: '<path d="M%.1f %.1f L%.1f %.1f" stroke="%s" stroke-width="%.1f" stroke-linecap="round"/>' % (a,y-size*0.36,b,y-size*0.36,accent,size*0.14)
    return ''.join(out)+dash(x0-size*1.7,x0-size*0.55)+dash(x0+total+size*0.55,x0+total+size*1.7), x0, total
def tagline2(x,y,size,color,align='center'):
    d,_,_=text_path(sora_s,"YOUR CAR. PASSIVE INCOME.",size,0.14,x,y,align); return '<path d="%s" fill="%s"/>'%(d,color)

def svg(vb, body, w=None, h=None):
    W,H=vb.split()[2:]; return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s" width="%s" height="%s">\n%s\n</svg>\n' % (vb,w or W,h or H,body)

def vertical(P, bg=None):
    b='<rect width="1000" height="640" fill="%s"/>'%bg if bg else ''
    wm,_,_=wordmark(P['wm'],P['ebar'],500,560,270)
    return svg("0 0 1000 640", b+car(P['body'],P['glass'],P['panel'],P['ptext'],P['accent'],P['rim'],P['hub'],P['shadow'],x=170,y=80,s=0.94)+wm)
def horizontal(P, bg=None, tag=True):
    b='<rect width="1400" height="360" fill="%s"/>'%bg if bg else ''
    wm,_,_=wordmark(P['wm'],P['ebar'],730,258 if tag else 262,230,'left')
    tl=''
    if tag:
        t,_,_=tagline(730+30,326,30,P['tag1'],P['accent'],'left'); tl=t
    return svg("0 0 1400 360", b+car(P['body'],P['glass'],P['panel'],P['ptext'],P['accent'],P['rim'],P['hub'],P['shadow'],x=10,y=64,s=0.95)+wm+tl)
def mark(P, bg=None):
    b='<rect width="760" height="330" fill="%s"/>'%bg if bg else ''
    return svg("0 0 760 330", b+car(P['body'],P['glass'],P['panel'],P['ptext'],P['accent'],P['rim'],P['hub'],P['shadow'],x=30,y=50,s=1.0), 1520, 660)
def icon(P, bg):
    return svg("0 0 100 100", '<rect width="100" height="100" rx="24" fill="%s"/>'%bg + car(P['body'],P['glass'],P['panel'],P['ptext'],P['accent'],P['rim'],P['hub'],P['shadow'],x=5,y=31,s=0.128), 512, 512)

LIGHT=dict(body=INK,glass=WHITE,panel=ORANGE,ptext=WHITE,accent=ORANGE,rim=WHITE,hub=INK,shadow=SHADOW,wm=INK,ebar=ORANGE,tag1=INK,tag2=INK2)
DARK =dict(body=CREAM,glass=INK,panel=ORANGE,ptext=WHITE,accent=ORANGE,rim=INK,hub=CREAM,shadow="#3A424B",wm=CREAM,ebar=ORANGE,tag1=CREAM,tag2="#B3ACA5")
MONO =dict(body=INK,glass=WHITE,panel=INK,ptext=WHITE,accent=INK,rim=WHITE,hub=INK,shadow="#9AA3AD",wm=INK,ebar=INK,tag1=INK,tag2=INK)
ONORANGE=dict(body=INK,glass=ORANGE,panel=WHITE,ptext=INK,accent=WHITE,rim=ORANGE,hub=INK,shadow="#C9540F",wm=INK,ebar=WHITE,tag1=INK,tag2=INK)

F={}
F['zumee-logo-vertical.svg']=vertical(LIGHT); F['zumee-logo-vertical-dark.svg']=vertical(DARK,bg=INK); F['zumee-logo-vertical-mono.svg']=vertical(MONO)
F['zumee-logo-horizontal.svg']=horizontal(LIGHT,tag=False); F['zumee-logo-horizontal-dark.svg']=horizontal(DARK,bg=INK,tag=False); F['zumee-logo-horizontal-mono.svg']=horizontal(MONO,tag=False); F['zumee-logo-horizontal-white.svg']=horizontal(DARK,tag=False)
F['zumee-logo-mark.svg']=mark(LIGHT); F['zumee-logo-mark-white.svg']=mark(DARK)
F['zumee-logo-icon.svg']=icon(LIGHT,WHITE); F['zumee-logo-icon-dark.svg']=icon(DARK,INK); F['zumee-logo-icon-orange.svg']=icon(ONORANGE,ORANGE)
wm,_,_=wordmark(INK,ORANGE,20,215,230,'left'); F['zumee-logo-wordmark.svg']=svg("0 0 720 270",wm)
wm,_,_=wordmark(WHITE,ORANGE,20,215,230,'left'); F['zumee-logo-wordmark-white.svg']=svg("0 0 720 270",wm)
for n,c in F.items(): open(n,'w').write(c)
print(len(F),'files')
cells=[]
for n in F:
    s=open(n).read(); s=re.sub(r'\swidth="\d+"\sheight="\d+"','',s,count=1).replace('<svg ','<svg style="width:100%;height:auto" ',1)
    dark=('dark' in n) or ('white' in n); bg='#1B1F24' if dark else '#FFFFFF'; fg='#eee' if dark else '#333'
    w=180 if 'icon' in n else (400 if 'vertical' in n else 520)
    cells.append('<div style="background:%s;padding:14px;border:1px solid #bbb"><div style="font:11px monospace;color:%s;margin-bottom:6px">%s</div><div style="width:%spx">%s</div></div>'%(bg,fg,n,w,s))
open('sheetE.html','w').write('<!doctype html><html><body style="margin:0;background:#888;padding:12px"><div style="display:grid;grid-template-columns:repeat(2,1fr);gap:10px">'+''.join(cells)+'</div></body></html>')
