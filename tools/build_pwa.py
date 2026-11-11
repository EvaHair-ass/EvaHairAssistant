#!/usr/bin/env python3
"""Собирает установочную версию приложения (PWA) в папку docs/ из prototype/index.html.

Запуск из корня репозитория:  python3 tools/build_pwa.py
Нужен Pillow для иконок (pip install pillow).
"""
import hashlib, json, math, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "prototype" / "index.html"
SB_CONFIG = ROOT / "supabase" / "config.json"
VENDOR = ROOT / "tools" / "vendor"
OUT = ROOT / "docs"
ICONS = OUT / "icons"

NAME = "Моя мастерская"
SHORT = "Мастерская"
BG_LIGHT = "#F1E8D6"
BG_DARK = "#17120D"
CLAY = (166, 79, 46)
CREAM = (246, 235, 214)


def draw_icon(size, maskable=False):
    """Иконка: ловец снов кремовыми линиями на глиняном фоне (в безопасной зоне для maskable)."""
    from PIL import Image, ImageDraw
    k = 4
    S = size * k
    img = Image.new("RGB", (S, S), CLAY)
    d = ImageDraw.Draw(img)
    # область рисунка: 120x206 -> вписываем в безопасный квадрат (maskable: 62%, обычная: 74%)
    box = S * (0.62 if maskable else 0.74)
    sc = box / 206.0
    ox = (S - 120 * sc) / 2
    oy = (S - 206 * sc) / 2
    lw = max(2, int(2.1 * sc))

    def P(x, y):
        return (ox + x * sc, oy + y * sc)

    cx, cy, R, n = 60, 58, 44, 10
    d.ellipse([*P(cx - R, cy - R), *P(cx + R, cy + R)], outline=CREAM, width=lw + 1)
    rs = [R - 4, R - 13, R - 21, R - 28, R - 34]
    layers = [[(cx + r * math.cos(((i + (0.5 if j % 2 else 0)) / n) * 2 * math.pi - math.pi / 2),
                cy + r * math.sin(((i + (0.5 if j % 2 else 0)) / n) * 2 * math.pi - math.pi / 2)) for i in range(n)]
              for j, r in enumerate(rs)]
    for j in range(1, len(layers)):
        pts = [P(*q) for q in layers[j]]
        d.line(pts + [pts[0]], fill=CREAM, width=lw)
    for j in range(len(layers) - 1):
        for i, p in enumerate(layers[j]):
            for q in (layers[j + 1][i], layers[j + 1][(i - 1) % n]):
                d.line([P(*p), P(*q)], fill=CREAM, width=max(1, lw - 1))
    d.ellipse([*P(cx - 3, cy - 3), *P(cx + 3, cy + 3)], fill=CREAM)
    d.line([P(cx, 0), P(cx, cy - R)], fill=CREAM, width=lw)
    # нити с перьями
    for dx, ln in ((-26, 62), (0, 92), (26, 70)):
        y0 = cy + math.sqrt(R * R - dx * dx)
        yb = y0 + ln * 0.55
        d.line([P(cx + dx, y0), P(cx + dx, yb)], fill=CREAM, width=lw)
        fl = ln * 0.5
        w = fl * 0.17
        leaf = [P(cx + dx, yb + fl * 0.28)]
        for t in range(0, 11):
            u = t / 10
            leaf.append(P(cx + dx + w * math.sin(math.pi * u) * 1.1, yb + fl * (0.28 + 0.72 * u)))
        for t in range(10, -1, -1):
            u = t / 10
            leaf.append(P(cx + dx - w * math.sin(math.pi * u) * 1.1, yb + fl * (0.28 + 0.72 * u)))
        d.polygon(leaf, outline=CREAM, fill=None, width=lw) if hasattr(d, "polygon") else None
        d.line([P(cx + dx, yb), P(cx + dx, yb + fl)], fill=CREAM, width=lw)
    return img.resize((size, size), Image.LANCZOS)


def build_icons():
    ICONS.mkdir(parents=True, exist_ok=True)
    draw_icon(192).save(ICONS / "icon-192.png")
    draw_icon(512).save(ICONS / "icon-512.png")
    draw_icon(512, maskable=True).save(ICONS / "icon-maskable-512.png")
    draw_icon(180).save(ICONS / "apple-touch-icon.png")
    draw_icon(32).save(ICONS / "favicon-32.png")


def main():
    if not SRC.exists():
        sys.exit("Не найден " + str(SRC))
    src = SRC.read_text(encoding="utf-8")
    m = re.search(r"</style>\s*", src)
    head_part, body_part = src[: m.end()], src[m.end():]

    OUT.mkdir(exist_ok=True)
    build_icons()

    extra_head = f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="{BG_LIGHT}" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="{BG_DARK}" media="(prefers-color-scheme: dark)">
