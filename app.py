import streamlit as st
import os
from dotenv import load_dotenv
from autoresponder import Autoresponder

load_dotenv()

# Page config
st.set_page_config(
    page_title="AI Autoresponder Demo",
    page_icon="",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
    }
    .outreach-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    .response-box {
        background-color: #e8f5e9;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #4caf50;
    }
    .category-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    .category-strong { background-color: #c8e6c9; color: #2e7d32; }
    .category-soft { background-color: #dcedc8; color: #558b2f; }
    .category-neutral { background-color: #fff9c4; color: #f9a825; }
    .category-objection { background-color: #ffe0b2; color: #ef6c00; }
    .category-no { background-color: #ffcdd2; color: #c62828; }
    .example-btn {
        margin: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='main-header'>AI Autoresponder</h1>", unsafe_allow_html=True)

st.markdown("""
This is an **AI-powered autoresponder** for cold outreach replies.

It automatically:
- **Classifies** incoming replies by intent (interested, curious, neutral, objection, hard no)
- **Generates** appropriate responses in a natural, non-salesy tone
- **Flags** messages that need manual attention

---
""")

# Sidebar for API key
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=os.getenv("OPENAI_API_KEY", ""),
        help="Enter your OpenAI API key"
    )

    calendar_link = st.text_input(
        "Calendar Link",
        value="https://cal.com/your-calendar",
        help="Your booking calendar link"
    )

    st.markdown("---")
    st.markdown("**How it works:**")
    st.markdown("""
    1. You send cold outreach
    2. Prospect replies
    3. AI classifies intent
    4. AI generates response
    """)

# Example outreach message with variables
st.subheader("Example Outreach Message")

col1, col2 = st.columns([3, 1])
with col1:
    prospect_name = st.text_input("Prospect Name", value="Dan", key="prospect_name")
with col2:
    sender_name = st.text_input("Your Name", value="Mariah", key="sender_name")

outreach_template = f"""hey {prospect_name}

your name came up on my end,

figured i'd reach out - i talk to a lot of founders and they keep saying they waste hours on things that don't move the needle.

can plug you into the deal flow if you want


best,
{sender_name}"""

st.markdown(f"<div class='outreach-box'><pre>{outreach_template}</pre></div>", unsafe_allow_html=True)

st.markdown("---")

# Test section
st.subheader("Test the Autoresponder")

st.markdown("**Click an example or type your own reply:**")

# Example reply buttons
example_replies = {
    "Interested": "Sounds interesting. Happy to learn more.",
    "Curious": "How does this work exactly?",
    "Clarification": "What company are you with?",
    "Not now": "Not a priority right now, maybe later.",
    "Hard no": "Not interested, please remove me.",
}

# Create columns for buttons
cols = st.columns(len(example_replies))
for i, (label, reply) in enumerate(example_replies.items()):
    if cols[i].button(label, key=f"btn_{label}", use_container_width=True):
        st.session_state.user_reply = reply

# Text input for custom reply
user_reply = st.text_area(
    "Prospect's Reply",
    value=st.session_state.get("user_reply", ""),
    height=100,
    placeholder="Type a reply here or click an example above...",
    key="reply_input"
)

# Update session state
if user_reply:
    st.session_state.user_reply = user_reply

# Process button
if st.button("Generate Response", type="primary", use_container_width=True):
    if not api_key:
        st.error("Please enter your OpenAI API key in the sidebar")
    elif not user_reply:
        st.warning("Please enter a reply to test")
    else:
        with st.spinner("Analyzing and generating response..."):
            try:
                responder = Autoresponder(api_key=api_key, calendar_link=calendar_link)
                result = responder.process(user_reply)

                # Store result in session
                st.session_state.last_result = result

            except Exception as e:
                st.error(f"Error: {str(e)}")

# Display result
if "last_result" in st.session_state:
    result = st.session_state.last_result

    st.markdown("---")
    st.subheader("Result")

    # Category badge
    category = result["category"]
    category_colors = {
        "STRONG_POSITIVE": "strong",
        "SOFT_POSITIVE": "soft",
        "NEUTRAL": "neutral",
        "SOFT_OBJECTION": "objection",
        "HARD_NO": "no"
    }
    color_class = category_colors.get(category, "neutral")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Category:** <span class='category-badge category-{color_class}'>{category}</span>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"**Confidence:** {result['confidence']}")
    with col3:
        if result["manual_required"]:
            st.markdown("**Manual review needed**")

    # Generated response
    st.markdown("**Generated Response:**")
    st.markdown(f"<div class='response-box'>{result['response']}</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; font-size: 0.85rem;'>
    Built for B2B outreach automation
</div>
""", unsafe_allow_html=True)
