import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import re
from nltk.corpus import wordnet
from plotly.colors import n_colors

SYSTEM_PROMPTS= {
    "generic_prompts": [
        "You are a child of 3 years old learning about the world.",
        "You are a child of 5 years old learning about the world.",
        "You are a child of 8 years old learning in elementary school.",
        "You are a child of 12 years old learning in middle school.",
        "You are a teenager of 15 years old learning in high school.",
        "You are a teenager of 18 years old learning in college.",
        "You are a young adult of 22 years old learning in university.",
        "You are a young adult of 25 years old learning in graduate school.",
        "You are a young adult of 30 years old learning in a professional setting.",
        "You are a middle-aged adult of 40 years old learning in a professional setting.",
        "You are a middle-aged adult of 50 years old working in a professional setting.",
        "You are a middle-aged adult of 60 years old working in a professional setting.",
        "You are a senior of 70 years old who is now retired.",

        "You are a teacher explaining the concept of abstraction and concreteness to a class of 5th grade students.",
        "You are a researcher studying the concept of abstraction and concreteness in language.",
        "You are an expert linguist analysing the abstraction and concreteness of words.",

        "You are a poet trying to find the perfect words to describe a feeling.",
        "You are a writer trying to find the perfect words to describe a scene.",
    ],
    "female_prompts":
        [
        "You are a girl of 3 years old learning about the world.",
        "You are a girl of 5 years old learning about the world.",
        "You are a girl of 8 years old learning in elementary school.",
        "You are a girl of 12 years old learning in middle school.",
        "You are a female teenager of 15 years old learning in high school.",
        "You are a female teenager of 18 years old learning in college.",
        "You are a young woman of 22 years old learning in university.",
        "You are a young woman of 25 years old learning in graduate school.",
        "You are a young woman of 30 years old learning in a professional setting.",
        "You are a middle-aged woman of 40 years old learning in a professional setting.",
        "You are a middle-aged woman of 50 years old working in a professional setting.",
        "You are a middle-aged woman of 60 years old working in a professional setting.",
        "You are a senior woman of 70 years old who is now retired.",

        "You are a female teacher explaining the concept of abstraction and concreteness to a class of 5th grade students.",
        "You are a female researcher studying the concept of abstraction and concreteness in language.",
        "You are a female expert linguist analysing the abstraction and concreteness of words.",

        "You are a female poet trying to find the perfect words to describe a feeling.",
        "You are a female writer trying to find the perfect words to describe a scene.",
    ],
    "male_prompts": [
        "You are a boy of 3 years old learning about the world.",
        "You are a boy of 5 years old learning about the world.",
        "You are a boy of 8 years old learning in elementary school.",
        "You are a boy of 12 years old learning in middle school.",
        "You are a male teenager of 15 years old learning in high school.",
        "You are a male teenager of 18 years old learning in college.",
        "You are a young man of 22 years old learning in university.",
        "You are a young man of 25 years old learning in graduate school.",
        "You are a young man of 30 years old learning in a professional setting.",
        "You are a middle-aged man of 40 years old learning in a professional setting.",
        "You are a middle-aged man of 50 years old working in a professional setting.",
        "You are a middle-aged man of 60 years old working in a professional setting.",
        "You are a senior man of 70 years old who is now retired.",

        "You are a male teacher explaining the concept of abstraction and concreteness to a class of 5th grade students.",
        "You are a male researcher studying the concept of abstraction and concreteness in language.",
        "You are a male expert linguist analysing the abstraction and concreteness of words.",

        "You are a male poet trying to find the perfect words to describe a feeling.",
        "You are a male writer trying to find the perfect words to describe a scene.",
    ],
}

USER_PROMPTS=[
    "Construct a list of single word concepts around the word: {word}. "
    "The bullets before the word {word} have to be increasingly more generic while those after the word {word} increasingly more specific. "
    "Make it look like one list."
]

def get_random_prompt(word):
    out =  [
        {"role":"system", "content":SYSTEM_PROMPTS[0]},
        {"role":"user", "content":USER_PROMPTS[0].format(word=word)}
    ]
    print(out)
    return out


def get_all_prompts(words):
    return [
        [
            [
                {"role": "system", "content": i},
                {"role": "user", "content": USER_PROMPTS[0].format(word=word)}
            ]
            for word in words
        ]
        for j in SYSTEM_PROMPTS.values() for i in j
    ]

def get_closure_size(word):
    hypernym_closure = lambda s: s.hypernyms()
    ss = wordnet.synsets(word, pos="n")
    if len(ss) == 0:
        return 0
    ss = ss[0]

    closure = list(ss.closure(hypernym_closure))
    closure_size = len(closure)
    return closure_size

