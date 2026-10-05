"""Rebuild original, editable 32px barista sprites (no filtered source art)."""
import json
from pathlib import Path
from best_served_warm.pixel_art import render

ROOT = Path(__file__).resolve().parents[1]
PALETTE = {'ink':'#583d35','shadow':'#a98069','cream':'#fff4d8','white':'#fffdf2','sage':'#8fa68b','sage_dark':'#5d7869','blue':'#b6d5d6','blue_dark':'#72979f','caramel':'#c38b4d','coffee':'#704832','steel':'#adb9af','pink':'#d38677'}

def sprite(name, draw):
 p={'size':[32,32], 'palette':PALETTE, 'layers':[{'name':name,'draw':draw}]}
 path=ROOT/'art_sources'/'barista'/(name+'.json'); path.write_text(json.dumps(p,indent=2)+'\n')
 render(p).save(ROOT/'assets'/'barista'/(name+'.png'))

def rect(x,y,w,h,c): return dict(type='rect',box=[x,y,w,h],color=c)
def line(points,c,w=1): return dict(type='line',points=points,color=c,width=w)
def poly(points,c): return dict(type='polygon',points=points,color=c)
def ellipse(x,y,w,h,c): return dict(type='ellipse',box=[x,y,w,h],color=c)

for name,x,y,w,h in [('demitasse',6,13,17,12),('mug',5,8,19,19),('tall',8,3,17,26),('rocks',5,13,23,16)]:
 ops=[]
 if name in ('mug','demitasse'):
  ops += [ellipse(x+w-1,y+2,8,10,'ink'),ellipse(x+w+1,y+4,4,6,'cream')]
 ops += [poly([[x,y],[x+w,y],[x+w-2,y+h],[x+2,y+h]],'ink'),poly([[x+1,y+1],[x+w-1,y+1],[x+w-3,y+h-1],[x+3,y+h-1]],'blue' if name in ('tall','rocks') else 'cream'),line([[x+3,y+3],[x+4,y+h-4]],'white'),rect(x+2,y+1,w-3,1,'white'),rect(x+3,y+h-2,w-5,1,'shadow')]
 if name=='mug': ops += [ellipse(11,16,7,5,'sage_dark'),line([[14,16],[13,20]],'cream')]
 sprite(name,ops)
for name,c in [('whole','blue_dark'),('oat','sage_dark')]:
 sprite('milk_'+name,[poly([[8,8],[12,3],[21,3],[25,8],[25,29],[8,29]],'ink'),rect(9,9,15,19,'cream'),poly([[9,8],[13,4],[21,4],[24,8]],c),rect(9,13,15,8,c),ellipse(13,14,7,6,'cream'),line([[11,10],[11,12]],'white')])
sprite('milk_foam',[poly([[7,10],[21,10],[26,7],[24,24],[10,27]],'ink'),poly([[9,11],[21,11],[24,9],[22,23],[11,25]],'steel'),ellipse(9,9,14,5,'white'),rect(24,13,4,9,'ink'),rect(25,15,2,5,'cream')])
for name,c in [('vanilla','cream'),('caramel','caramel'),('chocolate','coffee')]:
 sprite('syrup_'+name,[rect(13,3,7,5,'ink'),rect(10,8,13,21,'ink'),rect(11,9,11,19,c),rect(11,15,11,8,'cream'),ellipse(14,17,5,5,'coffee'),rect(14,1,11,2,'ink'),line([[12,10],[12,13]],'white')])
sprite('ice',[poly([[5,8],[13,5],[19,9],[19,20],[11,24],[5,19]],'blue_dark'),poly([[6,9],[13,7],[17,10],[11,12]],'white'),poly([[6,11],[11,14],[11,22],[6,18]],'blue'),poly([[13,14],[18,11],[18,19],[13,22]],'cream'),poly([[18,18],[25,15],[30,18],[30,27],[23,30],[18,27]],'blue_dark'),poly([[19,19],[25,17],[28,19],[23,21]],'white'),rect(20,22,3,5,'blue'),rect(25,22,3,5,'cream')])
sprite('straw_paper',[line([[11,29],[11,9],[23,2]],'ink',4),line([[11,28],[11,9],[23,2]],'cream',2),rect(10,14,3,3,'pink'),rect(10,23,3,3,'pink'),line([[17,5],[18,7]],'pink',2)])
sprite('straw_steel',[line([[11,29],[11,9],[23,2]],'ink',4),line([[11,28],[11,9],[23,2]],'steel',2),line([[10,27],[10,12]],'white')])
sprite('grinder',[rect(7,26,21,4,'ink'),rect(10,11,15,16,'ink'),rect(11,12,13,13,'sage_dark'),rect(14,18,9,3,'steel'),poly([[7,3],[27,3],[24,12],[10,12]],'ink'),poly([[9,4],[25,4],[22,10],[12,10]],'caramel'),rect(10,4,15,2,'cream'),rect(14,23,7,3,'coffee'),rect(11,27,13,1,'steel'),rect(20,14,3,3,'cream')])
sprite('tamper',[ellipse(8,3,16,10,'ink'),ellipse(9,4,14,7,'coffee'),rect(13,11,6,12,'ink'),rect(14,12,4,10,'caramel'),rect(6,23,21,6,'ink'),rect(7,24,19,3,'steel'),rect(8,24,17,1,'white')])
sprite('portafilter',[ellipse(3,4,20,13,'ink'),ellipse(4,5,18,9,'steel'),ellipse(6,6,14,6,'coffee'),line([[16,14],[28,28]],'ink',5),line([[17,16],[27,27]],'shadow',2)])
sprite('none',[ellipse(5,5,22,22,'shadow'),ellipse(7,7,18,18,'cream'),line([[9,23],[23,9]],'shadow',2)])
print('Rendered original barista art.')
