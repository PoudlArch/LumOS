#!/usr/bin/env python3
"""Dessine les fonds d'écran de Lumos OS, un par maison, dans assets/fonds/.

Illustration originale (château sur un lac, la nuit), générée à partir de la
palette de themes/maisons.conf. Le tirage aléatoire est figé : relancer le
script redonne exactement les mêmes images.

    python tools/dessiner_fonds.py
"""
import random
from pathlib import Path

L, H = 2560, 1440
HORIZON = 1122          # ligne d'eau
BASE = 985              # pied des murs, caché derrière la colline
LUNE = (1960, 330, 150)
RACINE = Path(__file__).resolve().parent.parent

# Tours : centre, largeur, hauteur du sommet du mur, hauteur du toit
TOURS = [
    (772, 46, 800, 92),
    (884, 66, 690, 132),
    (1012, 50, 642, 112),
    (1122, 86, 520, 196),
    (1334, 70, 652, 142),
    (1452, 42, 566, 122),
    (1542, 40, 806, 84),
]
# Corps de logis : gauche, droite, sommet du mur, hauteur du toit (0 = créneaux)
CORPS = [
    (795, 992, 830, 0),
    (985, 1165, 748, 62),
    (1160, 1306, 770, 74),
    (1300, 1525, 838, 0),
]


def hexa(c):
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def mel(a, b, t):
    """Mélange deux couleurs hexadécimales (t = 0 donne a, t = 1 donne b)."""
    ca, cb = hexa(a), hexa(b)
    return '#%02x%02x%02x' % tuple(round(ca[i] + (cb[i] - ca[i]) * t) for i in range(3))


def n(v):
    return ('%.1f' % v).rstrip('0').rstrip('.')


def etoiles(rnd):
    s = []
    for _ in range(460):
        x, y = rnd.uniform(0, L), 1060 * rnd.random() ** 1.5
        if (x - LUNE[0]) ** 2 + (y - LUNE[1]) ** 2 < 205 ** 2:
            continue
        r = rnd.choice([.7, .8, .9, 1, 1.1, 1.3, 1.6, 2.1])
        o = rnd.uniform(.35, 1) * (1 - y / 1350)
        c = rnd.choice(['#ffffff', '#ffffff', '#cfe0ff', '#ffe9c4'])
        s.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{r}" fill="{c}" opacity="{o:.2f}"/>')
    for _ in range(9):  # quelques étoiles à quatre branches
        x, y, r = rnd.uniform(80, L - 80), rnd.uniform(60, 620), rnd.uniform(7, 13)
        if (x - LUNE[0]) ** 2 + (y - LUNE[1]) ** 2 < 300 ** 2:
            continue
        s.append(f'<path d="M{n(x - r)} {n(y)} Q{n(x)} {n(y)} {n(x)} {n(y - r)} Q{n(x)} {n(y)} {n(x + r)} {n(y)} '
                 f'Q{n(x)} {n(y)} {n(x)} {n(y + r)} Q{n(x)} {n(y)} {n(x - r)} {n(y)} Z" fill="#fff8e0" opacity=".9"/>')
    return '\n'.join(s)


def crete(rnd, base, hmin, hmax, pas, rugosite):
    """Ligne de crête adoucie, refermée jusqu'en bas de l'image."""
    pts, x, h = [], -pas, rnd.uniform(hmin, hmax)
    while x <= L + 2 * pas:
        h = max(hmin, min(hmax, h + rnd.uniform(-rugosite, rugosite)))
        pts.append((x, base - h))
        x += pas * rnd.uniform(.6, 1.4)
    d = f'M{n(pts[0][0])} {H} L{n(pts[0][0])} {n(pts[0][1])}'
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        d += f' Q{n(x1)} {n(y1)} {n((x1 + x2) / 2)} {n((y1 + y2) / 2)}'
    return d + f' L{n(pts[-1][0])} {H} Z'


def creneaux(x0, x1, haut):
    d, x = f'M{x0} {BASE} V{haut}', x0
    while x < x1:
        w = min(9, x1 - x)
        d += f' v-10 h{w} v10'
        x += w
        if x < x1:
            g = min(8, x1 - x)
            d += f' h{g}'
            x += g
    return f'<path d="{d} V{BASE} Z"/>'


def logis(x0, x1, haut, toit):
    if not toit:
        return creneaux(x0, x1, haut)
    retrait = (x1 - x0) * .17
    return (f'<path d="M{x0} {BASE} V{haut} H{x0 - 8} Q{n(x0 + retrait * .4)} {n(haut - toit * .55)} {n(x0 + retrait)} {haut - toit} '
            f'H{n(x1 - retrait)} Q{n(x1 - retrait * .4)} {n(haut - toit * .55)} {x1 + 8} {haut} H{x1} V{BASE} Z"/>')


