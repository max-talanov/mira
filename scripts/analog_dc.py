"""Preserved MIRA.05 CV and trip DC calculation; no transient model."""
import itertools
def trip(rp=45300,rgp=10000,bp=100000,rn=34000,rgn=10000,bn=100000,ru=1.5e6,vio=3.3,offset=0):
 a=(1/rp)/(1/rp+1/rgp+1/bp);den=1/rn+1/rgn+1/bn+1/ru;b=1/rn/den;d=1/ru/den
 return {'slope':b/a,'offset_V':(d*vio+offset)/a,'sense16_5_input_V':16.5*a}
nom=trip();corners=[]
# 1% passive envelope; comparator offset +/-5 mV conservative allocation, not a certified system bound.
for sig in itertools.product([-1,1],repeat=9):
 vals=[v*(1+.01*s) for v,s in zip([45300,10000,100000,34000,10000,100000,1.5e6],sig[:7])]
 c=trip(*vals,vio=3.3*(1+.05*sig[7]),offset=.005*sig[8]);corners.append(c)
# CV DC nodal result: sense divider -> CV error; BF + buffer resistance with local 100k bleed.
def cv(vcmd,Rin=100000,Rf=101000,rin_plus=100000,rbias=100000,rser=1000,ron_mux=4,ron_guard=10,rout=4.7,bleed=100000,bias=2.5):
 ro=ron_guard+rout;k=bleed/(bleed+ro);rth=bleed*ro/(bleed+ro);a=Rf/(Rin+rser+ron_mux+rth)
 # vn=(VS/rin_plus + bias/rbias)/(1/rin_plus+1/rbias); VERR=bias at ideal CV equilibrium.
 q=rbias/(rbias+rin_plus)
 return ((a*k*vcmd+bias)/(1+a)-(1-q)*bias)/q
nomcv=[cv(v) for v in [0,.1,.5,5,10]]
cvcs=[]
for sig in itertools.product([-1,1],repeat=8):
 kw=dict(zip(['Rin','Rf','rin_plus','rbias','rser','bleed'],[v*(1+t*s) for v,t,s in zip([100000,101000,100000,100000,1000,100000],[.001]*4+[.01]*2,sig[:6])]))
 kw.update(ron_mux=7.4 if sig[6]>0 else 0,ron_guard=14 if sig[7]>0 else 0)
 cvcs.append({'zero_V':cv(0,**kw),'point_0_1_V':cv(.1,**kw),'point_10_V':cv(10,**kw)})

def summary():
 return {"CV_ideal_nominal":list(zip([0,.1,.5,5,10],nomcv)),"CV_nominal_gain":(cv(10)-cv(0))/10,"CV_corners":{k:[min(x[k] for x in cvcs),max(x[k] for x in cvcs)] for k in cvcs[0]},"trip_corners":{"slope":[min(x["slope"] for x in corners),max(x["slope"] for x in corners)],"threshold_at_ILIM0_1_V":[min(.1*x["slope"]+x["offset_V"] for x in corners),max(.1*x["slope"]+x["offset_V"] for x in corners)],"conditions":"1% resistors, IO3V3 +/-5%, comparator offset allocation +/-5mV; excludes switch leakage, dynamics and temperature drift"}}
