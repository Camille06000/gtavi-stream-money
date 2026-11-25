"""Outils Twitch sans compte.

irc_chat() : lecture seule et anonyme du chat via IRC (pseudo justinfan, sans mot de passe).
             Méthode non officielle mais très répandue ; rien n'est jamais envoyé dans le chat.
vod_chat() : non implémenté, voir la note en bas.

La liste des streams passe par l'API officielle Helix (voir streams.py). L'adaptation française a retiré
l'accès à l'API interne GQL de Twitch qu'utilisait l'original.
"""
import json, random, socket, ssl, sys, threading, time
from datetime import datetime, timezone

try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass


def started_ts(iso):
    try:
        return datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()
    except Exception:
        return None


def _parse_privmsg(line):
    """'@tags :user!user@user.tmi.twitch.tv PRIVMSG #chan :text' -> (user, text) or None"""
    tags = ""
    if line.startswith("@"):
        tags, _, line = line.partition(" ")
    if " PRIVMSG " not in line:
        return None
    prefix, _, rest = line.partition(" PRIVMSG ")
    user = prefix.lstrip(":").split("!")[0]
    for t in tags.lstrip("@").split(";"):
        if t.startswith("display-name=") and t[13:]:
            user = t[13:]
    _, _, text = rest.partition(" :")
    return user, text.strip()


def irc_chat(channel, out_path, stop_event=None, host="irc.chat.twitch.tv", port=6697):
    """Append {t, user, text} JSON lines to out_path until stop_event is set. Reconnects on drop.
    Uses TLS (6697); falls back to plain 6667 if TLS fails."""
    stop_event = stop_event or threading.Event()
    channel = channel.lower().lstrip("#")
    use_tls = True
    with open(out_path, "a", encoding="utf-8", buffering=1) as out:
        while not stop_event.is_set():
            sock = None
            try:
                raw = socket.create_connection((host, port if use_tls else 6667), timeout=15)
                sock = ssl.create_default_context().wrap_socket(raw, server_hostname=host) if use_tls else raw
                sock.settimeout(5)
                sock.sendall(f"NICK justinfan{random.randint(10000, 99999)}\r\n".encode())
                sock.sendall(f"JOIN #{channel}\r\n".encode())
                buf = b""
                while not stop_event.is_set():
                    try:
                        data = sock.recv(4096)
                    except socket.timeout:
                        continue
                    if not data:
                        break
                    buf += data
                    *lines, buf = buf.split(b"\r\n")
                    for ln in lines:
                        s = ln.decode("utf-8", "replace")
                        if s.startswith("PING"):
                            sock.sendall(("PONG" + s[4:] + "\r\n").encode())
                            continue
                        m = _parse_privmsg(s)
                        if m and m[1]:
                            out.write(json.dumps({"t": time.time(), "user": m[0], "text": m[1]}, ensure_ascii=False) + "\n")
            except (OSError, ssl.SSLError) as ex:
                if use_tls and not isinstance(ex, socket.timeout):
                    use_tls = False  # maybe TLS is blocked; try plain 6667 next
            finally:
                if sock:
                    try: sock.close()
                    except OSError: pass
            stop_event.wait(3)


def vod_chat(video_id):
    """Not implemented: VideoCommentsByOffsetOrCursor is only served through a persisted-query sha256 hash
    that cannot be verified offline here, and plain-text queries for it are rejected."""
    raise NotImplementedError("Twitch VOD chat needs a persisted-query hash; not supported")
