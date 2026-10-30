import sys
from PIL import Image
groups=dict(a=[12,13,14,15,16,18],b=[19,20,21,23,24,25],c=[26,27,28,32,33,34],d=[35,36,62,70,72,75],e=[81,96,102,103,104,105],f=[106,108,110,112,114,117],g=[121,129,130,131,132,133],h=[134,138,140,142,144,146],i=[151,152,153,154,156,158],j=[160,162,163,164,166,167],k=[174,176,178,181,182,183],l=[187,188,189,197,201,203],m=[206,207,210,213,216,218],n=[220,221,224,227,229,231],o=[232,234,237,238,141,143])
for k,ps in groups.items():
    W=640;ims=[Image.open(f'img/s-{p:03d}.jpg') for p in ps]
    ims=[im.resize((W,int(im.height*W/im.width))) for im in ims];H=ims[0].height
    S=Image.new('RGB',(W*3+8,H*2+4),'#333')
    for i,im in enumerate(ims): S.paste(im,((i%3)*(W+4),(i//3)*(H+4)))
    S.save(f'sheet_{k}.jpg',quality=85)
