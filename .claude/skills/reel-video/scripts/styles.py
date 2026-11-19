"""İki stil ailesinin ortak ön ayarları. build_ae_jsx.py ve preview_ffmpeg.py ikisi de buradan okur.

earn = earn.edits tarzı: karışık medya belgesel (AI görsel + masa üstü obje + kalın kinetik başlık,
        hap altyazı, blur/whip geçişler, kırmızı-sarı vurgu, sonda CTA).
hex  = hex_creatives tarzı: vintage arşiv / gravür (sepya veya siyah-beyaz AI gravür-tablo görselleri,
        yavaş itme + parallax, ışık sızması, ortada tek kelime italik serif altyazı).
"""


def hexrgb(h):
    h = h.lstrip("#")
    return [round(int(h[i:i + 2], 16) / 255.0, 4) for i in (0, 2, 4)]


STYLES = {
    "earn": {
        "colors": {
            "white": "#FFFFFF", "yellow": "#FFD21F", "red": "#E53935", "orange": "#FF8A1F",
            "blue": "#2F6BFF", "black": "#111111", "cream": "#F3E6C4",
        },
        "fonts": {  # PostScript adları; AE'de kurulu değilse AE yerine başka font koyar (log'a bakın)
            "title": "Anton-Regular",
            "caption": "Poppins-SemiBold",
            "serif": "PlayfairDisplay-Italic",
        },
        "caption": {"mode": "pill", "size": 46, "y": 0.70, "color": "white", "key_color": "red",
                    "pill": "#1E1E1E", "pill_opacity": 78},
        "title": {"size": 150, "color": "yellow", "anim": "slam", "pos": "top"},
        "default_transition": "blur_whip",
        "default_move": "push_in",
        "grade": {"noise": 3, "tint": 0, "vignette": 35, "light_leak_every": 0},
        "sfx_map": {"transition": "whoosh", "slam": "hit", "pop": "pop", "stamp": "hit", "type": "type"},
        "music_db": -19,
    },
    "hex": {
        "colors": {
            "white": "#F7F2E8", "cream": "#F3E6C4", "gold": "#E8C46A", "red": "#B23A2E",
            "green": "#2E5E4E", "black": "#0D0B09", "yellow": "#E8C46A", "orange": "#D98A3D",
            "blue": "#5B7A99",
        },
        "fonts": {
            "title": "PlayfairDisplay-BoldItalic",
            "caption": "PlayfairDisplay-Italic",
            "serif": "PlayfairDisplay-Italic",
        },
        "caption": {"mode": "word", "size": 70, "y": 0.50, "color": "white", "key_color": "gold"},
        "title": {"size": 120, "color": "cream", "anim": "fade", "pos": "upper"},
        "default_transition": "light_leak",
        "default_move": "parallax",
        "grade": {"noise": 6, "tint": 65, "vignette": 60, "light_leak_every": 4.5},
        "sfx_map": {"transition": "whoosh_soft", "slam": "hit_soft", "pop": "paper", "stamp": "paper",
                    "type": "typewriter"},
        "music_db": -17,
    },
}

TRANSITIONS = ["cut", "blur_whip", "zoom_blur", "flash", "fade", "light_leak", "circle_reveal", "slide_up"]
MOVES = ["static", "push_in", "pull_out", "pan_left", "pan_right", "pan_up", "pan_down", "parallax"]
FRAMES = ["full", "circle", "polaroid", "split", "cutout"]
TITLE_ANIMS = ["slam", "pop", "type", "fade", "stamp"]


def resolve(style_name, overrides=None):
    st = STYLES[style_name]
    out = {k: (dict(v) if isinstance(v, dict) else v) for k, v in st.items()}
    for k, v in (overrides or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k].update(v)
        else:
            out[k] = v
    return out


def color(st, name_or_hex):
    if not name_or_hex:
        return hexrgb(st["colors"]["white"])
    if name_or_hex.startswith("#"):
        return hexrgb(name_or_hex)
    return hexrgb(st["colors"].get(name_or_hex, st["colors"]["white"]))
