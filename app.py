import streamlit as st
import requests
from llm import answer

# Function to get YouTube transcript
def get_transcript(video_id):
    url = f"https://yt.vl.comp.polyu.edu.hk/transcript?password=for_demo&video_id={video_id}"
    response = requests.get(url)
    response.raise_for_status()
    transcript_data = response.json()
    transcript = " ".join([item['text'] for item in transcript_data['transcript']])
    return transcript

# Streamlit app
st.title("YouTube Summarizer")

# Layout with two columns
col1, col2 = st.columns([1, 2])

with col1:
    # Input YouTube URL
    video_url = st.text_input("Enter YouTube URL")
    video_id = video_url.split("v=")[-1] if "v=" in video_url else None

    # Language selection
    language = st.selectbox("Select summary language", ["en", "zh-TW", "zh-CN"])

    # Generate summary button
    if st.button("Generate Summary"):
        if video_id:
            with st.spinner("Fetching transcript..."):
                transcript = get_transcript(video_id)

            system_prompt = f"Summarize the following transcript in {language};The report should use subheadings and standardized typesetting to make the main text clearer."
            user_prompt = transcript

            with st.spinner("Generating summary..."):
                summary = answer(system_prompt, user_prompt, model_type="github")

            with col2:
                with st.expander("Show Prompt"):
                    st.write("**System Prompt:**", system_prompt)
                    st.write("**User Prompt:**", user_prompt)

                with st.expander("Show LLM Output"):
                    st.write("**LLM Output:**", summary)
                    st.subheader("Summary")
                    st.write(summary)
        else:
            st.error("Invalid YouTube URL")
