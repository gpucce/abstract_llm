import re
import os
import sys
import json
import random
import pandas as pd
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer
from argparse import ArgumentParser

sys.path.insert(0, os.path.dirname(__file__))

from utils import get_random_prompt, get_all_prompts

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--model_name", type=str, required=True,
        choices=["llama-3.1-8b-instruct-hf", "llama-3.1-70b-instruct-hf", "llama-3.1-405b-instruct-hf"])
    parser.add_argument("--n_samples", type=int, required=True, default=100)
    return parser.parse_args()

def generate(prompts, llm, params):
    return llm.generate(prompts, sampling_params=params)

def prepare_inputs(prompts, llm):
    tokenizer = llm.get_tokenizer()
    prompts = tokenizer.apply_chat_template(
        prompts, truncation=None, padding=False,
        add_generation_prompt=True)
    prompts = tokenizer.batch_decode(prompts)
    return prompts

def get_tp_and_pp_size(model_name):
    tensor_parallel_size = 1
    pipeline_parallel_size = 1
    if "70" in model_name:
        tensor_parallel_size = 4
    if "405" in model_name:
        tensor_parallel_size = 16
        pipeline_parallel_size = 1
    return tensor_parallel_size, pipeline_parallel_size

def get_vllm_llm_and_params(model_name: str, tokenizer_name: str):

    if tokenizer_name != model_name:
        print("vllm will ignore the tokenizer_name and use the same as model_name")

    params = SamplingParams(
        max_tokens=2048,
        # min_tokens=512,
        temperature=0,
        # POSSIBLE PARAMS
        # temperature=args.temperature if not args.use_beam_search else 0,
        # top_p=args.top_p if not args.use_beam_search else 1,
        # top_k=args.top_k if not args.use_beam_search else -1,
        # repetition_penalty=1.05,
        # use_beam_search=args.use_beam_search,
        # best_of=3 if args.use_beam_search else 1,
        # skip_special_tokens=True,
    )

    # this is not the right way
    tensor_parallel_size, pipeline_parallel_size = get_tp_and_pp_size(model_name)
    llm = LLM(
        model=model_name,
        tokenizer_mode="slow",
        tensor_parallel_size=tensor_parallel_size,
        # pipeline_parallel_size=pipeline_parallel_size,
        max_model_len=4096,
        enforce_eager=True)

    return llm, params

def postprocess_text(text):
    try:
        text = re.sub(r"\s+", " ", text)
    except:
        pass
    return text

if __name__ == "__main__":


    args = parse_args()
    my_folder = "/leonardo_scratch/large/userexternal/gpuccett/"
    models_folder = os.path.join(my_folder, "models/hf_llama/")
    data_path = os.path.join(my_folder, "Repos/abstact_llm/data/Scores_Conc_and_Spec_for_study1.csv")
    df = pd.read_csv(data_path)
    # df = df.loc[df.token.apply(lambda x: len(x) > 1000 if isinstance(x, str) else False), :]
    _model_name = args.model_name
    model_path = os.path.join(models_folder, _model_name)
    tok = AutoTokenizer.from_pretrained(model_path)

    n_samples = args.n_samples
    messages = df["token"].values[:n_samples]
    # prompts = [get_random_prompt(m) for m in messages]
    all_prompts = get_all_prompts(messages)

    llm, params = get_vllm_llm_and_params(model_path, model_path)

    if not os.path.exists("gender_prompts"):
        os.mkdir("gender_prompts")

    for prompts in all_prompts:
        sys_prompt = prompts[0][0]["content"]
        prompts = prepare_inputs(prompts, llm)
        output_text = generate(prompts, llm, params)

        sep = "-"*10
        prompts = []
        outputs = []
        count = 0
        with open(f"gender_prompts/generation_output_{_model_name}_{sys_prompt}.jsonl", "w") as jf:
            for output, message in zip(output_text, messages):
                count += 1
                prompt = output.prompt
                prompts.append(prompt)
                generated_text = postprocess_text(output.outputs[0].text)
                # print(sep, f"Prompt: {prompt}")
                # print(sep, f"Generated text: {generated_text}")

                to_dump = {
                    "prompt": prompt,
                    "generated_text": generated_text,
                    "token": message,
                    "source": "brysbaert",
                }

                # print(to_dump)
                jf.write(json.dumps(to_dump) + "\n")
