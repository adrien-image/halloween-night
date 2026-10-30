"""Bibliothèque de dessin SVG commune à toutes les illustrations.

Style unique : cartoon « cell-shaded » — contours épais violet-noir, aplats de
couleur, une seule ombre dure par forme (lumière venant d'en haut à gauche),
palette nocturne violet / orange citrouille.

Chaque personnage est toujours dessiné par la même fonction, avec les mêmes
couleurs et proportions, ce qui garantit leur cohérence d'une image à l'autre.
"""
import itertools
import math

W, H = 960, 600
OUT = "#1b1226"     # couleur des contours
SW = 4              # épaisseur des contours
FLOOR = 540         # ligne du sol par défaut

_ids = itertools.count()


def uid(prefix="c"):
    return f"{prefix}{next(_ids)}"


# ---------------------------------------------------------------- formes
def E(cx, cy, rx, ry=None):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry if ry is not None else rx}"/>'


def R(x, y, w, h, r=0):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"/>'


def P(d):
    return f'<path d="{d}"/>'


def POLY(*pts):
    return '<polygon points="' + " ".join(f"{x},{y}" for x, y in pts) + '"/>'


# ---------------------------------------------------------------- remplissages
def flat(shape, fill, sw=SW, stroke=OUT, extra=""):
    """Aplat avec contour."""
    st = f'stroke="{stroke}" stroke-width="{sw}"' if sw else 'stroke="none"'
    return (f'<g fill="{fill}" {st} stroke-linejoin="round" '
            f'stroke-linecap="round" {extra}>{shape}</g>')


def fill(shape, color, extra=""):
    """Aplat sans contour."""
    st = "" if "stroke=" in extra else 'stroke="none"'
    return f'<g fill="{color}" {st} {extra}>{shape}</g>'


def cel(shape, base, shade, dx=7, dy=6, sw=SW):
    """Aplat + ombre dure en bas à droite (cell-shading) + contour."""
    cid = uid()
    return (
        f'<clipPath id="{cid}">{shape}</clipPath>'
        f'<g clip-path="url(#{cid})" stroke="none">'
        f'<g fill="{shade}">{shape}</g>'
        f'<g fill="{base}" transform="translate({-dx},{-dy})">{shape}</g></g>'
        + (f'<g fill="none" stroke="{OUT}" stroke-width="{sw}" '
           f'stroke-linejoin="round">{shape}</g>' if sw else "")
    )


def tube(d, color, w=16, sw=SW):
    """Membre (bras, jambe) : trait épais avec contour."""
    return (f'<path d="{d}" fill="none" stroke="{OUT}" stroke-width="{w + 2 * sw}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def line(d, w=SW, color=OUT, extra=""):
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" '
            f'stroke-linecap="round" stroke-linejoin="round" {extra}/>')


def g(content, x=0, y=0, s=1, flip=False, opacity=None, rot=0):
    t = f"translate({x},{y})"
    if rot:
        t += f" rotate({rot})"
    t += f" scale({-s if flip else s},{s})"
    op = f' opacity="{opacity}"' if opacity is not None else ""
    return f'<g transform="{t}"{op}>{content}</g>'


def text(x, y, txt, size=40, color="#fff", weight=800, anchor="middle", extra=""):
    return (f'<text x="{x}" y="{y}" font-family="Open Sans, Arial, sans-serif" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}" '
            f'text-anchor="{anchor}" stroke="{OUT}" stroke-width="{max(2, size // 9)}" '
            f'paint-order="stroke" {extra}>{txt}</text>')


# ---------------------------------------------------------------- impression risographie
# Encres : du plus sombre au plus clair (luminance -> encre), papier crème en dernier.
INKS = ["#1f1433", "#3d2466", "#8a3f7a", "#ff6b2c", "#ffb07a", "#f6ecd8"]
PAPER_COLOR = INKS[-1]


def _table(channel):
    return " ".join(f"{int(c[1 + 2 * channel:3 + 2 * channel], 16) / 255:.3f}" for c in INKS)


PRINT_DEFS = (
    '<defs>'
    # 1. luminance, ombres relevées (les fonds tombent sur l'encre prune, les contours restent noirs),
    #    puis réduction à 6 encres
    '<filter id="riso" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
    '<feColorMatrix type="matrix" values="0.3 0.59 0.11 0 0  0.3 0.59 0.11 0 0  0.3 0.59 0.11 0 0  0 0 0 1 0" result="lum"/>'
    '<feComponentTransfer in="lum" result="contrast">'
    '<feFuncR type="gamma" amplitude="1.05" exponent="0.62" offset="-0.02"/>'
    '<feFuncG type="gamma" amplitude="1.05" exponent="0.62" offset="-0.02"/>'
    '<feFuncB type="gamma" amplitude="1.05" exponent="0.62" offset="-0.02"/></feComponentTransfer>'
    '<feComponentTransfer in="contrast" result="ink">'
    f'<feFuncR type="discrete" tableValues="{_table(0)}"/><feFuncG type="discrete" tableValues="{_table(1)}"/>'
    f'<feFuncB type="discrete" tableValues="{_table(2)}"/></feComponentTransfer>'
    # 2. second passage légèrement décalé (défaut de repérage)
    '<feOffset in="ink" dx="3" dy="2" result="shift"/>'
    '<feComposite in="shift" operator="arithmetic" k2="0.35" k4="0.65" result="ghost"/>'
    '<feBlend in="ink" in2="ghost" mode="multiply" result="printed"/>'
    # 3. grain du papier et encre irrégulière
    '<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7" result="noise"/>'
    '<feColorMatrix in="noise" type="saturate" values="0" result="grey"/>'
    '<feComposite in="printed" in2="grey" operator="arithmetic" k2="1" k3="0.16" k4="-0.08"/>'
    '</filter>'
    # trame de demi-teinte
    '<pattern id="halftone" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(22)">'
    f'<circle cx="3" cy="3" r="1.3" fill="{INKS[1]}"/></pattern>'
    # fibres du papier
    '<filter id="fibres"><feTurbulence type="fractalNoise" baseFrequency="0.35" numOctaves="3" seed="3"/>'
    '<feColorMatrix values="0 0 0 0 0.24  0 0 0 0 0.14  0 0 0 0 0.4  0 0 0 -1.8 1"/></filter>'
    '</defs>'
)


def print_finish(content):
    """Imprime la scène en risographie : encres limitées, décalage, trame et papier."""
    return (PRINT_DEFS
            + f'<g filter="url(#riso)">{content}</g>'
            + f'<rect width="{W}" height="{H}" fill="url(#halftone)" opacity="0.18" style="mix-blend-mode:multiply"/>'
            + f'<rect width="{W}" height="{H}" filter="url(#fibres)" opacity="0.18"/>'
            # marge blanche irrégulière, comme une feuille imprimée
            + f'<rect x="4" y="4" width="{W - 8}" height="{H - 8}" fill="none" stroke="{PAPER_COLOR}" stroke-width="10" rx="6"/>')


def svg(content):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'width="{W}" height="{H}">{content}</svg>\n')


# ---------------------------------------------------------------- palette
SKIN_HERO = ("#e3ead6", "#aebfa6")      # teint blafard du vampire
SKIN_OLD = ("#f1d2b6", "#cfa58a")       # Mme Morticia (Yvonne)
SKIN_HENRI = ("#eec7a6", "#c99a7a")
GHOST = ("#cfe6ef", "#9cc0cf")
WHITE = ("#f6f2fa", "#c9c2d6")
CAPE = ("#231d33", "#120e1c")
JACKET = ("#2e2742", "#1a1528")
RED = ("#c22a40", "#7f1528")
PLUM = ("#4b2d63", "#2e1a40")
CARDIGAN = ("#a07a42", "#6e5228")
TROUSERS = ("#4d4a5c", "#33303f")
CAT = ("#2c2938", "#15131e")
GOLD = ("#f4c54d", "#c48f1d")
WOOD = ("#7a4a2c", "#53301b")
WOOD_DARK = ("#5a3420", "#3b2012")
ORANGE = ("#f28c28", "#c4601a")
GREEN = ("#6aa84f", "#457a32")
PAPER = ("#f5ecd6", "#d6c7a2")
GLASS = "#bfe6f5"


# ---------------------------------------------------------------- visages communs
def eye(x, y, rx=9, ry=10, px=0, py=1, pr=4, white="#fff"):
    return flat(E(x, y, rx, ry), white, sw=3) + fill(E(x + px, y + py, pr, pr), OUT)


def arc_eye(x, y, w=8, up=True):
    k = -8 if up else 8
    return line(f"M{x - w},{y} Q{x},{y + k} {x + w},{y}", 4)


def fangs(x, y, size=8):
    return (flat(POLY((x - 9, y), (x - 4, y), (x - 6.5, y + size)), "#fff", sw=2)
            + flat(POLY((x + 4, y), (x + 9, y), (x + 6.5, y + size)), "#fff", sw=2))


def sweat(x, y, s=1):
    return g(flat(P("M0,-14 Q10,0 0,6 Q-10,0 0,-14 Z"), "#9fdcf5", sw=3), x, y, s)


def cheeks(xs, y, color="#f29a9a"):
    return "".join(fill(E(x, y, 8, 5), color, 'opacity="0.7"') for x in xs)


