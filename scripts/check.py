"""Vérification d'un clip terminé avant publication.

usage : python check.py <clip.mp4> [--campaign campagnes.md] [--caption "texte de la légende"]
Lit clip_<n>.json (écrit par cut.py) à côté du clip s'il existe. Code de sortie 1 si une vérification échoue.
Lignes comprises dans campagnes.md (français ou anglais) :
  duree_min: 15 / duree_max: 60 / hashtags_obligatoires: #a #b / mention_obligatoire: @x
  (ou min_seconds / max_seconds / required_hashtags / required_mention)
"""
import argparse, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import ffprobe, load_json

BANNED = ["leak", "leaked build", "play early", "early access download", "free download", "crack", "piracy",
          "mod menu", "money glitch", "afk bot",
          # français
          "fuite", "version fuitée", "jouer en avance", "accès anticipé gratuit", "téléchargement gratuit",
          "telechargement gratuit", "piratage", "version craquée", "glitch d'argent", "argent infini", "bot afk"]


def parse_campaign(path):
    rules = {"min": 7.0, "max": 60.0, "tags": [], "mention": None}
    if not path or not Path(path).exists():
        return rules, False
    txt = Path(path).read_text(encoding="utf-8", errors="replace")
    m = re.search(r"(?:min_seconds|dur[ée]e_min):\s*(\d+(?:[.,]\d+)?)", txt, re.I)
    if m: rules["min"] = float(m.group(1).replace(",", "."))
    m = re.search(r"(?:max_seconds|dur[ée]e_max):\s*(\d+(?:[.,]\d+)?)", txt, re.I)
    if m: rules["max"] = float(m.group(1).replace(",", "."))
    m = re.search(r"(?:required_hashtags|hashtags_obligatoires):\s*(.+)", txt, re.I)
    if m: rules["tags"] = re.findall(r"#\w+", m.group(1))
    m = re.search(r"(?:required_mention|mention_obligatoire):\s*(@\w+)", txt, re.I)
    if m: rules["mention"] = m.group(1)
    return rules, True


def fps_of(s):
    try:
        a, b = s.split("/"); return float(a) / float(b)
    except Exception:
        return 0.0


def banned_in(text):
    low = text.lower()
    return [b for b in BANNED if b in low]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clip"); ap.add_argument("--campaign"); ap.add_argument("--caption", default="")
    a = ap.parse_args()
    clip = Path(a.clip)
    res = []  # (name, ok, detail)

    def add(name, ok, detail=""):
        res.append((name, ok, detail))

    if not clip.exists():
        sys.exit(f"ÉCHEC fichier introuvable : {clip}")
    side = clip.with_suffix(".json")
    meta = load_json(side) if side.exists() else {}
    rules, have_campaign = parse_campaign(a.campaign)
    p = ffprobe(clip)
    streams = p.get("streams", [])
    v = next((s for s in streams if s.get("codec_type") == "video"), None)
    au = next((s for s in streams if s.get("codec_type") == "audio"), None)
    dur = float(p.get("format", {}).get("duration", 0) or 0)

    add("résolution 1080x1920", bool(v) and (v.get("width"), v.get("height")) == (1080, 1920),
        f"{v.get('width')}x{v.get('height')}" if v else "pas de vidéo")
    f = fps_of(v.get("r_frame_rate", "0/1")) if v else 0
    add("environ 30 images/s", 29 <= f <= 31, f"{f:.2f}")
    add("piste audio présente", au is not None)
    add(f"durée {rules['min']:g}-{rules['max']:g} s" + ("" if have_campaign else " (par défaut)"),
        rules["min"] <= dur <= rules["max"], f"{dur:.1f} s")
    hook = meta.get("hook", "")
    hits = banned_in(hook + " " + a.caption)
    add("aucun terme interdit dans l'accroche ou la légende", not hits, ", ".join(hits))
    if rules["tags"]:
        miss = [t for t in rules["tags"] if t.lower() not in a.caption.lower()]
        add("hashtags obligatoires", not miss, ("manquants : " + " ".join(miss)) if miss else " ".join(rules["tags"]))
    if rules["mention"]:
        ok = rules["mention"].lower() in a.caption.lower()
        add("mention obligatoire", ok, rules["mention"])
    if not have_campaign:
        add("fichier de règles de campagne", True, "aucun fourni, valeurs par défaut (ce n'est PAS une vérification des règles)")

    for n, ok, d in res:
        print(f"{'OK   ' if ok else 'ÉCHEC'}  {n}" + (f"  [{d}]" if d else ""))
    bad = [r for r in res if not r[1]]
    print("RÉSULTAT : " + ("ÉCHEC" if bad else "OK"))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
