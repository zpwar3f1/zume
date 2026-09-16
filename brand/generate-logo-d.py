from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
import re

bold=instancer.instantiateVariableFont(TTFont('Sora-VF.ttf'),{'wght':700},inplace=False)
semi=instancer.instantiateVariableFont(TTFont('Sora-VF.ttf'),{'wght':600},inplace=False)
def text_path(font,text,size,tracking_em=0.0,x=0,y=0,align='center'):
    gs=font.getGlyphSet(); cmap=font.getBestCmap(); upem=font['head'].unitsPerEm
    sc=size/upem; hmtx=font['hmtx']
    adv=0; parts=[]
    for ch in text:
        g=cmap.get(ord(ch))
        if g is None: adv+=size*0.3; continue
        w=hmtx[g][0]*sc
        parts.append((g,adv)); adv+=w+tracking_em*size
    total=adv-tracking_em*size
    x0 = x-total/2 if align=='center' else (x-total if align=='right' else x)
    d=[]
    for g,off in parts:
        pen=SVGPathPen(gs); tp=TransformPen(pen,(sc,0,0,-sc,x0+off,y)); gs[g].draw(tp)
        p=pen.getCommands()
        if p: d.append(p)
    return ' '.join(d)

ORANGE="#F26B1D"; INK="#1B1F24"; CREAM="#FFF7EF"; WHITE="#FFFFFF"; INK2="#4A4F55"

def wordmark(color, x=0, y=0, scale=1.0, sw=11, ebar=None):
    ebar = ebar or color
    return ('<g transform="translate(%s %s) scale(%s)" fill="none" stroke-width="%s" stroke-linecap="round" stroke-linejoin="round">'
            '<g stroke="%s"><path d="M0 0 H30 L0 40 H30"/><path d="M52 0 V22 A15 15 0 0 0 82 22 M82 0 V40"/><path d="M104 40 V12 A12 12 0 0 1 128 12 V40 M128 12 A12 12 0 0 1 152 12 V40"/><path d="M206 20 A16 16 0 1 0 201.3 31.3"/></g>'
            '<path d="M174 20 H199" stroke="%s"/></g>') % (x,y,scale,sw,color,ebar)

def car(body, glass, panel, panel_text, spark, hub, x=0, y=0, scale=1.0):
    return ('<g transform="translate(%s %s) scale(%s)">'
    '<path d="M18 118 C16 104 20 96 34 92 L112 84 C126 82 134 78 146 66 C160 52 182 46 214 46 L262 46 C290 46 312 58 330 76 L356 84 C372 86 378 92 380 104 L382 118 L382 130 L18 130 Z" fill="%s"/>'
    '<path d="M150 82 C162 60 184 54 214 54 L260 54 C282 54 300 64 316 82 Z" fill="%s"/>'
    '<path d="M226 54 L234 54 L238 82 L230 82 Z" fill="%s"/>'
    '<path d="M30 96 L46 94 L44 102 L30 102 Z" fill="%s"/>'
    '<path d="M366 92 L380 96 L380 104 L366 104 Z" fill="%s"/>'
    '<path d="M146 92 L258 92 L252 122 L140 122 Z" fill="%s"/>'
    '%s'
    '<g stroke="%s" stroke-width="8" stroke-linecap="round" fill="none"><path d="M336 26 L344 10"/><path d="M358 32 L372 20"/></g>'
    '<g><circle cx="92" cy="126" r="23" fill="%s"/><circle cx="92" cy="126" r="12.5" fill="none" stroke="%s" stroke-width="5"/><circle cx="92" cy="126" r="4" fill="%s"/></g>'
    '<g><circle cx="312" cy="126" r="23" fill="%s"/><circle cx="312" cy="126" r="12.5" fill="none" stroke="%s" stroke-width="5"/><circle cx="312" cy="126" r="4" fill="%s"/></g>'
    '</g>') % (x,y,scale, body, glass, body, glass, spark, panel, wordmark(panel_text,x=157,y=99,scale=0.40,sw=12), spark, body,hub,hub, body,hub,hub)

def svg(vb, body, w=None, h=None):
    W,H = vb.split()[2:]
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s" width="%s" height="%s">\n%s\n</svg>\n' % (vb, w or W, h or H, body)

def T1(x,y,size,fill,align='center'): return '<path d="%s" fill="%s"/>' % (text_path(bold,"DRIVE & EARN",size,0.26,x,y,align), fill)
def T2(x,y,size,fill,align='center'): return '<path d="%s" fill="%s"/>' % (text_path(semi,"YOUR CAR. PASSIVE INCOME.",size,0.18,x,y,align), fill)

