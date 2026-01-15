import streamlit as st
from autoresponder import Autoresponder

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
    .cta-box {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        text-align: center;
    }
    .cta-box h3 {
        color: #1a1a1a;
        margin-top: 0;
    }
    .cta-box p {
        color: #4a4a4a;
    }
    .cta-box a {
        color: #667eea;
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

# Sidebar
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value="",
        help="Enter your OpenAI API key to test"
    )

    calendar_link = st.text_input(
        "Calendar Link",
        value="https://cal.com/your-calendar",
        help="Your booking calendar link"
    )

    st.markdown("---")

    # How it works - simple
    st.markdown("**How it works:**")
    st.markdown("""
    1. You send cold outreach
    2. Prospect replies
    3. AI classifies intent
    4. AI generates response
    """)

    st.markdown("---")

    # Expander with detailed info
    with st.expander("Why speed matters"):
        st.markdown("""
        Research shows that responding within **5 minutes** increases positive reply rates by **15-30%** compared to delayed responses.

        Leads go cold fast. This system ensures instant engagement while you focus on closing deals.
        """)

    with st.expander("Integration"):
        st.markdown("""
        Connects directly with your sending tools:
        - Instantly
        - SmartLead
        - PlusVibe
        - Lemlist
        - Any tool with webhook/API

        Also integrates with CRMs (HubSpot, Pipedrive, Close) via webhooks or Zapier/Make.
        """)

    with st.expander("Customization"):
        st.markdown("""
        Prompts are tailored to your specific service:
        - Your positioning (connector, agency, SaaS)
        - Response style and length
        - Calendar booking flow
        - Objection handling approach
        """)

    with st.expander("How it's built"):
        st.markdown("""
        The system uses **few-shot prompting** - each response category has curated examples of ideal replies that guide the AI.

        Combined with strict formatting rules (max word counts, no salesy language, no greetings), responses stay natural and on-brand.

        No robotic AI tone. Sounds like a real person wrote it.
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

# Initialize session state
if "selected_reply" not in st.session_state:
    st.session_state.selected_reply = ""

# Example reply buttons
example_replies = {
    "Let's talk": "Sure, let's chat. Send me your calendar.",
    "Curious": "Interesting. How does this work?",
    "Who is this?": "What company are you with?",
    "Not now": "Not a priority right now, maybe later.",
    "Hard no": "Not interested, please remove me.",
}

# Create columns for buttons
cols = st.columns(len(example_replies))
for i, (label, reply) in enumerate(example_replies.items()):
    if cols[i].button(label, key=f"btn_{label}", use_container_width=True):
        st.session_state.selected_reply = reply
        st.rerun()

# Text input for custom reply
user_reply = st.text_area(
    "Prospect's Reply",
    value=st.session_state.selected_reply,
    height=100,
    placeholder="Type a reply here or click an example above..."
)

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

# CTA Section
st.markdown("---")
st.markdown("""
<div class='cta-box'>
    <h3>Want to build your own sales machine?</h3>
    <p>If you want to create an automated system that generates meetings with your clients, improve your existing outreach, or just connect - reach out to Leo.</p>
    <p style='margin-bottom: 0;'>
        <strong>WhatsApp:</strong> +628175755953<br>
        <strong>Email:</strong> <a href="mailto:leo@systemhustle.com">leo@systemhustle.com</a>
    </p>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style='text-align: center; color: #888; font-size: 0.85rem; margin-top: 1rem;'>
    Built for B2B outreach automation
</div>
""", unsafe_allow_html=True)