<meta name="description" content="Фото-склад, закупки, мастерская и архив для мастериц handmade.">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" sizes="32x32" href="icons/favicon-32.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="{SHORT}">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
"""
    extra_css = """<style>
:root{padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px)}
body{overscroll-behavior:none}
</style>
"""
    cfg = None
    if SB_CONFIG.exists():
        cfg = json.loads(SB_CONFIG.read_text(encoding="utf-8"))
        if not cfg.get("url") or not cfg.get("anonKey"):
            sys.exit("В supabase/config.json нужны поля url и anonKey")
        public = {k: cfg[k] for k in ("url", "anonKey", "payUrl", "support") if cfg.get(k)}
        (OUT / "config.js").write_text("window.__SB__=" + json.dumps(public, ensure_ascii=False) + ";\n", encoding="utf-8")
    elif (OUT / "config.js").exists():
        (OUT / "config.js").unlink()
    pwa_js = "<script>window.__PWA__=true;</script>\n"
    if cfg:
        (OUT / "vendor").mkdir(exist_ok=True)
        for f in VENDOR.glob("*.js"):
            (OUT / "vendor" / f.name).write_bytes(f.read_bytes())
        pwa_js += '<script src="config.js"></script>\n<script src="vendor/supabase.js"></script>\n'
    sw_js = """<script>
if('serviceWorker' in navigator){addEventListener('load',function(){navigator.serviceWorker.register('sw.js').catch(function(){});});}
if(navigator.storage&&navigator.storage.persist){navigator.storage.persist().catch(function(){});}
addEventListener('beforeinstallprompt',function(e){e.preventDefault();window.__installPrompt=e;});
</script>
"""
    html = ("<!doctype html>\n<html lang=\"ru\">\n<head>\n" + extra_head + head_part + extra_css +
            "</head>\n<body>\n" + pwa_js + body_part.rstrip() + "\n" + sw_js + "</body>\n</html>\n")
    (OUT / "index.html").write_text(html, encoding="utf-8")

    manifest = {
        "id": "./", "name": NAME, "short_name": SHORT, "lang": "ru", "dir": "ltr",
        "description": "Фото-склад, закупки, мастерская и архив для мастериц handmade.",
        "start_url": "./", "scope": "./", "display": "standalone", "orientation": "portrait",
        "background_color": BG_LIGHT, "theme_color": BG_LIGHT, "categories": ["productivity", "business"],
        "icons": [
            {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": "icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }
    (OUT / "manifest.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    cfg_txt = (OUT / "config.js").read_text(encoding="utf-8") if (OUT / "config.js").exists() else ""
    version = hashlib.sha1((html + cfg_txt).encode("utf-8")).hexdigest()[:10]
    shell_extra = ", './config.js', './vendor/supabase.js'" if cfg_txt else ""
    sw = f"""/* Service worker: офлайн-режим. Версия кэша меняется при каждой сборке, чтобы обновления доходили до пользователя. */
const CACHE = 'mm-{version}';
const SHELL = ['./', './index.html', './manifest.webmanifest', './icons/icon-192.png', './icons/icon-512.png', './icons/apple-touch-icon.png', './icons/favicon-32.png'{shell_extra}];
self.addEventListener('install', e => {{ e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); }});
self.addEventListener('activate', e => {{
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('mm-') && k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
}});
self.addEventListener('fetch', e => {{
  const r = e.request; if (r.method !== 'GET') return;
  const u = new URL(r.url);
  if (u.origin === location.origin) {{
    if (r.mode === 'navigate') {{
      e.respondWith(fetch(r).then(res => {{ const cp = res.clone(); caches.open(CACHE).then(c => c.put('./index.html', cp)); return res; }}).catch(() => caches.match('./index.html')));
      return;
    }}
    e.respondWith(caches.match(r).then(m => m || fetch(r).then(res => {{ const cp = res.clone(); caches.open(CACHE).then(c => c.put(r, cp)); return res; }})));
  }} else if (u.hostname === 'fonts.googleapis.com' || u.hostname === 'fonts.gstatic.com' || u.hostname === 'cdn.jsdelivr.net') {{
    e.respondWith(caches.open(CACHE).then(c => c.match(r).then(m => {{
      const net = fetch(r).then(res => {{ c.put(r, res.clone()); return res; }}).catch(() => m);
      return m || net;
    }})));
  }}
}});
"""
    (OUT / "sw.js").write_text(sw, encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    print("Готово: docs/ собрана, версия кэша mm-" + version)


if __name__ == "__main__":
    main()