# ---------------------------------------------------------------- héros (vampire)
def hero(x, y, s=1, flip=False, expr="neutral", pose="stand", legs="stand",
         item=None, bite=False, opacity=None):
    o = []
    dy = 40 if legs == "sit" else 0
    sk, sk_sh = SKIN_HERO

    # cape (derrière)
    if pose == "cape":
        cape = P("M-36,-180 L-120,-150 L-110,-12 Q0,-30 110,-12 L120,-150 L36,-180 Z")
    elif legs == "run":
        cape = P("M-30,-182 Q-120,-170 -170,-90 Q-120,-80 -90,-40 Q-40,-90 30,-120 Z")
    else:
        bottom = -12 - dy
        cape = P(f"M-36,-180 L-84,{bottom} Q0,{bottom - 12} 84,{bottom} L36,-180 Z")

    # jambes
    if legs == "stand":
        o.append(tube("M-14,-92 L-16,-10", TROUSERS[1], 18))
        o.append(tube("M14,-92 L16,-10", TROUSERS[1], 18))
        o.append(flat(E(-22, -7, 17, 8), "#111", 3) + flat(E(22, -7, 17, 8), "#111", 3))
    elif legs == "run":
        o.append(tube("M-14,-92 L-40,-52 L-64,-14", TROUSERS[1], 18))
        o.append(tube("M14,-92 L44,-58 L70,-70", TROUSERS[1], 18))
        o.append(flat(E(-70, -10, 17, 8), "#111", 3) + flat(E(78, -70, 14, 8), "#111", 3))
    elif legs == "sit":
        o.append(tube("M-16,-52 L-18,-10", TROUSERS[1], 18))
        o.append(tube("M16,-52 L18,-10", TROUSERS[1], 18))
        o.append(flat(E(-24, -7, 17, 8), "#111", 3) + flat(E(24, -7, 17, 8), "#111", 3))

    up = []
    up.append(cel(cape, *CAPE))
    # col rouge de la cape
    up.append(cel(P("M-30,-186 L-74,-272 L-18,-208 Z"), *RED, dx=3, dy=3))
    up.append(cel(P("M30,-186 L74,-272 L18,-208 Z"), *RED, dx=3, dy=3))
    # buste
    up.append(cel(P("M-36,-182 Q0,-190 36,-182 L32,-88 Q0,-80 -32,-88 Z"), *JACKET))
    up.append(flat(POLY((-13, -184), (13, -184), (0, -140)), "#f4f0f7", 3))
    up.append(flat(POLY((0, -176), (-12, -184), (-12, -168)) + POLY((0, -176), (12, -184), (12, -168)), RED[0], 3))
    up.append(flat(R(-9, -198, 18, 18), sk, 3))
    if bite:
        up.append(fill(E(-5, -189, 2.6) + E(5, -189, 2.6), "#5a0d18"))
    # oreilles pointues + tête
    up.append(cel(P("M-36,-240 L-58,-262 L-38,-218 Z"), sk, sk_sh, 3, 3))
    up.append(cel(P("M36,-240 L58,-262 L38,-218 Z"), sk, sk_sh, 3, 3))
    up.append(cel(E(0, -234, 40, 46), sk, sk_sh))
    # cheveux plaqués en pointe
    up.append(cel(P("M-42,-236 C-52,-294 52,-294 42,-236 L30,-258 L14,-252 L0,-238 L-14,-252 L-30,-258 Z"),
                  "#1f1a33", "#0d0a16", 5, 4))
    up.append(hero_face(expr))

    # bras
    A = HERO_ARMS.get(pose, HERO_ARMS["stand"])
    for d in A["arms"]:
        up.append(tube(d, JACKET[0], 15))
    for hx, hy in A["hands"]:
        up.append(cel(E(hx, hy, 9, 9), sk, sk_sh, 2, 2, 3))
    if item:
        ix, iy = A["item"]
        up.append(g(prop(item), ix, iy))

    o.append(g("".join(up), 0, dy))
    return g("".join(o), x, y, s, flip, opacity)


HERO_ARMS = {
    "stand": {"arms": ["M-34,-172 Q-50,-130 -46,-98", "M34,-172 Q50,-130 46,-98"],
              "hands": [(-46, -95), (46, -95)], "item": (46, -95)},
    "hold": {"arms": ["M-34,-172 Q-50,-130 -46,-98", "M34,-172 Q54,-130 30,-128"],
             "hands": [(-46, -95), (30, -128)], "item": (34, -132)},
    "hold2": {"arms": ["M-34,-172 Q-50,-130 -16,-124", "M34,-172 Q50,-130 16,-124"],
              "hands": [(-16, -124), (16, -124)], "item": (0, -128)},
    "scared": {"arms": ["M-34,-172 Q-74,-190 -52,-246", "M34,-172 Q74,-190 52,-246"],
               "hands": [(-52, -248), (52, -248)], "item": (52, -248)},
    "phone": {"arms": ["M-34,-172 Q-50,-130 -46,-98", "M34,-172 Q66,-206 40,-232"],
              "hands": [(-46, -95), (40, -234)], "item": (44, -240)},
    "cape": {"arms": ["M-34,-172 L-96,-150", "M34,-172 L96,-150"],
             "hands": [(-98, -150), (98, -150)], "item": (98, -150)},
    "reach": {"arms": ["M-34,-172 Q-50,-130 -46,-98", "M34,-172 L104,-158"],
              "hands": [(-46, -95), (106, -158)], "item": (110, -162)},
    "knock": {"arms": ["M-34,-172 Q-50,-130 -46,-98", "M34,-172 Q72,-198 96,-206"],
              "hands": [(-46, -95), (98, -206)], "item": (98, -206)},
    "run": {"arms": ["M-34,-172 L-62,-130 L-52,-108", "M34,-172 L64,-196 L86,-178"],
            "hands": [(-52, -106), (88, -176)], "item": (88, -176)},
    "think": {"arms": ["M-34,-172 Q-50,-130 -46,-98", "M34,-172 Q52,-150 18,-196"],
              "hands": [(-46, -95), (16, -196)], "item": (16, -196)},
    "offer": {"arms": ["M-34,-172 Q-50,-130 -46,-98", "M34,-172 Q70,-150 96,-140"],
              "hands": [(-46, -95), (98, -140)], "item": (100, -146)},
    "pocket": {"arms": ["M-34,-172 Q-50,-130 -46,-98", "M34,-172 Q46,-130 26,-100"],
               "hands": [(-46, -95), (26, -98)], "item": (26, -98)},
}


def hero_face(expr):
    o = []
    ey, my = -236, -208
    if expr in ("neutral", "talk"):
        o += [eye(-15, ey), eye(15, ey), line("M-24,-254 L-8,-252"), line("M8,-252 L24,-254")]
        if expr == "talk":
            o.append(flat(P(f"M-12,{my - 2} Q0,{my + 12} 12,{my - 2} Z"), "#5a0d18", 3))
        else:
            o.append(line(f"M-12,{my} Q0,{my + 7} 12,{my}"))
        o.append(fangs(0, my + 1, 7))
    elif expr == "happy":
        o += [arc_eye(-15, ey), arc_eye(15, ey)]
        o.append(flat(P(f"M-17,{my - 4} Q0,{my + 16} 17,{my - 4} Z"), "#5a0d18", 3))
        o.append(fangs(0, my - 3, 8))
        o.append(cheeks((-26, 26), -220, "#c8d9b8"))
    elif expr in ("scared", "surprised"):
        pr = 2.6 if expr == "scared" else 4
        o += [eye(-15, ey, 11, 13, 0, 0, pr), eye(15, ey, 11, 13, 0, 0, pr)]
        o += [line("M-26,-258 L-8,-262"), line("M8,-262 L26,-258")]
        o.append(flat(E(0, my + 2, 7, 9), "#5a0d18", 3))
        o.append(fangs(0, my - 6, 6))
        if expr == "scared":
            o.append(sweat(46, -262) + sweat(-48, -250, 0.8))
    elif expr == "worried":
        o += [eye(-15, ey, 9, 10, 0, 2), eye(15, ey, 9, 10, 0, 2)]
        o += [line("M-24,-250 L-8,-258"), line("M8,-258 L24,-250")]
        o.append(line(f"M-12,{my} q4,-4 8,0 q4,4 8,0 q2,-2 4,-2"))
        o.append(fangs(-2, my + 1, 6))
        o.append(sweat(46, -258))
    elif expr == "determined":
        o += [eye(-15, ey, 9, 9), eye(15, ey, 9, 9)]
        o += [line("M-26,-258 L-6,-248", 5), line("M6,-248 L26,-258", 5)]
        o.append(line(f"M-12,{my + 2} Q4,{my + 6} 14,{my - 4}"))
        o.append(fangs(0, my + 3, 7))
    elif expr == "sleepy":
        o += [line(f"M-24,{ey} Q-15,{ey + 5} -6,{ey}"), line(f"M6,{ey} Q15,{ey + 5} 24,{ey}")]
        o += [line(f"M-24,{ey - 4} L-6,{ey - 4}", 3), line(f"M6,{ey - 4} L24,{ey - 4}", 3)]
        o.append(flat(E(0, my + 2, 5, 6), "#5a0d18", 3))
    elif expr == "dizzy":
        for ex in (-15, 15):
            o.append(line(f"M{ex},{ey} m-2,0 a2,2 0 1,1 4,0 a5,5 0 1,1 -9,0 a8,8 0 1,1 15,1", 2.5))
        o.append(line(f"M-12,{my} q4,-4 8,0 q4,4 8,0 q2,-2 4,-2"))
    elif expr == "moved":
        o += [eye(-15, ey, 9, 10, 0, -1, 5), eye(15, ey, 9, 10, 0, -1, 5)]
        o.append(fill(E(-13, ey - 4, 2) + E(17, ey - 4, 2), "#fff"))
        o.append(flat(P("M-22,-226 Q-26,-214 -22,-208 Q-18,-214 -22,-226 Z"), "#9fdcf5", 2))
        o.append(line(f"M-12,{my} Q0,{my + 8} 12,{my}"))
        o.append(fangs(0, my + 1, 6))
    elif expr == "blank":
        o += [fill(E(-15, ey, 4), OUT), fill(E(15, ey, 4), OUT)]
        o.append(line(f"M-10,{my + 2} L10,{my + 2}"))
    return "".join(o)


