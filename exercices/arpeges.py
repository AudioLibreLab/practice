"""Fiche : arpèges à 4 sons en position (Δ7, 7, m7, m7♭5, °7), en Do, basse ou guitare.

Deux groupes : fondamentale sur la corde de Mi grave (case 8) et sur la corde de La (case 3).
Par groupe : fondamentale à gauche (doigt 1 ou 2) et fondamentale à droite (doigt 4 ou 3),
en prenant le doigté qui demande le moins d'extensions (à égalité : doigt 2 si tierce majeure,
1 si mineure ; doigt 4 à droite).
Une case par doigt ; on joue toutes les notes de l'arpège de la plus grave à la plus aiguë
(cycle 1-3-5-7-1-...). Une note qui tombe dans le trou entre deux cordes (case p+4) est une
extension ; la même note se trouve aussi sur la corde suivante, case p-1 (notée entre parenthèses).

Lisible en noir et blanc : chaque degré a une forme et un niveau de gris distincts.
Usage : python3 arpeges.py basse|guitare <sortie.pdf>
        python3 arpeges.py basse|guitare --check   (recense tous les doigtés possibles)
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle

INSTRUMENTS = {
    # (nom affiché, [(étiquette, MIDI à vide)] de la plus grave à la plus aiguë)
    "basse": ("basse", [("E", 28), ("A", 33), ("D", 38), ("G", 43)]),
    "guitare": ("guitare", [("E", 40), ("A", 45), ("D", 50), ("G", 55), ("B", 59), ("e", 64)]),
}
ROOT_PC = 0  # Do

STYLE = {
    "1": dict(marker="o", face="#000000", text="white"),
    "3": dict(marker="o", face="#2e86c1", text="white"),
    "5": dict(marker="o", face="#f7dc6f", text="black"),
    "7": dict(marker="s", face="#ffffff", text="black"),
}

CHORDS = [
    ("CΔ7", "majeur 7", [("1", 0), ("3", 4), ("5", 7), ("7", 11)], "C  E  G  B"),
    ("C7", "7e de dominante", [("1", 0), ("3", 4), ("5", 7), ("♭7", 10)], "C  E  G  B♭"),
    ("Cm7", "mineur 7", [("1", 0), ("♭3", 3), ("5", 7), ("♭7", 10)], "C  E♭  G  B♭"),
    ("Cm7♭5", "demi-diminué (ø)", [("1", 0), ("♭3", 3), ("♭5", 6), ("♭7", 10)], "C  E♭  G♭  B♭"),
    ("C°7", "diminué 7", [("1", 0), ("♭3", 3), ("♭5", 6), ("♭♭7", 9)], "C  E♭  G♭  B♭♭ (= A)"),
]

GROUPS = [(0, 8, "Groupe 1 : fondamentale sur la corde de Mi grave (case 8)"),
          (1, 3, "Groupe 2 : fondamentale sur la corde de La (case 3)")]


class Inst:
    def __init__(self, key):
        self.name, strings = INSTRUMENTS[key]
        self.labels = [s for s, _ in strings]
        self.midi = [m for _, m in strings]
        self.n = len(strings)

    def gap(self, i):
        """Intervalle (demi-tons) entre la corde i et la suivante."""
        return self.midi[i + 1] - self.midi[i]


def degree_of_pitch(midi, degrees):
    semis = (midi - ROOT_PC) % 12
    for d, s in degrees:
        if s == semis:
            return d
    return None


def func(d):
    return d[-1]


def position_notes(inst, p, degrees):
    """Notes de l'arpège pour la position p (doigt 1 sur la case p, cases p..p+3).

    Entre deux cordes à la quarte, les cases p..p+3 laissent un trou d'un demi-ton (case p+4).
    Une note qui y tombe est prise en extension (case p+4). Entre Sol et Si (tierce majeure,
    guitare) il n'y a pas de trou. Renvoie une liste (corde, case, degré, extension) triée par hauteur.
    """
    notes = []
    for i in range(inst.n):
        frets = list(range(p, p + 4))
        if i < inst.n - 1 and inst.gap(i) == 5:
            frets.append(p + 4)
        for f in frets:
            if f < 0:
                continue
            d = degree_of_pitch(inst.midi[i] + f, degrees)
            if d:
                notes.append((i, f, d, f == p + 4))
    notes.sort(key=lambda n: inst.midi[n[0]] + n[1])
    return notes


def n_ext(inst, p, degrees):
    return sum(1 for n in position_notes(inst, p, degrees) if n[3])


def left_position(inst, root_fret, degrees):
    """Fondamentale à gauche : doigt 1 ou 2, le moins d'extensions ; à égalité doigt 2 si la
    tierce est majeure, doigt 1 si elle est mineure."""
    pref = 2 if dict((func(d), s) for d, s in degrees)["3"] == 4 else 1
    cands = [(n_ext(inst, root_fret - (f - 1), degrees), f != pref, f, root_fret - (f - 1)) for f in (1, 2)]
    _, _, finger, p = min(cands)
    return finger, p


def right_position(inst, root_fret, degrees):
    """Fondamentale à droite : doigt 4 ou 3, le moins d'extensions ; à égalité le doigt 4."""
    cands = [(n_ext(inst, root_fret - (f - 1), degrees), -f, f, root_fret - (f - 1)) for f in (4, 3)]
    _, _, finger, p = min(cands)
    return finger, p


