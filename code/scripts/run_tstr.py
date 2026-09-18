#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold

ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'code'/'src')); sys.path.insert(0,str(ROOT/'experiments'))
from sepaware.config import data_root,load_manifest,validate_source
from sepaware.data import load_task
from sepaware.diagnostics import fidelity,structure_privacy
from sepaware.selection import SelectionConfig,score_candidates,select_by_quota
import run_strengthened_experiments as legacy


def class_generator(kind,train,features,target,label,epochs,seed):
    from sdv.metadata import SingleTableMetadata
    from sdv.single_table import TVAESynthesizer
    legacy.seed_everything(seed); subset=train.loc[train[target].eq(label),features].copy(); metadata=SingleTableMetadata(); metadata.detect_from_dataframe(subset)
    for column in features:
        if subset[column].nunique()<=10 and np.allclose(subset[column],subset[column].round()): metadata.update_column(column_name=column,sdtype='categorical')
    model=TVAESynthesizer(metadata,epochs=epochs,verbose=False,cuda=False); model.fit(subset); return model


def class_pool(kind,generator,train,features,target,label,count,multiplier):
    if kind=='CTGAN':
        from sdv.sampling import Condition
        raw=generator.sample_from_conditions([Condition({target:label},num_rows=count*multiplier)],max_tries_per_batch=500,batch_size=max(100,count*multiplier))
        return legacy.clean_generated(raw,train,features,target)
    raw=generator.sample(num_rows=count*multiplier); raw[target]=label; return legacy.clean_generated(raw,train,features,target)


def main():
    p=argparse.ArgumentParser(); p.add_argument('--config',default=ROOT/'code/configs/experiment_manifest.yaml'); p.add_argument('--tasks',nargs='*'); p.add_argument('--epochs',type=int); p.add_argument('--smoke',action='store_true'); p.add_argument('--output-dir',type=Path,default=ROOT/'results/raw'); args=p.parse_args()
    manifest=load_manifest(args.config); study=manifest['study']; root=data_root(); out=args.output_dir; out.mkdir(parents=True,exist_ok=True); rows=[]; diags=[]
    task_keys=args.tasks or list(manifest['tasks']); repeats=1 if args.smoke else study['repeats']; folds=2 if args.smoke else study['folds']; epochs=args.epochs or (2 if args.smoke else study['generator_epochs']); multiplier=2 if args.smoke else study['candidate_pool_multiplier']
    for task_key in task_keys:
        task=manifest['tasks'][task_key]; validate_source(root/task['path'],task['sha1']); raw=load_task(task_key,task,root); features=task['features']; target=task['outcome']
        for repeat in range(repeats):
            split=StratifiedKFold(folds,shuffle=True,random_state=study['partition_seeds'][repeat])
            for fold,(tr,te) in enumerate(split.split(raw,raw[target])):
                train0,test0=raw.iloc[tr],raw.iloc[te]; imputer,_=legacy.fit_fold_imputer(train0,features); train=legacy.impute_frame(train0,imputer,features,target); test=legacy.impute_frame(test0,imputer,features,target)
                cat=[c for c in task['categorical'] if c in features]; num=[c for c in features if c not in cat]
                for gi,kind in enumerate(['CTGAN','TVAE']):
                    seed=study['generator_seed_base']*(gi+1)+study['partition_seeds'][repeat]+fold*37; started=time.time()
                    joint=legacy.train_generator(kind,train,features,target,epochs,seed) if kind=='CTGAN' else None
                    pools=[]
                    for label in [0,1]:
                        quota=int(train[target].eq(label).sum()); generator=joint if joint is not None else class_generator(kind,train,features,target,label,epochs,seed+label)
                        pool=class_pool(kind,generator,train,features,target,label,quota,multiplier); pools.append(pool)
                    pool=pd.concat(pools,ignore_index=True); quotas={label:int(train[target].eq(label).sum()) for label in [0,1]}
                    standard=pd.concat([pool.loc[pool[target].eq(label)].sample(n=quota,random_state=seed+label) for label,quota in quotas.items()],ignore_index=True)
                    scored=score_candidates(pool,train,features=features,numerical=num,categorical=cat,target=target,seed=seed,config=SelectionConfig()); selected=select_by_quota(scored,target,quotas)[features+[target]]
                    for condition,syn in [(f'Standard {kind}',standard),(f'SepAware {kind}',selected)]:
                        for metric in legacy.fit_evaluate(syn,test,features,target,seed): rows.append({'dataset':task['display_name'],'task':task_key,'repeat':repeat,'fold':fold,'partition_seed':study['partition_seeds'][repeat],'generator_seed':seed,'condition':condition,'regime':'TSTR',**metric})
                        diags.append({'dataset':task['display_name'],'task':task_key,'repeat':repeat,'fold':fold,'condition':condition,'regime':'TSTR','generator_seed':seed,'seconds':time.time()-started,**fidelity(train,syn,num,cat,seed),**structure_privacy(train,test,syn,features,target)})
                    pd.DataFrame(rows).to_csv(out/'tstr_fold_metrics_checkpoint.csv',index=False); pd.DataFrame(diags).to_csv(out/'tstr_diagnostics_checkpoint.csv',index=False)
                    print(json.dumps({'task':task_key,'repeat':repeat,'fold':fold,'generator':kind}),flush=True)
    pd.DataFrame(rows).to_csv(out/'tstr_fold_metrics.csv',index=False); pd.DataFrame(diags).to_csv(out/'tstr_diagnostics.csv',index=False)

if __name__=='__main__': main()
