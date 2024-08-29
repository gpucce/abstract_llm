import random

SYSTEM_PROMPTS=[
    # "You are a child of 3 years old learning about the world.",
    # "You are a child of 8 years old learning in elementary school.",
    # "You are a boy of 12 years old learning in middle school.",
    # "You are a teenager of 15 years old learning in high school.",
    # "You are a teenager of 18 years old learning in college.",
    # "You are a young adult of 22 years old learning in university.",
    # "You are a young adult of 25 years old learning in graduate school.",
    # "You are a young adult of 30 years old learning in a professional setting.",
    # "You are a middle-aged adult of 40 years old learning in a professional setting.",
    # "You are a middle-aged adult of 50 years old working in a professional setting.",
    # "You are a middle-aged adult of 60 years old working in a professional setting.",
    # "You are a senior of 70 years old who is now retired.",

    # "You are a teacher explaining the concept of abstraction and concreteness to a class of 5th grad",
    # "You are a researcher studying the concept of abstraction and concreteness in language.",
    # "You are an expert linguist analysing the abstraction and concretenss of words.",

    "You are a poet trying to find the perfect words to describe a feeling.",
    "You are a writer trying to find the perfect words to describe a scene.",
]

USER_PROMPTS=[
    "Construct a list of words around the word: {word}. "
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
        for i in SYSTEM_PROMPTS
    ]