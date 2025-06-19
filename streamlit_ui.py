# === File: streamlit_ui.py ===
import streamlit as st
from generator import generate_post
from db import init_db, save_post, get_pending_posts
from publisher import publish_to_bluesky

init_db()

st.image("assets/logo/averisaxiom-logo.png", width=200)
st.title("AverisAxiom Content Agent")

prompt = st.text_area("Enter topic / prompt:")

if st.button("Generate Post"):
    with st.spinner("Generating..."):
        post = generate_post(prompt)
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