# ---------------------------------------------------------------- dessin

def draw_style_note(ax, x, y, d, ms):
    st = STYLE[func(d)]
    ax.plot(x, y, st["marker"], ms=ms if st["marker"] == "o" else ms - 2,
            mfc=st["face"], mec="black", mew=1.2, zorder=3)
    ax.text(x, y, d, ha="center", va="center", fontsize=(6.5 if len(d) > 2 else 7.5) * ms / 15,
            color=st["text"], weight="bold", zorder=4)


def draw_frame(ax, inst, lo, hi, fs=7):
    top = inst.n - 1
    for i in range(inst.n):
        ax.plot([lo - 0.5, hi + 0.5], [i, i], color="#444", lw=0.6 + 0.35 * (top - i), zorder=1)
    for f in range(max(lo, 1), hi + 1):
        ax.plot([f + 0.5, f + 0.5], [0, top], color="#888", lw=0.9, zorder=1)
        ax.text(f, -0.8, str(f), ha="center", va="center", fontsize=fs, color="#555")
    if lo <= 0:
        ax.plot([0.5, 0.5], [0, top], color="#000", lw=4, zorder=1)
    else:
        ax.plot([lo - 0.5, lo - 0.5], [0, top], color="#888", lw=0.9, zorder=1)
    for i, s in enumerate(inst.labels):
        ax.text(lo - 1.0, i, s, ha="center", va="center", fontsize=8.5, weight="bold")


def draw_position(ax, inst, p, root_finger, degrees, side):
    lo, hi = max(p - 1, 0), p + 4
    top = inst.n - 1
    ms = 15 if inst.n == 4 else 12
    draw_frame(ax, inst, lo, hi)
    x0 = p - 0.5 if p >= 1 else -0.5
    ax.add_patch(Rectangle((x0, -0.35), (p + 3.5) - x0, top + 0.7, color="#ececec", zorder=0))
    notes = position_notes(inst, p, degrees)
    for k, (i, f, d, ext) in enumerate(notes):
        draw_style_note(ax, f, i, d, ms)
        ax.text(f + 0.38, i + 0.38, str(k + 1), ha="center", va="center", fontsize=6.5, zorder=5)
        if ext and p >= 1:
            alt = f - inst.gap(i)  # même note sur la corde suivante
            ax.plot(alt, i + 1, "o", ms=ms, mfc="white", mec="#777", mew=1, zorder=3)
            ax.text(alt, i + 1, f"({d})", ha="center", va="center", fontsize=5.5, zorder=4)
    e = sum(1 for n in notes if n[3])
    cycle = "-".join(func(n[2]) for n in notes)
    ext_txt = "aucune extension" if e == 0 else f"{e} extension{'s' if e > 1 else ''}"
    head = (f"doigt {root_finger} sur la fondamentale · doigt 1 case {p}" if p >= 1
            else f"doigt {root_finger} sur la fondamentale · cordes à vide = doigt 1")
    ax.set_title(f"Fondamentale à {side} — {head}\n{ext_txt} · ordre : {cycle}", fontsize=8.3, loc="left")
    ax.set_xlim(lo - 1.4, hi + 0.7)
    ax.set_ylim(-1.2, top + 0.6)
    ax.axis("off")


