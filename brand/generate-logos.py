from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
import re

bold=instancer.instantiateVariableFont(TTFont('Sora-VF.ttf'),{'wght':700},inplace=False)
semi=instancer.instantiateVariableFont(TTFont('Sora-VF.ttf'),{'wght':600},inplace=False)
def text_path(font,text,size,tracking_em=0.0,x=0,y=0,align='center'):
    gs=font.getGlyphSet(); cmap=font.getBestCmap(); upem=font['head'].unitsPerEm
    sc=size/upem; hmtx=font['hmtx']; adv=0; parts=[]
    for ch in text:
        g=cmap.get(ord(ch))
        if g is None: adv+=size*0.3; continue
        parts.append((g,adv)); adv+=hmtx[g][0]*sc+tracking_em*size
    total=adv-tracking_em*size
    x0 = x-total/2 if align=='center' else (x-total if align=='right' else x)
    d=[]
    for g,off in parts:
        pen=SVGPathPen(gs); TransformPen(pen,(sc,0,0,-sc,x0+off,y)); tp=TransformPen(pen,(sc,0,0,-sc,x0+off,y)); gs[g].draw(tp)
        p=pen.getCommands()
        if p: d.append(p)
    return ' '.join(d)

ORANGE="#F26B1D"; INK="#1B1F24"; CREAM="#FFF7EF"; WHITE="#FFFFFF"; INK2="#4A4F55"
WM_W=260  # centerline width of "zumee"; add 11 for stroke

def wordmark(color, x=0, y=0, scale=1.0, sw=11, ebar=None):
    """Monoline 'zumee'. Only the last e's crossbar takes the accent colour."""
    ebar = ebar or color
    return ('<g transform="translate(%s %s) scale(%s)" fill="none" stroke-width="%s" stroke-linecap="round" stroke-linejoin="round">'
            '<g stroke="%s"><path d="M0 0 H30 L0 40 H30"/><path d="M52 0 V22 A15 15 0 0 0 82 22 M82 0 V40"/>'
            '<path d="M104 40 V12 A12 12 0 0 1 128 12 V40 M128 12 A12 12 0 0 1 152 12 V40"/>'
            '<path d="M206 20 A16 16 0 1 0 201.3 31.3"/><path d="M174 20 H199"/>'
            '<path d="M260 20 A16 16 0 1 0 255.3 31.3"/></g>'
            '<path d="M228 20 H253" stroke="%s"/></g>') % (x,y,scale,sw,color,ebar)

def wordmark_wheel(ink, accent, x=0, y=0, scale=1.0):
    return ('<g transform="translate(%s %s) scale(%s)" fill="none" stroke-width="11" stroke-linecap="round" stroke-linejoin="round">'
            '<g stroke="%s"><path d="M-46 4 H-24"/><path d="M-58 20 H-24"/><path d="M-46 36 H-24"/></g>'
            '<g stroke="%s"><path d="M0 0 H30 L0 40 H30"/><path d="M52 0 V22 A15 15 0 0 0 82 22 M82 0 V40"/>'
            '<path d="M104 40 V12 A12 12 0 0 1 128 12 V40 M128 12 A12 12 0 0 1 152 12 V40"/>'
            '<path d="M174 20 H206 A16 16 0 1 0 201.3 31.3"/></g>'
            '<g stroke="%s"><path d="M228 20 H260 A16 16 0 1 0 255.3 31.3"/></g>'
            '<circle cx="244" cy="20" r="7.5" fill="%s" stroke="none"/></g>') % (x,y,scale,accent,ink,accent,accent)

