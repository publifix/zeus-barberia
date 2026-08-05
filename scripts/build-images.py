"""One-off asset pipeline: resizes/reformats the repo's existing source photos
and logo into the responsive WebP/JPEG/icon set the landing page references.
Run once from the repo root: python3 scripts/build-images.py
"""
from PIL import Image
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "assets", "img")
SERV = os.path.join(IMG, "servicios")
GAL = os.path.join(IMG, "gallery")
ICONS = os.path.join(ROOT, "assets", "icons")
LOGO_DIR = os.path.join(ROOT, "assets", "logo")

ORIGINALS = os.path.join(ROOT, "assets", "img", "originals")

SOURCES = {
    "hero": "allef-vinicius-IvQeAVeJULw-unsplash.jpg",
    "servicio-corte-caballero": "hai-phung-m4Pd_e-4zKs-unsplash.jpg",
    "servicio-arreglo-barba": "arthur-humeau-Twd3yaqA2NM-unsplash.jpg",
    "servicio-facial-relajante": "andrea-donato-MNu0n-3BIKs-unsplash.jpg",
    "servicio-paquetes": "stefan-schauberger-Tper6bHeSUo-unsplash.jpg",
}

WEBP_Q = 74
JPG_Q = 78


def save_webp(im, path, width, quality=WEBP_Q):
    w_percent = width / float(im.size[0])
    h = int(float(im.size[1]) * w_percent)
    resized = im.resize((width, h), Image.LANCZOS)
    resized.save(path, "WEBP", quality=quality, method=6)
    return resized


def save_jpg(im, path, width, quality=JPG_Q):
    w_percent = width / float(im.size[0])
    h = int(float(im.size[1]) * w_percent)
    resized = im.convert("RGB").resize((width, h), Image.LANCZOS)
    resized.save(path, "JPEG", quality=quality, optimize=True, progressive=True)
    return resized


def center_crop(im, target_ratio):
    w, h = im.size
    cur_ratio = w / h
    if cur_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return im.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        return im.crop((0, top, w, top + new_h))


os.makedirs(SERV, exist_ok=True)
os.makedirs(GAL, exist_ok=True)
os.makedirs(ICONS, exist_ok=True)
os.makedirs(LOGO_DIR, exist_ok=True)

# --- Hero: wide responsive set ---
hero_src = Image.open(os.path.join(ORIGINALS, SOURCES["hero"]))
for w in (640, 960, 1280, 1600, 1920, 2400):
    save_webp(hero_src, os.path.join(IMG, f"hero-{w}.webp"), min(w, hero_src.size[0]))
save_jpg(hero_src, os.path.join(IMG, "hero-1280.jpg"), 1280)

# OG share image 1200x630
og = center_crop(hero_src, 1200 / 630)
og = og.convert("RGB").resize((1200, 630), Image.LANCZOS)
og.save(os.path.join(IMG, "og-image.jpg"), "JPEG", quality=85, optimize=True)

# --- Service / gallery photos ---
for key, fname in SOURCES.items():
    if key == "hero":
        continue
    im = Image.open(os.path.join(ORIGINALS, fname))
    slug = key.replace("servicio-", "")
    for w in (480, 768, 1080, 1440):
        save_webp(im, os.path.join(SERV, f"{slug}-{w}.webp"), min(w, im.size[0]))
    save_jpg(im, os.path.join(SERV, f"{slug}-768.jpg"), 768)

    # square gallery crop
    sq = center_crop(im, 1.0)
    for w in (480, 700, 960):
        s = sq.resize((w, w), Image.LANCZOS)
        s.save(os.path.join(GAL, f"{slug}-sq-{w}.webp"), "WEBP", quality=WEBP_Q, method=6)
    # large version for lightbox
    save_webp(im, os.path.join(GAL, f"{slug}-large-1600.webp"), min(1600, im.size[0]))

# Hero also appears in the gallery grid (real editorial shot of the shop)
hero_sq = center_crop(hero_src, 1.0)
for w in (480, 700, 960):
    hero_sq.resize((w, w), Image.LANCZOS).save(
        os.path.join(GAL, f"ambiente-sq-{w}.webp"), "WEBP", quality=WEBP_Q, method=6
    )
save_webp(hero_src, os.path.join(GAL, "ambiente-large-1600.webp"), 1600)

# --- Logo: right-sized, optimized web copy (source PNG is a 2MB print-res file) ---
logo = Image.open(os.path.join(ORIGINALS, "zeuz-logo.png")).convert("RGBA")
logo_web_w = 640  # crisp up to ~320px CSS width at 2x DPR, far smaller than the 1536px source
logo_web_h = int(logo.size[1] * (logo_web_w / logo.size[0]))
logo.resize((logo_web_w, logo_web_h), Image.LANCZOS).save(
    os.path.join(LOGO_DIR, "zeus-logo.png"), "PNG", optimize=True
)

bbox = logo.getbbox()
pad = int((bbox[2] - bbox[0]) * 0.08)
cropped = logo.crop((
    max(bbox[0] - pad, 0),
    max(bbox[1] - pad, 0),
    min(bbox[2] + pad, logo.size[0]),
    min(bbox[3] + pad, logo.size[1]),
))

# --- Favicon / touch icons: logo mark centered on solid brand-black square ---
def make_icon(size, filename, corner_radius_pct=0):
    canvas = Image.new("RGBA", (size, size), (11, 11, 11, 255))  # #0B0B0B
    target_w = int(size * 0.82)
    ratio = target_w / cropped.size[0]
    target_h = int(cropped.size[1] * ratio)
    logo_resized = cropped.resize((target_w, target_h), Image.LANCZOS)
    # render logo in white (brightness->0, invert) for contrast on black
    r, g, b, a = logo_resized.split()
    white_rgb = Image.merge("RGB", (a.point(lambda x: 255), a.point(lambda x: 255), a.point(lambda x: 255)))
    white_logo = Image.merge("RGBA", (*white_rgb.split(), a))
    x = (size - target_w) // 2
    y = (size - target_h) // 2
    canvas.alpha_composite(white_logo, (x, y))
    canvas.save(os.path.join(ICONS, filename), "PNG")
    return canvas


icon_512 = make_icon(512, "icon-512.png")
make_icon(192, "icon-192.png")
make_icon(180, "apple-touch-icon.png")
icon_48 = make_icon(48, "favicon-48.png")
icon_32 = make_icon(32, "favicon-32.png")
icon_16 = make_icon(16, "favicon-16.png")

icon_16.convert("RGBA").save(
    os.path.join(ROOT, "favicon.ico"),
    format="ICO",
    sizes=[(16, 16), (32, 32), (48, 48)],
)

print("Done. Generated files:")
for base, _, files in os.walk(IMG):
    for f in sorted(files):
        print(os.path.relpath(os.path.join(base, f), ROOT))
for f in sorted(os.listdir(ICONS)):
    print(os.path.relpath(os.path.join(ICONS, f), ROOT))
print("favicon.ico")
