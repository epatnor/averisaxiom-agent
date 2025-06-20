# === File: streamlit_ui.py ===
import streamlit as st
from generator import generate_post
from db import init_db, save_post, get_pending_posts, get_setting, set_setting
from publisher import publish_to_bluesky
from config import Config

init_db()

st.image("assets/logo/averisaxiom-logo.png", width=200)
st.title("AverisAxiom Content Agent")
st.caption("Model: GPT-4o")

st.header("Settings")
def_prompt = (
    "You are AverisAxiom, a calm and thoughtful assistant helping to craft short, clear, conversational social media posts. "
    "Avoid complicated technical terms, statistics, or rhetorical questions. Use simple language that feels human, reflective, and respectful. "
    "Do not invite debate, do not ask questions to the audience. Make neutral, informative statements that are thought-provoking but not provocative. "
    "Keep each post self-contained, neutral, and friendly. Assume a well-educated but general audience."
)
current_prompt = get_setting("system_prompt", def_prompt)

new_prompt = st.text_area("System Prompt:", value=current_prompt, height=250)
if st.button("Save System Prompt"):
    set_setting("system_prompt", new_prompt)
    st.success("System Prompt saved!")

st.divider()
st.header("Post Generation")

prompt = st.text_area("Enter topic / prompt:")
draft_mode = st.checkbox("Draft Mode", value=False)

if st.button("Generate Post"):
    with st.spinner("Generating..."):
        post = generate_post(prompt, draft_mode)
        st.write("### Suggested Post:")
        st.write(post)
        if st.button("Approve & Save"):
            save_post(prompt, post)
            st.success("Post saved for publishing queue.")

st.divider()
st.header("Publishing Queue")

pending = get_pending_posts()
for post in pending:
    post_id, pr, content = post
    st.write(f"**Prompt:** {pr}")
    st.write(content)
    if st.button(f"Publish Post #{post_id}", key=post_id):
        publish_to_bluesky(post_id, content)
        st.success(f"Post #{post_id} published!")
