#!/usr/bin/env python3
"""Evaluate a complete report set; no missing/empty reports or skipped-test inflation."""
import argparse, collections, hashlib, json, re, sys, time
import xml.etree.ElementTree as ET
from pathlib import Path

def evaluate(report_dir, policy, bugs):
    modules={m:collections.Counter() for m in policy['required_modules']}
    reasons=[]; triage=[]; total=passed=critical_failed=0
    for framework in policy['required_frameworks']:
        path=report_dir/f'{framework}.xml'
        try:
            cases=list(ET.parse(path).getroot().iter('testcase'))
            if not cases: raise ValueError('empty report')
        except (OSError, ET.ParseError, ValueError) as exc:
            reasons.append(f'{framework}: missing/invalid report: {exc}');continue
        for case in cases:
            name=case.get('name',''); identity=case.get('classname','')+'::'+name
            match=re.search(r'(temperature|configuration|faults|release)__',name)
            if not match:
                reasons.append(f'unmapped test: {identity}'); continue
            module=match.group(1)
            if case.find('error') is not None: outcome='error'
            elif case.find('failure') is not None: outcome='failed'
            elif case.find('skipped') is not None: outcome='skipped'
            else: outcome='passed'
            total+=1; passed+=outcome=='passed'; modules[module][outcome]+=1
            if '__critical__' in name and outcome!='passed': critical_failed+=1
            if outcome in ('failed','error'):
                triage.append({'test_id':hashlib.sha256((framework+identity).encode()).hexdigest()[:16],
                  'framework':framework,'module':module,'test':identity,'outcome':outcome,
                  'state':'Needs triage','note':'Not automatically classified as an application bug.'})
    rate=100*passed/total if total else 0
    if total < policy['minimum_tests']: reasons.append('incomplete full regression suite')
    for module, counts in modules.items():
        if not sum(counts.values()): reasons.append('missing module: '+module)
    if rate <= policy['threshold_percent']: reasons.append('pass rate must be strictly above threshold')
    if critical_failed: reasons.append('critical tests failed, errored or skipped')
    if any(c['error'] for c in modules.values()): reasons.append('test execution errors require triage')
    approved=not reasons
    summary={'total':total,'passed':passed,'pass_rate_percent':rate,'critical_nonpassing':critical_failed,
             'gate_passed':approved,'reasons':reasons,'modules':modules,'timestamp':int(time.time())}
    report_dir.mkdir(parents=True,exist_ok=True)
    (report_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (report_dir/'triage.json').write_text(json.dumps(triage,indent=2)+'\n')
    lines=[f'embedded_test_gate_passed {int(approved)}',f'embedded_test_last_run_timestamp_seconds {summary["timestamp"]}',
           f'embedded_test_pass_rate_percent {rate}']
    for module, counts in modules.items():
        n=sum(counts.values())
        for status in ['passed','failed','error','skipped']:
            lines.append(f'embedded_test_cases{{module="{module}",status="{status}"}} {counts[status]}')
        lines.append(f'embedded_module_pass_rate_percent{{module="{module}"}} {100*counts["passed"]/n if n else 0}')
        for state in ['open','resolved','closed']:
            count=sum(b.get('module')==module and b.get('state')==state for b in bugs)
            lines.append(f'embedded_tracked_bugs{{module="{module}",state="{state}"}} {count}')
    (report_dir/'metrics.prom').write_text('\n'.join(lines)+'\n')
    return summary
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--reports',type=Path,default=Path('reports'))
    p.add_argument('--policy',type=Path,default=Path('config/test-policy.json'))
    p.add_argument('--bugs',type=Path,default=Path('bugs/bugs.json'));a=p.parse_args()
    try: result=evaluate(a.reports,json.loads(a.policy.read_text()),json.loads(a.bugs.read_text()))
    except Exception as exc: print(f'Gate infrastructure error: {exc}',file=sys.stderr);sys.exit(2)
    print(json.dumps(result,indent=2));sys.exit(0 if result['gate_passed'] else 1)