def tour(cx, larg, haut, toit):
    x0, x1 = cx - larg / 2, cx + larg / 2
    return (f'<rect x="{n(x0)}" y="{haut}" width="{larg}" height="{BASE - haut}"/>'
            f'<rect x="{n(x0 - 5)}" y="{haut - 6}" width="{larg + 10}" height="18" rx="2"/>'
            f'<path d="M{n(x0 - 9)} {haut - 5} Q{n(cx - larg * .15)} {n(haut - toit * .5)} {cx} {haut - toit} '
            f'Q{n(cx + larg * .15)} {n(haut - toit * .5)} {n(x1 + 9)} {haut - 5} Z"/>'
            f'<rect x="{n(cx - 1.2)}" y="{haut - toit - 26}" width="2.4" height="30"/>')


def fanion(cx, larg, haut, toit):
    x, y = cx + 1, haut - toit - 26
    return (f'<path d="M{x} {y} C{x + 9} {y - 4} {x + 15} {y + 6} {x + 25} {y + 2} L{x + 25} {y + 10} '
            f'C{x + 15} {y + 14} {x + 9} {y + 4} {x} {y + 9} Z"/>')


def reflet_lune_sur_tour(cx, larg, haut, toit):
    x1 = cx + larg / 2
    return (f'<rect x="{n(x1 - 2.5)}" y="{haut + 12}" width="2.5" height="{BASE - haut - 12}"/>'
            f'<path d="M{cx} {haut - toit} Q{n(cx + larg * .15)} {n(haut - toit * .5)} {n(x1 + 9)} {haut - 5}" '
            f'fill="none" stroke="#fff1c4" stroke-width="2"/>')


def fenetres(rnd):
    s = []
    for cx, larg, haut, _ in TOURS:
        for _ in range(rnd.randint(2, 4)):
            x = cx + rnd.uniform(-larg * .22, larg * .22) - 3
            y = rnd.uniform(haut + 26, 890)
            c = rnd.choice(['#ffd684', '#ffc46a', '#ffe2a6'])
            s.append(f'<rect x="{n(x)}" y="{n(y)}" width="6" height="13" rx="3" fill="{c}" opacity="{rnd.uniform(.7, 1):.2f}"/>')
    for x0, x1, haut, toit in CORPS:
        if toit:
            continue
        for _ in range(4):
            x, y = rnd.uniform(x0 + 14, x1 - 20), rnd.uniform(haut + 22, 895)
            s.append(f'<rect x="{n(x)}" y="{n(y)}" width="5" height="11" rx="2.5" fill="#ffd684" opacity="{rnd.uniform(.6, .95):.2f}"/>')
    for i in range(5):  # hautes fenêtres en ogive de la grande salle
        x, y, w, h = 1179 + i * 24, 800, 12, 46
        s.append(f'<path d="M{x} {y + h} V{y + 12} C{x} {y + 5} {x + w / 2} {y} {x + w / 2} {y} '
                 f'C{x + w / 2} {y} {x + w} {y + 5} {x + w} {y + 12} V{y + h} Z" fill="#ffcf7a"/>')
    for i in range(3):
        s.append(f'<rect x="{1012 + i * 46}" y="786" width="8" height="26" rx="4" fill="#ffd684" opacity=".9"/>')
    return '\n'.join(s)


def viaduc():
    haut, bas, pas = 912, 930, 98
    s = [f'<rect x="1575" y="{haut}" width="830" height="{bas - haut}"/>',
         f'<rect x="1575" y="{haut - 5}" width="830" height="3"/>']
    piles = list(range(1650, 2400, pas))
    for x in piles:
        s.append(f'<path d="M{x - 8} {bas} L{x - 11} {HORIZON + 4} H{x + 11} L{x + 8} {bas} Z"/>')
    for a, b in zip(piles, piles[1:]):
        r = (b - a - 16) / 2
        s.append(f'<path d="M{a + 8} {bas} V{bas + r} A{r} {r} 0 0 1 {b - 8} {bas + r} V{bas} Z"/>')
    return '\n'.join(s)


