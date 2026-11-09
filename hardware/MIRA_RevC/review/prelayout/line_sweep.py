"""Run with Python 3, numpy, ngspice 42 (KLU), and TI SBOM862F OPAx192.LIB."""
from pathlib import Path
import argparse
import csv
import hashlib
import itertools
import subprocess
import tempfile
import numpy as np

def simulate(directory, model, ron, feedback, load, capacitance, amplitude, rise_ns=10):
    deck = f"""BL/NL closed driver at connector; voltages referenced to GND
.include "{model}"
Vp vp 0 15
Vn vn 0 -15
Vcommand cmd 0 dc 0 pulse(0 {amplitude} 2u {rise_ns}n 10n 80u 150u)
Xamp cmd neg vp vn drv OPAx192
Rsense drv s 5
Rmain s line {ron}
Cpar line 0 30p
Rload line 0 {load}
Cload line 0 {capacitance}p
Rfeedback line fb {1000+feedback}
Rlocal drv fb 100k
Clocal drv fb 220p
Vinsert fb neg dc 0 ac 1
.options rshunt=1e12 srcsteps=0 itl1=1000 klu
.control
set wr_singlescale
set wr_vecnames
ac dec 60 100 100Meg
let loop=-v(fb)/v(neg)
wrdata ac.txt real(loop) imag(loop)
tran 5n 40u
wrdata tr.txt v(line) v(drv) v(s)
quit
.endc
.end
"""
    path = directory / 'line.cir'
    path.write_text(deck)
    for fn in ['tr.txt','ac.txt']:
        (directory/fn).unlink(missing_ok=True)
    subprocess.run(['ngspice','-b',path.name],cwd=directory,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT,check=True)
    f,re,im = np.loadtxt(directory/'ac.txt',skiprows=1,unpack=True)
    loop = re + 1j*im
    db = 20*np.log10(abs(loop))
    crosses = np.flatnonzero((db[:-1]>0) & (db[1:]<=0))
    assert len(crosses) == 1
    i = crosses[0]
    frac = db[i]/(db[i]-db[i+1])
    phase = np.unwrap(np.angle(loop))*180/np.pi
    pm = 180 + phase[i] + frac*(phase[i+1]-phase[i])
    unity = f[i]*(f[i+1]/f[i])**frac
    t,v,drv,s = np.loadtxt(directory/'tr.txt',skiprows=1,unpack=True)
    assert t[-1] >= .999*40e-6 and np.isfinite(v).all()
    # t settling is to final loaded DC, separate from the absolute static error.
    active=t>=2e-6
    err=np.flatnonzero(active & (abs(v-v[-1])>0.01*amplitude))
    settled=(t[min(err[-1]+1,len(t)-1)]-2e-6)*1e6 if len(err) else 0
    return [ron,feedback,load,capacitance,amplitude,rise_ns,round(unity/1e6,3),round(pm,2),round(v[-1],6),
            round(100*max(0,max(v[active])-v[-1])/amplitude,2),round(settled,3),round(1000*max(abs((drv-s)/5)),3)]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('model',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    model=args.model.resolve()
    if hashlib.sha256(model.read_bytes().replace(b'\r\n',b'\n')).hexdigest() != '8ab00e5269e2b2980d751daeece0e3956c95c04ec7c5a8403e9700d070fedf48':
        raise ValueError('Expected TI SBOM862F; use the original OPAx192.LIB from that archive.')
    rows=[]
    with tempfile.TemporaryDirectory() as tmp:
        directory=Path(tmp)
        (directory/'.spiceinit').write_text('set ngbehavior=ps\n')
        for (ron,rf),r,c,a in itertools.product([(40,120),(85,245)],[1000,10000,1e6],[10,100,1000,10000],[1,10]):
            rows.append(simulate(directory,model,ron,rf,r,c,a))
        for c in [100,1000,10000]:
            rows.append(simulate(directory,model,40,120,10000,c,10,10000))
    with args.output.open('w',newline='') as f:
        csv.writer(f).writerows([['Rswitch_ohm','Rremote_switch_ohm','Rload_ohm','Cload_pF','step_V','input_rise_ns','unity_MHz','phase_margin_deg','Vfinal_V','overshoot_pct','settle_1pct_us','shunt_peak_mA'],*rows])

if __name__=='__main__':
    main()
