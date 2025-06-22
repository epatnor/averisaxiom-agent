import streamlit as st
from generator import generate_post
from db import init_db, save_post, get_setting, set_setting, DB_PATH
from publisher import publish_to_bluesky
from config import Config
import sqlite3
from atproto import Client
from daily_report import update_stats, generate_report, send_email

# Globala loggar för sessionen
if 'action_logs' not in st.session_state:
    st.session_state['action_logs'] = []

def log_action(msg):
    st.session_state['action_logs'].append(msg)
    if len(st.session_state['action_logs']) > 10:
        st.session_state['action_logs'].pop(0)

st.set_page_config(page_title="AverisAxiom Agent", page_icon="🤖", layout="wide")

init_db()

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
    new_prompt = st.text_area("System Prompt:", value=current_prompt, height=180)
    if st.button("Save System Prompt"):
        set_setting("system_prompt", new_prompt)
        st.success("System Prompt saved!")
        log_action("System prompt updated.")

col1, col2, col3 = st.columns([1,1,1])

with col1:
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
                        c.execute("UPDATE posts SET like_count = ?, repost_count = ?, reply_count = ? WHERE id = ?", 
                                  (like_count, repost_count, reply_count, post_id))
                        conn.commit()
                        conn.close()
                    except Exception as e:
                        log_action(f"Error updating post #{post_id}: {e}")
                st.success("All stats updated!")
                log_action("Stats updated from Bluesky.")
            except Exception as e:
                st.error(f"Failed to update stats: {e}")
                log_action(f"Failed to update stats: {e}")

with col2:
    if st.button("Send Daily Report Email"):
        with st.spinner("Generating and sending daily report..."):
            try:
                update_stats()
                report = generate_report()
                send_email(report)
                st.success("Daily report email sent!")
                log_action("Daily report email sent.")
            except Exception as e:
                st.error(f"Failed to send daily report email: {e}")
                log_action(f"Failed to send daily report email: {e}")

# --- Overview ---
st.divider()
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT COUNT(*), SUM(like_count), SUM(repost_count), SUM(reply_count) FROM posts WHERE status = 'published'")
total_published, total_likes, total_reposts, total_replies = c.fetchone()
conn.close()

st.markdown(
    f"✅ **Total Published:** {total_published or 0} &nbsp;&nbsp; "
    f"❤️ **Likes:** {total_likes or 0} &nbsp;&nbsp; "
    f"🔄 **Reposts:** {total_reposts or 0} &nbsp;&nbsp; "
    f"💬 **Replies:** {total_replies or 0}"
)

# --- Post Generation ---
st.divider()
st.header("Post Generation")

prompt = st.text_area("Enter topic / prompt:")

mood = st.radio("Select Post Style:", ["news", "thoughts", "questions", "raw"], index=0, horizontal=True)

if st.button("Generate Post"):
    with st.spinner("Generating..."):
        post = generate_post(prompt, False, mood)
    st.write("### Suggested Post:")
    st.write(post)
    if st.button("Approve & Save"):
        save_post(prompt, post)
        st.success("Post saved for publishing queue.")
        log_action(f"Post saved for prompt: '{prompt}'")

# --- Publishing Queue ---
st.divider()
st.header("Publishing Queue")

if st.button("Refresh Publishing Queue"):
    st.experimental_rerun()

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT id, prompt, post, status, like_count, repost_count, reply_count FROM posts ORDER BY id DESC")
posts = c.fetchall()
conn.close()

for post_id, prompt, content, status, likes, reposts, replies in posts:
    cols = st.columns([1.2, 3.5, 1, 1, 1, 1, 1])
    cols[0].write(f"#{post_id}")
    cols[1].write(f"**Prompt:** {prompt}\n\n{content}")
    cols[2].write(f"**Status:** {status}")
    cols[3].write(f"❤️ {likes}")
    cols[4].write(f"🔄 {reposts}")
    cols[5].write(f"💬 {replies}")

    if status == "pending":
        if cols[6].button(f"Publish", key=f"pub_{post_id}"):
            try:
                publish_to_bluesky(post_id, content)
                st.success(f"Post #{post_id} published!")
                log_action(f"Published post #{post_id}")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Failed to publish post #{post_id}: {e}")
                log_action(f"Failed to publish post #{post_id}: {e}")

        if cols[6].button(f"Delete", key=f"del_{post_id}"):
            try:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("DELETE FROM posts WHERE id = ?", (post_id,))
                conn.commit()
                conn.close()
                st.success(f"Post #{post_id} deleted!")
                log_action(f"Deleted post #{post_id}")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Failed to delete post #{post_id}: {e}")
                log_action(f"Failed to delete post #{post_id}: {e}")
    else:
        cols[6].write("")

# --- Action log panel ---
st.divider()
st.header("Action Log (Last 10)")

if st.session_state['action_logs']:
    for log in reversed(st.session_state['action_logs']):
        st.write(f"- {log}")
else:
    st.write("_No actions yet._")
