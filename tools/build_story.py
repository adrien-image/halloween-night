"""Construit story.js à partir de story/Halloween_version_2.md.

Le texte de chaque page est repris tel quel : seules les lignes de structure
(marqueurs « PAGE », séparateurs « --- », titres « SI CHOIX … ») sont retirées,
et les blocs « CHOIX … » deviennent des boutons de choix.

Usage : python3 tools/build_story.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "story" / "Halloween_version_2.md"
OUT = ROOT / "story.js"

PAGE_RE = re.compile(r"^\*\*PAGE (\d+)\*\*\s*$")
SEPARATOR_RE = re.compile(r"^-{3,}\s*$")
IF_CHOICE_RE = re.compile(r"^(#+\s*)?\**\s*si choix", re.IGNORECASE)
CHOICE_RE = re.compile(r"^(#+\s*)?\**\s*(CHOIX\s+([AB][\d.]*))\s*(:?)\s*\**\s*(:?)\s*$", re.IGNORECASE)

# Où mène chaque choix (première page de sa conséquence).
TARGETS = {
    "A": "13", "B": "50",
    "A.1": "20", "A.2": "34",
    "A.1.1": "24", "A.1.2": "28",
    "A.2.1": "38", "A.2.2": "44",
    "B.1": "56", "B.2": "73",
    "B.1.1": "59", "B.1.2": "65",
    "B.2.1": "77", "B.2.2": "81",
}


def paragraphs(lines):
    """Regroupe les lignes en paragraphes (séparés par des lignes vides)."""
    out, cur = [], []
    for line in lines:
        if line.strip() == "":
            if cur:
                out.append("\n".join(cur))
                cur = []
        else:
            cur.append(line.rstrip())
    if cur:
        out.append("\n".join(cur))
    return out


def main():
    lines = SRC.read_text(encoding="utf-8").splitlines()

    # Découpage en pages, dans l'ordre du fichier.
    pages, cur = [], None
    for line in lines:
        m = PAGE_RE.match(line.strip())
        if m:
            num = m.group(1)
            pid = num
            while any(p["id"] == pid for p in pages):  # « PAGE 15 » apparaît deux fois
                pid += "b"
            cur = {"id": pid, "lines": []}
            pages.append(cur)
        elif cur is not None:
            if SEPARATOR_RE.match(line.strip()) or IF_CHOICE_RE.match(line.strip()):
                continue
            cur["lines"].append(line)

    slides = []
    for i, page in enumerate(pages):
        intro, choices, current = [], [], None
        for line in page["lines"]:
            m = CHOICE_RE.match(line.strip())
            if m:
                key = m.group(3).upper()
                label = m.group(2) + (" :" if (m.group(4) or m.group(5)) else "")
                current = {"label": label, "lines": [], "target": TARGETS[key]}
                choices.append(current)
            elif current is not None:
                if line.strip() == "OU":
                    continue  # affiché entre les boutons
                current["lines"].append(line)
            else:
                intro.append(line)

        slide = {"id": page["id"], "text": paragraphs(intro)}
        if choices:
            slide["choices"] = [
                {"label": c["label"], "text": paragraphs(c["lines"]), "target": c["target"]}
                for c in choices
            ]
        elif slide["text"] == ["**FIN !**"]:
            slide["end"] = True
        else:
            slide["next"] = pages[i + 1]["id"]
        slides.append(slide)

    OUT.write_text(
        "// Généré par tools/build_story.py à partir de story/Halloween_version_2.md\n"
        "window.STORY = " + json.dumps(slides, ensure_ascii=False, indent=1) + ";\n",
        encoding="utf-8",
    )
    print(f"{len(slides)} slides -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
