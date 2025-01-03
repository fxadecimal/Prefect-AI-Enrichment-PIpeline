import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(".env")
OPENAI_KEY = os.getenv("OPENAI_KEY")

client = OpenAI(api_key=OPENAI_KEY)


def get_openai_completion(
    prompt, system_prompt="You are a helpful assistant", model="gpt-3.5-turbo"
):

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]

    inputs = dict(model=model, messages=messages, temperature=0.7, max_tokens=100)
    response = client.chat.completions.create(**inputs)

    return response.choices[0].message.content, inputs, response.model_dump()


if __name__ == "__main__":
    prompt = "What is the meaning of life?"
    completion, inputs, response = get_openai_completion(prompt)
    print(completion)
    print(inputs)
    print(response)
