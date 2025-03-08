import json, os, toml
from openai import OpenAI
import streamlit as st

# Load API key from credentials.txt or secrets manager
file_path = 'credentials'
if os.path.exists(file_path):
    with open(file_path, 'r') as f:
        secrets = toml.load(f)
else:
    secrets = st.secrets


def answer(system_prompt, user_prompt, model_type="github"):
    if model_type == "github":
        print("Answer using Github API")
        endpoint = os.getenv("GITHUB_API_ENDPOINT", "https://models.inference.ai.azure.com")
        token = os.getenv("GITHUB_API_KEY", secrets.get('GITHUB', {}).get('GITHUB_API_KEY'))
        model_name = os.getenv("GITHUB_API_MODEL_NAME", "gpt-4o-mini")

        if not token:
            raise ValueError("Github API key not found")

    elif model_type == "openrouter":
        print("Answer using Openrouter API")
        endpoint = os.getenv("OPENROUTER_API_ENDPOINT", "https://openrouter.ai/api/v1")
        token = os.getenv("OPENROUTER_API_KEY", secrets.get('OPENROUTER', {}).get('OPENROUTER_API_KEY'))
        model_name = os.getenv("OPENROUTER_API_MODEL_NAME", "gpt-4o-mini")

        if not token:
            raise ValueError("OpenRouter API key not found")
    else:
        raise ValueError("Invalid API type")

    client = OpenAI(
        base_url=endpoint,
        api_key=token,
    )

    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            }
        ],
        temperature=1.0,
        top_p=1.0,
        max_tokens=1000,
        model=model_name
    )

    return response.choices[0].message.content
    
        
# execute if the script is run directly
if __name__ == "__main__":
    # model_type = "openrouter"
    model_type = "github"
    result = answer("Answer in chinese", "What is the capital of France?", model_type)
    print(result)