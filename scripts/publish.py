"""Publication des clips via les API officielles : YouTube Data API v3, Instagram Graph API, TikTok Content Posting API.

usage : python publish.py auth youtube|instagram|tiktok     (une fois par plateforme ; la connexion se fait dans TON navigateur)
        python publish.py check                             (quelles plateformes sont prêtes)
        python publish.py post <clip.mp4> --title "..." [--description "..."] [--platforms youtube,instagram,tiktok]
                               [--max-per-day 4] [--test]
        python publish.py today

Réglages dans le fichier .env du dossier de la page (écrits par l'utilisateur, jamais collés dans le chat) :
  YOUTUBE_CLIENT_SECRET_FILE=jetons/youtube_client_secret.json   (client OAuth « Application de bureau » de Google Cloud)
  INSTAGRAM_ACCESS_TOKEN=...                                     (jeton longue durée généré dans le tableau de bord Meta)
  TIKTOK_CLIENT_KEY=...  TIKTOK_CLIENT_SECRET=...  TIKTOK_REDIRECT_URI=http://localhost:8765/callback/
Les jetons obtenus sont rangés dans jetons/ (dossier local, à ne jamais publier). Aucun jeton n'est affiché ni journalisé.
Sans réglages, ou avec --test, rien n'est envoyé : le script affiche ce qui partirait et le note en « test ».
Chaque publication est notée dans publications.csv, avec un plafond par plateforme et par jour.
"""
import argparse, base64, csv, hashlib, http.server, json, os, secrets, sys, threading, time, urllib.parse, webbrowser
from datetime import datetime
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

LOG = Path("publications.csv")
TOK = Path("jetons")
FIELDS = ["date", "heure", "mode", "plateforme", "fichier", "titre", "id", "lien", "statut"]
PLATFORMS = ("youtube", "instagram", "tiktok")


# ---------------------------------------------------------------- réglages, journal, plafond
def env():
    vals = {}
    p = Path(".env")
    if p.exists():
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                vals[k.strip()] = v.strip().strip('"').strip("'")
    return lambda k, d=None: os.environ.get(k) or vals.get(k) or d


def load_tok(name):
    p = TOK / f"{name}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def save_tok(name, data):
    TOK.mkdir(exist_ok=True)
    (TOK / f"{name}.json").write_text(json.dumps(data, indent=1), encoding="utf-8")


def log(row):
    new = not LOG.exists()
    with open(LOG, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, FIELDS)
        if new:
            w.writeheader()
        w.writerow({k: row.get(k, "") for k in FIELDS})


def today_counts():
    counts, day = {}, datetime.now().strftime("%Y-%m-%d")
    if LOG.exists():
        with open(LOG, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["date"] == day and r["mode"] == "réel" and r["statut"] in ("publié", "en ligne privée"):
                    counts[r["plateforme"]] = counts.get(r["plateforme"], 0) + 1
    return counts


def client():
    import requests
    try:
        import truststore
        truststore.inject_into_ssl()
    except Exception:
        pass
    return requests


# ---------------------------------------------------------------- connexion OAuth locale (navigateur de l'utilisateur)
def pkce(hex_digest=False):
    verifier = secrets.token_urlsafe(64)[:96]
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = digest.hex() if hex_digest else base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


def catch_code(auth_url, port, path="/"):
    """Ouvre la page de connexion dans le navigateur et attend le retour sur http://localhost:<port><path>."""
    box = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            box.update({k: v[0] for k, v in q.items()})
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers()
            self.wfile.write("<h2>Connexion reçue. Tu peux fermer cet onglet et revenir à Claude Code.</h2>".encode())

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", port), H)
    threading.Thread(target=srv.handle_request, daemon=True).start()
    print("Ouvre cette adresse si le navigateur ne s'ouvre pas tout seul, puis connecte-toi toi-même :\n" + auth_url)
    webbrowser.open(auth_url)
    t0 = time.time()
    while not box and time.time() - t0 < 300:
        time.sleep(.3)
    srv.server_close()
    if not box:
        sys.exit("Pas de réponse au bout de 5 minutes : relance la commande.")
    if "error" in box:
        sys.exit(f"Connexion refusée : {box.get('error')} {box.get('error_description', '')}")
    return box


def free_port():
    import socket
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


# ---------------------------------------------------------------- YouTube
YT_SCOPES = "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly"


def yt_client(get):
    f = Path(get("YOUTUBE_CLIENT_SECRET_FILE", "jetons/youtube_client_secret.json"))
    if not f.exists():
        return None
    d = json.loads(f.read_text(encoding="utf-8"))
    d = d.get("installed") or d.get("web") or {}
    return d.get("client_id"), d.get("client_secret")


def yt_auth(get):
    cl = yt_client(get)
    if not cl:
        sys.exit("Fichier client Google introuvable : télécharge le JSON du client OAuth « Application de bureau » "
                 "et range-le dans jetons/youtube_client_secret.json (voir docs/API-OFFICIELLES.md).")
    cid, csec = cl
    port, (ver, ch), state = free_port(), pkce(), secrets.token_urlsafe(16)
    redirect = f"http://127.0.0.1:{port}"
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": cid, "redirect_uri": redirect, "response_type": "code", "scope": YT_SCOPES,
        "access_type": "offline", "prompt": "consent", "code_challenge": ch, "code_challenge_method": "S256", "state": state})
    box = catch_code(url, port)
    if box.get("state") != state:
        sys.exit("Réponse de connexion inattendue (state différent) : relance la commande.")
    r = client().post("https://oauth2.googleapis.com/token", timeout=30, data={
        "code": box["code"], "client_id": cid, "client_secret": csec, "redirect_uri": redirect,
        "grant_type": "authorization_code", "code_verifier": ver})
    t = r.json()
    if "refresh_token" not in t:
        sys.exit(f"Google n'a pas donné de jeton de rafraîchissement : {t.get('error_description') or t.get('error') or r.status_code}")
    save_tok("youtube", {"refresh_token": t["refresh_token"]})
    print("YouTube connecté.")


