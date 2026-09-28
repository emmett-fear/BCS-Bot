from PIL import Image, ImageDraw, ImageFont
from core.io import read_json
from core.config import DATA_ROOT

def _font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()

def main():
    rows=read_json(str(DATA_ROOT/"standings.json"))["rows"]
    # Only rank teams with a real BCS+ score; a missing score (no Marbles
    # match that week) must never be drawn as if it were rank "—".
    data=sorted((r for r in rows if r.get("bcs_plus_score") is not None),
                key=lambda r:r["bcs_plus_score"], reverse=True)[:25]
    title_font, sub_font, row_font = _font(34, bold=True), _font(18), _font(20)
    W,H,P=1200,1400,24
    img=Image.new("RGB",(W,H),(11,15,20)); d=ImageDraw.Draw(img); y=36
    d.text((P,y),"BCS+ — Top 25",fill=(200,240,255),font=title_font); y+=46
    d.text((P,y),"25% AP  ·  25% Coaches  ·  25% Computers  ·  25% Marbles",fill=(148,163,184),font=sub_font); y+=40
    for r in data:
        rank=r.get("bcs_plus_rank")
        score=r["bcs_plus_score"]
        marbles=r.get("marbles")
        marbles_txt = f"{marbles:.0f}" if marbles is not None else "—"
        line=f"{rank:>2}. {r['team']:<20}  BCS+ {score:.3f}  Marbles {marbles_txt}  Classic {r['bcs_score']:.3f}"
        d.text((P,y),line,fill=(226,232,240),font=row_font); y+=30
    img.save("top25.png")

if __name__=="__main__": main()
