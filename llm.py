import json, os, toml
from openai import OpenAI
import streamlit as st

# Load API key from credentials.txt or secrets manager
file_path = 'credentials'
if os.path.exists(file_path):
    with open(file_path, 'r') as f:
        secrets = toml.load(f)
else:
    try:
        secrets = st.secrets
    except Exception:
        secrets_path = os.path.join(os.path.expanduser("~"), ".streamlit", "secrets.toml")
        if os.path.exists(secrets_path):
            with open(secrets_path, 'r') as f:
                secrets = toml.load(f)
        else:
            secrets_path = os.path.join("/workspaces/youtube-summarizer-IVANSU04/.streamlit", "secrets.toml")
            if os.path.exists(secrets_path):
                with open(secrets_path, 'r') as f:
                    secrets = toml.load(f)
            else:
                raise FileNotFoundError("No secrets found. Valid paths for a secrets.toml file or secret directories are: /home/codespace/.streamlit/secrets.toml, /workspaces/youtube-summarizer-IVANSU04/.streamlit/secrets.toml")

def get_api_details(model_type):
    if model_type == "github":
        endpoint = os.getenv("GITHUB_API_ENDPOINT", secrets.get('GITHUB', {}).get('GITHUB_API_ENDPOINT', "https://models.inference.ai.azure.com"))
        token = os.getenv("GITHUB_API_KEY", secrets.get('GITHUB', {}).get('GITHUB_API_KEY'))
        model_name = os.getenv("GITHUB_API_MODEL_NAME", secrets.get('GITHUB', {}).get('GITHUB_API_MODEL_NAME', "gpt-4o-mini"))
    elif model_type == "openrouter":
        endpoint = os.getenv("OPENROUTER_API_ENDPOINT", secrets.get('OPENROUTER', {}).get('OPENROUTER_API_ENDPOINT', "https://openrouter.ai/api/v1"))
        token = os.getenv("OPENROUTER_API_KEY", secrets.get('OPENROUTER', {}).get('OPENROUTER_API_KEY'))
        model_name = os.getenv("OPENROUTER_API_MODEL_NAME", secrets.get('OPENROUTER', {}).get('OPENROUTER_API_MODEL_NAME', "gpt-4o-mini"))
    else:
        raise ValueError("Invalid API type")
    
    if not token:
        raise ValueError(f"{model_type.capitalize()} API key not found")
    
    return endpoint, token, model_name

def answer(system_prompt, user_prompt, model_type="github"):
    endpoint, token, model_name = get_api_details(model_type)

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
        max_tokens=10000,
        model=model_name
    )

    return response.choices[0].message.content

def generate_detailed_summary(transcript, language, model_type):
    system_prompt = f"Summarize the following transcript in {language} with a lot of details. Each section should correspond to a subheading and should not be too short. The report should use subheadings and standardized typesetting to make the main text clearer."
    user_prompt = transcript
    return answer(system_prompt, user_prompt, model_type=model_type)

def generate_concise_summary(transcript, language, model_type):
    system_prompt = f"Summarize the following transcript in {language} in a very concise manner. Each section should correspond to a subheading and should be very short. The report should use subheadings and standardized typesetting to make the main text clearer."
    user_prompt = transcript
    return answer(system_prompt, user_prompt, model_type=model_type)

def generate_fun_summary(transcript, language, model_type):
    system_prompt = f"Summarize the following transcript in {language} using fun and engaging language with emojis. Each section should correspond to a subheading and should not be too short. The report should use subheadings and standardized typesetting to make the main text clearer."
    user_prompt = transcript
    return answer(system_prompt, user_prompt, model_type=model_type)

def generate_section_summary(transcript, language, model_type):
    system_prompt = f"Generate a summary report with subheadings for the following transcript in {language}. Each section should correspond to a subheading and should not be too short. The report should use subheadings and standardized typesetting to make the main text clearer."
    user_prompt = transcript
    return answer(system_prompt, user_prompt, model_type=model_type)

def extract_sections(summary):
    sections = summary.split("\n\n")
    section_titles = [section.split("\n")[0] for section in sections]
    return sections, section_titles

# execute if the script is run directly
if __name__ == "__main__":
    # model_type = "openrouter"
    model_type = "github"
    result = answer("Answer in chinese", "What is the capital of France?", model_type)
    print(result)