# ---------------------------------------------------------------- Mme Morticia (Yvonne)
def morticia(x, y, s=1, flip=False, expr="smile", pose="fold", item=None,
             key=True, ghost=False, opacity=None):
    sk = GHOST if ghost else SKIN_OLD
    dress = ("#8fa9c4", "#6c87a3") if ghost else PLUM
    o = []
    o.append(cel(P("M-30,-178 Q0,-186 30,-178 L60,-4 Q0,6 -60,-4 Z"), *dress))
    o.append(flat(P("M-22,-180 Q0,-160 22,-180 L16,-168 Q0,-152 -16,-168 Z"), "#e6dcef", 3))
    o.append(flat(R(-8, -192, 16, 16), sk[0], 3))
    # cheveux (chignon) + tête
    o.append(cel(E(0, -258, 18, 16), *WHITE, 4, 4))
    o.append(cel(E(0, -214, 34, 38), *sk))
    o.append(cel(P("M-37,-208 C-42,-262 42,-262 37,-208 C32,-238 10,-244 0,-236 C-10,-244 -32,-238 -37,-208 Z"),
                 *WHITE, 4, 4))
    o.append(morticia_face(expr))
    # collier de perles
    for i in range(9):
        t = i / 8
        px = -22 + 44 * t
        py = -178 + 22 * (1 - (2 * t - 1) ** 2)
        o.append(flat(E(round(px, 1), round(py, 1), 3.6), "#fbf8ff", 1.5))
    if key:
        o.append(g(prop("key"), 0, -146, 0.55, rot=90))
    A = MORTICIA_ARMS.get(pose, MORTICIA_ARMS["fold"])
    for d in A["arms"]:
        o.append(tube(d, dress[0], 14))
    for hx, hy in A["hands"]:
        o.append(cel(E(hx, hy, 8, 8), *sk, 2, 2, 3))
    if item:
        ix, iy = A["item"]
        o.append(g(prop(item), ix, iy))
    op = opacity if opacity is not None else (0.5 if ghost else None)
    return g("".join(o), x, y, s, flip, op)


MORTICIA_ARMS = {
    "fold": {"arms": ["M-30,-172 Q-46,-130 -10,-114", "M30,-172 Q46,-130 10,-114"],
             "hands": [(-8, -114), (8, -114)], "item": (0, -118)},
    "hold2": {"arms": ["M-30,-172 Q-46,-130 -18,-124", "M30,-172 Q46,-130 18,-124"],
              "hands": [(-18, -124), (18, -124)], "item": (0, -128)},
    "hold": {"arms": ["M-30,-172 Q-46,-130 -10,-114", "M30,-172 Q48,-130 28,-126"],
             "hands": [(-10, -114), (28, -126)], "item": (32, -130)},
    "point_up": {"arms": ["M-30,-172 Q-46,-130 -10,-114", "M30,-172 L58,-212 L62,-252"],
                 "hands": [(-10, -114), (62, -254)], "item": (62, -254)},
    "point": {"arms": ["M-30,-172 Q-46,-130 -10,-114", "M30,-172 L84,-196"],
              "hands": [(-10, -114), (86, -197)], "item": (86, -197)},
    "key": {"arms": ["M-30,-172 Q-46,-130 -40,-100", "M30,-172 Q40,-136 10,-146"],
            "hands": [(-40, -98), (8, -146)], "item": (8, -146)},
    "cross": {"arms": ["M-30,-172 Q-52,-132 16,-140", "M30,-172 Q52,-128 -16,-134"],
              "hands": [(18, -140), (-18, -134)], "item": (0, -140)},
    "caress": {"arms": ["M-30,-172 Q-46,-130 -40,-100", "M30,-172 Q70,-176 96,-190"],
               "hands": [(-40, -98), (98, -191)], "item": (98, -191)},
    "stand": {"arms": ["M-30,-172 Q-46,-130 -40,-100", "M30,-172 Q46,-130 40,-100"],
              "hands": [(-40, -98), (40, -98)], "item": (40, -98)},
}


def morticia_face(expr):
    o = []
    ey, my = -214, -194
    if expr in ("smile", "tender"):
        o += [arc_eye(-13, ey, 7), arc_eye(13, ey, 7)]
        o.append(flat(P(f"M-12,{my - 2} Q0,{my + 10} 12,{my - 2} Z"), "#7a2a3a", 3) if expr == "smile"
                 else line(f"M-10,{my} Q0,{my + 7} 10,{my}"))
        o.append(cheeks((-22, 22), -202))
    elif expr == "wink":
        o += [arc_eye(-13, ey, 7), eye(13, ey, 7, 8, 0, 0, 3.5)]
        o.append(flat(P(f"M-12,{my - 2} Q0,{my + 10} 12,{my - 2} Z"), "#7a2a3a", 3))
        o.append(cheeks((-22, 22), -202))
    elif expr == "sly":
        o += [eye(-13, ey, 7, 7, 2, 1, 3.2), eye(13, ey, 7, 7, 2, 1, 3.2)]
        o += [line(f"M-21,{ey - 4} L-5,{ey - 3}", 5), line(f"M5,{ey - 3} L21,{ey - 4}", 5)]
        o.append(line(f"M-10,{my} Q4,{my + 6} 14,{my - 5}"))
    elif expr in ("stern", "annoyed"):
        o += [eye(-13, ey, 7, 7, 0, 0, 3.2), eye(13, ey, 7, 7, 0, 0, 3.2)]
        o += [line(f"M-22,{ey - 14} L-6,{ey - 9}", 4), line(f"M6,{ey - 9} L22,{ey - 14}", 4)]
        o.append(line(f"M-9,{my + 2} Q0,{my - 4} 9,{my + 2}") if expr == "annoyed"
                 else line(f"M-9,{my} L9,{my}"))
    elif expr == "surprised":
        o += [eye(-13, ey, 8, 9, 0, 0, 3), eye(13, ey, 8, 9, 0, 0, 3)]
        o.append(flat(E(0, my, 5, 6), "#7a2a3a", 3))
    # rides
    o.append(line(f"M-26,{ey + 6} l-4,3", 2) + line(f"M26,{ey + 6} l4,3", 2))
    return "".join(o)


# ---------------------------------------------------------------- Henri
def henri(x, y, s=1, flip=False, expr="smile", pose="stand", legs="stand", item=None,
          ghost=False, float_=False, fangs_=False, young=False, opacity=None):
    sk = GHOST if ghost else SKIN_HENRI
    if expr == "swollen":
        sk = ("#ee8f80", "#c4615a")
    cardi = ("#9fb6c4", "#7a93a3") if ghost else CARDIGAN
    trou = ("#8aa0b0", "#6d8291") if ghost else TROUSERS
    o = []
    dy = 40 if legs == "sit" else 0
    if float_:
        o.append(fill(E(0, -2, 46, 8), "#9fdcf5", 'opacity="0.35"'))
    if legs == "stand":
        o.append(tube("M-15,-94 L-17,-10", trou[0], 19))
        o.append(tube("M15,-94 L17,-10", trou[0], 19))
        o.append(flat(E(-22, -7, 18, 8), "#5a2e2e", 3) + flat(E(22, -7, 18, 8), "#5a2e2e", 3))
    elif legs == "sit":
        o.append(tube("M-16,-52 L-18,-10", trou[0], 19))
        o.append(tube("M16,-52 L18,-10", trou[0], 19))
        o.append(flat(E(-24, -7, 18, 8), "#5a2e2e", 3) + flat(E(24, -7, 18, 8), "#5a2e2e", 3))
    up = []
    up.append(cel(P("M-40,-184 Q0,-194 40,-184 L37,-90 Q0,-82 -37,-90 Z"), *cardi))
    up.append(flat(POLY((-13, -188), (13, -188), (0, -146)), "#f4f0f7", 3))
    up.append(flat(POLY((-4, -180), (4, -180), (6, -152), (0, -146), (-6, -152)), "#3f6b4f", 2))
    for by in (-132, -112):
        up.append(flat(E(0, by, 3.5), "#5a3a1a", 2))
    up.append(flat(R(-10, -200, 20, 18), sk[0], 3))
    hr = 1.12 if expr == "swollen" else 1
    head = []
    head.append(cel(E(-38, -232, 8, 12), *sk, 2, 2, 3) + cel(E(38, -232, 8, 12), *sk, 2, 2, 3))
    head.append(cel(E(0, -236, 38, 44), *sk))
    hair = ("#5a4a3a", "#3a2e22") if young else WHITE
    if young:
        head.append(cel(P("M-38,-240 C-44,-290 44,-290 38,-240 C30,-262 -30,-262 -38,-240 Z"), *hair, 4, 4))
    else:
        head.append(cel(E(-36, -250, 9, 15), *hair, 3, 3) + cel(E(36, -250, 9, 15), *hair, 3, 3))
        head.append(fill(E(-12, -266, 9, 5), "#fff", 'opacity="0.6"'))
    head.append(henri_face(expr, fangs_, young))
    # tête agrandie (visage gonflé) autour de son centre
    up.append(g("".join(head), 0, round((1 - hr) * -236, 1), hr))
    A = HENRI_ARMS.get(pose, HENRI_ARMS["stand"])
    for d in A["arms"]:
        up.append(tube(d, cardi[0], 16))
    for hx, hy in A["hands"]:
        up.append(cel(E(hx, hy, 9, 9), *sk, 2, 2, 3))
    if item:
        ix, iy = A["item"]
        up.append(g(prop(item), ix, iy))
    o.append(g("".join(up), 0, dy))
    op = opacity if opacity is not None else (0.55 if ghost else None)
    return g("".join(o), x, y - (18 if float_ else 0), s, flip, op)