def icon_car_A(bg, fg, rounded=True):
    rx = 24 if rounded else 0
    return ('<rect width="100" height="100" rx="%s" fill="%s"/>'
    '<g fill="none" stroke="%s" stroke-width="5" stroke-linecap="round"><path d="M9 47 H21"/><path d="M5 57 H17"/><path d="M11 67 H19"/></g>'
    '<path d="M27 70 L27 55 L41 52 L49 39 L69 39 L78 52 L89 55 L89 70 Z" fill="%s" stroke="%s" stroke-width="6" stroke-linejoin="round"/>'
    '<circle cx="41" cy="70" r="7.5" fill="%s" stroke="%s" stroke-width="5"/><circle cx="76" cy="70" r="7.5" fill="%s" stroke="%s" stroke-width="5"/>') % (rx,bg,fg,fg,fg,bg,fg,bg,fg)

def plate(bg, ink, bolt, w=220, h=120):
    sc=0.62; ww=WM_W*sc; hh=40*sc
    return ('<rect x="0" y="0" width="%s" height="%s" rx="16" fill="%s"/>'
    '<rect x="7" y="7" width="%s" height="%s" rx="11" fill="none" stroke="%s" stroke-opacity="0.35" stroke-width="2.5"/>'
    '<circle cx="20" cy="20" r="4" fill="%s"/><circle cx="%s" cy="20" r="4" fill="%s"/><circle cx="20" cy="%s" r="4" fill="%s"/><circle cx="%s" cy="%s" r="4" fill="%s"/>%s') % (
    w,h,bg, w-14,h-14,ink, bolt,w-20,bolt,h-20,bolt,w-20,h-20,bolt, wordmark(ink,x=(w-ww)/2,y=(h-hh)/2,scale=sc))

def plate_icon(bg, ink, bolt):
    return ('<rect width="100" height="100" rx="24" fill="%s"/><rect x="14" y="30" width="72" height="40" rx="8" fill="%s"/>'
    '<circle cx="21" cy="37" r="2" fill="%s"/><circle cx="79" cy="37" r="2" fill="%s"/><circle cx="21" cy="63" r="2" fill="%s"/><circle cx="79" cy="63" r="2" fill="%s"/>'
    '<path d="M39 41 H61 L39 59 H61" fill="none" stroke="%s" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>') % (bg,ink,bg,bg,bg,bg,bg)

def icon_z(bg, fg):
    return ('<rect width="100" height="100" rx="24" fill="%s"/><g fill="none" stroke="%s" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"><path d="M38 30 H74 L38 70 H74"/></g>'
    '<g fill="none" stroke="%s" stroke-width="6" stroke-linecap="round"><path d="M16 36 H26"/><path d="M10 50 H26"/><path d="M16 64 H26"/></g>') % (bg,fg,fg)

def car(body, glass, panel, panel_text, spark, hub, x=0, y=0, scale=1.0):
    return ('<g transform="translate(%s %s) scale(%s)">'
    '<path d="M18 118 C16 104 20 96 34 92 L112 84 C126 82 134 78 146 66 C160 52 182 46 214 46 L262 46 C290 46 312 58 330 76 L356 84 C372 86 378 92 380 104 L382 118 L382 130 L18 130 Z" fill="%s"/>'
    '<path d="M150 82 C162 60 184 54 214 54 L260 54 C282 54 300 64 316 82 Z" fill="%s"/>'
    '<path d="M226 54 L234 54 L238 82 L230 82 Z" fill="%s"/>'
    '<path d="M30 96 L46 94 L44 102 L30 102 Z" fill="%s"/>'
    '<path d="M366 92 L380 96 L380 104 L366 104 Z" fill="%s"/>'
    '<path d="M146 92 L258 92 L252 122 L140 122 Z" fill="%s"/>%s'
    '<g stroke="%s" stroke-width="8" stroke-linecap="round" fill="none"><path d="M336 26 L344 10"/><path d="M358 32 L372 20"/></g>'
    '<g><circle cx="92" cy="126" r="23" fill="%s"/><circle cx="92" cy="126" r="12.5" fill="none" stroke="%s" stroke-width="5"/><circle cx="92" cy="126" r="4" fill="%s"/></g>'
    '<g><circle cx="312" cy="126" r="23" fill="%s"/><circle cx="312" cy="126" r="12.5" fill="none" stroke="%s" stroke-width="5"/><circle cx="312" cy="126" r="4" fill="%s"/></g></g>') % (
    x,y,scale, body, glass, body, glass, spark, panel, wordmark(panel_text,x=152,y=100,scale=0.36,sw=12), spark, body,hub,hub, body,hub,hub)

