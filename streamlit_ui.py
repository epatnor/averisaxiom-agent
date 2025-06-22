# === File: streamlit_ui.py ===

import streamlit as st
from generator import generate_post, autodetect_mood
from db import init_db, save_post, get_setting, set_setting, DB_PATH
from publisher import publish_to_bluesky, update_account_stats
from config import Config
import sqlite3
import pandas as pd
from atproto import Client
from daily_report import update_stats, generate_report, send_email

# === Safe DB init: only run once per session
if 'db_initialized' not in st.session_state:
    init_db()
    st.session_state['db_initialized'] = True

# === Action log init
if 'action_logs' not in st.session_state:
    st.session_state['action_logs'] = []

def log_action(msg):
    st.session_state['action_logs'].append(msg)
    if len(st.session_state['action_logs']) > 10:
        st.session_state['action_logs'].pop(0)

st.set_page_config(page_title="AverisAxiom Agent", page_icon="🤖", layout="wide")
st.image("assets/logo/averisaxiom-logo.png", width=100)
st.title("AverisAxiom Content Agent")
st.caption("Model: GPT-4o")

# --- SETTINGS ---
st.header("Settings")

def_prompt = (
    "You are AverisAxiom, a calm, clear, reflective AI assistant helping craft short, thoughtful, friendly social media posts "
    "for a well-educated but general audience. Avoid hype, slang, or overly casual language. Keep a professional, respectful tone."
)
current_prompt = get_setting("system_prompt", def_prompt)

with st.expander("Base Prompt Settings"):
    new_prompt = st.text_area("Base System Prompt:", value=current_prompt, height=200)
    if st.button("Save Base Prompt"):
        set_setting("system_prompt", new_prompt)
        st.success("Base Prompt saved!")
        log_action("Base prompt updated.")

col1, col2, col3 = st.columns([1,1,1])

# === Update buttons
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
                st.success("All post stats updated!")
                log_action("Post stats updated from Bluesky.")
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

with col3:
    if st.button("Update Account Stats"):
        with st.spinner("Fetching account stats from Bluesky..."):
            try:
                update_account_stats()
                st.success("Account stats updated!")
                log_action("Account stats updated.")
            except Exception as e:
                st.error(f"Failed to update account stats: {e}")
                log_action(f"Failed to update account stats: {e}")

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

# --- Account Statistics ---
st.divider()
st.header("Account Statistics")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT timestamp, followers, following, posts FROM account_stats ORDER BY timestamp ASC")
rows = c.fetchall()
conn.close()

if rows:
    df = pd.DataFrame(rows, columns=["timestamp", "followers", "following", "posts"])
    st.line_chart(df.set_index("timestamp"))
else:
    st.write("No account stats recorded yet.")

# --- Post Generation ---
st.divider()
st.header("Post Generation")

prompt = st.text_area("Enter topic / prompt:")

mood = st.radio("Select Post Style:", ["auto", "news", "thoughts", "questions", "raw"], index=0, horizontal=True)

if st.button("Generate Post"):
    with st.spinner("Generating..."):
        if mood == "auto":
            detected_mood = autodetect_mood(prompt)
            log_action(f"Auto-detected mood: {detected_mood}")
        else:
            detected_mood = mood

        post = generate_post(prompt, False, detected_mood)
        # Spara resultatet i session_state
        st.session_state['generated_post'] = post
        st.session_state['generated_prompt'] = prompt
        st.session_state['generated_mood'] = detected_mood

# Visa genererat inlägg om det finns
if 'generated_post' in st.session_state:
    st.write(f"### Suggested Post (Mood: {st.session_state['generated_mood']}):")
    st.write(st.session_state['generated_post'])
    if st.button("Approve & Save"):
        save_post(
            st.session_state['generated_prompt'],
            st.session_state['generated_post'],
            st.session_state['generated_mood']
        )
        st.success("Post saved for publishing queue.")
        log_action(f"Post saved for prompt: '{st.session_state['generated_prompt']}'")
        # Rensa state efter sparat
        del st.session_state['generated_post']
        del st.session_state['generated_prompt']
        del st.session_state['generated_mood']
        st.rerun()

# --- Publishing Queue ---
st.divider()
st.header("Publishing Queue")

if st.button("Refresh Publishing Queue"):
    st.rerun()

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT id, prompt, post, status, mood, like_count, repost_count, reply_count FROM posts ORDER BY id DESC")
posts = c.fetchall()
conn.close()

for post_id, prompt, content, status, mood_value, likes, reposts, replies in posts:
    cols = st.columns([1.2, 3.5, 1, 1, 1, 1, 1, 1])
    cols[0].write(f"#{post_id}")
    cols[1].write(f"**Prompt:** {prompt}\n\n{content}")
    cols[2].write(f"**Status:** {status}")
    cols[3].write(f"**Mood:** {mood_value}")
    cols[4].write(f"❤️ {likes}")
    cols[5].write(f"🔄 {reposts}")
    cols[6].write(f"💬 {replies}")

    if status == "pending":
        if cols[7].button(f"Publish", key=f"pub_{post_id}"):
            try:
                publish_to_bluesky(post_id, content)
                st.success(f"Post #{post_id} published!")
                log_action(f"Published post #{post_id}")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to publish post #{post_id}: {e}")
                log_action(f"Failed to publish post #{post_id}: {e}")

        if cols[7].button(f"Delete", key=f"del_{post_id}"):
            try:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("DELETE FROM posts WHERE id = ?", (post_id,))
                conn.commit()
                conn.close()
                st.success(f"Post #{post_id} deleted!")
                log_action(f"Deleted post #{post_id}")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to delete post #{post_id}: {e}")
                log_action(f"Failed to delete post #{post_id}: {e}")
    else:
        cols[7].write("")

# --- Action Log Panel ---
st.divider()
st.header("Action Log (Last 10)")

if st.session_state['action_logs']:
    for log in reversed(st.session_state['action_logs']):
        st.write(f"- {log}")
else:
    st.write("_No actions yet._")
