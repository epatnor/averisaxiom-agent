# === File: streamlit_ui.py ===
import streamlit as st
from generator import generate_post
from db import init_db, save_post, get_pending_posts, get_setting, set_setting
from publisher import publish_to_bluesky
from config import Config
import sqlite3
from atproto import Client

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

if st.button("Update Stats from Bluesky"):
    with st.spinner("Fetching stats from Bluesky..."):
        conn = sqlite3.connect("posts.db")
        c = conn.cursor()
        c.execute("SELECT id, bluesky_uri FROM posts WHERE status = 'published' AND bluesky_uri IS NOT NULL")
        rows = c.fetchall()
        conn.close()

        client = Client()
        client.login(Config.BLUESKY_HANDLE, Config.BLUESKY_APP_PASSWORD)

        for post_id, uri in rows:
            try:
                post = client.get_post(uri)
                like_count = post.record.like_count if hasattr(post.record, 'like_count') else 0
                repost_count = post.record.repost_count if hasattr(post.record, 'repost_count') else 0
                reply_count = post.record.reply_count if hasattr(post.record, 'reply_count') else 0

                conn = sqlite3.connect("posts.db")
                c = conn.cursor()
                c.execute("""
                    UPDATE posts SET like_count = ?, repost_count = ?, reply_count = ? WHERE id = ?
                """, (like_count, repost_count, reply_count, post_id))
                conn.commit()
                conn.close()
            except Exception as e:
                st.error(f"Failed to update stats for post {post_id}: {e}")
        st.success("All stats updated!")

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

# Load all posts (pending + published)
conn = sqlite3.connect("posts.db")
c = conn.cursor()
c.execute("SELECT id, prompt, post, status, like_count, repost_count, reply_count FROM posts ORDER BY id DESC")
rows = c.fetchall()
conn.close()

for row in rows:
    post_id, pr, content, status, likes, reposts, replies = row
    st.write(f"**Prompt:** {pr}")
    st.write(content)
    st.write(f"**Status:** {status}")
    if status == "published":
        st.write(f"❤️ Likes: {likes}   🔄 Reposts: {reposts}   💬 Replies: {replies}")
    if status == "pending":
        if st.button(f"Publish Post #{post_id}", key=post_id):
            publish_to_bluesky(post_id, content)
            st.success(f"Post #{post_id} published!")
    st.divider()