def svg(vb, body, w=None, h=None):
    W,H = vb.split()[2:]
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s" width="%s" height="%s">\n%s\n</svg>\n' % (vb, w or W, h or H, body)
def T1(x,y,size,fill,align='center'): return '<path d="%s" fill="%s"/>' % (text_path(bold,"DRIVE & EARN",size,0.26,x,y,align), fill)
def T2(x,y,size,fill,align='center'): return '<path d="%s" fill="%s"/>' % (text_path(semi,"YOUR CAR. PASSIVE INCOME.",size,0.18,x,y,align), fill)

def vertical(body, glass, panel, ptext, spark, hub, wm, ebar, tag1, tag2, bg=None):
    bgrect = '<rect width="420" height="345" fill="%s"/>' % bg if bg else ''
    sc=1.25; x0=(420-(WM_W*sc+11*sc))/2+5.5*sc
    return svg("0 0 420 345", bgrect + car(body,glass,panel,ptext,spark,hub,x=10,y=6,scale=0.95)
        + wordmark(wm, x=x0, y=180, scale=sc, sw=14, ebar=ebar) + T1(210,281,24,tag1) + T2(210,311,13.5,tag2))
def horizontal(body, glass, panel, ptext, spark, hub, wm, ebar, tag1, bg=None):
    bgrect = '<rect width="640" height="170" fill="%s"/>' % bg if bg else ''
    return svg("0 0 640 170", bgrect + car(body,glass,panel,ptext,spark,hub,x=6,y=14,scale=0.62)
        + wordmark(wm, x=290, y=50, scale=1.05, sw=13, ebar=ebar) + T1(290,124,15,tag1,'left'))
def compact(body, glass, panel, ptext, spark, hub, wm, ebar):
    return svg("0 0 640 150", car(body,glass,panel,ptext,spark,hub,x=6,y=0,scale=0.62) + wordmark(wm, x=290, y=42, scale=1.05, sw=13, ebar=ebar))
def mark(body, glass, panel, ptext, spark, hub, bg=None, tile=False):
    if tile: return svg("0 0 100 100", '<rect width="100" height="100" rx="24" fill="%s"/>' % bg + car(body,glass,panel,ptext,spark,hub,x=6,y=31,scale=0.22), 512, 512)
    return svg("0 0 400 160", car(body,glass,panel,ptext,spark,hub), 800, 320)