HENRI_ARMS = {
    "stand": {"arms": ["M-38,-174 Q-54,-130 -48,-98", "M38,-174 Q54,-130 48,-98"],
              "hands": [(-48, -95), (48, -95)], "item": (48, -95)},
    "hold": {"arms": ["M-38,-174 Q-54,-130 -48,-98", "M38,-174 Q58,-132 30,-130"],
             "hands": [(-48, -95), (30, -130)], "item": (34, -136)},
    "hold2": {"arms": ["M-38,-174 Q-54,-130 -18,-126", "M38,-174 Q54,-130 18,-126"],
              "hands": [(-18, -126), (18, -126)], "item": (0, -132)},
    "menace": {"arms": ["M-38,-174 L-20,-176 L30,-196", "M38,-174 L80,-180 L104,-196"],
               "hands": [(32, -197), (106, -197)], "item": (106, -197)},
    "point": {"arms": ["M-38,-174 Q-54,-130 -48,-98", "M38,-174 L96,-186"],
              "hands": [(-48, -95), (98, -187)], "item": (100, -187)},
    "eat": {"arms": ["M-38,-174 Q-54,-130 -18,-126", "M38,-174 Q56,-150 18,-200"],
            "hands": [(-18, -126), (16, -200)], "item": (16, -200)},
    "offer": {"arms": ["M-38,-174 Q-54,-130 -48,-98", "M38,-174 Q72,-150 98,-146"],
              "hands": [(-48, -95), (100, -146)], "item": (104, -152)},
    "chin": {"arms": ["M-38,-174 Q-54,-130 -48,-98", "M38,-174 Q56,-150 20,-192"],
             "hands": [(-48, -95), (18, -192)], "item": (18, -192)},
    "shrug": {"arms": ["M-38,-174 L-70,-150 L-80,-180", "M38,-174 L70,-150 L80,-180"],
              "hands": [(-80, -182), (80, -182)], "item": (80, -182)},
    "wave_off": {"arms": ["M-38,-174 Q-54,-130 -48,-98", "M38,-174 L84,-170 L100,-206"],
                 "hands": [(-48, -95), (100, -208)], "item": (100, -208)},
}


def henri_face(expr, fangs_=False, young=False):
    o = []
    ey, my = -240, -200
    brow = "#e8e4ee" if not young else "#4a3a2a"
    mus = WHITE if not young else ("#5a4a3a", "#3a2e22")
    if expr in ("smile", "talk", "blissful"):
        o += [arc_eye(-15, ey, 7), arc_eye(15, ey, 7)]
        o.append(flat(P(f"M-26,{ey - 14} Q-15,{ey - 22} -5,{ey - 14}") + P(f"M5,{ey - 14} Q15,{ey - 22} 26,{ey - 14}"), brow, 3))
        if expr == "blissful":
            o.append(cheeks((-26, 26), -222))
    elif expr in ("sad",):
        o += [eye(-15, ey, 7, 8, 0, 3, 3.4), eye(15, ey, 7, 8, 0, 3, 3.4)]
        o.append(flat(P(f"M-26,{ey - 10} L-5,{ey - 20} L-6,{ey - 14} Z") + P(f"M26,{ey - 10} L5,{ey - 20} L6,{ey - 14} Z"), brow, 3))
    elif expr in ("angry", "furious", "stern"):
        red = expr == "furious"
        o += [eye(-15, ey, 8, 7, 0, 0, 3.6, "#ffd2d2" if red else "#fff"),
              eye(15, ey, 8, 7, 0, 0, 3.6, "#ffd2d2" if red else "#fff")]
        if red:
            o.append(fill(E(-15, ey, 3.6) + E(15, ey, 3.6), "#e0142c"))
        if expr == "stern":
            o.append(flat(R(-27, ey - 17, 22, 6, 3) + R(5, ey - 17, 22, 6, 3), brow, 3))
        else:
            o.append(flat(P(f"M-28,{ey - 20} L-4,{ey - 8} L-6,{ey - 14} Z") + P(f"M28,{ey - 20} L4,{ey - 8} L6,{ey - 14} Z"), brow, 3))
    elif expr == "hungry":
        o += [eye(-15, ey, 8, 6, 2, 0, 3.4, "#fff6c2"), eye(15, ey, 8, 6, 2, 0, 3.4, "#fff6c2")]
        o.append(flat(P(f"M-28,{ey - 16} L-4,{ey - 8} L-6,{ey - 14} Z") + P(f"M28,{ey - 16} L4,{ey - 8} L6,{ey - 14} Z"), brow, 3))
    elif expr == "disgust":
        o += [line(f"M-22,{ey - 5} L-9,{ey} L-22,{ey + 5}"), line(f"M22,{ey - 5} L9,{ey} L22,{ey + 5}")]
        o.append(flat(P(f"M-26,{ey - 12} L-5,{ey - 16} L-6,{ey - 10} Z") + P(f"M26,{ey - 12} L5,{ey - 16} L6,{ey - 10} Z"), brow, 3))
    elif expr in ("swollen", "cough"):
        o += [line(f"M-22,{ey} L-8,{ey}", 4), line(f"M8,{ey} L22,{ey}", 4)]
        o.append(flat(P(f"M-26,{ey - 12} L-5,{ey - 16} L-6,{ey - 10} Z") + P(f"M26,{ey - 12} L5,{ey - 16} L6,{ey - 10} Z"), brow, 3))
    elif expr == "excited":
        for ex in (-15, 15):
            o.append(flat(E(ex, ey, 9, 10), "#fff", 3))
            o.append(fill(P(f"M{ex},{ey - 7} L{ex + 2},{ey - 2} L{ex + 7},{ey} L{ex + 2},{ey + 2} L{ex},{ey + 7} "
                            f"L{ex - 2},{ey + 2} L{ex - 7},{ey} L{ex - 2},{ey - 2} Z"), "#f2a800"))
        o.append(flat(P(f"M-26,{ey - 16} Q-15,{ey - 26} -5,{ey - 18}") + P(f"M5,{ey - 18} Q15,{ey - 26} 26,{ey - 16}"), brow, 3))
    elif expr == "surprised":
        o += [eye(-15, ey, 9, 10, 0, 0, 3), eye(15, ey, 9, 10, 0, 0, 3)]
        o.append(flat(P(f"M-26,{ey - 18} Q-15,{ey - 28} -5,{ey - 18}") + P(f"M5,{ey - 18} Q15,{ey - 28} 26,{ey - 18}"), brow, 3))
    else:  # neutral
        o += [eye(-15, ey, 7, 8, 0, 1, 3.4), eye(15, ey, 7, 8, 0, 1, 3.4)]
        o.append(flat(R(-27, ey - 18, 22, 6, 3) + R(5, ey - 18, 22, 6, 3), brow, 3))
    # nez
    o.append(cel(E(0, -224, 8, 10), "#e6a98a" if expr != "swollen" else "#d9665e", "#b97c62", 2, 2, 3))
    # bouche
    if expr in ("smile", "talk"):
        o.append(flat(P(f"M-14,{my} Q0,{my + 14} 14,{my} Z"), "#6b1f2a", 3))
    elif expr == "blissful":
        o.append(line(f"M-12,{my + 2} Q0,{my + 10} 12,{my + 2}"))
    elif expr in ("hungry",):
        o.append(flat(P(f"M-20,{my - 2} Q0,{my + 20} 20,{my - 2} Z"), "#6b1f2a", 3))
    elif expr in ("angry", "furious"):
        o.append(flat(R(-14, my - 2, 28, 12, 4), "#fff", 3))
        o.append(line(f"M-14,{my + 4} L14,{my + 4}", 2))
    elif expr == "disgust":
        o.append(flat(P(f"M-14,{my + 4} q7,-8 14,0 q7,8 14,0 L14,{my + 10} Q0,{my + 16} -14,{my + 10} Z"), "#6b1f2a", 3))
        o.append(flat(E(4, my + 14, 6, 7), "#e07a8a", 2))
    elif expr == "swollen":
        o.append(flat(E(0, my + 4, 16, 9), "#b8404a", 3))
    elif expr == "cough":
        o.append(flat(E(0, my + 4, 10, 12), "#6b1f2a", 3))
    elif expr == "excited":
        o.append(flat(P(f"M-16,{my} Q0,{my + 18} 16,{my} Z"), "#6b1f2a", 3))
    elif expr == "surprised":
        o.append(flat(E(0, my + 4, 6, 8), "#6b1f2a", 3))
    elif expr == "sad":
        o.append(line(f"M-10,{my + 6} Q0,{my - 1} 10,{my + 6}"))
    else:
        o.append(line(f"M-10,{my + 3} L10,{my + 3}"))
    if fangs_ or expr == "hungry":
        o.append(fangs(0, my - 1, 11))
    # moustache
    o.append(cel(P(f"M-28,-208 Q-16,-222 0,-212 Q16,-222 28,-208 Q18,-200 0,-206 Q-18,-200 -28,-208 Z"), *mus, 2, 3, 3))
    return "".join(o)


def henri_head_back(x, y, s=1):
    """Arrière du crâne d'Henri (vu de dos, dans son fauteuil)."""
    o = cel(E(0, 0, 34, 38), *SKIN_HENRI) + cel(E(-30, 4, 9, 15), *WHITE, 3, 3) + cel(E(30, 4, 9, 15), *WHITE, 3, 3)
    o += cel(P("M-30,10 Q0,30 30,10 L30,26 Q0,40 -30,26 Z"), *WHITE, 3, 3)
    return g(o, x, y, s)


