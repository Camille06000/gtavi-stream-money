"""Streams en direct sur un sujet, classés par nombre de spectateurs.

usage : python streams.py [--query "gta 6"] [--limit 20] [--lang fr] [--out streams.md]

- YouTube : toujours, sans clé.
- Twitch : API officielle Helix. Il faut une application Twitch gratuite (https://dev.twitch.tv/console)
  et TWITCH_CLIENT_ID + TWITCH_CLIENT_SECRET dans les variables d'environnement ou dans un fichier .env
  du dossier courant. Sans clés, Twitch est ignoré (rien n'est inventé).
- --lang fr : ne garde que les streams Twitch en français (filtre natif de Helix). YouTube n'a pas ce filtre :
  ajoute "fr" à --query si besoin.
Les nombres de spectateurs sont exactement ceux renvoyés par les plateformes au moment de l'exécution.
"""
import argparse, json, os, sys, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus
sys.path.insert(0, str(Path(__file__).parent))
from common import ytdlp_json, ytdlp_base, run

try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

TWITCH_GAME = "Grand Theft Auto VI"


def fmt_dur(sec):
    if not sec or sec < 0:
        return ""
    sec = int(sec)
    return f"{sec // 3600}h{sec % 3600 // 60:02d}"


def youtube(query, limit):
    url = f"https://www.youtube.com/results?search_query={quote_plus(query)}&sp=EgJAAQ%253D%253D"
    r = run(ytdlp_base() + ["--flat-playlist", "-J", "--playlist-end", str(limit), url], capture=True, check=False)
    if r.returncode != 0 or not r.stdout.strip():
        print(f"recherche YouTube échouée : {(r.stderr or '')[-300:]}", file=sys.stderr)
        return []
    ids = []
    for e in json.loads(r.stdout).get("entries") or []:
        if e and e.get("id"):
            ids.append(e.get("url") or f"https://www.youtube.com/watch?v={e['id']}")

    def one(u):
        try:
            return ytdlp_json(u)
        except BaseException:  # run() appelle sys.exit en cas d'échec
            return None

    with ThreadPoolExecutor(max_workers=8) as ex:
        infos = list(ex.map(one, ids))
    now = time.time(); out = []
    for i in infos:
        if not i or not i.get("is_live"):
            continue
        start = i.get("release_timestamp") or i.get("timestamp")
        out.append({"platform": "YouTube", "channel": i.get("channel") or i.get("uploader") or "",
                    "title": i.get("title") or "", "url": i.get("webpage_url") or "",
                    "viewers": i.get("concurrent_view_count"), "live_for": fmt_dur(now - start) if start else ""})
    return out


def read_env(path=".env"):
    """Variables d'environnement d'abord, puis un fichier .env simple (CLE=valeur) dans le dossier courant."""
    vals = {}
    p = Path(path)
    if p.exists():
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            vals[k.strip()] = v.strip().strip('"').strip("'")
    get = lambda k: os.environ.get(k) or vals.get(k)
    return get("TWITCH_CLIENT_ID"), get("TWITCH_CLIENT_SECRET"), get("TWITCH_TOKEN")


def twitch(limit, lang=None):
    """None = Twitch ignoré (pas de clés). Liste (éventuellement vide) sinon."""
    cid, secret, tok = read_env()
    if not cid or not (secret or tok):
        print("Twitch ignoré : ajoute TWITCH_CLIENT_ID et TWITCH_CLIENT_SECRET dans le fichier .env de la page "
              "(application gratuite sur https://dev.twitch.tv/console).", file=sys.stderr)
        return None
    import requests
    try:
        if not tok:
            r = requests.post("https://id.twitch.tv/oauth2/token", timeout=15,
                              data={"client_id": cid, "client_secret": secret, "grant_type": "client_credentials"})
            r.raise_for_status()
            tok = r.json()["access_token"]  # gardé en mémoire uniquement, jamais écrit sur le disque
        h = {"Client-Id": cid, "Authorization": f"Bearer {tok}"}
        g = requests.get("https://api.twitch.tv/helix/games", params={"name": TWITCH_GAME}, headers=h, timeout=15)
        g.raise_for_status()
        data = g.json().get("data") or []
        if not data:
            print(f"Twitch : catégorie « {TWITCH_GAME} » introuvable.", file=sys.stderr)
            return []
        params = {"game_id": data[0]["id"], "first": 100}
        if lang:
            params["language"] = lang
        s = requests.get("https://api.twitch.tv/helix/streams", params=params, headers=h, timeout=15)
        s.raise_for_status()
    except Exception as e:
        print(f"Twitch en échec : {e}", file=sys.stderr)
        return []
    now = time.time(); out = []
    for x in s.json().get("data", []):
        try:
            st = datetime.strptime(x["started_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()
        except Exception:
            st = None
        out.append({"platform": "Twitch", "channel": x.get("user_name", ""), "title": x.get("title", ""),
                    "url": f"https://twitch.tv/{x.get('user_login', '')}", "viewers": x.get("viewer_count"),
                    "live_for": fmt_dur(now - st) if st else ""})
    return sorted(out, key=lambda r: r["viewers"] or -1, reverse=True)[:limit]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", default="gta 6"); ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--lang", help="code langue pour Twitch, ex. fr")
    ap.add_argument("--out", default="streams.md")
    a = ap.parse_args()
    sections = [("YouTube", youtube(a.query, a.limit))]
    t = twitch(a.limit, a.lang)
    if t is not None:
        sections.append(("Twitch" + (f" ({a.lang})" if a.lang else ""), t))
    stamp = time.strftime("%Y-%m-%d %H:%M")
    md = [f"# Streams en direct : {a.query}", f"Vérifié le {stamp}. Spectateurs tels que renvoyés à cet instant.", ""]
    if t is None:
        md += ["_Twitch ignoré : pas de clés dans .env (voir le skill `installation`)._", ""]
    for name, rows in sections:
        rows = sorted(rows, key=lambda r: r["viewers"] or -1, reverse=True)
        md += [f"## {name}", ""]
        if not rows:
            md += ["Aucun stream en direct trouvé.", ""]
            continue
        md += ["| # | Chaîne | Titre | Spectateurs | En direct depuis | Lien |", "|---|---|---|---|---|---|"]
        for n, r in enumerate(rows, 1):
            v = "" if r["viewers"] is None else r["viewers"]
            md.append(f"| {n} | {r['channel']} | {r['title'].replace('|', '/')} | {v} | {r['live_for']} | {r['url']} |")
            print(f"{name[:8]:8} {str(v):>7}  {r['channel'][:24]:24} {r['title'][:50]:50} {r['url']}")
        md.append("")
    Path(a.out).write_text("\n".join(md), encoding="utf-8")
    print(f"écrit : {a.out}")


if __name__ == "__main__":
    main()
