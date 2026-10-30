#!/usr/bin/env python3
import argparse, os, subprocess, sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--build',default='build');p.add_argument('--version',required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1];os.chdir(root);build=Path(a.build).resolve();reports=root/'reports';reports.mkdir(exist_ok=True)
for name in ['ctest.xml','pytest.xml','robot.xml','summary.json','metrics.prom','triage.json']:
    (reports/name).unlink(missing_ok=True)
env=dict(os.environ,SENSOR_BINARY=str(build/'sensor-gateway'),EXPECTED_VERSION=a.version)
commands=[['ctest','--test-dir',str(build),'--output-on-failure','--output-junit',str(reports/'ctest.xml')],
 [sys.executable,'-m','pytest','tests/pytest','-q','--junitxml='+str(reports/'pytest.xml')],
 [sys.executable,'-m','robot','--outputdir',str(reports/'robot'),'--xunit',str(reports/'robot.xml'),'tests/robot']]
for command in commands:
    result=subprocess.run(command,env=env)
    print('Framework exit status:',result.returncode,flush=True)
result=subprocess.run([sys.executable,'scripts/gate.py'],env=env)
sys.exit(result.returncode)
