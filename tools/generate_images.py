"""Génère une illustration SVG par slide dans images/.

Chaque scène suit le même « prompt » de style (STYLE) et une description propre
à la slide ; elle est composée uniquement à partir des éléments communs de
art.py (mêmes personnages, mêmes décors, mêmes couleurs) pour rester cohérente.

Usage : python3 tools/generate_images.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from art import *  # noqa: E402,F401,F403
import art  # noqa: E402

art.PRINT_MODE = True

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "images"

STYLE = ("Illustration semi-réaliste (modelé en dégradés, textures, ombres douces) imprimée "
         "en risographie : réduite à six encres (violet nuit, prune, magenta, orange citrouille, "
         "pêche) sur papier crème, léger décalage de repérage, trame de demi-teinte et grain du papier. "
         "Personnages récurrents : le héros déguisé en vampire (teint blafard, cheveux noirs "
         "en pointe, cape noire à col rouge, nœud papillon rouge), Mme Morticia / Yvonne "
         "(vieille dame, chignon blanc, robe prune, collier de perles avec une clé), Henri "
         "(vieil homme chauve, touffes et moustache blanches, gilet moutarde, cravate verte), "
         "Minou (chat noir aux yeux jaunes, médaillon doré).")

SCENES = {}


def scene(pid, description):
    def deco(fn):
        SCENES[pid] = (description, fn)
        return fn
    return deco


def clip(content, shape):
    cid = uid("k")
    return f'<clipPath id="{cid}">{shape}</clipPath><g clip-path="url(#{cid})">{content}</g>'


# =============================================================== décors
def set_street(lit=True, silhouette=False, flash=False):
    o = sky() + stars(7) + moon(820, 90)
    o += fill(P("M0,330 Q120,300 240,330 T480,320 T720,330 T960,320 L960,470 L0,470 Z"), "#2a1f45")
    o += house_party(230, 470, 0.95) + house_old(720, 470, 0.95, lit, silhouette, flash)
    o += fill(R(0, 470, W, 130), "#2b2638") + fill(R(0, 466, W, 10), "#4a4458")
    o += "".join(fill(R(x, 530, 60, 8), "#d9cf9a", 'opacity="0.7"') for x in range(20, W, 120))
    o += lamp_post(480, 470, 0.9)
    return o


def set_party(window_house=False):
    o = fill(R(0, 0, W, H), "#3a2458")
    o += "".join(fill(P(f"M{x},0 L{x - 160},470 L{x - 60},470 Z"), c, 'opacity="0.18"')
                 for x, c in ((200, "#ff5fa2"), (480, "#5fe0ff"), (760, "#ffd23f"), (960, "#9b72ff")))
    o += line("M0,40 Q240,90 480,40 T960,40", 3, "#1b1226")
    for i in range(12):
        x = 40 + i * 80
        o += g(flat(POLY((-12, 0), (12, 0), (0, 26)), ["#f28c28", "#6b3fa0", "#6aa84f"][i % 3], 2), x, 52 + (10 if i % 2 else 0))
    o += flat(E(480, 90, 30), "#c9d3e0", 4) + "".join(
        fill(R(462 + c * 9, 66 + r * 9, 7, 7), "#fff", 'opacity="0.7"') for r in range(5) for c in range(4) if (r + c) % 2)
    o += line("M480,0 L480,60", 3)
    if window_house:
        o += window(600, 110, 260, 200, "night", curtains=True)
        o += clip(house_old(730, 330, 0.42, lit=True), R(600, 110, 260, 200))
        o += flat(R(727, 110, 6, 200) + R(600, 207, 260, 6), WOOD_DARK[0], 2)
    else:
        o += bat(150, 140, 0.9) + bat(820, 170, 0.7)
    o += fill(R(0, 470, W, 130), "#241638")
    for r in range(3):
        for c in range(12):
            col = ["#5a2f7a", "#2f5a7a", "#7a2f5a"][(r + c) % 3]
            o += flat(R(c * 80 + (r % 2) * 40 - 40, 470 + r * 44, 80, 44), col, 2)
    return o


def set_porch(state="open"):
    o = sky() + stars(11, 25, 200) + moon(110, 80, 36)
    o += cel(R(260, 40, 700, 460), "#5b4f73", "#3d3452", 0, 0)
    o += "".join(line(f"M260,{y} L960,{y}", 2, "#4a4060") for y in range(70, 500, 34))
    o += door(470, 470, 150, 300, state, color=WOOD_DARK, inside="#ffcf7a")
    if state == "open":
        o += glow(545, 330, 220, "#ffcf7a", 0.35)
    o += flat(R(400, 470, 290, 26, 2) + R(380, 496, 330, 26, 2), "#6d6480", 4)
    o += fill(R(0, 520, W, 80), "#2b2638")
    o += g(flat(R(-14, -40, 28, 40, 4), "#2a2438", 3) + flat(R(-10, -36, 20, 30, 3), "#ffd27a", 2), 730, 300)
    o += glow(730, 280, 90, "#ffd27a", 0.4)
    o += pumpkin(110, 590, 0.8) + pumpkin(780, 530, 0.6)
    return o


def set_living(fire=True, day=False):
    o = wallpaper(("#4f6b58", "#435c4b"))
    o += floor(470)
    o += flat(E(480, 560, 360, 40), "#7d2a3a", 4) + line("M150,560 Q480,610 810,560", 3, "#a8475a")
    o += frame_wall(120, 120, 80, 100, "face") + frame_wall(230, 90, 60, 70, "couple", -3)
    o += frame_wall(230, 190, 70, 60, "face", 4) + frame_wall(340, 120, 70, 90, "couple")
    o += window(470, 70, 140, 170, "day" if day else "night")
    o += fireplace(800, 470, 1, fire, clock_on=True)
    if not day:
        o += darken(0.2)
    return o


def set_kitchen():
    o = fill(R(0, 0, W, 470), "#cfc4a8")
    o += "".join(line(f"M0,{y} L{W},{y}", 2, "#b8ac8e") for y in range(40, 470, 40))
    o += "".join(line(f"M{x},0 L{x},470", 2, "#b8ac8e") for x in range(40, W, 40))
    o += floor(470, ("#6d6480", "#4f4760"), planks=False)
    o += "".join(fill(R(x, 470, 60, 130), "#5d5570") for x in range(0, W, 120))
    o += window(420, 70, 160, 130, "night")
    o += counter(470, 470, 420)
    o += flat(E(400, 330, 40, 10), "#3a3a44", 4) + line("M440,330 L490,320", 6)
    o += darken(0.15)
    return o


def set_stairs():
    o = wallpaper(("#3f4a5e", "#36404f"), 600, stripes=True)
    o += frame_wall(300, 120, 60, 80, "face", -4) + frame_wall(520, 60, 60, 80, "couple", 3)
    o += stairs(80, 600, 10, 90, 52)
    o += darken(0.35)
    return o


def set_corridor():
    o = fill(R(0, 0, W, H), "#2b2440")
    o += fill(POLY((0, 0), (380, 150), (380, 420), (0, 600)), "#3a3152")
    o += fill(POLY((960, 0), (580, 150), (580, 420), (960, 600)), "#332b49")
    o += fill(POLY((0, 600), (380, 420), (580, 420), (960, 600)), WOOD_DARK[0])
    o += fill(POLY((0, 0), (380, 150), (580, 150), (960, 0)), "#1f1932")
    o += fill(R(380, 150, 200, 270), "#2a2342")
    o += window(440, 200, 80, 110, "street", curtains=False)
    o += glow(480, 260, 200, "#ffe9a0", 0.2)
    for i, (x0, x1) in enumerate(((40, 130), (180, 245), (290, 340))):
        def yy(x, top):
            t = x / 380
            return (0 + 150 * t) + (60 + 60 * (1 - t)) if top else 600 - 180 * t
        o += cel(POLY((x0, yy(x0, True)), (x1, yy(x1, True)), (x1, yy(x1, False) - 10), (x0, yy(x0, False) - 20)), *WOOD, 3, 3)
        o += flat(E(x1 - 12, (yy(x1, True) + yy(x1, False)) / 2, 4), GOLD[0], 2)
    o += darken(0.3)
    return o


def set_bedroom(lit=False, photos=False):
    wall = ("#4e5a7a", "#455170") if lit else ("#3a4260", "#343b57")
    o = wallpaper(wall)
    o += floor(470)
    o += window(380, 60, 200, 230, "street")
    if photos:
        for (x, y, w, h, t) in ((90, 90, 70, 90, -3), (180, 70, 60, 70, 2), (100, 210, 60, 70, 3), (190, 180, 80, 100, -2),
                                (700, 90, 70, 90, 2), (800, 80, 60, 70, -3), (720, 210, 80, 70, -1), (820, 200, 60, 80, 3)):
            o += frame_wall(x, y, w, h, "couple", t)
    # lumière du lampadaire projetée au sol
    o += fill(POLY((380, 470), (580, 470), (660, 600), (330, 600)), "#ffe9a0", 'opacity="0.12" filter="url(#blur20)"')
    o += bed(860, 520, 0.8)
    if not lit:
        o += darken(0.35)
    return o


def set_hall(mirror_content=""):
    o = wallpaper(("#5a4a6a", "#4e405d"))
    o += floor(470)
    o += door(720, 470, 140, 290, "closed", WOOD_DARK)
    o += flat(R(800, 300, 30, 14, 3), "#444", 2)
    o += cel(E(180, 210, 80, 120), *GOLD)
    mirror = E(180, 210, 66, 106)
    o += flat(mirror, "#bcd2e0", 3)
    o += clip(mirror_content, mirror)
    o += fill(P("M140,140 L160,120 L150,180 Z"), "#fff", 'opacity="0.5"')
    o += line("M420,470 L420,200", 8, WOOD_DARK[0]) + line("M390,210 L450,210", 8, WOOD_DARK[0])
    o += darken(0.15)
    return o


def set_home(time="day", with_table=False):
    o = fill(R(0, 0, W, 470), "#e6d6c4" if time == "day" else "#8f7f9e")
    o += floor(470, ("#c79a6b", "#a07548"))
    o += window(620, 70, 200, 180, "day" if time == "day" else "night")
    o += cel(R(60, 100, 120, 120, 6), "#f6f2fa", "#c9c2d6", 3, 3) + line("M80,190 L110,150 L130,170 L160,130", 4, "#6aa84f")
    if with_table:
        o += table(460, 540, 360, 110)
    if time != "day":
        o += darken(0.25)
    return o


def set_fin(color="#2a1a40"):
    o = fill(R(0, 0, W, H), color) + stars(21, 50, 600)
    o += glow(480, 300, 320, "#f28c28", 0.35)
    o += bat(140, 120, 1.1) + bat(820, 110, 0.9) + bat(780, 480, 0.7)
    return o


def finish(o, vig=True):
    """Passe finale commune : impression risographie (sans vignettage ni halo, qui formeraient
    des ovales durs une fois réduits à quelques encres)."""
    return print_finish(o)


# =============================================================== scènes
@scene("1", "Rue la nuit d'Halloween : la maison de la fête à gauche, la vieille maison des Morticia à droite, citrouilles et chauves-souris.")
def _():
    o = set_street() + pumpkin(140, 590, 1.4) + pumpkin(830, 590, 1.1) + pumpkin(470, 600, 0.8)
    o += bat(300, 120, 1.2) + bat(380, 80, 0.8) + bat(620, 140, 1)
    o += cat(600, 470, 0.5)
    return finish(o)


@scene("2", "Le héros fièrement déguisé en vampire, cape déployée, devant la maison de la fête.")
def _():
    o = set_street() + darken(0.15) + glow(480, 360, 260, "#c22a40", 0.25)
    o += hero(480, 570, 1.1, expr="happy", pose="cape")
    o += sparkle(330, 200) + sparkle(640, 240, 0.8) + pumpkin(140, 590, 1.1) + pumpkin(830, 590, 1)
    return finish(o)


@scene("3", "La piste de danse bondée ; un chat noir apparaît au milieu, sous un projecteur ; le héros s'arrête de danser.")
def _():
    o = set_party()
    o += ghost_friend(120, 520, 0.8) + person(250, 520, 0.8, hat="witch", skin=("#9fd17a", "#6fa84a"), top=("#4b2d63", "#2e1a40"))
    o += person(820, 520, 0.8, head="pumpkin") + notes(200, 230) + notes(760, 200, 0.8)
    o += glow(450, 520, 140, "#fff6c2", 0.5) + cat(450, 560, 1.1, ears_up=True)
    o += hero(640, 570, 1, expr="surprised") + excl(700, 260)
    return finish(o)


@scene("4", "Le héros tient le chat dans ses bras et regarde par la fenêtre la vieille maison d'en face, où une lumière brille.")
def _():
    o = set_party(window_house=True)
    o += person(120, 530, 0.75, head="pumpkin") + ghost_friend(240, 520, 0.7)
    o += hero(470, 575, 1.05, expr="neutral", pose="hold2", item="cat")
    o += thought(640, 380, 120, 70, g(prop("cat"), 640, 380, 0.9), (520, 300))
    return finish(o)


@scene("5", "Sur le perron : la porte s'ouvre sur Mme Morticia souriante qui serre Minou contre elle ; le héros sur les marches.")
def _():
    o = set_porch("open")
    o += morticia(545, 470, 1, expr="smile", pose="hold2", item="cat")
    o += hero(290, 580, 0.95, expr="happy")
    o += burst(150, 120, 60, "DING DONG !", size=34)
    return finish(o)


@scene("6", "Le salon d'un autre temps : le héros assis sur le sofa près de la cheminée, Mme Morticia lui propose un café.")
def _():
    o = set_living()
    o += sofa_rear(330, 545) + hero(330, 545, 0.95, expr="worried", legs="sit") + sofa_front(330, 545)
    o += morticia(600, 560, 1, expr="smile", pose="hold", item="cup")
    return finish(o)


@scene("7", "Mme Morticia dans son fauteuil, Minou ronronnant sur ses genoux ; le héros boit son café sur le sofa.")
def _():
    o = set_living()
    o += sofa_rear(280, 545) + hero(280, 545, 0.95, expr="neutral", legs="sit", pose="hold", item="cup") + sofa_front(280, 545)
    o += armchair_rear(620, 550) + morticia(620, 560, 0.95, expr="tender", pose="hold2", item="cat") + armchair_front(620, 550)
    o += heart(700, 300, 0.6)
    return finish(o)


@scene("8", "BOUM ! venant de l'étage : le héros sursaute, Minou dresse les oreilles, Mme Morticia fait un clin d'œil amusé.")
def _():
    o = set_living()
    o += sofa_rear(280, 545) + hero(280, 545, 0.95, expr="scared", legs="sit", pose="scared") + sofa_front(280, 545)
    o += armchair_rear(640, 550) + morticia(640, 560, 0.95, expr="wink", pose="fold") + armchair_front(640, 550)
    o += cat(470, 560, 0.8, ears_up=True) + excl(470, 420, 0.8)
    o += burst(470, 100, 70, "BOUM !")
    return finish(o)


@scene("9", "L'escalier qui grince, dans la pénombre : le héros monte avec un verre d'eau ; en bas, Mme Morticia indique le chemin.")
def _():
    o = set_stairs()
    o += morticia(110, 600, 0.85, expr="smile", pose="point_up")
    o += hero(530, 600 - 4 * 52, 0.9, expr="worried", pose="hold", item="glass")
    o += glow(900, 80, 200, "#ffe9a0", 0.15)
    return finish(o)


@scene("10", "Le couloir sombre de l'étage, des portes à gauche ; le héros frappe doucement à la troisième porte. Toc, toc, toc.")
def _():
    o = set_corridor()
    o += hero(430, 590, 0.95, expr="worried", pose="knock", flip=True)
    o += burst(250, 130, 60, "TOC TOC TOC", "#e9e2f2", 30, -4)
    return finish(o)


@scene("11", "La chambre froide : de dos, une silhouette dans un vieux fauteuil face à la fenêtre éclairée par les lampadaires.")
def _():
    o = set_bedroom()
    o += nightstand(640, 540) + armchair_back_view(480, 540, 1)
    o += hero(160, 570, 0.9, expr="worried", pose="hold", item="glass")
    o += zzz(560, 250, 0.8)
    return finish(o)


@scene("12", "Le héros hésite, verre d'eau à la main, entre parler au vieil homme endormi ou poser le verre sur la table de chevet.")
def _():
    o = set_bedroom()
    o += nightstand(640, 540) + armchair_back_view(480, 540, 1)
    o += hero(220, 570, 0.95, expr="worried", pose="hold", item="glass")
    o += qmark(130, 250) + qmark(300, 230, 0.8) + g(prop("glass"), 640, 440, 0.8, opacity=0.4)
    return finish(o)


@scene("13", "Henri, assis dans son fauteuil, tourne la tête et sourit chaleureusement au héros.")
def _():
    o = set_bedroom()
    o += armchair_rear(620, 550) + henri(620, 550, 1, expr="smile", legs="sit") + armchair_front(620, 550)
    o += hero(250, 570, 0.95, expr="neutral", pose="hold", item="glass") + nightstand(810, 540)
    return finish(o)


@scene("14", "Henri, nostalgique, baisse les yeux en parlant d'Yvonne ; le héros se sent mal à l'aise.")
def _():
    o = set_bedroom()
    o += armchair_rear(620, 550) + henri(620, 550, 1, expr="sad", legs="sit") + armchair_front(620, 550)
    o += hero(250, 570, 0.95, expr="worried", pose="hold", item="glass") + nightstand(810, 540)
    o += thought(740, 160, 130, 90, frame_wall(740, 160, 60, 60, "couple"), (650, 270))
    return finish(o)


@scene("15", "BAM ! La porte claque. Henri se lève, ses pieds semblent flotter, avec un large sourire affamé ; la pendule indique 23 h 44.")
def _():
    o = set_bedroom()
    o += door(40, 540, 110, 250, "closed")
    o += clock(820, 200, 0.9) + nightstand(820, 540)
    o += henri(600, 560, 1, expr="hungry", float_=True)
    o += hero(300, 570, 0.9, expr="scared", pose="scared")
    o += burst(110, 120, 60, "BAM !")
    return finish(o)


@scene("16", "Le grand-père, affamé, se tourne lentement vers le héros figé : « vous tombez à pic ! »")
def _():
    o = set_bedroom()
    o += door(40, 540, 110, 250, "closed") + nightstand(820, 540)
    o += henri(580, 565, 1.05, expr="hungry", pose="point", flip=True)
    o += hero(270, 570, 0.9, expr="blank")
    return finish(o)


@scene("17", "Henri s'approche et renifle l'air autour du héros, qui transpire de nervosité.")
def _():
    o = set_bedroom()
    o += henri(530, 565, 1.05, expr="surprised", flip=True)
    o += hero(320, 570, 0.95, expr="worried")
    o += line("M440,320 q-10,-8 -20,0 q-10,8 -20,0", 3, "#cfe3ff") + line("M440,340 q-10,-8 -20,0 q-10,8 -20,0", 3, "#cfe3ff")
    return finish(o)


@scene("18", "Henri recule avec un cri de dégoût en sentant l'ail ; le héros tient une tartine à l'ail.")
def _():
    o = set_bedroom()
    o += henri(650, 565, 1, expr="disgust", pose="shrug") + anger(720, 280) + anger(560, 300, 0.8)
    o += hero(280, 570, 0.95, expr="surprised", pose="hold", item="toast")
    o += garlic(400, 250, 0.7) + garlic(450, 200, 0.5)
    return finish(o)


@scene("19", "Henri, troublé, se parle à voix haute : souvenirs de l'ail d'Yvonne et tentation interdite.")
def _():
    o = set_bedroom()
    o += henri(560, 565, 1, expr="hungry", pose="chin")
    inner = garlic(720, 150, 0.9) + g(prop("plate"), 800, 175, 0.9) + heart(650, 160, 0.6)
    o += thought(730, 150, 240, 140, inner, (610, 260))
    o += hero(200, 570, 0.85, expr="scared")
    return finish(o)


@scene("20", "Face à Henri tiraillé par l'odeur d'ail, le héros décide de reprendre son destin en main.")
def _():
    o = set_bedroom()
    o += henri(650, 565, 1, expr="hungry", pose="chin")
    o += hero(300, 575, 1, expr="determined") + garlic(470, 230, 0.6) + qmark(480, 150)
    return finish(o)


@scene("21", "Henri tousse violemment dans un nuage d'haleine à l'ail, puis BAM ! la porte s'ouvre et ses yeux deviennent furieux.")
def _():
    o = set_bedroom()
    o += door(140, 540, 110, 250, "open")
    o += henri(600, 565, 1, expr="furious")
    o += fill(E(520, 310, 60, 40) + E(470, 290, 40, 30), "#b8d98a", 'opacity="0.6"')
    o += hero(340, 570, 0.9, expr="scared", pose="scared")
    o += burst(120, 110, 60, "BAM !")
    return finish(o)


@scene("22", "Le héros dévale l'escalier trois marches à la fois ; en bas, Mme Morticia l'attend dans l'embrasure du salon.")
def _():
    o = set_stairs()
    o += door(30, 600, 120, 260, "open", inside="#ffcf7a") + morticia(110, 600, 0.85, expr="tender")
    o += hero(560, 600 - 4 * 52, 0.9, expr="scared", pose="run", legs="run", flip=True)
    o += motion(700, 270, 1)
    return finish(o)


@scene("23", "Dans l'entrée, Mme Morticia serre la clé pendue à son cou pendant qu'une voix résonne à l'étage. Gloups.")
def _():
    o = set_hall(morticia(180, 330, 0.5))
    o += morticia(380, 560, 1, expr="sly", pose="key")
    o += hero(640, 570, 0.95, expr="scared")
    o += line("M520,40 q20,-10 40,0 q20,10 40,0", 4, "#ffd23f") + line("M500,70 q30,-12 60,0 q30,12 60,0", 4, "#ffd23f")
    o += sweat(700, 280) + excl(560, 120)
    return finish(o)


@scene("24", "Coincé dans l'entrée entre Mme Morticia et la porte fermée à clé : que faire ?")
def _():
    o = set_hall()
    o += morticia(330, 560, 1, expr="smile", pose="key")
    o += hero(560, 570, 0.95, expr="worried", pose="think") + qmark(500, 230) + qmark(640, 210, 0.8)
    o += g(prop("key"), 790, 260, 1.2)
    return finish(o)


@scene("25", "Le héros fait semblant de répondre au téléphone ; Mme Morticia l'observe sans ciller.")
def _():
    o = set_hall()
    o += morticia(330, 560, 1, expr="stern", pose="fold")
    o += hero(580, 570, 0.95, expr="worried", pose="phone", item="phone")
    o += line("M650,290 q10,-10 0,-20 M664,298 q16,-16 0,-34", 3, "#ffd23f")
    return finish(o)


@scene("26", "Mme Morticia ne sourit plus et fait tourner la petite clé ; à l'étage, des pas résonnent lentement.")
def _():
    o = set_hall()
    o += fill(P("M440,60 Q470,30 500,60 L520,190 L420,190 Z") + E(470, 40, 26, 30), "#140e1e", 'opacity="0.5"')
    o += morticia(330, 560, 1, expr="annoyed", pose="hold", item="key")
    o += hero(600, 570, 0.95, expr="scared", pose="reach")
    return finish(o)


@scene("27", "Le lendemain matin : deux petites marques de crocs sur le cou du héros et une carte des Morticia dans la boîte aux lettres.")
def _():
    o = set_home("day")
    o += hero(420, 570, 1.05, expr="scared", pose="hold", item="card", bite=True)
    o += glow(420, 380, 60, "#ff4060", 0.4) + excl(330, 180)
    return finish(o)


@scene("28", "Fin : la carte « Henri et Yvonne Morticia » et deux petits points rouges.")
def _():
    o = set_fin() + g(prop("card"), 480, 300, 4)
    o += fill(E(450, 420, 6) + E(510, 420, 6), "#c4122e")
    return finish(o)


@scene("29", "Mme Morticia, ravie, revient avec un plateau de trois tasses fumantes ; le héros installé dans un fauteuil ancien.")
def _():
    o = set_living()
    o += armchair_rear(280, 550) + hero(280, 550, 0.95, expr="happy", legs="sit") + armchair_front(280, 550)
    o += morticia(600, 560, 1, expr="smile", pose="hold2", item="tray3")
    o += qmark(660, 300, 0.7)
    return finish(o)


@scene("30", "Le héros s'endort, la tête qui tourne ; Mme Morticia lui caresse la joue comme une grand-mère.")
def _():
    o = set_living()
    o += armchair_rear(320, 550) + hero(320, 550, 0.95, expr="dizzy", legs="sit") + armchair_front(320, 550)
    o += g(prop("cup"), 170, 420)
    o += morticia(500, 560, 1, expr="tender", pose="caress", flip=True)
    o += zzz(380, 220)
    return finish(o)


@scene("31", "À la lueur des bougies, Henri s'accroupit devant le héros paralysé et dévoile deux longues canines ; Yvonne derrière.")
def _():
    o = set_living(fire=True) + darken(0.35)
    o += armchair_rear(260, 550) + hero(260, 550, 0.95, expr="scared", legs="sit") + armchair_front(260, 550)
    o += morticia(720, 540, 0.85, expr="tender")
    o += henri(500, 570, 1, expr="hungry", pose="menace", flip=True)
    for x in (110, 860):
        o += glow(x, 420, 90, "#ffcf7a", 0.4) + flat(R(x - 8, 420, 16, 50, 2), "#f4f0d8", 3) + fill(E(x, 410, 5, 10), "#ffd23f")
    return finish(o)


@scene("32", "Dans l'obscurité, seuls brillent les yeux rouges et les crocs d'Henri ; une chauve-souris s'envole.")
def _():
    o = set_living(fire=False) + darken(0.8)
    o += fill(E(440, 260, 10, 6) + E(500, 260, 10, 6), "#ff2a3c") + glow(470, 260, 90, "#ff2a3c", 0.4)
    o += flat(POLY((452, 310), (462, 310), (457, 336)) + POLY((478, 310), (488, 310), (483, 336)), "#fff", 2)
    o += bat(700, 160, 1.2) + bat(240, 120, 0.8)
    return finish(o)


@scene("33", "Le lendemain matin, Henri et Yvonne côte à côte devant la cheminée ; une nouvelle photo du héros entre eux sur la commode.")
def _():
    o = set_living(fire=True, day=True)
    o += sofa_rear(420, 550) + henri(340, 550, 0.9, expr="smile", legs="sit") + morticia(500, 560, 0.85, expr="smile") + sofa_front(420, 550)
    o += cel(R(640, 350, 120, 120, 4), *WOOD) + frame_wall(700, 310, 80, 70, "trio") + glow(700, 310, 80, "#fff6a8", 0.4)
    return finish(o)


@scene("34", "Fin : la photo du héros souriant, assis entre Henri et Yvonne.")
def _():
    o = set_fin() + frame_wall(480, 300, 300, 240, "trio") + sparkle(320, 160) + sparkle(650, 180, 0.8)
    return finish(o)


@scene("35", "Le héros propose un marché à Henri : les deux se serrent la main, le vieil homme sourit d'un air inquiétant.")
def _():
    o = set_bedroom()
    o += hero(320, 570, 1, expr="determined", pose="offer")
    o += henri(620, 570, 1, expr="hungry", pose="offer", flip=True)
    o += sparkle(470, 400, 1.2, "#ffd23f")
    return finish(o)


@scene("36", "À la porte ouverte, le héros remarque deux petits points noirs sur sa peau ; Henri sourit toujours.")
def _():
    o = set_bedroom()
    o += door(120, 540, 110, 250, "ajar")
    o += armchair_rear(680, 550) + henri(680, 550, 1, expr="smile", legs="sit") + armchair_front(680, 550)
    o += hero(330, 570, 1, expr="surprised", pose="hold")
    o += fill(E(360, 440, 2.6) + E(370, 440, 2.6), "#2a0a12") + glow(365, 440, 30, "#fff", 0.6)
    return finish(o)


@scene("37", "Dans la cuisine déserte, le héros inspecte le réfrigérateur et trouve des gousses d'ail.")
def _():
    o = set_kitchen() + fridge(780, 540, 1, open_=True)
    o += hero(560, 575, 1, expr="happy", pose="hold", item="garlic")
    o += qmark(180, 200) + g(prop("plate"), 260, 330)
    return finish(o)


@scene("38", "Le héros prépare une omelette aux restes ; sur le plan de travail, un couteau, de l'ail et une goutte de sang.")
def _():
    o = set_kitchen() + fridge(820, 540)
    o += hero(470, 575, 1, expr="worried", pose="hold2", item="plate")
    o += g(prop("knife"), 250, 330, 1.2) + garlic(310, 330, 0.6) + g(prop("drop"), 640, 260, 1.4) + qmark(640, 200)
    return finish(o)


@scene("39", "Henri goûte l'omelette, les yeux fermés, un sourire béat ; le héros satisfait.")
def _():
    o = set_bedroom(lit=True)
    o += armchair_rear(600, 550) + henri(600, 550, 1, expr="blissful", legs="sit", pose="eat", item="fork") + armchair_front(600, 550)
    o += nightstand(780, 540) + g(prop("plate"), 780, 445)
    o += hero(270, 570, 0.95, expr="happy") + heart(700, 250, 0.7) + sparkle(520, 230)
    return finish(o)


@scene("40", "Le visage d'Henri gonfle, rouge et enflé ; le héros affolé compose le 15.")
def _():
    o = set_bedroom(lit=True)
    o += armchair_rear(620, 550) + henri(620, 550, 1, expr="swollen", legs="sit") + armchair_front(620, 550)
    o += hero(280, 570, 0.95, expr="scared", pose="phone", item="phone") + excl(700, 230) + excl(740, 250, 0.7)
    return finish(o)


@scene("41", "Les secours arrivent, gyrophares bleus et rouges ; un secouriste interroge le héros pendant qu'on prend Henri en charge.")
def _():
    o = set_bedroom(lit=True)
    o += glow(480, 175, 260, "#3a7bff", 0.45) + glow(380, 175, 160, "#ff3a3a", 0.35)
    o += armchair_rear(760, 550) + henri(760, 550, 0.9, expr="swollen", legs="sit") + armchair_front(760, 550)
    o += paramedic(500, 570, 1, flip=True)
    o += hero(250, 570, 0.95, expr="worried")
    return finish(o)


@scene("42", "Dans la cuisine, le secouriste range son matériel et explique : la femme de M. Morticia est morte il y a six ans. Le héros est figé.")
def _():
    o = set_kitchen()
    o += paramedic(640, 575, 1, flip=True)
    o += hero(330, 575, 1, expr="blank")
    o += g(prop("plate"), 140, 330, 0.9) + garlic(200, 330, 0.5) + garlic(230, 332, 0.45)
    return finish(o)


@scene("43", "Sur la table, une tasse de café fume encore à côté d'un petit mot élégant ; la silhouette fantomatique d'Yvonne s'efface.")
def _():
    o = set_kitchen()
    o += morticia(760, 560, 1, expr="smile", ghost=True, opacity=0.35)
    o += table(480, 570, 300, 120) + g(prop("cup"), 430, 445, 1.6) + g(prop("letter_typed"), 540, 440, 1, rot=-6)
    o += hero(220, 575, 1, expr="surprised")
    return finish(o)


@scene("44", "Fin : la tasse fumante, le petit mot d'Yvonne et son ombre fantomatique.")
def _():
    o = set_fin("#1e2a3a") + morticia(480, 520, 1.2, expr="smile", ghost=True, opacity=0.3)
    o += g(prop("cup"), 420, 480, 3) + g(prop("card"), 600, 480, 2, rot=8)
    return finish(o)


@scene("45", "Henri mâche une tranche de pain, puis s'immobilise, déçu ; le héros tient le plateau omelette et pain grillé.")
def _():
    o = set_bedroom(lit=True)
    o += armchair_rear(620, 550) + henri(620, 550, 1, expr="stern", legs="sit", pose="eat", item="bread") + armchair_front(620, 550)
    o += hero(280, 570, 0.95, expr="worried", pose="hold2", item="plate_bread")
    return finish(o)


@scene("46", "Henri se lève, menaçant : « Un pacte est un pacte » ; le héros recule jusqu'à la porte.")
def _():
    o = set_bedroom(lit=True) + darken(0.2)
    o += door(40, 540, 110, 250, "closed")
    o += henri(580, 570, 1.1, expr="angry", pose="menace", flip=True)
    o += hero(230, 570, 0.95, expr="scared", pose="scared")
    return finish(o)


@scene("47", "Le héros s'enfuit en courant de la maison des Morticia vers la fête, sans se retourner.")
def _():
    o = set_street()
    o += hero(470, 590, 0.8, expr="scared", pose="run", legs="run", flip=True) + motion(620, 410)
    return finish(o)


@scene("48", "Un an plus tard, chez lui, le héros goûte de l'ail confit : plus aucun goût, plus aucune odeur.")
def _():
    o = set_home("evening")
    o += hero(470, 545, 1, expr="blank", legs="sit", pose="hold", item="garlic")
    o += table(470, 560, 360, 80)
    o += cel(R(560, 440, 50, 40, 6), "#e9e0c0", "#bfb39c", 3, 3) + garlic(585, 450, 0.4)
    o += qmark(380, 230) + qmark(580, 230, 0.8)
    return finish(o)


@scene("49", "Le téléphone vibre : un message d'un numéro inconnu signé Henri. Un frisson parcourt le dos du héros.")
def _():
    o = set_home("night")
    o += hero(330, 570, 1, expr="scared")
    o += g(prop("phone_msg"), 640, 300, 2.2) + line("M560,180 l-16,-10 M560,200 l-20,0 M720,180 l16,-10 M720,200 l20,0", 4, "#ffd23f")
    return finish(o)


@scene("50", "Fin : une gousse d'ail barrée, l'odorat perdu à jamais.")
def _():
    o = set_fin() + garlic(480, 330, 4)
    o += line("M480,190 m-150,0 a150,150 0 1,0 300,0 a150,150 0 1,0 -300,0", 14, "#c4122e") + line("M375,85 L585,295", 14, "#c4122e")
    return finish(o)


@scene("51", "Un vieux cadre glisse de la table de chevet ; le héros ramasse la photo de mariage d'Yvonne et Henri.")
def _():
    o = set_bedroom()
    o += nightstand(640, 540) + armchair_back_view(470, 540, 1)
    o += hero(220, 570, 0.95, expr="surprised", pose="hold2", item="frame")
    o += g(prop("frame"), 830, 300, 2.4, rot=4) + glow(830, 300, 120, "#fff6c2", 0.3)
    return finish(o)


@scene("52", "Le héros, perplexe devant la date du cadre, quand BAM ! la porte claque derrière lui.")
def _():
    o = set_bedroom()
    o += door(40, 540, 110, 250, "closed")
    o += nightstand(640, 540) + armchair_back_view(470, 540, 1)
    o += hero(260, 570, 0.95, expr="worried", pose="think") + qmark(330, 200) + g(prop("frame"), 640, 430)
    o += burst(110, 110, 60, "BAM !")
    return finish(o)


@scene("53", "Le vieil homme se redresse dans son fauteuil, la voix rauque et agressive : « Qui va là ? »")
def _():
    o = set_bedroom()
    o += armchair_rear(620, 550) + henri(620, 550, 1, expr="angry", legs="sit") + armchair_front(620, 550)
    o += hero(250, 570, 0.95, expr="scared") + anger(700, 260)
    return finish(o)


@scene("54", "Le héros tire sur la poignée de la porte coincée ; derrière lui, une ombre se lève dans un silence absolu.")
def _():
    o = set_bedroom() + darken(0.2)
    o += door(120, 540, 120, 260, "closed")
    o += henri(600, 565, 1.1, expr="stern", opacity=0.55)
    o += hero(330, 570, 1, expr="scared", pose="reach", flip=True)
    return finish(o)


@scene("55", "Face au héros, un vieil homme presque transparent, triste et cadavérique, vêtu avec une élégance d'un autre temps.")
def _():
    o = set_bedroom() + darken(0.2)
    o += henri(600, 565, 1.1, expr="sad", ghost=True) + glow(600, 380, 180, "#9fdcf5", 0.25)
    o += hero(300, 570, 1, expr="worried")
    return finish(o)


@scene("56", "Le héros hésite entre montrer le cadre tombé et chercher un objet pour ouvrir la porte.")
def _():
    o = set_bedroom()
    o += door(40, 540, 110, 250, "closed") + henri(700, 565, 1, expr="sad", ghost=True)
    o += hero(400, 575, 1, expr="worried", pose="think") + qmark(330, 220) + qmark(480, 200, 0.8)
    o += g(prop("frame"), 230, 520, 1.2, rot=-20)
    return finish(o)


@scene("57", "Henri tient le cadre et effleure le visage d'Yvonne ; sa mine sévère laisse place à une profonde tristesse.")
def _():
    o = set_bedroom()
    o += henri(600, 565, 1.05, expr="sad", pose="hold2", item="frame")
    o += hero(300, 570, 0.95, expr="moved") + heart(690, 250, 0.6)
    return finish(o)


@scene("58", "Henri retourne s'asseoir dans son fauteuil et murmure : « Et je tiens toujours mes promesses. » Silence pesant.")
def _():
    o = set_bedroom()
    o += armchair_rear(620, 550) + henri(620, 550, 1, expr="stern", legs="sit") + armchair_front(620, 550)
    o += hero(270, 570, 0.95, expr="worried")
    return finish(o)


@scene("59", "Gêné par le silence, le héros réfléchit : parler de son grand amour, ou de l'échiquier posé sur une petite table ?")
def _():
    o = set_bedroom()
    o += armchair_rear(680, 550) + henri(680, 550, 1, expr="neutral", legs="sit") + armchair_front(680, 550)
    o += table(150, 540, 160, 100) + chessboard(150, 435, 0.7)
    o += hero(380, 570, 0.95, expr="neutral", pose="think")
    o += thought(400, 120, 200, 110, heart(350, 120, 0.9) + chess_piece(450, 145, 0.8, "knight", "#f6f2fa"), (390, 270))
    return finish(o)


@scene("60", "Le héros, assis sur le lit, raconte son grand amour ; Henri l'écoute avec un sourire sincère.")
def _():
    o = set_bedroom()
    o += hero(830, 520, 0.85, expr="happy", legs="sit")
    o += armchair_rear(420, 550) + henri(420, 550, 1, expr="smile", legs="sit") + armchair_front(420, 550)
    o += heart(760, 200, 0.8) + heart(840, 170, 0.5) + heart(890, 220, 0.6)
    return finish(o)


@scene("61", "Henri tend son alliance au héros ému : « certaines promesses sont faites pour durer ».")
def _():
    o = set_bedroom()
    o += henri(620, 570, 1, expr="smile", pose="offer", item="ring", flip=True)
    o += hero(320, 570, 1, expr="moved")
    o += glow(515, 420, 70, "#fff6a8", 0.6) + sparkle(540, 360, 0.8)
    return finish(o)


@scene("62", "De retour à la fête avec ses amis, le héros garde précieusement l'alliance dans sa poche.")
def _():
    o = set_party()
    o += ghost_friend(160, 530, 0.85) + person(780, 530, 0.85, hat="witch", skin=("#9fd17a", "#6fa84a"), top=("#4b2d63", "#2e1a40"))
    o += person(650, 530, 0.8, head="pumpkin", arms="down")
    o += hero(420, 570, 1, expr="moved", pose="pocket") + sparkle(460, 470, 0.8) + glow(446, 470, 40, "#fff6a8", 0.6)
    return finish(o)


@scene("63", "Après le mariage, au petit-déjeuner, le héros lit dans le journal l'avis de décès d'Henri Morticia.")
def _():
    o = set_home("day")
    o += frame_wall(150, 150, 120, 140, "couple") + heart(150, 60, 0.5)
    o += hero(470, 540, 1, expr="surprised", legs="sit", pose="hold2", item="newspaper")
    o += table(470, 560, 360, 80) + g(prop("cup"), 600, 474)
    return finish(o)


@scene("64", "Le héros serre l'alliance d'Henri dans sa main ; par la fenêtre, deux silhouettes fantomatiques enlacées dans le ciel.")
def _():
    o = set_home("night")
    o += clip(henri(690, 250, 0.45, expr="smile", ghost=True) + morticia(750, 250, 0.42, expr="smile", ghost=True), R(620, 70, 200, 180))
    o += hero(380, 570, 1.05, expr="moved", pose="hold", item="ring") + glow(416, 435, 50, "#fff6a8", 0.6)
    o += heart(720, 110, 0.4)
    return finish(o)


@scene("65", "Fin : deux alliances entrelacées et un cœur, un amour qui traverse le temps.")
def _():
    o = set_fin("#2a1a3a") + heart(480, 220, 3)
    o += g(prop("ring"), 430, 420, 4) + g(prop("ring"), 530, 420, 4)
    return finish(o)


@scene("66", "Les yeux d'Henri s'illuminent devant l'échiquier : « Cela vous dirait une petite partie ? »")
def _():
    o = set_bedroom(lit=True)
    o += armchair_rear(640, 550) + henri(640, 550, 1, expr="excited", legs="sit") + armchair_front(640, 550)
    o += table(330, 540, 180, 100) + chessboard(330, 435, 0.8)
    o += hero(130, 570, 0.85, expr="neutral") + sparkle(720, 220)
    return finish(o)


@scene("67", "Le héros s'installe face à Henri et avance son premier pion. La partie commence.")
def _():
    o = set_bedroom(lit=True)
    o += armchair_rear(720, 550) + henri(720, 550, 0.95, expr="smile", legs="sit") + armchair_front(720, 550)
    o += hero(240, 550, 0.95, expr="determined", legs="sit", pose="reach")
    o += table(480, 545, 220, 110) + chessboard(480, 430, 0.9)
    return finish(o)


@scene("68", "Partie endiablée : les pièces volent, Henri semble rajeunir à chaque coup, le cavalier surgit.")
def _():
    o = set_bedroom(lit=True) + glow(480, 300, 300, "#ffd23f", 0.2)
    o += armchair_rear(720, 550) + henri(720, 550, 0.95, expr="excited", legs="sit", young=True) + armchair_front(720, 550)
    o += hero(240, 550, 0.95, expr="surprised", legs="sit")
    o += table(480, 545, 220, 110) + chessboard(480, 430, 0.9, scatter=True)
    o += chess_piece(480, 260, 1.4, "knight", "#231d33") + sparkle(420, 220) + sparkle(560, 210, 0.8) + motion(560, 300, 0.6)
    return finish(o)


@scene("69", "CLAC ! La porte s'ouvre : Mme Morticia, contrariée, se tient sur le seuil ; le fauteuil d'Henri devient flou.")
def _():
    o = set_bedroom(lit=True)
    o += door(40, 540, 110, 250, "open", inside="#ffcf7a") + morticia(100, 545, 0.95, expr="annoyed", pose="cross")
    o += armchair_rear(740, 550) + henri(740, 550, 0.95, expr="smile", legs="sit", opacity=0.25) + armchair_front(740, 550)
    o += hero(380, 550, 0.95, expr="surprised", legs="sit")
    o += table(560, 545, 200, 110) + chessboard(560, 430, 0.8)
    o += burst(250, 100, 56, "CLAC !")
    return finish(o)


@scene("70", "Le fauteuil est vide, les pièces toujours sur l'échiquier ; le héros, déboussolé, face à Mme Morticia agacée.")
def _():
    o = set_bedroom(lit=True)
    o += armchair_rear(740, 550) + armchair_front(740, 550)
    o += table(560, 545, 200, 110) + chessboard(560, 430, 0.8)
    o += morticia(150, 555, 0.95, expr="annoyed", pose="cross")
    o += hero(370, 570, 0.95, expr="surprised") + qmark(450, 220) + qmark(740, 280, 1.2)
    return finish(o)


@scene("71", "Dehors, le héros se retourne une dernière fois : une silhouette se tient derrière la fenêtre de l'étage.")
def _():
    o = set_street(silhouette=True)
    o += hero(380, 590, 0.75, expr="scared", flip=True) + excl(440, 330, 0.8)
    o += glow(797, 288, 50, "#9fdcf5", 0.6)
    return finish(o)


@scene("72", "Le vieil homme derrière la fenêtre articule « Échec et mat » ; un éclair de lumière et la silhouette disparaît.")
def _():
    o = fill(R(0, 0, W, H), "#5b4f73") + "".join(line(f"M0,{y} L{W},{y}", 2, "#4a4060") for y in range(20, H, 34))
    o += window(280, 80, 400, 380, "flash", curtains=True)
    o += clip(henri(480, 640, 1.3, expr="stern", ghost=True), R(280, 80, 400, 380))
    o += glow(480, 270, 360, "#ffffff", 0.6)
    o += flat(P("M760,40 L700,180 L740,180 L690,320 L800,150 L760,150 L810,40 Z"), "#fff6a8", 4)
    o += chess_piece(150, 520, 1.6, "king", "#231d33")
    return finish(o)


@scene("73", "Fin : un cavalier noir sur l'échiquier, qui attend patiemment sa revanche.")
def _():
    o = set_fin() + chessboard(480, 560, 3) + chess_piece(480, 400, 3, "knight", "#231d33") + glow(480, 300, 120, "#9fdcf5", 0.3)
    return finish(o)


@scene("74", "CLIC : le héros allume la lumière ; la chambre apparaît, meubles anciens et dizaines de photographies.")
def _():
    o = set_bedroom(lit=True, photos=True)
    o += armchair_back_view(580, 545, 1)
    o += flat(R(250, 280, 24, 36, 3), "#f4f0f7", 3)
    o += hero(170, 570, 0.95, expr="surprised", pose="knock")
    o += burst(300, 210, 40, "CLIC !", size=28)
    return finish(o)


@scene("75", "Sur chaque photo, le même couple à travers les années ; le héros glisse un coupe-papier dans la porte quand Henri murmure.")
def _():
    o = set_bedroom(lit=True, photos=True)
    o += door(380, 540, 120, 260, "closed")
    o += hero(560, 570, 0.95, expr="worried", pose="reach", item="letter_opener", flip=True)
    o += armchair_rear(800, 550) + henri(800, 550, 0.9, expr="neutral", legs="sit") + armchair_front(800, 550)
    return finish(o)


@scene("76", "Dans le reflet de la vitre, Henri se tient debout derrière le héros ; pourtant il est assis dans son fauteuil, des lettres sur la table.")
def _():
    o = set_bedroom(lit=True, photos=True)
    o += clip(henri(500, 400, 0.6, expr="stern", ghost=True) + hero(450, 410, 0.55, expr="scared", opacity=0.5), R(380, 60, 200, 230))
    o += hero(470, 580, 1, expr="scared")
    o += armchair_rear(800, 550) + henri(800, 550, 0.9, expr="neutral", legs="sit") + armchair_front(800, 550)
    o += table(160, 540, 200, 100) + g(prop("letter_hand"), 130, 438, 1.1, rot=-6) + g(prop("letter_typed"), 200, 436, 1.1, rot=8)
    return finish(o)


@scene("77", "Sur la table, deux lettres : une adresse écrite à la main avec un timbre des USA, l'autre tapée à la machine.")
def _():
    o = set_bedroom(lit=True) + table(480, 600, 760, 200)
    o += g(prop("letter_hand"), 320, 330, 3.2, rot=-5) + g(prop("letter_typed"), 650, 330, 3.2, rot=5)
    o += qmark(480, 170, 1.3)
    return finish(o)


@scene("78", "Le héros lit à voix haute la lettre d'Élise envoyée de Los Angeles, pleine de soleil et d'Hollywood.")
def _():
    o = set_bedroom(lit=True, photos=True)
    o += hero(330, 570, 1, expr="neutral", pose="hold2", item="letter_hand")
    inner = (fill(E(640, 140, 26), "#ffd23f") + line("M560,190 Q570,140 600,120", 6, WOOD[0])
             + flat(P("M600,120 q-30,-10 -44,6 q20,-6 44,-6 q-10,-26 -36,-26 q26,10 36,26 q14,-24 40,-20 q-26,6 -40,20 Z"), "#6aa84f", 3)
             + sparkle(690, 110, 0.7) + sparkle(540, 120, 0.5))
    o += thought(620, 150, 220, 130, inner, (420, 270))
    o += armchair_rear(800, 550) + henri(800, 550, 0.9, expr="sad", legs="sit") + armchair_front(800, 550)
    return finish(o)


@scene("79", "La porte s'ouvre toute seule ; Minou se frotte contre les jambes d'Henri qui se penche pour le caresser, nostalgique.")
def _():
    o = set_bedroom(lit=True, photos=True)
    o += door(380, 540, 120, 260, "ajar")
    o += henri(640, 565, 1, expr="sad", pose="hold") + cat(560, 560, 0.9, flip=True)
    o += hero(220, 570, 0.9, expr="moved") + heart(560, 400, 0.5)
    return finish(o)


@scene("80", "Sur le perron, le héros caresse Minou une dernière fois avant de s'éloigner dans la nuit, avec le sentiment d'un petit moment de bonheur partagé.")
def _():
    o = set_street()
    o += cat(700, 482, 0.55) + heart(700, 400, 0.4)
    o += hero(520, 590, 0.85, expr="moved", flip=True)
    return finish(o)


@scene("81", "Fin : Minou et son médaillon doré sous la lune, qui retrouvera toujours le chemin de la fête.")
def _():
    o = set_fin() + moon(480, 200, 110) + cat(480, 560, 2.6)
    return finish(o)


@scene("82", "Le héros lit à voix haute la lettre du notaire, Maître Delorme, au sujet de la succession d'Henri ; il est perplexe.")
def _():
    o = set_bedroom(lit=True, photos=True)
    o += hero(380, 570, 1, expr="worried", pose="hold2", item="letter_typed") + qmark(470, 220)
    o += armchair_rear(760, 550) + henri(760, 550, 0.9, expr="neutral", legs="sit") + armchair_front(760, 550)
    return finish(o)


@scene("83", "Henri raconte calmement son « décès » de 1986 et son réveil chez lui quelques jours plus tard.")
def _():
    o = set_bedroom(lit=True, photos=True)
    o += armchair_rear(620, 550) + henri(620, 550, 1, expr="smile", legs="sit") + armchair_front(620, 550)
    o += hero(270, 570, 0.95, expr="surprised")
    return finish(o)


@scene("84", "La pendule sur la cheminée est arrêtée à 23 h 44 ; Henri à la fenêtre, son reflet presque imperceptible.")
def _():
    o = set_bedroom(lit=True)
    o += fireplace(220, 540, 0.9, fire=False) + clock(220, 300, 1.4)
    o += henri(480, 560, 1, expr="neutral")
    o += clip(henri(480, 360, 0.6, expr="neutral", opacity=0.2), R(380, 60, 200, 230))
    o += hero(780, 570, 0.9, expr="surprised")
    return finish(o)


@scene("85", "La porte s'entrouvre toute seule ; sur le seuil, le héros se retourne : Henri est déjà rassis dans son fauteuil.")
def _():
    o = set_bedroom(lit=True, photos=True)
    o += door(120, 540, 120, 260, "ajar")
    o += armchair_rear(640, 550) + henri(640, 550, 1, expr="smile", legs="sit", opacity=0.75) + armchair_front(640, 550)
    o += hero(250, 570, 0.95, expr="surprised", flip=True)
    return finish(o)


@scene("86", "Dans l'entrée, Mme Morticia tend son manteau au héros ; dans le miroir, un instant, le reflet d'Henri.")
def _():
    reflection = hero(150, 330, 0.5, expr="surprised") + morticia(205, 330, 0.48) + henri(180, 300, 0.45, expr="smile", ghost=True)
    o = set_hall(reflection)
    o += morticia(520, 560, 1, expr="smile", pose="hold2")
    o += cel(P("M482,428 L558,428 L552,474 L488,474 Z"), *CAPE, 3, 3) + fill(R(490, 462, 60, 8), RED[0])
    o += hero(720, 560, 0.95, expr="surprised", flip=True) + qmark(250, 80, 0.8)
    return finish(o)


@scene("87", "Fin : la pendule figée à 23 h 44.")
def _():
    o = set_fin("#1e1a33") + clock(480, 340, 3.6)
    return finish(o)


def main():
    story = json.loads((ROOT / "story.js").read_text(encoding="utf-8").split("=", 1)[1].strip().rstrip(";"))
    OUT_DIR.mkdir(exist_ok=True)
    prompts = {}
    for slide in story:
        pid = slide["id"]
        desc, fn = SCENES[pid]
        art.reset()
        body = fn()
        content = f"<title>{desc}</title><desc>{STYLE}</desc>" + body
        (OUT_DIR / f"page-{pid}.svg").write_text(svg(content), encoding="utf-8")
        prompts[pid] = f"{STYLE} Scène : {desc}"
    (OUT_DIR / "prompts.json").write_text(json.dumps(prompts, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(story)} images -> {OUT_DIR.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
