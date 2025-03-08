import streamlit as st
import requests
from llm import answer, generate_detailed_summary, generate_concise_summary, generate_fun_summary, generate_section_summary, extract_sections

# Function to get YouTube transcript
def get_transcript(video_id):
    url = f"https://yt.vl.comp.polyu.edu.hk/transcript?password=for_demo&video_id={video_id}"
    response = requests.get(url)
    response.raise_for_status()
    transcript_data = response.json()
    transcript = " ".join([item['text'] for item in transcript_data['transcript']])
    return transcript, transcript_data['transcript']

# Function to format timestamp
def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

# Function to evenly distribute section start times
def distribute_section_times(transcript_data, num_sections):
    total_duration = transcript_data[-1]['start']
    interval = total_duration / num_sections
    section_times = [i * interval for i in range(num_sections)]
    return section_times

# Streamlit app
st.title("YouTube Summarizer")

# Layout with two columns
col1, col2 = st.columns([1, 3])

with col1:
    # Input YouTube URL
    video_url = st.text_input("Enter YouTube URL")
    video_id = video_url.split("v=")[-1] if "v=" in video_url else None

    # Language selection
    language = st.selectbox("Select summary language", ["en", "zh-TW", "zh-CN"])

    # Model type selection
    model_type = st.selectbox("Select model type", ["github", "openrouter"])

    # Generate summary button
    if st.button("Generate Summary"):
        if video_id:
            with st.spinner("Fetching transcript..."):
                transcript, transcript_data = get_transcript(video_id)

            system_prompt = f"Generate a summary report with subheadings for the following transcript in {language}. Each section should correspond to a subheading and should not be too short. The report should use subheadings and standardized typesetting to make the main text clearer."
            user_prompt = transcript

            with st.spinner("Generating summary..."):
                summary = generate_section_summary(transcript, language, model_type)

            sections, section_titles = extract_sections(summary)
            section_summaries = {i: section for i, section in enumerate(sections)}

            # Distribute section start times evenly
            section_times = distribute_section_times(transcript_data, len(sections))

            st.session_state['section_summaries'] = section_summaries
            st.session_state['section_titles'] = section_titles
            st.session_state['transcript_data'] = transcript_data
            st.session_state['section_times'] = section_times

if 'section_summaries' in st.session_state:
    section_summaries = st.session_state['section_summaries']
    section_titles = st.session_state['section_titles']
    transcript_data = st.session_state['transcript_data']
    section_times = st.session_state['section_times']

    with col2:
        section_keys = list(section_summaries.keys())
        section_index = st.slider("Select Section", 0, len(section_keys) - 1, 0)

        i = section_keys[section_index]
        section = section_summaries[i]
        start_time = format_timestamp(section_times[i])
        end_time = format_timestamp(section_times[section_index + 1]) if section_index + 1 < len(section_keys) else None
        st.markdown(f"### **{section_titles[i]}** [{start_time}](https://www.youtube.com/watch?v={video_id}&t={int(section_times[i])})")
        section_text = st.text_area(f"Section {i+1} Summary", section, key=f"section_{i}")
        section_summaries[i] = section_text

        # Save button
        if st.button("Save", key=f"save_{i}"):
            st.session_state['section_summaries'][i] = section_text

        # More buttons
        col_buttons = st.columns(3)
        with col_buttons[0]:
            if st.button("More Details", key=f"more_details_{i}"):
                section_summaries[i] = generate_detailed_summary(transcript_data[i]['text'], language, model_type)
                st.session_state['section_summaries'] = section_summaries
                
        with col_buttons[1]:
            if st.button("More Concise", key=f"more_concise_{i}"):
                section_summaries[i] = generate_concise_summary(transcript_data[i]['text'], language, model_type)
                st.session_state['section_summaries'] = section_summaries
               
        with col_buttons[2]:
            if st.button("More Fun", key=f"more_fun_{i}"):
                section_summaries[i] = generate_fun_summary(transcript_data[i]['text'], language, model_type)
                st.session_state['section_summaries'] = section_summaries
                

        with st.expander(f"Show transcript for Section {i+1}"):
            for item in transcript_data:
                if section_times[i] <= item['start'] < (section_times[section_index + 1] if section_index + 1 < len(section_keys) else float('inf')):
                    st.write(f"{format_timestamp(item['start'])} - {item['text']}")

    if st.button("Download Summary as HTML"):
        html_content = "<html><body>"
        for i, section in section_summaries.items():
            start_time = format_timestamp(section_times[i])
            html_content += f"<h3><a href='https://www.youtube.com/watch?v={video_id}&t={int(section_times[i])}'>{start_time}</a></h3>"
            html_content += f"<p>{section}</p>"
        html_content += "</body></html>"
        st.download_button("Download HTML", data=html_content, file_name="summary.html", mime="text/html")
else:
    st.error("Please generate a summary first.")