def sapin(rnd, x, base, h):
    etages = max(6, int(h / 40))
    tiers = []
    for i in range(1, etages + 1):
        y = base - h + i * h / etages
        tiers.append(((i / etages) ** .9 * h * .2 * rnd.uniform(.85, 1.15), y, rnd.uniform(4, 13), rnd.uniform(4, 13)))
    d = f'M{n(x)} {n(base - h)}'
    for demi, y, tombe, _ in tiers:
        d += f' Q{n(x + demi * .5)} {n(y - 12)} {n(x + demi)} {n(y + tombe)} L{n(x + demi * .4)} {n(y - 2)}'
    d += f' L{n(x + 7)} {n(base)} L{n(x - 7)} {n(base)}'
    for i in range(len(tiers) - 1, -1, -1):
        demi, y, _, tombe = tiers[i]
        fin = (x - tiers[i - 1][0] * .4, tiers[i - 1][1] - 2) if i else (x, base - h)
        d += (f' L{n(x - demi * .4)} {n(y - 2)} L{n(x - demi)} {n(y + tombe)} '
              f'Q{n(x - demi * .5)} {n(y - 12)} {n(fin[0])} {n(fin[1])}')
    return f'<path d="{d} Z"/>'


def dessiner(nom, libelle, accent, ciel_haut, ciel_bas, lueur):
    rnd = random.Random(1991)
    noir = '000000'
    pierre_g, pierre_d = mel(ciel_haut, noir, .5), mel(ciel_bas, noir, .55)
    premier_plan = mel(ciel_haut, noir, .72)
    brume = mel(lueur, 'ffffff', .5)
    lx, ly, lr = LUNE

    silhouette = '\n'.join(
        [logis(*c) for c in CORPS] + [tour(*t) for t in TOURS] + [viaduc()] + [
            # colline du château et rive droite
            '<path d="M380 1126 C520 1100 600 1010 720 965 C800 932 900 918 1000 914 L1560 912 '
            'C1650 918 1720 960 1790 1010 C1860 1060 1950 1105 2080 1126 Z"/>',
            '<path d="M2225 1126 C2290 1060 2330 932 2420 906 C2480 890 2530 884 2560 882 L2560 1126 Z"/>',
        ])
    rides = []
    for _ in range(110):
        y = HORIZON + 10 + (H - HORIZON - 20) * rnd.random() ** 1.6
        longueur = rnd.uniform(30, 90) + (y - HORIZON) * .5
        x = rnd.uniform(-50, L)
        rides.append(f'<path d="M{n(x)} {n(y)} q{n(longueur / 2)} {n(rnd.uniform(-2, 2))} {n(longueur)} 0" '
                     f'opacity="{rnd.uniform(.05, .16):.2f}"/>')
    reflet_lune = []
    for i in range(26):
        y = HORIZON + 14 + i * 11.5
        larg = rnd.uniform(50, 120) + i * 5
        reflet_lune.append(f'<ellipse cx="{n(lx + rnd.uniform(-14, 14))}" cy="{n(y)}" rx="{n(larg / 2)}" '
                           f'ry="{n(rnd.uniform(1.6, 3.4))}" opacity="{max(.06, .5 - i * .017):.2f}"/>')
    sapins_g = [sapin(rnd, x, H + 30, h) for x, h in
                [(40, 620), (150, 760), (265, 540), (360, 660), (470, 470), (560, 380)]]
    sapins_d = [sapin(rnd, x, H + 30, h) for x, h in
                [(2110, 360), (2200, 500), (2300, 430), (2390, 640), (2480, 560), (2545, 700)]]

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<!-- Lumos OS, fond d'écran {libelle}. Illustration originale générée par tools/dessiner_fonds.py -->
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {L} {H}" width="{L}" height="{H}">
<defs>
  <linearGradient id="g-ciel" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#{ciel_haut}"/>
    <stop offset=".42" stop-color="{mel(ciel_haut, ciel_bas, .5)}"/>
    <stop offset=".68" stop-color="#{ciel_bas}"/>
    <stop offset=".78" stop-color="{mel(ciel_bas, lueur, .3)}"/>
  </linearGradient>
  <radialGradient id="g-lune" cx=".38" cy=".36" r=".75">
    <stop offset="0" stop-color="#fffdf2"/>
    <stop offset=".55" stop-color="#f6eac0"/>
    <stop offset="1" stop-color="#d6c38a"/>
  </radialGradient>
  <radialGradient id="g-halo">
    <stop offset="0" stop-color="#fff3c9" stop-opacity=".5"/>
    <stop offset=".3" stop-color="#fff3c9" stop-opacity=".16"/>
    <stop offset=".65" stop-color="{mel(lueur, 'fff3c9', .5)}" stop-opacity=".05"/>
    <stop offset="1" stop-color="#fff3c9" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="g-pierre" gradientUnits="userSpaceOnUse" x1="700" y1="0" x2="1700" y2="0">
    <stop offset="0" stop-color="{pierre_g}"/>
    <stop offset=".6" stop-color="{mel(ciel_haut, noir, .4)}"/>
    <stop offset="1" stop-color="{pierre_d}"/>
  </linearGradient>
  <linearGradient id="g-lac" gradientUnits="userSpaceOnUse" x1="0" y1="{HORIZON}" x2="0" y2="{H}">
    <stop offset="0" stop-color="{mel(ciel_bas, lueur, .22)}"/>
    <stop offset=".18" stop-color="#{ciel_bas}"/>
    <stop offset=".6" stop-color="{mel(ciel_haut, ciel_bas, .35)}"/>
    <stop offset="1" stop-color="{mel(ciel_haut, noir, .45)}"/>
  </linearGradient>
  <linearGradient id="g-fondu" gradientUnits="userSpaceOnUse" x1="0" y1="{HORIZON}" x2="0" y2="{HORIZON + 300}">
    <stop offset="0" stop-color="#fff" stop-opacity=".62"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="g-filante" x1="0" y1="1" x2="1" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/>
    <stop offset="1" stop-color="#fff" stop-opacity=".9"/>
  </linearGradient>
  <radialGradient id="g-vignette" cx=".5" cy=".46" r=".75">
    <stop offset=".55" stop-color="#000" stop-opacity="0"/>
    <stop offset="1" stop-color="#000" stop-opacity=".6"/>
  </radialGradient>
  <filter id="f-flou-90" filterUnits="userSpaceOnUse" x="-400" y="-400" width="{L + 800}" height="{H + 800}"><feGaussianBlur stdDeviation="90"/></filter>
  <filter id="f-flou-30" filterUnits="userSpaceOnUse" x="-200" y="-200" width="{L + 400}" height="{H + 400}"><feGaussianBlur stdDeviation="30"/></filter>
  <filter id="f-flou-14" filterUnits="userSpaceOnUse" x="-100" y="-100" width="{L + 200}" height="{H + 200}"><feGaussianBlur stdDeviation="14"/></filter>
  <filter id="f-flou-3" filterUnits="userSpaceOnUse" x="0" y="{HORIZON - 20}" width="{L}" height="{H - HORIZON + 40}"><feGaussianBlur stdDeviation="3 1.2"/></filter>
  <filter id="f-lueur" x="-200%" y="-200%" width="500%" height="500%">
    <feGaussianBlur stdDeviation="5" result="halo"/>
    <feMerge><feMergeNode in="halo"/><feMergeNode in="halo"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <mask id="m-reflet"><rect x="0" y="{HORIZON}" width="{L}" height="{H - HORIZON}" fill="url(#g-fondu)"/></mask>