def draw_full_neck(ax, inst, degrees, last=20):
    top = inst.n - 1
    draw_frame(ax, inst, 0, last)
    for f in (3, 5, 7, 9, 15, 17, 19):
        ax.plot(f, top / 2, "o", color="#e5e5e5", ms=6, zorder=0)
    ax.plot([12, 12], [top / 2 - 1, top / 2 + 1], "o", color="#e5e5e5", ms=6, ls="none", zorder=0)
    for i in range(inst.n):
        for f in range(0, last + 1):
            d = degree_of_pitch(inst.midi[i] + f, degrees)
            if d:
                draw_style_note(ax, f, i, d, 13 if inst.n == 4 else 10)
    ax.set_xlim(-1.4, last + 0.7)
    ax.set_ylim(-1.2, top + 0.6)
    ax.set_title(f"Repère : toutes les notes de l'arpège sur le manche (cases 0 à {last})", fontsize=9, loc="left")
    ax.axis("off")


def page(pdf, inst, name, desc, degrees, spelled):
    fig = plt.figure(figsize=(11.69, 8.27))  # A4 paysage
    fig.suptitle(f"{name} — {desc}     ({spelled})     · {inst.name}", fontsize=15, weight="bold",
                 x=0.04, ha="left", y=0.975)
    six = inst.n == 6
    draw_full_neck(fig.add_axes([0.04, 0.765 if six else 0.775, 0.94, 0.155 if six else 0.135]), inst, degrees)

    w, h = 0.44, (0.205 if six else 0.19)
    for g, (_, root_fret, gtitle) in enumerate(GROUPS):
        y = (0.455 if six else 0.47) if g == 0 else (0.15 if six else 0.17)
        fig.text(0.04, y + h + 0.065, gtitle, fontsize=11, weight="bold")
        f, p = left_position(inst, root_fret, degrees)
        draw_position(fig.add_axes([0.04, y, w, h]), inst, p, f, degrees, "gauche")
        f, p = right_position(inst, root_fret, degrees)
        draw_position(fig.add_axes([0.53, y, w, h]), inst, p, f, degrees, "droite")

    fig.text(0.04, 0.105 if six else 0.115,
             "Fondamentale à gauche : doigt 1 ou 2 ; à droite : doigt 4 ou 3 (le moins d'extensions ; à égalité, doigt 2 si tierce majeure, 1 si mineure)."
             "\nZone grise = une case par doigt, la main ne bouge pas. Note hors de la zone = extension d'une case (doigt 4 qui s'étire).\n"
             "Entre parenthèses : la même note "
             "sur la corde suivante (doigt 1 qui recule d'une case). Choisir l'une ou l'autre.\n"
             "Jouer toutes les notes dans l'ordre des petits chiffres, de la plus grave à la plus aiguë puis retour : "
             "le cycle 1-3-5-7 ne s'interrompt jamais.\n"
             "En chantant les degrés, métronome sur 2 et 4. Formes mobiles : déplacer pour changer de tonalité. "
             "Doigtés à vérifier à l'instrument.\n"
             "Légende (lisible en noir et blanc) : fondamentale = rond noir · tierce = rond gris foncé · "
             "quinte = rond gris clair · septième = carré blanc.",
             fontsize=8.0, va="top")
    pdf.savefig(fig)
    plt.close(fig)


def check(inst):
    """Recense, pour chaque accord et chaque groupe, les 4 doigtés possibles (fondamentale sous
    le doigt 1 à 4) avec leur nombre d'extensions ; * = doigté présent sur la fiche."""
    for name, _, degrees, _ in CHORDS:
        for s, r, _ in GROUPS:
            shown = {left_position(inst, r, degrees), right_position(inst, r, degrees)}
            row = []
            for f in (1, 2, 3, 4):
                p = r - (f - 1)
                row.append(f"doigt {f} : {n_ext(inst, p, degrees)} ext{'*' if (f, p) in shown else ' '}")
            print(f"{name:6} corde {inst.labels[s]}   " + "   ".join(row))


def main():
    inst = Inst(sys.argv[1])
    if sys.argv[2] == "--check":
        check(inst)
        return
    with PdfPages(sys.argv[2]) as pdf:
        for name, desc, degrees, spelled in CHORDS:
            page(pdf, inst, name, desc, degrees, spelled)


if __name__ == "__main__":
    main()