def yt_access(get):
    cl, tok = yt_client(get), load_tok("youtube")
    if not cl or not tok:
        return None
    r = client().post("https://oauth2.googleapis.com/token", timeout=30, data={
        "client_id": cl[0], "client_secret": cl[1], "refresh_token": tok["refresh_token"], "grant_type": "refresh_token"})
    if r.status_code != 200:
        sys.exit("Jeton YouTube refusé : relance « publish.py auth youtube » (un projet Google en mode « Test » "
                 "fait expirer la connexion au bout de 7 jours, voir docs/API-OFFICIELLES.md).")
    return r.json()["access_token"]


def yt_check(get):
    at = yt_access(get)
    if not at:
        return "non configuré"
    r = client().get("https://www.googleapis.com/youtube/v3/channels", params={"part": "snippet", "mine": "true"},
                   headers={"Authorization": f"Bearer {at}"}, timeout=30)
    items = r.json().get("items") or []
    return f"prêt (chaîne : {items[0]['snippet']['title']})" if items else f"connecté, mais aucune chaîne trouvée (HTTP {r.status_code})"


def yt_post(get, clip, title, desc, privacy):
    at = yt_access(get)
    rq, size = client(), clip.stat().st_size
    meta = {"snippet": {"title": title[:100].replace("<", "").replace(">", ""), "description": desc[:4900].replace("<", "").replace(">", ""),
                        "categoryId": "20", "defaultLanguage": "fr", "tags": ["GTA 6", "GTA VI", "Shorts"]},
            "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}}
    r = rq.post("https://www.googleapis.com/upload/youtube/v3/videos", params={"uploadType": "resumable", "part": "snippet,status"},
                headers={"Authorization": f"Bearer {at}", "Content-Type": "application/json; charset=UTF-8",
                         "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)}, data=json.dumps(meta), timeout=60)
    if r.status_code != 200 or "Location" not in r.headers:
        raise RuntimeError(f"YouTube a refusé l'envoi (HTTP {r.status_code}) : {r.text[:300]}")
    with open(clip, "rb") as f:
        u = rq.put(r.headers["Location"], data=f, headers={"Content-Type": "video/mp4", "Content-Length": str(size)}, timeout=1800)
    if u.status_code not in (200, 201):
        raise RuntimeError(f"YouTube : envoi du fichier échoué (HTTP {u.status_code}) : {u.text[:300]}")
    v = u.json()
    got = (v.get("status") or {}).get("privacyStatus", privacy)
    return v["id"], f"https://youtube.com/shorts/{v['id']}", ("publié" if got == privacy else "en ligne privée")


# ---------------------------------------------------------------- Instagram (API Instagram avec connexion Instagram)
IG = "https://graph.instagram.com"


def ig_token(get):
    tok = load_tok("instagram")
    return (tok or {}).get("token") or get("INSTAGRAM_ACCESS_TOKEN")


def ig_auth(get):
    t = get("INSTAGRAM_ACCESS_TOKEN")
    if not t:
        sys.exit("Ajoute INSTAGRAM_ACCESS_TOKEN dans .env (jeton généré dans le tableau de bord Meta, voir docs/API-OFFICIELLES.md).")
    rq = client()
    r = rq.get(f"{IG}/refresh_access_token", params={"grant_type": "ig_refresh_token", "access_token": t}, timeout=30)
    if r.status_code == 200 and r.json().get("access_token"):
        t = r.json()["access_token"]
    me = rq.get(f"{IG}/me", params={"fields": "user_id,username", "access_token": t}, timeout=30).json()
    if "user_id" not in me:
        sys.exit(f"Jeton Instagram refusé : {(me.get('error') or {}).get('message', me)}")
    save_tok("instagram", {"token": t, "user_id": me["user_id"], "username": me.get("username"), "renouvele": time.strftime("%Y-%m-%d")})
    print(f"Instagram connecté : @{me.get('username')}")


def ig_check(get):
    t, tok = ig_token(get), load_tok("instagram") or {}
    if not t or not tok.get("user_id"):
        return "non configuré"
    me = client().get(f"{IG}/me", params={"fields": "username", "access_token": t}, timeout=30).json()
    return f"prêt (@{me['username']})" if "username" in me else "jeton refusé : relance « publish.py auth instagram »"


def ig_post(get, clip, caption):
    t, tok, rq = ig_token(get), load_tok("instagram") or {}, client()
    uid, size = tok.get("user_id"), clip.stat().st_size
    c = rq.post(f"{IG}/{uid}/media", params={"media_type": "REELS", "upload_type": "resumable", "caption": caption[:2200],
                                             "share_to_feed": "true", "access_token": t}, timeout=60).json()
    if "id" not in c or "uri" not in c:
        raise RuntimeError(f"Instagram : création du Reel refusée : {(c.get('error') or {}).get('message', c)}")
    with open(clip, "rb") as f:
        u = rq.post(c["uri"], data=f, headers={"Authorization": f"OAuth {t}", "offset": "0", "file_size": str(size)}, timeout=1800)
    if u.status_code != 200:
        raise RuntimeError(f"Instagram : envoi du fichier échoué (HTTP {u.status_code}) : {u.text[:300]}")
    for _ in range(60):  # traitement côté Instagram : jusqu'à 5 minutes
        s = rq.get(f"{IG}/{c['id']}", params={"fields": "status_code,status", "access_token": t}, timeout=30).json()
        if s.get("status_code") == "FINISHED":
            break
        if s.get("status_code") == "ERROR":
            raise RuntimeError(f"Instagram : traitement de la vidéo en erreur : {s.get('status')}")
        time.sleep(5)
    else:
        raise RuntimeError("Instagram : la vidéo n'a pas fini d'être traitée en 5 minutes")
    p = rq.post(f"{IG}/{uid}/media_publish", params={"creation_id": c["id"], "access_token": t}, timeout=60).json()
    if "id" not in p:
        raise RuntimeError(f"Instagram : publication refusée : {(p.get('error') or {}).get('message', p)}")
    link = rq.get(f"{IG}/{p['id']}", params={"fields": "permalink", "access_token": t}, timeout=30).json().get("permalink", "")
    return p["id"], link, "publié"


# ---------------------------------------------------------------- TikTok
TT = "https://open.tiktokapis.com/v2"


def tt_auth(get):
    key, sec, redirect = get("TIKTOK_CLIENT_KEY"), get("TIKTOK_CLIENT_SECRET"), get("TIKTOK_REDIRECT_URI", "http://localhost:8765/callback/")
    if not key or not sec:
        sys.exit("Ajoute TIKTOK_CLIENT_KEY et TIKTOK_CLIENT_SECRET dans .env (voir docs/API-OFFICIELLES.md).")
    pu = urllib.parse.urlparse(redirect)
    if pu.hostname not in ("localhost", "127.0.0.1") or not pu.port:
        sys.exit("TIKTOK_REDIRECT_URI doit être une adresse locale avec un port, ex. http://localhost:8765/callback/")
    (ver, ch), state = pkce(hex_digest=True), secrets.token_urlsafe(16)
    url = "https://www.tiktok.com/v2/auth/authorize/?" + urllib.parse.urlencode({
        "client_key": key, "scope": "user.info.basic,video.publish", "response_type": "code", "redirect_uri": redirect,
        "state": state, "code_challenge": ch, "code_challenge_method": "S256"})
    box = catch_code(url, pu.port, pu.path)
    if box.get("state") != state:
        sys.exit("Réponse de connexion inattendue (state différent) : relance la commande.")
    t = client().post(f"{TT}/oauth/token/", timeout=30, headers={"Content-Type": "application/x-www-form-urlencoded"}, data={
        "client_key": key, "client_secret": sec, "code": box["code"], "grant_type": "authorization_code",
        "redirect_uri": redirect, "code_verifier": ver}).json()
    if "refresh_token" not in t:
        sys.exit(f"TikTok n'a pas donné de jeton : {t.get('error_description') or t.get('error') or t}")
    save_tok("tiktok", {"refresh_token": t["refresh_token"]})
    print("TikTok connecté.")


def tt_access(get):
    tok, key, sec = load_tok("tiktok"), get("TIKTOK_CLIENT_KEY"), get("TIKTOK_CLIENT_SECRET")
    if not tok or not key:
        return None
    t = client().post(f"{TT}/oauth/token/", timeout=30, headers={"Content-Type": "application/x-www-form-urlencoded"}, data={
        "client_key": key, "client_secret": sec, "grant_type": "refresh_token", "refresh_token": tok["refresh_token"]}).json()
    if "access_token" not in t:
        sys.exit("Jeton TikTok refusé : relance « publish.py auth tiktok ».")
    if t.get("refresh_token"):
        save_tok("tiktok", {"refresh_token": t["refresh_token"]})
    return t["access_token"]


def tt_creator(at):
    r = client().post(f"{TT}/post/publish/creator_info/query/", headers={"Authorization": f"Bearer {at}",
                    "Content-Type": "application/json; charset=UTF-8"}, timeout=30).json()
    return r.get("data") or {}, r.get("error") or {}


def tt_check(get):
    at = tt_access(get)
    if not at:
        return "non configuré"
    d, e = tt_creator(at)
    if not d:
        return f"connecté, mais refus : {e.get('message', e)}"
    pub = "PUBLIC_TO_EVERYONE" in (d.get("privacy_level_options") or [])
    return f"prêt (@{d.get('creator_username')})" + ("" if pub else " : appli non auditée, publication en privé uniquement")


def tt_post(get, clip, caption):
    at, rq, size = tt_access(get), client(), clip.stat().st_size
    d, e = tt_creator(at)
    if not d:
        raise RuntimeError(f"TikTok : compte indisponible : {e.get('message', e)}")
    opts = d.get("privacy_level_options") or ["SELF_ONLY"]
    privacy = "PUBLIC_TO_EVERYONE" if "PUBLIC_TO_EVERYONE" in opts else "SELF_ONLY"
    if size > 64 * 1024 * 1024:
        raise RuntimeError("TikTok : clip de plus de 64 Mo, réduis-le avant de publier")
    body = {"post_info": {"title": caption[:2200], "privacy_level": privacy, "disable_duet": False,
                          "disable_comment": False, "disable_stitch": False},
            "source_info": {"source": "FILE_UPLOAD", "video_size": size, "chunk_size": size, "total_chunk_count": 1}}
    r = rq.post(f"{TT}/post/publish/video/init/", headers={"Authorization": f"Bearer {at}",
                "Content-Type": "application/json; charset=UTF-8"}, data=json.dumps(body), timeout=60).json()
    data = r.get("data") or {}
    if "upload_url" not in data:
        raise RuntimeError(f"TikTok : envoi refusé : {(r.get('error') or {}).get('message', r)}")
    with open(clip, "rb") as f:
        u = rq.put(data["upload_url"], data=f, timeout=1800, headers={
            "Content-Type": "video/mp4", "Content-Length": str(size), "Content-Range": f"bytes 0-{size - 1}/{size}"})
    if u.status_code not in (200, 201):
        raise RuntimeError(f"TikTok : envoi du fichier échoué (HTTP {u.status_code}) : {u.text[:300]}")
    return data.get("publish_id", ""), "", "publié" if privacy == "PUBLIC_TO_EVERYONE" else "en ligne privée"


# ---------------------------------------------------------------- commandes
def cmd_auth(a):
    get = env()
    {"youtube": yt_auth, "instagram": ig_auth, "tiktok": tt_auth}[a.platform](get)


def cmd_check(a):
    get = env()
    for name, fn in (("youtube", yt_check), ("instagram", ig_check), ("tiktok", tt_check)):
        try:
            print(f"{name:10} {fn(get)}")
        except SystemExit as e:
            print(f"{name:10} {e}")
        except Exception as e:
            print(f"{name:10} erreur : {e}")


def cmd_today(a):
    c = today_counts()
    print("Publications réelles aujourd'hui : " + (", ".join(f"{k} {v}" for k, v in sorted(c.items())) or "aucune"))


def ready(name, get):
    return {"youtube": lambda: bool(yt_client(get) and load_tok("youtube")),
            "instagram": lambda: bool(ig_token(get) and (load_tok("instagram") or {}).get("user_id")),
            "tiktok": lambda: bool(load_tok("tiktok") and get("TIKTOK_CLIENT_KEY"))}[name]()


def cmd_post(a):
    clip = Path(a.clip)
    if not clip.exists():
        sys.exit(f"Clip introuvable : {clip}")
    plats = [p.strip().lower() for p in a.platforms.split(",") if p.strip()]
    bad = [p for p in plats if p not in PLATFORMS]
    if bad:
        sys.exit(f"Plateformes non prises en charge : {', '.join(bad)} (vidéo : youtube, instagram, tiktok ; Reddit : jamais en automatique).")
    if not a.title.strip():
        sys.exit("Titre vide : chaque post a besoin d'une légende avec le crédit du créateur.")
    if "🎥" not in a.title + a.description:
        sys.exit("Pas de crédit dans la légende : ajoute « 🎥 @créateur » au titre ou à la description.")
    counts, get = today_counts(), env()
    caption = (a.title + ("\n\n" + a.description if a.description else "")).strip()
    errors = 0
    for p in plats:
        now = datetime.now()
        row = {"date": now.strftime("%Y-%m-%d"), "heure": now.strftime("%H:%M"), "plateforme": p, "fichier": str(clip), "titre": a.title[:200]}
        if counts.get(p, 0) >= a.max_per_day:
            print(f"{p:10} plafond du jour atteint ({a.max_per_day}) : rien n'est envoyé")
            continue
        if a.test or not ready(p, get):
            why = "--test" if a.test else "pas encore connecté (publish.py auth " + p + ")"
            print(f"{p:10} MODE TEST ({why}) : rien n'est publié | {a.title}")
            log({**row, "mode": "test", "statut": "test"})
            continue
        try:
            if p == "youtube":
                vid, link, st = yt_post(get, clip, a.title, a.description, a.youtube_privacy)
            elif p == "instagram":
                vid, link, st = ig_post(get, clip, caption)
            else:
                vid, link, st = tt_post(get, clip, caption)
            log({**row, "mode": "réel", "id": vid, "lien": link, "statut": st})
            print(f"{p:10} {st} {link}")
        except SystemExit as e:
            errors += 1; log({**row, "mode": "réel", "statut": "erreur"}); print(f"{p:10} erreur : {e}")
        except Exception as e:
            errors += 1; log({**row, "mode": "réel", "statut": "erreur"}); print(f"{p:10} erreur : {e}")
    if errors:
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("auth"); s.add_argument("platform", choices=PLATFORMS); s.set_defaults(f=cmd_auth)
    sub.add_parser("check").set_defaults(f=cmd_check)
    sub.add_parser("today").set_defaults(f=cmd_today)
    s = sub.add_parser("post"); s.add_argument("clip")
    s.add_argument("--title", required=True); s.add_argument("--description", default="")
    s.add_argument("--platforms", default="youtube,instagram,tiktok")
    s.add_argument("--youtube-privacy", choices=["public", "unlisted", "private"], default="public")
    s.add_argument("--max-per-day", type=int, default=4)
    s.add_argument("--test", action="store_true", help="n'envoie rien, affiche seulement")
    s.set_defaults(f=cmd_post)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