def get_bubble_plot(_plot_data, size_factor=500):
    plot_data = _plot_data.to_numpy()
    fig, ax = plt.subplots(1,1, figsize=(10, 10), dpi=150)

    # Get the dimensions of the data
    rows, cols = plot_data.shape

    # Create a meshgrid for the bubble positions
    x = np.arange(cols)
    y = np.arange(rows)
    X, Y = np.meshgrid(x, y)

    # Flatten the arrays to pass to scatter
    X = X.flatten()
    Y = Y.flatten()
    sizes = plot_data.flatten() * size_factor  # Adjust size scaling as needed

    # Create a scatter plot with bubbles
    # plt.figure(figsize=(8, 8))
    scatter = ax.scatter(X, Y, s=sizes, c=plot_data.flatten(), cmap='viridis', alpha=0.6)

    # Reverse the y-axis to match heatmap orientation
    ax.invert_yaxis()
    ax.set_xticks(np.arange(cols))
    ax.set_xticklabels(list(_plot_data.columns), rotation=90,)
    ax.set_yticks(np.arange(cols))
    ax.set_yticklabels(list(_plot_data.index), rotation=0)

    fig.colorbar(scatter, ax=ax, label='Intensity')
    return fig

def get_violin_plot(prompts, out_name):
    fig = go.Figure()
    colors = n_colors('rgb(30, 19, 217)', 'rgb(255, 0, 39)', 18, colortype='rgb')
    for (prompt, _specs), color in zip(prompts.items(), colors):
        _specs_corr = [i["list_spec_corr"] for i in _specs if i is not None and not (isinstance(i, float) and np.isnan(i))]
        age = re.search(r"\d+ ", prompt)
        trace_name = "Age " + age.group(0) if age is not None else prompt[:20]
        fig.add_trace(go.Violin(x=np.array(_specs_corr), line_color=color, name=trace_name))

    fig.update_traces(orientation='h', side="positive", width=3, points=False)
    fig.update_layout(
            # width=500, height=500, margin=dict(l=20, r=20, t=20, b=20), yaxis_showgrid=True, yaxis_gridwidth=0.25,
            # yaxis_zeroline=True, yaxis_zerolinecolor="gray", yaxis_gridcolor="gray", yaxis_dtick=0.25, xaxis_showgrid=False, 
            # xaxis_gridcolor="gray", xaxis_dtick=0.1, xaxis_zeroline=True, showlegend=False
            xaxis_showgrid=False, xaxis_zeroline=False, showlegend=False)

    # fig.show(width=100, height=100)
    fig.write_image(out_name)
    fig.write_image(out_name.replace("pdf", "png"))
    return fig

def get_box_plot(prompts, out_name):
    fig = go.Figure()
    colors = n_colors('rgb(30, 19, 217)', 'rgb(255, 0, 39)', 18, colortype='rgb')
    for (prompt, _specs), color in zip(prompts.items(), colors):
        _specs_corr = [i["list_spec_corr"] for i in _specs if i is not None and not (isinstance(i, float) and np.isnan(i))]
        age = re.search(r"\d+ ", prompt)
        trace_name = "Age " + age.group(0) if age is not None else prompt[:20]
        fig.add_trace(go.Box(y=np.array(_specs_corr), line_color=color, name=trace_name))

    fig.update_traces(orientation='v', width=0.5)
    fig.update_layout(
            width=500, height=500, margin=dict(l=20, r=20, t=20, b=20), yaxis_showgrid=True, yaxis_gridwidth=0.25,
            yaxis_zeroline=True, yaxis_zerolinecolor="gray", yaxis_gridcolor="gray", yaxis_dtick=0.25, xaxis_showgrid=False, 
            xaxis_gridcolor="gray", xaxis_dtick=0.1, xaxis_zeroline=True, showlegend=False)

    # fig.show(width=100, height=100)
    fig.write_image(out_name)
    fig.write_image(out_name.replace("pdf", "png"))
    return fig

def _rename_no_age(i):
    ids = ["poet", "writer", "linguist", "teacher", "researcher"]
    gends = ["female", "male",]
    new_i = ""
    for id in ids:
        if id in i:
            new_i += id
    for gend in gends:
        if gend in i:
            new_i += "_"
            new_i += gend
            break
    return new_i

def _rename_age(i):
    ids = [str(i) for i in [3, 5, 8, 12, 15, 18, 20, 22, 25, 30, 40, 50, 60, 70][::-1]]
    male_attrs = ["male", "boy", "man"]
    female_attrs = ["female", "girl", "woman", "womnan"]
    new_i = ""
    for id in ids:
        if id in i:
            new_i += id
            break
    found = False
    for gend in female_attrs:
        if gend in i:
            new_i += " female"
            found = True
            break
    if not found:
        for gend in male_attrs:
            if gend in i:
                new_i += " male"
                break

    return new_i

def rename(pvals, kind="age"):

    pvals_renamed = {}
    for i in pvals:
        new_i = _rename_age(i) if kind == "age" else _rename_no_age(i)
        if new_i not in pvals_renamed:
            pvals_renamed[new_i] = {}
        for j in pvals[i]:
            new_j = _rename_age(j) if kind == "age" else _rename_no_age(j)
            pvals_renamed[new_i][new_j] = pvals[i][j]
    return pvals_renamed