from PIL import Image, ImageDraw, ImageFont
from core.io import read_json

FONT = None  # system default

def main():
    data = read_json("data/2025/week05/standings.json")["rows"][:25]
    W, H, P = 1200, 1400, 20
    img = Image.new("RGB", (W,H), (11,15,20))
    d = ImageDraw.Draw(img)
    y = 40
    d.text((P,y), "Simulated BCS — Top 25", fill=(200,240,255), font=FONT); y += 40
    d.text((P,y), "⅓ Coaches, ⅓ AP, ⅓ Computers (drop hi/lo). Unofficial.", fill=(148,163,184), font=FONT); y += 30
    y += 10
    for r in data:
        line = f"{r['rank']:>2}. {r['team']:<20}  BCS {r['bcs_score']:.3f} (Comp {r['computers']:.3f}  AP {r['ap_pct']:.3f}  Coaches {r['coaches_pct']:.3f})"
        d.text((P,y), line, fill=(226,232,240), font=FONT); y += 28
    img.save("top25.png")

if __name__ == "__main__":
    main()


