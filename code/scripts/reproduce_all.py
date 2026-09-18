#!/usr/bin/env python3
from __future__ import annotations
import argparse, os, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PYTHON=sys.executable

def run(command,env):
    print('+',' '.join(map(str,command)),flush=True); subprocess.run(command,cwd=ROOT,env=env,check=True)

def main():
    p=argparse.ArgumentParser(); p.add_argument('--config',default='code/configs/experiment_manifest.yaml'); p.add_argument('--smoke',action='store_true'); args=p.parse_args()
    env=os.environ.copy(); env['PYTHONPATH']=str(ROOT/'code/src')
    run([PYTHON,'code/scripts/validate_data.py','--config',args.config],env)
    run([PYTHON,'-m','pytest','code/tests','-q'],env)
    if args.smoke:
        run([PYTHON,'experiments/run_strengthened_experiments.py','--mode','smoke','--datasets','covid','--output-dir','/tmp/sepaware-augmentation-smoke'],env)
        run([PYTHON,'code/scripts/run_tstr.py','--config',args.config,'--tasks','covid_mortality','--smoke','--output-dir','/tmp/sepaware-tstr-smoke'],env)
        return
    run([PYTHON,'experiments/run_strengthened_experiments.py','--mode','full','--epochs','30','--datasets','covid','vigitel','vigitel_smoking','kidney_mortality','--output-dir','results/raw'],env)
    run([PYTHON,'code/scripts/run_tstr.py','--config',args.config],env)
    run([PYTHON,'code/scripts/run_statistics.py'],env)
    run([PYTHON,'code/scripts/build_tables.py'],env)
    run([PYTHON,'code/scripts/build_figures.py'],env)
    run([PYTHON,'code/scripts/check_consistency.py'],env)

if __name__=='__main__': main()
