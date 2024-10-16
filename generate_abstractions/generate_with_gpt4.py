import os
import sys
import json
import time
from copy import deepcopy
from tqdm import tqdm
from openai import OpenAI
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))

from utils import get_random_prompt


# MODEL = "gpt-4o"
MODEL = "gpt-4o-mini"

PRICE_INPUT_PER_1M = 2.5
PRICE_OUTPUT_PER_1M = 7.5
if MODEL == "gpt-4o-mini":
    PRICE_INPUT_PER_1M = 0.075
    PRICE_OUTPUT_PER_1M = 0.3


# SYSTEM_PROMPT = """
# Act as an experienced ...
# [INSERT]
# Examples for few-shot learning are below.
# """.strip()

# USER_PROMPT = """
# [INSERT]
# """.lstrip()

# EXAMPLE_1_INPUT = """
# [INSERT]
# """.lstrip()

# EXAMPLE_2_INPUT = """
# [INSERT]
# """.lstrip()

# EXAMPLE_1_OUTPUT = """
# [INSERT]
# """.strip()

# EXAMPLE_2_OUTPUT = """
# [INSERT]
# """.strip()


if __name__ == "__main__":
    """Substitute all the [INSERT] and [INSERT ...] tags with your actual data"""



    # Load the input data. It can be any kind of iterable data, not necessarily json.
    # with open("[INSERT PATH HERE]") as f:
    #     data = json.load(f)

    my_folder = "/leonardo_scratch/large/userexternal/gpuccett/"
    models_folder = os.path.join(my_folder, "models/hf_llama/")
    data_path = os.path.join(my_folder, "datasets/Italian-Crime-News/italian_crime_news.csv")
    df = pd.read_csv(data_path, encoding="latin")

    # Load the API key
    with open("fakekey", "r") as f:
        api_key = f.readline().strip()

    # Make OpenAI client
    client = OpenAI(api_key=api_key)

    n_articles = 10
    messages = df["title"].values[:n_articles]
    ids = df["id"].values[:n_articles]
    crime_tags = df["newspaper_tag"].values[:n_articles]
    real_articles = df["text"].values[:n_articles]
    prompts = [get_random_prompt(m) for m in messages]

    # Create the file with the instances to process
    with open(f"batch_input.jsonl", "w") as f:
        for i, (prompt, message, _id, crime_tag, real_article) in enumerate(tqdm(zip(prompts, messages, ids, crime_tags, real_articles), total=len(messages))):
            
            id = str(_id)
            # Insert it into the `USER_PROMPT`

            request = {
                "custom_id": f"{id}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": MODEL,
                    "messages": prompt,
                    "max_tokens": 258,
                    "temperature": 0.0,
                },
            }
            json.dump(request, f)
            if i != len(messages) - 1:
                print(i)
                f.write("\n")
            print(f"OTHER {i}")

    print("Done with processing the data for generation.")

    # Upload the file to OpenAI

    batch_input_file = client.files.create(
        file=open(f"batch_input.jsonl", "rb"), purpose="batch"
    )

    # Create the request to OpenAI. This line will start the generation.
    # If at any point you decide to stop it (or you've launched it with
    # errors and need to relaunch it), use `client.batches.cancel(create_id)`.
    # Make sure to use the same OpenAI API key for your client
    # that you used to launch the process.

    create = client.batches.create(
        input_file_id=batch_input_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"description": f"Test GPT-4o mini on Italian"},
    )
    create_id = create.id
    print('Process id (for debugging purposes):', create_id)

    # Loop to check when the process is completed

    while True:
        batch_data = client.batches.retrieve(create_id)
        status = batch_data.status
        if status == "completed":
            content = client.files.content(batch_data.output_file_id)
            content.write_to_file(f"openai_batch_results.jsonl")
            break
        localtime = time.localtime()
        print(
            f"{localtime.tm_hour}:{localtime.tm_min}:{localtime.tm_sec}\t Status: {status}"
        )
        time.sleep(60)
    print("Done with generating the data.")

    # Load the results and potentially combine them etc.

    # outputs = []
    # with open(f"openai_batch_results.jsonl") as f:
    #     for line in f.readlines():
    #         outputs.append(json.loads(line))

    # Calculate the price and write it to the file

    # price = sum(
    #     [
    #         x["response"]["body"]["usage"]["prompt_tokens"]
    #         * PRICE_INPUT_PER_1M
    #         / 1_000_000
    #         + x["response"]["body"]["usage"]["completion_tokens"]
    #         * PRICE_OUTPUT_PER_1M
    #         / 1_000_000
    #         for x in outputs
    #     ]
    # )
    # with open(f"price.txt", "w") as f:
    #     f.write(f"Price: ${price:.2f}")