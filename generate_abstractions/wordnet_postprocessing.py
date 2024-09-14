import json
import os
import re
from tqdm.auto import tqdm
from nltk.corpus import wordnet
from scipy.stats import pearsonr

def fix_record(x):
    try:
        _x = x["generated_text"].lower()
        seps = ["in this list", "this list"]
        for sep in seps:
            if sep in _x.lower():
                _x = _x.split(sep)[0]
                break

        _x = [j.strip() for j in re.split("\d\.|•|\*|- ", _x)]
        _x = _x if len(_x[0].split()) == 1 else _x[1:]
        x["list"] = _x
    except:
        x["list"] = None

    if not isinstance(x["list"], list):
        x["list"] = None
    return x

def compute_spec(x):
    hypernym_closure = lambda s: s.hypernyms()
    ss = wordnet.synsets(x, pos="n")
    if len(ss) == 0:
        return 0
    ss = ss[0]
    spec = len(list(ss.closure(hypernym_closure)))
    if spec == 0:
        ss = ss.instance_hypernyms()
        if not len(ss) == 0:
            ss = ss[0]
            spec = len(list(ss.closure(hypernym_closure)))
    spec = float(5 *  spec) / float(20)
    return spec

def compute_corr(x):
    x = x[:x.index(0)] if 0 in x else x
    _idxs = list(range(len(x)))
    _idxs = [i for i,j in zip(_idxs, x) if j > 0]
    _x = [i for i in x if i > 0]
    try:
        return pearsonr(_idxs, _x)[0]
    except:
        return None

def normalize_score(x, _min, _max):
    return ((x - _min) / (_max - _min)) * (5.0 - 1.0) + 1.0

if __name__ == "__main__":

    _files = os.listdir("./gen_1")
    _files = [_file for _file in _files if "405" in _file]

    for _file in tqdm(_files):
        with open("gen_1/" + _file) as jf:
            out = [json.loads(i) for i in jf.readlines()]

        out = [fix_record(i) for i in tqdm(out)]
        out = [i for i in out if i["list"] is not None]

        for i in out:
            if i["list"] is not None:
                i["list_spec"] = [compute_spec(j) for j in i["list"] if j is not None]
            else:
                i["list_spec"] = None

        for i in out:
            if i["list_spec"] is not None:
                i["list_spec_corr"] = compute_corr(i["list_spec"])
            else:
                i["list_spec_corr"] = None

        with open("processed_gen_1/" + _file, "w") as jf:
            for i in out:
                jf.write(json.dumps(i) + "\n")