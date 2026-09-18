#!/usr/bin/env python3
import argparse, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'code'/'src'))
from sepaware.config import data_root, load_manifest, validate_source
from sepaware.data import load_task

p=argparse.ArgumentParser(); p.add_argument('--config',default=ROOT/'code/configs/experiment_manifest.yaml'); args=p.parse_args()
manifest=load_manifest(args.config); root=data_root()
for key,task in manifest['tasks'].items():
 validate_source(root/task['path'],task['sha1']); frame=load_task(key,task,root); counts=frame[task['outcome']].value_counts()
 assert int(counts.get(1,0))==task['expected_positive'] and int(counts.get(0,0))==task['expected_negative'], (key,counts.to_dict())
 print(key,len(frame),counts.to_dict())
