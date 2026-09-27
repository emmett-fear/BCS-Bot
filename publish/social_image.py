from PIL import Image, ImageDraw
from core.io import read_json
from core.config import DATA_ROOT

FONT=None

def main():
    rows=read_json(str(DATA_ROOT/"standings.json"))["rows"]
    data=sorted(rows,key=lambda r:r.get("bcs_plus_score") if r.get("bcs_plus_score") is not None else -1,reverse=True)[:25]
    W,H,P=1200,1400,20
    img=Image.new("RGB",(W,H),(11,15,20)); d=ImageDraw.Draw(img); y=40
    d.text((P,y),"BCS+ — Top 25",fill=(200,240,255),font=FONT); y+=40
    d.text((P,y),"25% AP · 25% Coaches · 25% Computers · 25% Marbles",fill=(148,163,184),font=FONT); y+=40
    for r in data:
        score=r.get("bcs_plus_score")
        marbles=r.get("marbles")
        line=f"{r.get('bcs_plus_rank','—'):>2}. {r['team']:<20}  BCS+ {score:.3f}  Marbles {marbles:.0f}  Classic {r['bcs_score']:.3f}"
        d.text((P,y),line,fill=(226,232,240),font=FONT); y+=28
    img.save("top25.png")

if __name__=="__main__": main()
