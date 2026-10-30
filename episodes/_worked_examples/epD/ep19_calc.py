from math import sqrt
from scipy.stats import norm
print('p195',6/16,4/16)
for a in (0,0.5,1): print('p200 a',a,round((4+a*7)/24,4),round((6+a*4)/24,4))
for e,L in ((4,7),(3,7),(4,6),(4,5),(4,8)): print('p202',e,L,round((e+0.5*L)/24,4))
def wil(N,e,a):
    z=norm.ppf(1-a/2)
    return (e+z*z/(2*N)+z*sqrt(e*(1-e)/N+z*z/(4*N*N)))/(1+z*z/N)
print('z',norm.ppf(1-0.25/2))
b=wil(7,2/7,0.25);l=wil(4,1/4,0.25);r=wil(3,1/3,0.25);print('p205',round(b,3),round(7*b,3),round(l,3),round(r,3),round(4*l+3*r,3))
print('p215',10/30,(10+0.5)/30,9/30,(9+4*0.5)/30)
print('p220',round(2/14,3),round(4/14,3),round(2/14-4/14,3))
p=(10+4*0.5)/100;Eb=100*p;sd=sqrt(100*p*(1-p));print('p224',p,Eb,round(sd,3),14.5,Eb+sd)
print('p229 keep',1/3*3/10+0+0.01*2,'prune',1/4*4/10+0.01)
print('p230 R5',1/5*5/10,'Ra T5',1/4*4/10+0+0.01*2,'leaf with alpha',1/5*5/10+0.01)
print('p227 alpha weakest',)