# ---------------------------------------------------------------- Minou
def cat(x, y, s=1, flip=False, pose="sit", ears_up=False, opacity=None):
    o = []
    c, sh = CAT
    if pose == "sit":
        o.append(tube("M18,-8 Q56,-6 48,-44 Q46,-60 56,-66", c, 10))
        o.append(cel(E(0, -32, 24, 32), c, sh))
        o.append(flat(E(-10, -4, 9, 6) + E(10, -4, 9, 6), c, 3))
        hy = -76
    elif pose == "walk":
        o.append(tube("M-34,-46 Q-60,-70 -52,-96", c, 10))
        o.append(tube("M-26,-30 L-30,-4", c, 9) + tube("M26,-30 L30,-4", c, 9))
        o.append(cel(E(0, -44, 40, 22), c, sh))
        o.append(tube("M-12,-30 L-14,-4", c, 9) + tube("M14,-30 L16,-4", c, 9))
        hy = -70
        o.append(g(_cat_head(ears_up), 36, hy + 6))
        return g("".join(o), x, y, s, flip, opacity)
    else:  # « held » : tête + buste seulement
        o.append(cel(E(0, -10, 22, 18), c, sh))
        hy = -36
    o.append(g(_cat_head(ears_up), 0, hy))
    if pose != "held":
        o.append(line("M-14,-58 Q0,-50 14,-58", 4, "#c22a40"))
        o.append(flat(E(0, -52, 6), GOLD[0], 2))
    else:
        o.append(flat(E(0, -18, 5), GOLD[0], 2))
    return g("".join(o), x, y, s, flip, opacity)


def _cat_head(ears_up=False):
    c, sh = CAT
    ear = -30 if ears_up else -24
    o = cel(POLY((-20, -6), (-18, ear), (-4, -14)), c, sh, 2, 2, 3)
    o += cel(POLY((20, -6), (18, ear), (4, -14)), c, sh, 2, 2, 3)
    o += cel(E(0, 0, 22, 19), c, sh, 4, 4)
    for ex in (-9, 9):
        o += flat(E(ex, -2, 5, 6), "#f6d743", 2) + fill(E(ex, -2, 1.4, 4.5), OUT)
    o += fill(POLY((-3, 5), (3, 5), (0, 8)), "#f29ab0")
    o += line("M6,7 L22,4", 1.5, "#ccc") + line("M-6,7 L-22,4", 1.5, "#ccc")
    return o


# ---------------------------------------------------------------- figurants
def person(x, y, s=1, flip=False, skin=("#f0c8a0", "#c9996e"), top=("#3a7bd5", "#25549a"),
           bottom=TROUSERS, hair=("#5a3a22", "#3a2414"), hat=None, expr="happy",
           arms="up", head=None, opacity=None):
    o = []
    o.append(tube("M-13,-90 L-15,-10", bottom[0], 17) + tube("M13,-90 L15,-10", bottom[0], 17))
    o.append(flat(E(-20, -7, 15, 7) + E(20, -7, 15, 7), "#222", 3))
    o.append(cel(P("M-32,-176 Q0,-184 32,-176 L30,-86 Q0,-78 -30,-86 Z"), *top))
    arm = {"up": ["M-30,-168 L-56,-206 L-62,-240", "M30,-168 L56,-206 L62,-240"],
           "down": ["M-30,-168 Q-46,-130 -42,-98", "M30,-168 Q46,-130 42,-98"],
           "talk": ["M-30,-168 Q-46,-130 -42,-98", "M30,-168 Q56,-150 70,-170"]}[arms]
    for d in arm:
        o.append(tube(d, top[0], 14))
    ends = {"up": [(-62, -242), (62, -242)], "down": [(-42, -96), (42, -96)],
            "talk": [(-42, -96), (72, -172)]}[arms]
    for hx, hy in ends:
        o.append(cel(E(hx, hy, 8, 8), *skin, 2, 2, 3))
    o.append(flat(R(-8, -192, 16, 16), skin[0], 3))
    if head == "pumpkin":
        o.append(cel(E(0, -226, 44, 38), *ORANGE))
        o.append(line("M0,-264 Q4,-276 12,-278", 6, "#3f6b2a"))
        o.append(fill(POLY((-22, -236), (-10, -236), (-16, -248)) + POLY((10, -236), (22, -236), (16, -248)), "#ffd23f"))
        o.append(fill(P("M-22,-214 L-12,-206 L-4,-214 L4,-206 L12,-214 L22,-214 Q0,-196 -22,-214 Z"), "#ffd23f"))
    else:
        o.append(cel(E(0, -226, 34, 38), *skin))
        o.append(cel(P("M-36,-226 C-40,-276 40,-276 36,-226 C24,-246 -24,-246 -36,-226 Z"), *hair, 4, 4))
        if expr == "happy":
            o += [arc_eye(-12, -228, 6), arc_eye(12, -228, 6)]
            o.append(flat(P("M-11,-210 Q0,-198 11,-210 Z"), "#6b1f2a", 3))
        elif expr == "laugh":
            o += [line("M-18,-232 L-8,-228 L-18,-224"), line("M18,-232 L8,-228 L18,-224")]
            o.append(flat(P("M-13,-212 Q0,-194 13,-212 Z"), "#6b1f2a", 3))
        else:
            o += [eye(-12, -228, 6, 7, 0, 0, 3), eye(12, -228, 6, 7, 0, 0, 3)]
            o.append(line("M-8,-208 L8,-208"))
    if hat == "witch":
        o.append(cel(P("M-50,-252 L50,-252 L30,-262 L4,-330 L-30,-262 Z"), "#2a2238", "#15111d"))
        o.append(flat(R(-30, -266, 60, 8), "#7d4fbf", 3))
    elif hat == "cap":
        o.append(cel(P("M-36,-244 C-36,-276 36,-276 36,-244 L60,-244 L60,-238 L-36,-238 Z"), "#e8502a", "#b33a1c", 3, 3))
    return g("".join(o), x, y, s, flip, opacity)


def ghost_friend(x, y, s=1, flip=False):
    o = cel(P("M-42,0 L-44,-120 C-44,-196 44,-196 44,-120 L42,0 L28,-14 L14,0 L0,-14 L-14,0 L-28,-14 Z"), *WHITE)
    o += fill(E(-14, -128, 7, 11) + E(14, -128, 7, 11) + E(0, -98, 8, 10), OUT)
    o += cel(P("M-44,-110 L-74,-150 L-62,-160 L-40,-130 Z"), *WHITE, 2, 2, 3)
    o += cel(P("M44,-110 L74,-150 L62,-160 L40,-130 Z"), *WHITE, 2, 2, 3)
    return g(o, x, y, s, flip)


def paramedic(x, y, s=1, flip=False, arms="talk"):
    p = person(0, 0, 1, False, top=("#e8502a", "#b33a1c"), bottom=("#2b3550", "#1b2236"),
               hair=("#2a2a2a", "#111"), hat="cap", expr="neutral", arms=arms)
    stripe = fill(R(-30, -130, 60, 8), "#e8e8a0") + fill(R(-30, -108, 60, 8), "#e8e8a0")
    return g(p + stripe, x, y, s, flip)


