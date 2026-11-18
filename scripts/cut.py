"""Cut one candidate into a finished vertical clip.

1080x1920, 30 fps, word-by-word burned captions, hook box in the first seconds, credit line,
loudness normalised to -14 LUFS. Writes jobs/<id>/edits/clip_<n>.mp4 + .json (metadata for check.py).

usage: python cut.py jobs/<id> --pick 1 [--layout fill|blur|facecam] [--hook "TEXT"] [--credit "@creator"]
                     [--cam x:y:w:h] (facecam box as fractions of the source frame, default bottom-right 0.70:0.68:0.30:0.32)
"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import load_json, run, save_json, tool

W, H = 1080, 1920


def ts(t):
    t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def esc(s):
    return s.replace("\\", "").replace("{", "(").replace("}", ")").replace("\n", " ")


def build_ass(words, s0, e0, hook, credit, cap_y):
    hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Arial Black,92,&H00FFFFFF,&H0000E5FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,3,5,60,60,0,1
Style: Hook,Arial Black,68,&H00000000,&H00000000,&H00FFFFFF,&H00FFFFFF,-1,0,0,0,100,100,0,0,3,18,0,8,70,70,170,1
Style: Credit,Arial,40,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,-1,0,0,0,100,100,0,0,1,3,1,2,40,40,90,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    ws = [w for w in words if s0 <= w["s"] < e0 and w["w"]]
    # groups of up to 3 words, break on punctuation or pauses
    groups, cur = [], []
    for w in ws:
        if cur and (len(cur) == 3 or w["s"] - cur[-1]["e"] > 0.6 or cur[-1]["w"][-1:] in ".?!,"):
            groups.append(cur); cur = []
        cur.append(w)
    if cur:
        groups.append(cur)
    hook_end = 2.6 if hook else 0
    for gi, g in enumerate(groups):
        g_end = groups[gi + 1][0]["s"] if gi + 1 < len(groups) else g[-1]["e"] + 0.4
        g_end = min(g_end, g[-1]["e"] + 0.8)
        for k, w in enumerate(g):
            a = w["s"] - s0; b = (g[k + 1]["s"] - s0) if k + 1 < len(g) else g_end - s0
            if b <= a:
                continue
            parts = []
            for j, x in enumerate(g):
                t = esc(x["w"].upper())
                parts.append("{\\c&H0000E5FF&}" + t + "{\\c&H00FFFFFF&}" if j == k else t)
            pop = "{\\fscx112\\fscy112\\t(0,90,\\fscx100\\fscy100)}" if k == 0 else ""
            ev.append(f"Dialogue: 0,{ts(a)},{ts(b)},Cap,,0,0,0,,{{\\pos({W // 2},{cap_y})}}{pop}{' '.join(parts)}")
    if hook:
        ev.append(f"Dialogue: 1,{ts(0)},{ts(hook_end)},Hook,,0,0,0,,{{\\fad(0,180)\\fscx92\\fscy92\\t(0,120,\\fscx100\\fscy100)}}{esc(hook)}")
    if credit:
        ev.append(f"Dialogue: 1,{ts(0)},{ts(e0 - s0)},Credit,,0,0,0,,{esc('clip: ' + credit)}")
    return hdr + "\n".join(ev) + "\n"


CAP_Y = {"fill": 1380, "blur": 1460, "facecam": 1120}


def video_filter(layout, cam, ass):
    """Layout + burned-caption filter graph ending in [vo]. Reused by translate.py."""
    if layout == "fill":
        v = f"[0:v]scale=-2:{H},crop={W}:{H}[v]"
    elif layout == "blur":
        v = (f"[0:v]split[a][b];[a]scale=-2:{H},crop={W}:{H},boxblur=24:2,eq=brightness=-0.08[bg];"
             f"[b]scale={W}:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2-80[v]")
    else:
        x, y, w, h = map(float, cam.split(":"))
        v = (f"[0:v]split[a][b];[a]crop=iw*{w}:ih*{h}:iw*{x}:ih*{y},scale={W}:{int(H * 0.38)}:force_original_aspect_ratio=increase,"
             f"crop={W}:{int(H * 0.38)}[cam];[b]scale=-2:{H - int(H * 0.38)},crop={W}:{H - int(H * 0.38)}[game];[cam][game]vstack[v]")
    sub = str(ass).replace("\\", "/").replace(":", "\\:")
    return v + f";[v]fps=30,subtitles='{sub}'[vo]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("job"); ap.add_argument("--pick", type=int, default=1)
    ap.add_argument("--layout", choices=["fill", "blur", "facecam"], default="blur")
    ap.add_argument("--hook", default=""); ap.add_argument("--credit", default="")
    ap.add_argument("--cam", default="0.70:0.68:0.30:0.32")
    ap.add_argument("--start", type=float); ap.add_argument("--end", type=float)
    a = ap.parse_args()
    d = Path(a.job); c = load_json(d / "candidates.json")
    pick = next(x for x in c["candidates"] if x["n"] == a.pick)
    s0 = a.start if a.start is not None else pick["start"]; e0 = a.end if a.end is not None else pick["end"]
    words = load_json(d / "transcript.json")
    out = d / "edits"; out.mkdir(exist_ok=True)
    cap_y = CAP_Y[a.layout]
    ass = out / f"clip_{a.pick}.ass"
    ass.write_text(build_ass(words, s0, e0, a.hook, a.credit, cap_y), encoding="utf-8")
    v = video_filter(a.layout, a.cam, ass)
    mp4 = out / f"clip_{a.pick}.mp4"
    run([tool("ffmpeg"), "-y", "-v", "error", "-ss", f"{s0:.2f}", "-to", f"{e0:.2f}", "-i", c["source"],
         "-filter_complex", v, "-map", "[vo]", "-map", "0:a?", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
         "-ar", "48000", "-movflags", "+faststart", str(mp4)])
    info = c.get("info", {})
    save_json(out / f"clip_{a.pick}.json", {"file": str(mp4), "start": s0, "end": e0, "layout": a.layout, "hook": a.hook,
                                            "credit": a.credit, "source_url": info.get("webpage_url"), "source_title": info.get("title"),
                                            "source_channel": info.get("channel") or info.get("uploader")})
    print(mp4)


if __name__ == "__main__":
    main()
