#!/usr/bin/env python3
"""Summarize native ERC without concealing errors or changing project settings."""
from pathlib import Path
import argparse,collections,hashlib,json,sys

def load(path):
    d=json.loads(path.read_text());items=[]
    for s in d.get('sheets',[]):
        for v in s.get('violations',[]):items.append({'sheet':s['path'],**v})
    return d,items

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline',type=Path,default=Path('compliance/baseline/MIRA_Control/docs/repair/FINAL_ERC.json'))
    p.add_argument('--final',type=Path,required=True)
    p.add_argument('--output',type=Path,default=Path('compliance/validation/FINAL_ERC_REVIEW.json'))
    a=p.parse_args();old,ov=load(a.baseline);new,nv=load(a.final)
    ignored=lambda d:{x['key'] for x in d.get('ignored_checks',[])}
    counts=lambda vs:dict(sorted(collections.Counter(v['type'] for v in vs).items()))
    oldtypes=set(counts(ov));errors=[v for v in nv if v.get('severity')=='error']
    newtypes=[v for v in nv if v['type'] not in oldtypes]
    suppressed=sorted(ignored(new)-ignored(old));excluded=sorted({'error','warning'}-set(new.get('included_severities',[])))
    report={'status':'PASS' if not(errors or newtypes or suppressed or excluded) else 'REVIEW_REQUIRED',
       'inputs':{'baseline_erc':str(a.baseline),'final_erc':str(a.final),
           'baseline_erc_sha256':hashlib.sha256(a.baseline.read_bytes()).hexdigest(),
           'final_erc_sha256':hashlib.sha256(a.final.read_bytes()).hexdigest()},
       'baseline_counts_by_type':counts(ov),'final_counts_by_type':counts(nv),
       'error_count':len(errors),'warning_count':sum(v.get('severity')=='warning' for v in nv),
       'newly_ignored_checks':suppressed,'excluded_required_severities':excluded,
       'electrical_errors':errors,'new_violation_types':newtypes,
       'final_ignored_checks':new.get('ignored_checks',[]),'all_final_violations':nv,
       'method':'Native ERC errors must be zero; both warning and error severities must be included; no new ignored check may be introduced. Existing warning families are retained in full for human review. A PASS does not certify every warning harmless or analog behavior.'}
    a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('status','error_count','warning_count','baseline_counts_by_type','final_counts_by_type','newly_ignored_checks')},ensure_ascii=False,indent=2))
    return 0 if report['status']=='PASS' else 2
if __name__=='__main__':sys.exit(main())