# ---------------------------------------------------------------- accessoires
def prop(name):
    if name == "glass":
        return (flat(P("M-11,-30 L11,-30 L8,6 L-8,6 Z"), GLASS, 3, extra='fill-opacity="0.85"')
                + fill(P("M-9,-14 L9,-14 L7.5,4 L-7.5,4 Z"), "#6fc3e8", 'opacity="0.8"')
                + line("M-6,-24 L-5,-4", 2, "#fff"))
    if name == "cup":
        return (flat(E(0, 4, 18, 5), "#f4f0f7", 2.5)
                + cel(P("M-12,-14 L12,-14 L9,4 L-9,4 Z"), "#f4f0f7", "#c9c2d6", 2, 2, 2.5)
                + line("M12,-10 q8,2 0,9", 3) + fill(E(0, -13, 10, 2.5), "#5a3420")
                + line("M-4,-20 q-4,-6 0,-12 q4,-6 0,-12", 2.5, "#e9e2f2", 'opacity="0.8"')
                + line("M5,-20 q-4,-6 0,-12", 2.5, "#e9e2f2", 'opacity="0.8"'))
    if name == "cups3":
        return g(prop("cup"), -30, 0) + g(prop("cup"), 0, -4) + g(prop("cup"), 30, 0)
    if name == "tray3":
        return flat(R(-52, 2, 104, 8, 3), "#c0c0c8", 3) + g(prop("cups3"), 0, 0)
    if name == "key":
        return (flat(E(-10, 0, 7) , GOLD[0], 2.5) + fill(E(-10, 0, 2.5), OUT)
                + flat(R(-3, -2.5, 20, 5, 1), GOLD[0], 2) + flat(R(10, 2, 3, 5) + R(15, 2, 3, 4), GOLD[0], 1.5))
    if name == "phone":
        return (flat(R(-9, -16, 18, 32, 4), "#2a2a35", 3) + fill(R(-6, -12, 12, 22, 2), "#3b3b4a"))
    if name == "phone_msg":
        return (flat(R(-26, -46, 52, 92, 8), "#2a2a35", 4) + fill(R(-21, -38, 42, 72, 4), "#cfe3ff")
                + flat(R(-17, -30, 30, 16, 6), "#fff", 2) + flat(R(-13, -8, 30, 16, 6), "#9fd1ff", 2)
                + fill(E(-8, -22, 2) + E(-2, -22, 2) + E(4, -22, 2), OUT))
    if name == "frame":
        return (cel(R(-26, -32, 52, 64, 3), *WOOD, 3, 3) + fill(R(-18, -24, 36, 48), "#e7d8b4")
                + fill(E(-7, -8, 6, 7) + E(8, -9, 6, 7), "#8b7355")
                + fill(P("M-16,24 Q-7,2 0,24 Z") + P("M0,24 Q8,0 18,24 Z"), "#5c4a38")
                + fill(P("M2,-14 Q8,-22 16,-12 L18,20 L12,6 Z"), "#fbf6ea"))
    if name == "letter_hand":
        return (cel(R(-34, -22, 68, 44, 3), *PAPER, 3, 3) + line("M-34,-22 L0,4 L34,-22", 2.5)
                + flat(R(16, -16, 12, 14), "#d94a4a", 2) + fill(R(18, -14, 8, 4), "#3a6fd8")
                + line("M-26,8 q6,-4 12,0 q6,4 12,0", 2, "#2d3a8c"))
    if name == "letter_typed":
        return (cel(R(-34, -22, 68, 44, 3), "#f4f4f0", "#cfcfc8", 3, 3)
                + "".join(fill(R(-26, -14 + 7 * i, 44 - (i % 2) * 14, 3), "#555") for i in range(5)))
    if name == "ring":
        return (flat(E(0, 0, 10, 9), "none", 0) + line("M0,-9 a10,9 0 1,0 0.1,0", 5, GOLD[1])
                + line("M0,-9 a10,9 0 1,0 0.1,0", 3, GOLD[0]) + flat(POLY((-5, -12), (5, -12), (0, -4)), "#bfe9ff", 2)
                + sparkle(12, -16, 0.6))
    if name == "plate":
        return (flat(E(0, 0, 34, 10), "#f4f0f7", 3) + cel(P("M-22,-2 Q0,-18 22,-2 Q0,6 -22,-2 Z"), "#f6d743", "#d9ae24", 2, 2, 3)
                + fill(E(-6, -5, 3) + E(8, -4, 2.5), "#6aa84f"))
    if name == "plate_bread":
        return (prop("plate") + cel(R(14, -14, 22, 14, 4), "#e3a95a", "#b97a32", 2, 2, 3))
    if name == "bread":
        return cel(R(-12, -8, 24, 16, 5), "#e3a95a", "#b97a32", 2, 2, 3)
    if name == "fork":
        return line("M0,0 L0,-24", 3, "#bbb") + line("M-4,-24 L-4,-32 M0,-24 L0,-32 M4,-24 L4,-32", 2, "#bbb")
    if name == "knife":
        return flat(P("M0,0 L4,-34 Q8,-38 6,-30 L4,0 Z"), "#d8dde6", 2) + flat(R(-2, 0, 7, 14, 2), WOOD[0], 2)
    if name == "garlic":
        return garlic(0, 0, 0.8)
    if name == "toast":
        return cel(R(-16, -10, 32, 20, 6), "#e3a95a", "#b97a32", 2, 2, 3) + fill(E(-4, -2, 3) + E(6, 2, 3), "#f4f0d0")
    if name == "card":
        return (cel(R(-30, -20, 60, 40, 3), *PAPER, 3, 3) + g(bat(0, 0, 0.5), 0, -4)
                + line("M-20,12 L20,12", 2, "#8a6"))
    if name == "cat":
        return cat(0, 18, 0.8, pose="held")
    if name == "newspaper":
        return (cel(R(-50, -36, 100, 72, 2), "#efeee8", "#cfcdc4", 3, 3)
                + fill(R(-42, -28, 84, 10), "#333")
                + "".join(fill(R(-42, -12 + 8 * i, 36, 3), "#888") for i in range(5))
                + flat(R(2, -12, 40, 36), "#fff", 2) + line("M22,-6 L22,18 M12,2 L32,2", 3))
    if name == "drop":
        return flat(P("M0,-14 Q10,0 0,6 Q-10,0 0,-14 Z"), "#c4122e", 3)
    if name == "letter_opener":
        return flat(P("M0,0 L3,-38 L6,0 Z"), "#cfd5df", 2) + flat(R(-2, 0, 10, 12, 3), GOLD[0], 2)
    return ""


def garlic(x, y, s=1):
    o = cel(P("M0,-30 Q26,-22 22,0 Q14,16 0,16 Q-14,16 -22,0 Q-26,-22 0,-30 Z"), "#f6f2e4", "#d8cfae")
    o += line("M0,-28 Q-6,-6 -4,14", 2, "#cfc59f") + line("M0,-28 Q8,-6 6,14", 2, "#cfc59f")
    o += line("M0,-30 Q-2,-40 4,-46", 4, "#cfc59f")
    return g(o, x, y, s)


def pumpkin(x, y, s=1, face=True, halo=True):
    o = ""
    if halo:
        o += glow(0, -34, 110, "#ffb347", 0.35)
    o += cel(E(-22, -34, 32, 36) + E(22, -34, 32, 36) + E(0, -34, 30, 38), *ORANGE)
    if not face:
        o += line("M0,-72 Q-4,-60 0,-40", 3) + line("M-20,-68 Q-28,-40 -18,-2", 2.5) + line("M20,-68 Q28,-40 18,-2", 2.5)
    o += flat(P("M-4,-70 Q-2,-86 8,-94 L12,-88 Q6,-80 6,-70 Z"), "#4f7d2a", 3)
    if face:
        o += fill(POLY((-30, -44), (-12, -44), (-21, -60)) + POLY((12, -44), (30, -44), (21, -60)), "#ffd23f",
                  f'stroke="{OUT}" stroke-width="2"')
        o += fill(P("M-32,-26 L-20,-18 L-10,-26 L0,-18 L10,-26 L20,-18 L32,-26 Q0,0 -32,-26 Z"), "#ffd23f",
                  f'stroke="{OUT}" stroke-width="2"')
    return g(o, x, y, s)


def bat(x, y, s=1, opacity=None):
    o = flat(P("M0,-6 Q-14,-18 -34,-14 Q-26,-8 -28,0 Q-20,-4 -14,4 Q-8,-2 0,6 Q8,-2 14,4 Q20,-4 28,0 "
               "Q26,-8 34,-14 Q14,-18 0,-6 Z"), "#1d1830", 2)
    o += fill(E(-3, -2, 1.5) + E(3, -2, 1.5), "#ffd23f")
    return g(o, x, y, s, opacity=opacity)


def sparkle(x, y, s=1, color="#fff6a8"):
    return g(flat(P("M0,-14 L3,-3 L14,0 L3,3 L0,14 L-3,3 L-14,0 L-3,-3 Z"), color, 2), x, y, s)


def heart(x, y, s=1, color="#e8455a"):
    return g(cel(P("M0,12 C-30,-8 -16,-30 0,-14 C16,-30 30,-8 0,12 Z"), color, "#a82235", 3, 3, 3), x, y, s)


def qmark(x, y, s=1, color="#ffd23f"):
    return g(text(0, 0, "?", 46, color), x, y, s)


def excl(x, y, s=1, color="#ffd23f"):
    return g(text(0, 0, "!", 46, color), x, y, s)


def notes(x, y, s=1):
    o = line("M0,0 L0,-30 L20,-36 L20,-6", 4, "#fff6a8") + fill(E(-5, 0, 7, 5) + E(15, -6, 7, 5), "#fff6a8",
                                                                 f'stroke="{OUT}" stroke-width="2"')
    return g(o, x, y, s)


def zzz(x, y, s=1):
    return g(text(0, 0, "z", 26, "#cfe3ff") + text(16, -18, "z", 32, "#cfe3ff") + text(36, -40, "Z", 40, "#cfe3ff"), x, y, s)


def anger(x, y, s=1):
    o = line("M-10,-4 Q-4,-4 -4,-10 M4,-10 Q4,-4 10,-4 M10,4 Q4,4 4,10 M-4,10 Q-4,4 -10,4", 4, "#e0142c")
    return g(o, x, y, s)


def motion(x, y, s=1, n=3):
    return g("".join(line(f"M0,{i * 16} L-50,{i * 16}", 4, "#e9e2f2", 'opacity="0.7"') for i in range(n)), x, y, s)


def burst(x, y, r, label, fill_color="#ffd23f", size=48, rot=-8):
    pts = []
    n = 14
    for i in range(n * 2):
        a = math.pi * i / n
        rr = r if i % 2 == 0 else r * 0.68
        pts.append((round(rr * math.cos(a) * 1.25, 1), round(rr * math.sin(a), 1)))
    o = flat(POLY(*pts), fill_color, 5) + text(0, size * 0.35, label, size, "#fff")
    return g(o, x, y, 1, rot=rot)


def thought(x, y, w, h, inner="", tail=(0, 0)):
    tx, ty = tail
    o = flat(E(x, y, w / 2, h / 2), "#f6f2fa", 4)
    o += flat(E(x + (tx - x) * 0.55, y + h / 2 + (ty - y - h / 2) * 0.55, 10, 8), "#f6f2fa", 3)
    o += flat(E(x + (tx - x) * 0.8, y + h / 2 + (ty - y - h / 2) * 0.8, 6, 5), "#f6f2fa", 3)
    return o + inner


# ---------------------------------------------------------------- décors : éléments
def sky(top="#1d1438", bottom="#4a2a6e"):
    gid = uid("sky")
    return (f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/></linearGradient></defs>'
            f'<rect width="{W}" height="{H}" fill="url(#{gid})"/>')


def stars(seed=3, n=40, h=300):
    o = []
    v = seed
    for i in range(n):
        v = (v * 9301 + 49297) % 233280
        x = v % W
        v = (v * 9301 + 49297) % 233280
        y = v % h
        o.append(E(x, y, 1.6 if i % 3 else 2.4))
    return fill("".join(o), "#fff6d8", 'opacity="0.8"')


def moon(x, y, r=46):
    return (fill(E(x, y, r * 1.8), "#f6e7a1", 'opacity="0.12"') + cel(E(x, y, r), "#f6e7a1", "#d9c46f", 8, 6)
            + fill(E(x - 12, y - 10, 8) + E(x + 14, y + 12, 6), "#d9c46f", 'opacity="0.7"'))