</defs>

<rect id="ciel" width="{L}" height="{H}" fill="url(#g-ciel)"/>

<g id="aurore" fill="none" stroke="#{lueur}" stroke-linecap="round">
  <ellipse cx="1150" cy="800" rx="700" ry="300" fill="#{lueur}" stroke="none" opacity=".2" filter="url(#f-flou-90)"/>
  <path d="M-100 560 C400 400 800 640 1300 450 S2200 320 2700 500" stroke-width="110" opacity=".12" filter="url(#f-flou-30)"/>
  <path d="M-100 330 C500 200 900 420 1500 250 S2300 180 2700 260" stroke-width="70" opacity=".07" filter="url(#f-flou-30)"/>
</g>

<g id="etoiles">
{etoiles(rnd)}
</g>
<path id="etoile-filante" d="M470 215 L700 120" stroke="url(#g-filante)" stroke-width="2.4" stroke-linecap="round"/>

<g id="lune">
  <circle cx="{lx}" cy="{ly}" r="560" fill="url(#g-halo)"/>
  <circle cx="{lx}" cy="{ly}" r="{lr}" fill="url(#g-lune)"/>
  <g fill="#a8945c">
    <ellipse cx="{lx - 46}" cy="{ly - 38}" rx="34" ry="28" opacity=".2"/>
    <ellipse cx="{lx + 38}" cy="{ly - 70}" rx="20" ry="16" opacity=".16"/>
    <ellipse cx="{lx + 54}" cy="{ly + 30}" rx="42" ry="34" opacity=".18"/>
    <ellipse cx="{lx - 30}" cy="{ly + 66}" rx="24" ry="18" opacity=".2"/>
    <ellipse cx="{lx - 88}" cy="{ly + 14}" rx="15" ry="20" opacity=".14"/>
    <ellipse cx="{lx + 4}" cy="{ly + 2}" rx="12" ry="10" opacity=".14"/>
  </g>
