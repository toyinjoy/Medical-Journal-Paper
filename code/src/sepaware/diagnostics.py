from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist
from scipy.stats import ks_2samp
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler


def fidelity(real: pd.DataFrame, synthetic: pd.DataFrame, numerical: list[str], categorical: list[str], seed: int) -> dict[str,float]:
    scores=[]
    for c in numerical: scores.append(1.0-ks_2samp(real[c],synthetic[c]).statistic)
    for c in categorical:
        levels=sorted(set(real[c]).union(set(synthetic[c]))); rp=real[c].value_counts(normalize=True).reindex(levels,fill_value=0); sp=synthetic[c].value_counts(normalize=True).reindex(levels,fill_value=0)
        scores.append(1.0-0.5*np.abs(rp-sp).sum())
    marginal=float(np.mean(scores))
    rc=real[numerical+categorical].corr(numeric_only=True).fillna(0); sc=synthetic[numerical+categorical].corr(numeric_only=True).fillna(0)
    correlation=float(1.0-np.abs(rc-sc).to_numpy().mean()/2.0)
    n=min(len(real),len(synthetic)); combined=pd.concat([real.sample(n=n,random_state=seed),synthetic.sample(n=n,random_state=seed)],ignore_index=True)
    labels=np.r_[np.zeros(n),np.ones(n)]; x=pd.get_dummies(combined[numerical+categorical],columns=categorical).fillna(0)
    model=RandomForestClassifier(n_estimators=150,min_samples_leaf=3,random_state=seed,n_jobs=1)
    prob=cross_val_predict(model,x,labels,cv=StratifiedKFold(3,shuffle=True,random_state=seed),method='predict_proba')[:,1]
    return {'marginal_similarity':marginal,'correlation_similarity':correlation,'detection_auroc':float(roc_auc_score(labels,prob))}


def structure_privacy(real_train,real_test,synthetic,features,target):
    syn=synthetic.loc[synthetic[target].eq(1)]; test=real_test.loc[real_test[target].eq(1)]
    scaler=StandardScaler().fit(real_train[features]); train_x=scaler.transform(real_train[features]); test_x=scaler.transform(real_test[features]); all_syn=scaler.transform(synthetic[features]); syn_x=scaler.transform(syn[features])
    coverage=float(NearestNeighbors(n_neighbors=1).fit(syn_x).kneighbors(test_x,return_distance=True)[0].mean())
    diversity=float(np.mean(pdist(syn_x[:min(1000,len(syn_x))]))) if len(syn_x)>1 else 0.0
    nearest=NearestNeighbors(n_neighbors=1).fit(train_x).kneighbors(all_syn,return_distance=True)[0].ravel(); exact=float(np.mean(nearest<1e-10))
    nn=NearestNeighbors(n_neighbors=1).fit(all_syn); member=nn.kneighbors(train_x,return_distance=True)[0].ravel(); nonmember=nn.kneighbors(scaler.transform(real_test[features]),return_distance=True)[0].ravel()
    membership=float(roc_auc_score(np.r_[np.ones(len(member)),np.zeros(len(nonmember))],-np.r_[member,nonmember]))
    return {'coverage_distance':coverage,'diversity':diversity,'exact_match_rate':exact,'membership_proxy_auroc':membership}
