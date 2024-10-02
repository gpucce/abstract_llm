import json
import os
import re
from tqdm.auto import tqdm
from nltk.corpus import wordnet
from scipy.stats import pearsonr

def fix_record(x):
    try:
        _x = x["generated_text"].lower()
        seps = ["in this list", "this list", "however", "here's a brief", "note:", "note that"]
        for sep in seps:
            if sep in _x.lower():
                _x = _x.split(sep)[0]

        _x = [j.strip() for j in re.split(r"\d\.|•|\*|- ", _x)]
        _x = _x if len(_x[0].split()) == 1 else _x[1:]
        x["list"] = _x
    except:
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
    _x = x
    # old version removing 
    # _x = x[:x.index(0)] if 0 in x else x
    _idxs = [i for i, j in enumerate(_x) if j > 0]
    _x = [i for i in _x if i > 0]
    corr = None
    if len(_x) > 0 and len(set(_x)) > 1:
        corr = pearsonr(_idxs, _x)[0]
    return corr, _idxs

def normalize_score(x, _min, _max):
    return ((x - _min) / (_max - _min)) * (5.0 - 1.0) + 1.0

if __name__ == "__main__":

    import sys
    _data_path = sys.argv[1]

    _files = os.listdir(_data_path)
    _files = [_file for _file in _files if "405" in _file]

    _files = [_file for _file in _files if "linguist" in _file or " 3 " in _file or "30" in _file]

    for _file in tqdm(_files):
        with open(_data_path + "/" + _file) as jf:
            out = [json.loads(i) for i in jf.readlines()]

        out = [fix_record(i) for i in tqdm(out, desc="fix record")]

        for i in out:
            i["list_spec"] = None
            if i["list"] is not None:
                i["list_spec"] = [compute_spec(j) for j in i["list"] if j is not None]

        for i in out:
            corr, _idxs = None, None
            if i["list_spec"] is not None:
                corr, _idxs = compute_corr(i["list_spec"])
            i.update({"list_spec_corr": corr, "idxs":_idxs})

        for i in out:
            i["token_spec"] = None
            if i["list"] is not None and i["list_spec"] is not None and i["token"] in i["list"]:
                i["token_spec"] = i["list_spec"][i["list"].index(i["token"])]

        if not os.path.exists("processed_" + _data_path + "/"):
            os.makedirs("processed_" + _data_path + "/")
        with open("processed_" + _data_path + "/" + _file, "w") as jf:
            for i in out:
                jf.write(json.dumps(i) + "\n")