F={}
# D primary
F['zumee-D-vertical.svg']      = vertical(INK,CREAM,ORANGE,WHITE,ORANGE,CREAM, INK,ORANGE, INK,INK2)
F['zumee-D-vertical-dark.svg'] = vertical(CREAM,INK,ORANGE,WHITE,ORANGE,INK, CREAM,ORANGE, CREAM,"#B3ACA5", bg=INK)
F['zumee-D-vertical-mono.svg'] = vertical(INK,WHITE,INK,WHITE,INK,WHITE, INK,INK, INK,INK)
F['zumee-D-horizontal.svg']      = horizontal(INK,CREAM,ORANGE,WHITE,ORANGE,CREAM, INK,ORANGE, INK)
F['zumee-D-horizontal-dark.svg'] = horizontal(CREAM,INK,ORANGE,WHITE,ORANGE,INK, CREAM,ORANGE, CREAM, bg=INK)
F['zumee-D-horizontal-mono.svg'] = horizontal(INK,WHITE,INK,WHITE,INK,WHITE, INK,INK, INK)
F['zumee-D-horizontal-compact.svg']       = compact(INK,CREAM,ORANGE,WHITE,ORANGE,CREAM, INK,ORANGE)
F['zumee-D-horizontal-compact-white.svg'] = compact(CREAM,INK,ORANGE,WHITE,ORANGE,INK, CREAM,ORANGE)
F['zumee-D-mark.svg']        = mark(INK,CREAM,ORANGE,WHITE,ORANGE,CREAM)
F['zumee-D-mark-white.svg']  = mark(CREAM,INK,ORANGE,WHITE,ORANGE,INK)
F['zumee-D-icon.svg']        = mark(INK,WHITE,ORANGE,WHITE,ORANGE,WHITE, bg=WHITE, tile=True)
F['zumee-D-icon-dark.svg']   = mark(CREAM,INK,ORANGE,WHITE,ORANGE,INK, bg=INK, tile=True)
F['zumee-D-icon-orange.svg'] = mark(INK,ORANGE,CREAM,INK,CREAM,ORANGE, bg=ORANGE, tile=True)
# A
def lockup_A(bg_tile, fg_tile, text): return svg("0 0 440 120", '<g transform="translate(10 10)">'+icon_car_A(bg_tile,fg_tile)+'</g>'+wordmark(text,x=138,y=40,scale=1.0))
F['zumee-A-lockup.svg']=lockup_A(ORANGE,WHITE,INK); F['zumee-A-lockup-dark.svg']=lockup_A(ORANGE,WHITE,WHITE); F['zumee-A-lockup-mono.svg']=lockup_A(INK,WHITE,INK)
F['zumee-A-icon.svg']=svg("0 0 100 100",icon_car_A(ORANGE,WHITE),512,512); F['zumee-A-icon-mono.svg']=svg("0 0 100 100",icon_car_A(INK,WHITE),512,512)
# B
F['zumee-B-plate.svg']=svg("0 0 220 120",plate(ORANGE,INK,INK),440,240); F['zumee-B-plate-dark.svg']=svg("0 0 220 120",plate(ORANGE,WHITE,WHITE),440,240); F['zumee-B-plate-mono.svg']=svg("0 0 220 120",plate(INK,WHITE,WHITE),440,240)
F['zumee-B-icon.svg']=svg("0 0 100 100",plate_icon(ORANGE,INK,INK),512,512)
# C
def lockup_C(ink,accent): return svg("0 0 440 120", wordmark_wheel(ink,accent,x=96,y=40,scale=1.15))
F['zumee-C-wordmark.svg']=lockup_C(INK,ORANGE); F['zumee-C-wordmark-dark.svg']=lockup_C(WHITE,ORANGE); F['zumee-C-wordmark-mono.svg']=lockup_C(INK,INK)
F['zumee-C-icon.svg']=svg("0 0 100 100",icon_z(ORANGE,WHITE),512,512)
# plain wordmarks
F['zumee-wordmark.svg']=svg("0 0 300 70",wordmark(INK,x=17,y=15)); F['zumee-wordmark-white.svg']=svg("0 0 300 70",wordmark(WHITE,x=17,y=15)); F['zumee-wordmark-orange.svg']=svg("0 0 300 70",wordmark(ORANGE,x=17,y=15))
for n,c in F.items(): open(n,'w').write(c)
print(len(F),'files')
cells=[]
for n in F:
    s=open(n).read(); s=re.sub(r'\swidth="\d+"\sheight="\d+"','',s,count=1).replace('<svg ','<svg style="width:100%;height:auto" ',1)
    dark=('dark' in n) or ('white' in n); bg='#1B1F24' if dark else '#FFF7EF'; fg='#eee' if dark else '#333'
    w=160 if 'icon' in n else (360 if 'vertical' in n else 440)
    cells.append('<div style="background:%s;padding:14px;border:1px solid #bbb"><div style="font:11px monospace;color:%s;margin-bottom:6px">%s</div><div style="width:%spx">%s</div></div>'%(bg,fg,n,w,s))
open('sheet.html','w').write('<!doctype html><html><body style="margin:0;background:#888;padding:12px"><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px">'+''.join(cells)+'</div></body></html>')