def vertical(body, glass, panel, ptext, spark, hub, wm, ebar, tag1, tag2, bg=None):
    bgrect = '<rect width="420" height="345" fill="%s"/>' % bg if bg else ''
    return svg("0 0 420 345", bgrect + car(body,glass,panel,ptext,spark,hub,x=10,y=6,scale=0.95)
        + wordmark(wm, x=55.5, y=176, scale=1.5, sw=14, ebar=ebar) + T1(210,281,24,tag1) + T2(210,311,13.5,tag2))

def horizontal(body, glass, panel, ptext, spark, hub, wm, ebar, tag1, bg=None):
    bgrect = '<rect width="640" height="170" fill="%s"/>' % bg if bg else ''
    return svg("0 0 640 170", bgrect + car(body,glass,panel,ptext,spark,hub,x=6,y=14,scale=0.62)
        + wordmark(wm, x=290, y=46, scale=1.15, sw=13, ebar=ebar) + T1(290,124,15,tag1,'left'))

def mark(body, glass, panel, ptext, spark, hub, bg=None, tile=False):
    if tile:
        return svg("0 0 100 100", '<rect width="100" height="100" rx="24" fill="%s"/>' % bg + car(body,glass,panel,ptext,spark,hub,x=6,y=31,scale=0.22), 512, 512)
    return svg("0 0 400 160", car(body,glass,panel,ptext,spark,hub), 800, 320)

files={}
files['zume-D-vertical.svg']      = vertical(INK,CREAM,ORANGE,WHITE,ORANGE,CREAM, INK,ORANGE, INK,INK2)
files['zume-D-vertical-dark.svg'] = vertical(CREAM,INK,ORANGE,WHITE,ORANGE,INK, CREAM,ORANGE, CREAM,"#B3ACA5", bg=INK)
files['zume-D-vertical-mono.svg'] = vertical(INK,WHITE,INK,WHITE,INK,WHITE, INK,INK, INK,INK)
files['zume-D-horizontal.svg']      = horizontal(INK,CREAM,ORANGE,WHITE,ORANGE,CREAM, INK,ORANGE, INK)
files['zume-D-horizontal-dark.svg'] = horizontal(CREAM,INK,ORANGE,WHITE,ORANGE,INK, CREAM,ORANGE, CREAM, bg=INK)
files['zume-D-horizontal-mono.svg'] = horizontal(INK,WHITE,INK,WHITE,INK,WHITE, INK,INK, INK)
files['zume-D-horizontal-compact.svg'] = svg("0 0 640 150", car(INK,CREAM,ORANGE,WHITE,ORANGE,CREAM,x=6,y=0,scale=0.62) + wordmark(INK, x=290, y=40, scale=1.15, sw=13, ebar=ORANGE))
files['zume-D-horizontal-compact-white.svg'] = svg("0 0 640 150", car(CREAM,INK,ORANGE,WHITE,ORANGE,INK,x=6,y=0,scale=0.62) + wordmark(CREAM, x=290, y=40, scale=1.15, sw=13, ebar=ORANGE))
files['zume-D-mark.svg']        = mark(INK,CREAM,ORANGE,WHITE,ORANGE,CREAM)
files['zume-D-mark-white.svg']  = mark(CREAM,INK,ORANGE,WHITE,ORANGE,INK)
files['zume-D-icon.svg']        = mark(INK,WHITE,ORANGE,WHITE,ORANGE,WHITE, bg=WHITE, tile=True)
files['zume-D-icon-dark.svg']   = mark(CREAM,INK,ORANGE,WHITE,ORANGE,INK, bg=INK, tile=True)
files['zume-D-icon-orange.svg'] = mark(INK,ORANGE,CREAM,INK,CREAM,ORANGE, bg=ORANGE, tile=True)
for n,c in files.items(): open(n,'w').write(c)
print(len(files),'files written')

cells=[]
for n in files:
    s=open(n).read(); s=re.sub(r'\swidth="\d+"\sheight="\d+"','',s,count=1).replace('<svg ','<svg style="width:100%;height:auto" ',1)
    dark = ('dark' in n) or ('white' in n)
    bg = '#1B1F24' if dark else '#FFF7EF'; fg = '#eee' if dark else '#333'
    w = 220 if ('icon' in n) else (400 if 'vertical' in n else 520)
    cells.append('<div style="background:%s;padding:16px;border:1px solid #bbb"><div style="font:12px monospace;color:%s;margin-bottom:8px">%s</div><div style="width:%spx">%s</div></div>' % (bg,fg,n,w,s))
open('sheetD.html','w').write('<!doctype html><html><body style="margin:0;background:#888;padding:14px"><div style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px">'+''.join(cells)+'</div></body></html>')
