"""Extract the nine supplied cup sprites without resizing or filtering."""
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[1]
sheet=Image.open(root/'assets/images/coffee_cup_station_master.png').convert('RGBA')
regions={
 ('takeaway','S'):(76,67,92,91),('takeaway','M'):(95,60,114,90),('takeaway','L'):(117,53,137,91),
 ('cold','S'):(129,114,146,136),('cold','M'):(149,107,169,136),('cold','L'):(175,105,195,141),
 ('mug','S'):(224,74,243,89),('mug','M'):(245,69,267,90),('mug','L'):(270,62,293,89),
}
for (style,size),box in regions.items():
 sheet.crop(box).save(root/'assets/cups'/f'{style}_{size.lower()}.png')
