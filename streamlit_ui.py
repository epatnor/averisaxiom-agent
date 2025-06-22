# === File: streamlit_ui.py ===
import streamlit as st
from generator import generate_post
from db import init_db, save_post, get_pending_posts, get_setting, set_setting, DB_PATH
from publisher import publish_to_bluesky
from config import Config
import sqlite3
from atproto import Client
from daily_report import update_stats, generate_report, send_email
import os

# Streamlit sida konfiguration
st.set_page_config(
    page_title="AverisAxiom Agent",
    page_icon="🤖",
    layout="wide"
)

# Initiera databasen om den inte finns
init_db()

# Läs eventuella query params (för framtida användning)
params = st.query_params

# Logga storlek på loggan till hälften
st.image("assets/logo/averisaxiom-logo.png", width=100)

st.title("AverisAxiom Content Agent")
st.caption("Model: GPT-4o")

# --- SETTINGS ---
st.header("Settings")

def_prompt = (
    "You are AverisAxiom, a calm and thoughtful assistant helping to craft short, clear, conversational social media posts. "
    "Avoid complicated technical terms, statistics, or rhetorical questions. Use simple language that feels human, reflective, and respectful. "
    "Do not invite debate, do not ask questions to the audience. Make neutral, informative statements that are thought-provoking but not provocative. "
    "Keep each post self-contained, neutral, and friendly. Assume a well-educated but general audience."
)
current_prompt = get_setting("system_prompt", def_prompt)

with st.expander("Advanced Settings"):
    new_prompt = st.text_area("System Prompt:", value=current_prompt, height=250)
    if st.button("Save System Prompt"):
        set_setting("system_prompt", new_prompt)
        st.success("System Prompt saved!")

# --- Bluesky stats update ---
if st.button("Update Stats from Bluesky"):
    with st.spinner("Fetching stats from Bluesky..."):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT id, bluesky_uri FROM posts WHERE status = 'published' AND bluesky_uri IS NOT NULL")
            rows = c.fetchall()
            conn.close()

            client = Client()
            client.login(Config.BLUESKY_HANDLE, Config.BLUESKY_APP_PASSWORD)

            for post_id, uri in rows:
                try:
                    post = client.get_post(uri)
                    like_count = getattr(post.record, 'like_count', 0)
                    repost_count = getattr(post.record, 'repost_count', 0)
                    reply_count = getattr(post.record, 'reply_count', 0)

                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute("""
                        UPDATE posts SET like_count = ?, repost_count = ?, reply_count = ? WHERE id = ?
                    """, (like_count, repost_count, reply_count, post_id))
                    conn.commit()
                    conn.close()
                except Exception as e:
                    st.error(f"Failed to update stats for post {post_id}: {e}")
            st.success("All stats updated!")
        except Exception as e:
            st.error(f"Failed to fetch Bluesky stats: {e}")

# --- Send daily report email ---
if st.button("Send Daily Report Email"):
    with st.spinner("Generating and sending daily report..."):
        try:
            update_stats()
            report = generate_report()
            send_email(report)
            st.success("Daily report email sent!")
        except Exception as e:
            st.error(f"Failed to send daily report email: {e}")

# --- DASHBOARD ---
st.divider()
st.header("Overview Dashboard")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT COUNT(*), SUM(like_count), SUM(repost_count), SUM(reply_count) FROM posts WHERE status = 'published'")
total_published, total_likes, total_reposts, total_replies = c.fetchone()
conn.close()

total_likes = total_likes or 0
total_reposts = total_reposts or 0
total_replies = total_replies or 0

st.markdown(
    f"✅ **Total Published:** {total_published} &nbsp;&nbsp; "
    f"❤️ **Likes:** {total_likes} &nbsp;&nbsp; "
    f"🔄 **Reposts:** {total_reposts} &nbsp;&nbsp; "
    f"💬 **Replies:** {total_replies}"
)

# --- TOP POSTS ---
st.divider()
with st.expander("Advanced Statistics"):
    st.subheader("Top Performing Posts")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, prompt, post, like_count, repost_count, reply_count 
        FROM posts 
        WHERE status = 'published' 
        ORDER BY like_count DESC, repost_count DESC, reply_count DESC
        LIMIT 10
    """)
    top_posts = c.fetchall()
    conn.close()

    for post in top_posts:
        post_id, pr, content, likes, reposts, replies = post
        st.write(f"**Post #{post_id}:** {content}")
        st.write(f"❤️ Likes: {likes}   🔄 Reposts: {reposts}   💬 Replies: {replies}")
        st.divider()

# --- POST GENERATION ---
st.header("Post Generation")

prompt = st.text_area("Enter topic / prompt:")

generate_clicked = st.button("Generate Post")

# Behåll genererad post i session state för att inte förlora den mellan klick
if "generated_post" not in st.session_state:
    st.session_state.generated_post = ""

if generate_clicked:
    with st.spinner("Generating..."):
        post = generate_post(prompt, False)
        st.session_state.generated_post = post

if st.session_state.generated_post:
    st.write("### Suggested Post:")
    st.write(st.session_state.generated_post)

    # Save-knappen visas bara om det finns en post att spara
    if st.button("Approve & Save"):
        try:
            save_post(prompt, st.session_state.generated_post)
            st.success("Post saved for publishing queue.")
            # Rensa session för genererad post efter sparande
            st.session_state.generated_post = ""
        except Exception as e:
            st.error(f"Failed to save post: {e}")

# --- PUBLISHING QUEUE ---
st.divider()
st.header("Publishing Queue")

conn = sqlite3.connect(DB_PATH)
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
        if st.button(f"Publish Post #{post_id}", key=f"publish_{post_id}"):
            try:
                publish_to_bluesky(post_id, content)
                st.success(f"Post #{post_id} published!")
            except Exception as e:
                st.error(f"Failed to publish post #{post_id}: {e}")

        if st.button(f"Delete Post #{post_id}", key=f"delete_{post_id}"):
            try:
                # Ta bort inlägget från DB
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("DELETE FROM posts WHERE id = ?", (post_id,))
                conn.commit()
                conn.close()
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Failed to delete post #{post_id}: {e}")
    st.divider()

# Rensa query params efter rendering (valfritt)
st.query_params = {}