</g>
<g id="nuages" fill="{mel(ciel_bas, 'ffffff', .3)}" filter="url(#f-flou-14)">
  <path d="M1620 412 C1730 376 1850 418 1960 396 S2210 366 2350 408 C2210 440 2060 432 1960 444 S1730 442 1620 412 Z" opacity=".5"/>
  <path d="M1780 250 C1850 232 1930 252 2010 240 S2170 226 2260 250 C2170 268 2080 262 2010 270 S1850 268 1780 250 Z" opacity=".28"/>
  <path d="M300 620 C460 590 640 630 800 606 S1100 580 1240 616 C1100 642 940 634 800 646 S460 648 300 620 Z" opacity=".16"/>
</g>

<g id="chouette" fill="{mel(ciel_haut, noir, .55)}" transform="translate(1700 262) scale(.42)">
  <path d="M0 2 C-30 -30 -74 -34 -112 -8 C-80 -16 -48 -6 -24 16 C-12 26 12 26 24 16 C48 -6 80 -16 112 -8 C74 -34 30 -30 0 2 Z"/>
  <ellipse cx="0" cy="12" rx="13" ry="17"/>
</g>

<g id="montagnes">
  <path d="{crete(rnd, HORIZON + 4, 150, 380, 120, 110)}" fill="{mel(ciel_bas, ciel_haut, .3)}" opacity=".85"/>
  <path d="{crete(rnd, HORIZON + 4, 60, 230, 90, 70)}" fill="{mel(ciel_bas, ciel_haut, .62)}"/>
</g>

<rect id="lac" x="0" y="{HORIZON}" width="{L}" height="{H - HORIZON}" fill="url(#g-lac)"/>
<g id="reflets" mask="url(#m-reflet)" filter="url(#f-flou-3)">
  <use xlink:href="#chateau" href="#chateau" transform="matrix(1 0 0 -1 0 {2 * HORIZON})"/>
</g>
<g id="reflet-lune" fill="#fff0c0">
{chr(10).join(reflet_lune)}
</g>
<g id="rides" fill="none" stroke="{mel(lueur, 'ffffff', .6)}" stroke-width="1.6" stroke-linecap="round">
{chr(10).join(rides)}
</g>

<g id="chateau">
  <g id="chateau-silhouette" fill="url(#g-pierre)">
{silhouette}
  </g>
  <g id="chateau-reflets-de-lune" fill="#fff1c4" opacity=".2">
{chr(10).join(reflet_lune_sur_tour(*t) for t in TOURS)}
  </g>
  <g id="chateau-fanions" fill="#{accent}">
{chr(10).join(fanion(*t) for t in TOURS[1:6])}
  </g>
  <g id="chateau-fenetres" filter="url(#f-lueur)">
{fenetres(rnd)}
  </g>
</g>

<g id="brume" fill="{brume}" filter="url(#f-flou-14)">
  <ellipse cx="620" cy="1124" rx="760" ry="20" opacity=".16"/>
  <ellipse cx="1500" cy="1130" rx="900" ry="26" opacity=".14"/>
  <ellipse cx="2260" cy="1122" rx="520" ry="18" opacity=".15"/>
  <ellipse cx="1180" cy="1090" rx="560" ry="16" opacity=".08"/>
</g>

<g id="premier-plan" fill="{premier_plan}">
  <path d="M0 1320 C220 1290 430 1350 620 1400 C700 1420 760 1440 760 1440 L0 1440 Z"/>
  <path d="M2560 1310 C2360 1296 2160 1360 2010 1410 C1960 1426 1930 1440 1930 1440 L2560 1440 Z"/>
  <g id="sapins-gauche">
{chr(10).join(sapins_g)}
  </g>
  <g id="sapins-droite">
{chr(10).join(sapins_d)}
  </g>
</g>

<rect id="vignette" width="{L}" height="{H}" fill="url(#g-vignette)"/>
</svg>
'''


def main():
    sortie = RACINE / 'assets' / 'fonds'
    sortie.mkdir(parents=True, exist_ok=True)
    for ligne in (RACINE / 'themes' / 'maisons.conf').read_text(encoding='utf-8').splitlines():
        if not ligne.strip() or ligne.startswith('#'):
            continue
        c = ligne.split('|')
        if c[11] == '-':    # thème sans fond d'écran (parchemin)
            continue
        svg = dessiner(nom=c[0], libelle=c[1], accent=c[2], ciel_haut=c[11], ciel_bas=c[12], lueur=c[13])
        (sortie / f'{c[0]}.svg').write_text(svg, encoding='utf-8', newline='\n')
        print(f'{c[0]}.svg  {len(svg) // 1024} Ko')


if __name__ == '__main__':
    main()