def glow(x, y, r, color="#ffd27a", op=0.25):
    gid = uid("gl")
    return (f'<defs><radialGradient id="{gid}"><stop offset="0" stop-color="{color}" stop-opacity="{op}"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient></defs>'
            f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r}" fill="url(#{gid})"/>')


def darken(op=0.35, color="#0d0820"):
    return f'<rect width="{W}" height="{H}" fill="{color}" opacity="{op}"/>'


def vignette():
    gid = uid("vg")
    return (f'<defs><radialGradient id="{gid}" cx="0.5" cy="0.5" r="0.75">'
            f'<stop offset="0.6" stop-color="#000" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="#000" stop-opacity="0.55"/></radialGradient></defs>'
            f'<rect width="{W}" height="{H}" fill="url(#{gid})"/>')


def floor(y=FLOOR - 70, color=WOOD, planks=True):
    o = cel(R(-10, y, W + 20, H - y + 10), color[0], color[1], 0, -10)
    if planks:
        o += "".join(line(f"M{x},{y} L{x - 40},{H}", 2, color[1]) for x in range(60, W + 60, 110))
    return o


def wallpaper(color=("#4f6b58", "#435c4b"), y_end=470, stripes=True):
    o = fill(R(0, 0, W, y_end), color[0])
    if stripes:
        o += "".join(fill(R(x, 0, 22, y_end), color[1]) for x in range(0, W, 64))
        o += "".join(fill(E(x + 43, y, 4), "#c9b98a", 'opacity="0.5"') for x in range(0, W, 64) for y in range(40, y_end, 80))
    o += flat(R(-10, y_end - 22, W + 20, 22), WOOD_DARK[0], 3)
    return o


def window(x, y, w, h, kind="night", curtains=True, light=False):
    o = cel(R(x - 10, y - 10, w + 20, h + 20, 4), *WOOD_DARK, 4, 4)
    if kind == "night":
        o += fill(R(x, y, w, h), "#2b2150")
        o += fill(E(x + w * 0.72, y + h * 0.28, min(w, h) * 0.12), "#f6e7a1")
        o += fill(E(x + w * 0.2, y + h * 0.2, 2) + E(x + w * 0.45, y + h * 0.12, 1.6) + E(x + w * 0.3, y + h * 0.5, 1.6), "#fff")
    elif kind == "street":
        o += fill(R(x, y, w, h), "#2b2150")
        o += fill(R(x + w * 0.6, y + h * 0.3, 6, h * 0.7), "#1b1226")
        o += fill(E(x + w * 0.6 + 3, y + h * 0.28, 14), "#ffe9a0")
        o += glow(x + w * 0.6 + 3, y + h * 0.28, w * 0.5, "#ffe9a0", 0.5)
    elif kind == "day":
        o += fill(R(x, y, w, h), "#a9dcf5")
        o += fill(E(x + w * 0.75, y + h * 0.3, min(w, h) * 0.14), "#fff2a8")
    elif kind == "flash":
        o += fill(R(x, y, w, h), "#e9f2ff")
    o += flat(R(x + w / 2 - 3, y, 6, h) + R(x, y + h / 2 - 3, w, 6), WOOD_DARK[0], 2)
    if curtains:
        o += cel(P(f"M{x - 18},{y - 16} L{x + w * 0.28},{y - 16} Q{x + w * 0.1},{y + h * 0.5} {x + w * 0.2},{y + h + 16} L{x - 18},{y + h + 16} Z"),
                 "#7d2a3a", "#561b28")
        o += cel(P(f"M{x + w + 18},{y - 16} L{x + w * 0.72},{y - 16} Q{x + w * 0.9},{y + h * 0.5} {x + w * 0.8},{y + h + 16} L{x + w + 18},{y + h + 16} Z"),
                 "#7d2a3a", "#561b28")
        o += flat(R(x - 26, y - 22, w + 52, 8, 4), GOLD[1], 3)
    return o


def door(x, y, w=110, h=230, state="closed", color=WOOD, inside="#120c1e"):
    """(x, y) = coin bas-gauche."""
    o = cel(R(x - 10, y - h - 10, w + 20, h + 10, 3), *WOOD_DARK, 4, 4)
    o += fill(R(x, y - h, w, h), inside)
    if state == "closed":
        o += cel(R(x, y - h, w, h, 2), *color)
        o += flat(R(x + 14, y - h + 16, w - 28, h * 0.38, 3) + R(x + 14, y - h * 0.5, w - 28, h * 0.38, 3), color[1], 3)
        o += flat(E(x + w - 16, y - h * 0.5, 6), GOLD[0], 3)
    elif state == "ajar":
        o += cel(POLY((x, y - h), (x + w * 0.3, y - h - 10), (x + w * 0.3, y + 8), (x, y)), *color)
    elif state == "open":
        o += cel(POLY((x, y - h), (x - w * 0.45, y - h - 18), (x - w * 0.45, y + 18), (x, y)), *color)
    return o


def frame_wall(x, y, w, h, kind="face", tilt=0):
    o = cel(R(-w / 2, -h / 2, w, h, 3), *GOLD, 3, 3)
    o += fill(R(-w / 2 + 6, -h / 2 + 6, w - 12, h - 12), "#d9c9a0")
    if kind == "face":
        o += fill(E(0, -h * 0.08, w * 0.17, h * 0.17) + P(f"M{-w * 0.3},{h / 2 - 6} Q0,{-h * 0.05} {w * 0.3},{h / 2 - 6} Z"), "#9b8466", 'opacity="0.55"')
    elif kind == "couple":
        o += fill(E(-w * 0.17, -h * 0.1, w * 0.12, h * 0.13) + E(w * 0.17, -h * 0.12, w * 0.12, h * 0.13), "#8b7355")
        o += fill(P(f"M{-w * 0.38},{h / 2 - 6} Q{-w * 0.17},{-h * 0.02} 0,{h / 2 - 6} Z") +
                  P(f"M0,{h / 2 - 6} Q{w * 0.17},{-h * 0.04} {w * 0.38},{h / 2 - 6} Z"), "#5c4a38")
    elif kind == "trio":
        for i, cx in enumerate((-0.28, 0, 0.28)):
            col = "#cfd8c4" if i == 1 else "#8b7355"
            o += fill(E(w * cx, -h * 0.1, w * 0.1, h * 0.12), col)
        o += fill(P(f"M{-w * 0.08},{h / 2 - 6} L{-w * 0.14},{-h * 0.0} L0,{h * 0.08} L{w * 0.14},{-h * 0.0} L{w * 0.08},{h / 2 - 6} Z"), "#231d33")
    return g(o, x, y, rot=tilt)


def clock(x, y, s=1, hh=23, mm=44):
    o = cel(P("M-40,40 L-40,-20 Q-40,-60 0,-60 Q40,-60 40,-20 L40,40 Z"), *WOOD)
    o += flat(E(0, -16, 30), "#f6efd8", 3)
    for i in range(12):
        a = math.pi * 2 * i / 12
        o += fill(E(round(24 * math.sin(a), 1), round(-16 - 24 * math.cos(a), 1), 2), OUT)
    am = math.pi * 2 * mm / 60
    ah = math.pi * 2 * ((hh % 12) + mm / 60) / 12
    o += line(f"M0,-16 L{round(14 * math.sin(ah), 1)},{round(-16 - 14 * math.cos(ah), 1)}", 4)
    o += line(f"M0,-16 L{round(22 * math.sin(am), 1)},{round(-16 - 22 * math.cos(am), 1)}", 3)
    return g(o, x, y, s)


def lamp_post(x, y, s=1, on=True):
    o = ""
    if on:
        o += glow(0, -280, 160, "#ffe9a0", 0.35)
    o += flat(R(-6, -270, 12, 270), "#2a2438", 3) + flat(R(-14, -10, 28, 10), "#2a2438", 3)
    o += flat(P("M-20,-270 L20,-270 L14,-300 L-14,-300 Z"), "#ffe9a0" if on else "#666", 3)
    o += flat(P("M-24,-300 L24,-300 L0,-318 Z"), "#2a2438", 3)
    return g(o, x, y, s)


def house_old(x, y, s=1, lit=True, silhouette=False, flash=False):
    """Maison victorienne des Morticia. (x, y) = bas-centre."""
    wall, wall_sh = "#5b4f73", "#3d3452"
    o = cel(R(-150, -260, 300, 260), wall, wall_sh)
    o += cel(POLY((-170, -258), (0, -380), (170, -258)), "#2e2540", "#1d1730")
    o += cel(R(70, -400, 34, 90), wall, wall_sh, 4, 4)
    o += flat(R(-30, -120, 60, 120, 3), WOOD_DARK[0], 4)
    o += flat(R(-60, 0, 120, 14), "#433a55", 3)
    win_lit = "#ffd27a"
    for wx, wy, on in ((-100, -220, False), (60, -220, lit), (-100, -110, False), (60, -110, False)):
        color = "#e9f2ff" if (flash and wx == 60 and wy == -220) else (win_lit if on else "#2b2150")
        o += flat(R(wx, wy, 44, 60, 2), color, 4)
        if on:
            o += glow(wx + 22, wy + 30, 70, "#ffd27a", 0.35)
        if silhouette and wx == 60 and wy == -220:
            o += fill(E(wx + 22, wy + 30, 10, 12) + R(wx + 8, wy + 40, 28, 20, 6), "#1b1226")
        o += line(f"M{wx + 22},{wy} L{wx + 22},{wy + 60} M{wx},{wy + 30} L{wx + 44},{wy + 30}", 3)
    o += flat(E(0, -310, 18), "#2b2150", 4)
    return g(o, x, y, s)


def house_party(x, y, s=1):
    """Maison des amis où a lieu la fête."""
    o = cel(R(-150, -230, 300, 230), "#3d5a80", "#2b4161")
    o += cel(POLY((-170, -228), (0, -320), (170, -228)), "#283b56", "#1a2840")
    o += flat(R(-28, -110, 56, 110, 3), "#8a4a2a", 4)
    colors = ["#ff5fa2", "#5fe0ff", "#ffd23f", "#9b72ff"]
    for i, (wx, wy) in enumerate(((-110, -200), (66, -200), (-110, -100), (66, -100))):
        o += flat(R(wx, wy, 44, 56, 2), colors[i], 4)
        o += glow(wx + 22, wy + 28, 60, colors[i], 0.35)
    o += "".join(fill(E(-140 + i * 28, -232, 6), colors[i % 4]) for i in range(11))
    return g(o, x, y, s)


# ---------------------------------------------------------------- meubles
def armchair_rear(x, y, s=1, color=("#7d2a3a", "#561b28")):
    o = cel(R(-70, -210, 140, 170, 34), *color)
    o += cel(R(-62, -70, 124, 34, 10), *color)
    return g(o, x, y, s)


def armchair_front(x, y, s=1, color=("#7d2a3a", "#561b28")):
    o = cel(R(-86, -110, 30, 100, 14), *color) + cel(R(56, -110, 30, 100, 14), *color)
    o += cel(R(-62, -44, 124, 34, 8), *color)
    o += flat(R(-80, -10, 10, 12) + R(70, -10, 10, 12), WOOD_DARK[0], 3)
    return g(o, x, y, s)


def armchair_back_view(x, y, s=1, occupant=True, color=("#7d2a3a", "#561b28")):
    o = henri_head_back(0, -238, 1) if occupant else ""
    o += cel(R(-74, -230, 148, 220, 36), *color)
    o += cel(R(-92, -120, 28, 110, 12), *color) + cel(R(64, -120, 28, 110, 12), *color)
    o += flat(R(-80, -10, 10, 12) + R(70, -10, 10, 12), WOOD_DARK[0], 3)
    if occupant:
        o += fill(E(-82, -112, 9), SKIN_HENRI[0], f'stroke="{OUT}" stroke-width="3"')
    return g(o, x, y, s)


def sofa_rear(x, y, s=1, color=("#5e3a7a", "#3f2554")):
    o = cel(R(-160, -170, 320, 130, 30), *color)
    o += cel(R(-150, -70, 300, 34, 10), *color)
    return g(o, x, y, s)


def sofa_front(x, y, s=1, color=("#5e3a7a", "#3f2554")):
    o = cel(R(-180, -110, 36, 100, 16), *color) + cel(R(144, -110, 36, 100, 16), *color)
    o += cel(R(-150, -44, 300, 34, 8), *color)
    o += flat(R(-170, -10, 12, 12) + R(158, -10, 12, 12), WOOD_DARK[0], 3)
    return g(o, x, y, s)


def table(x, y, w=200, h=90, color=WOOD, top_y=None):
    o = cel(R(-w / 2, -h, w, 18, 4), *color)
    o += flat(R(-w / 2 + 12, -h + 18, 14, h - 18) + R(w / 2 - 26, -h + 18, 14, h - 18), color[1], 3)
    return g(o, x, y)


def nightstand(x, y, s=1, lamp=False):
    o = cel(R(-40, -90, 80, 90, 4), *WOOD)
    o += flat(R(-30, -70, 60, 26, 3), WOOD[1], 3) + flat(E(0, -57, 4), GOLD[0], 2)
    if lamp:
        o += flat(R(-4, -130, 8, 40), GOLD[1], 2) + cel(P("M-24,-128 L24,-128 L16,-160 L-16,-160 Z"), "#efe1b0", "#c9b27a", 3, 3)
    return g(o, x, y, s)


def bed(x, y, s=1):
    o = cel(R(-200, -200, 30, 200, 6), *WOOD_DARK)
    o += cel(R(-180, -90, 360, 70, 10), "#e9e0f2", "#b8acc9")
    o += cel(R(-176, -120, 90, 36, 14), "#f6f2fa", "#c9c2d6", 3, 3)
    o += cel(R(-80, -96, 260, 60, 10), "#6b3fa0", "#4a2a72")
    o += flat(R(-180, -22, 360, 12), WOOD_DARK[0], 3)
    return g(o, x, y, s)


def bookshelf(x, y, s=1):
    o = cel(R(-70, -260, 140, 260, 4), *WOOD_DARK)
    cols = ["#7d2a3a", "#3f6b4f", "#4b2d63", "#a07a42", "#2b4161"]
    for row in range(4):
        yy = -250 + row * 62
        o += fill(R(-62, yy + 52, 124, 6), WOOD[1])
        for i in range(7):
            o += flat(R(-58 + i * 17, yy + 8 + (i % 3) * 4, 14, 44 - (i % 3) * 4, 2), cols[(i + row) % 5], 2)
    return g(o, x, y, s)


def fireplace(x, y, s=1, fire=True, clock_on=False):
    o = cel(R(-130, -200, 260, 200, 4), "#8a7f9a", "#655a75")
    o += cel(R(-150, -214, 300, 22, 4), *WOOD_DARK)
    o += fill(R(-80, -140, 160, 140), "#1a1222")
    if fire:
        o += glow(0, -50, 150, "#ff9a3c", 0.45)
        o += cel(P("M-50,0 Q-60,-50 -30,-70 Q-30,-40 -10,-40 Q-20,-90 10,-110 Q10,-60 30,-60 Q30,-90 46,-90 Q66,-40 50,0 Z"),
                 "#ff9a3c", "#e0531f", 6, 4, 3)
        o += fill(P("M-26,0 Q-30,-30 -10,-40 Q0,-20 10,-46 Q30,-20 26,0 Z"), "#ffd23f")
    if clock_on:
        o += clock(60, -238, 0.7)
    return g(o, x, y, s)


def fridge(x, y, s=1, open_=False):
    o = cel(R(-60, -280, 120, 280, 10), "#e9eef2", "#b9c3cc")
    if open_:
        o += fill(R(-50, -270, 100, 260), "#fffbe0")
        o += glow(0, -150, 140, "#fffbe0", 0.5)
        o += line("M-50,-190 L50,-190 M-50,-110 L50,-110", 3, "#b9c3cc")
        o += garlic(-24, -116, 0.6) + garlic(-4, -118, 0.55)
        o += flat(E(26, -206, 12, 14), "#f6f2e4", 3) + flat(R(10, -150, 30, 36, 4), "#9fd1ff", 3)
        o += cel(POLY((60, -280), (130, -300), (130, 20), (60, 0)), "#e9eef2", "#b9c3cc")
    else:
        o += line("M-60,-190 L60,-190", 3) + flat(R(40, -260, 8, 50, 3) + R(40, -170, 8, 60, 3), "#9aa5ae", 2)
    return g(o, x, y, s)


def counter(x, y, w=380, s=1):
    o = cel(R(-w / 2, -120, w, 120, 4), "#6b8f71", "#4d6b52")
    o += cel(R(-w / 2 - 10, -134, w + 20, 18, 4), "#e9e0d0", "#bfb39c", 3, 3)
    for i in range(int(w // 95)):
        o += flat(R(-w / 2 + 12 + i * 95, -104, 80, 88, 4), "#5b7d61", 3)
    return g(o, x, y, s)


def chessboard(x, y, s=1, scatter=False):
    o = cel(POLY((-90, 0), (90, 0), (60, -50), (-60, -50)), *WOOD_DARK, 3, 3)
    for r in range(4):
        for c in range(8):
            if (r + c) % 2 == 0:
                y0, y1 = -50 + r * 12.5, -50 + (r + 1) * 12.5
                def xl(yy, cc):
                    half = 60 + (yy + 50) / 50 * 30
                    return round(-half + cc * 2 * half / 8, 1)
                o += fill(POLY((xl(y0, c), y0), (xl(y0, c + 1), y0), (xl(y1, c + 1), y1), (xl(y1, c), y1)), "#f3e6c8")
    o += line("M-90,0 L90,0 L60,-50 L-60,-50 Z", 3)
    pieces = [(-50, -36, "#f6f2fa"), (-20, -40, "#f6f2fa"), (30, -14, "#231d33"), (56, -24, "#231d33"), (6, -26, "#231d33")]
    if scatter:
        pieces += [(-70, -64, "#f6f2fa"), (80, -70, "#231d33")]
    for px, py, col in pieces:
        o += chess_piece(px, py, 0.5, "pawn", col)
    o += chess_piece(-40, -10, 0.6, "knight", "#f6f2fa") + chess_piece(40, -40, 0.6, "king", "#231d33")
    return g(o, x, y, s)


def chess_piece(x, y, s=1, kind="pawn", color="#231d33"):
    if kind == "pawn":
        o = flat(P("M-14,0 L14,0 L10,-8 L6,-10 Q4,-24 6,-30 A10,10 0 1,0 -6,-30 Q-4,-24 -6,-10 L-10,-8 Z"), color, 3)
    elif kind == "king":
        o = flat(P("M-16,0 L16,0 L12,-10 L8,-12 L10,-44 L-10,-44 L-8,-12 L-12,-10 Z"), color, 3)
        o += flat(R(-3, -62, 6, 18) + R(-9, -56, 18, 6), color, 3)
    else:  # cavalier
        o = flat(P("M-16,0 L16,0 L12,-10 L10,-30 Q12,-52 -4,-58 L-8,-50 Q-20,-46 -20,-36 L-12,-34 L-4,-38 L-10,-12 L-12,-10 Z"), color, 3)
        o += fill(E(-4, -46, 2), "#e8455a" if color != "#231d33" else "#ffd23f")
    return g(o, x, y, s)


def stairs(x0=120, y0=560, n=9, step_w=70, step_h=52, color=WOOD):
    o = ""
    for i in range(n):
        x = x0 + i * step_w
        y = y0 - i * step_h
        o += cel(R(x, y - step_h, W - x + 20, step_h, 2), *color, 0, -6, 3)
    # rampe
    o += line(f"M{x0 - 10},{y0 - 130} L{x0 + n * step_w},{y0 - n * step_h - 130}", 10, WOOD_DARK[0])
    for i in range(n):
        x = x0 + i * step_w + 20
        y = y0 - i * step_h - step_h
        o += line(f"M{x},{y} L{x},{y - 100}", 5, WOOD_DARK[1])
    return o
