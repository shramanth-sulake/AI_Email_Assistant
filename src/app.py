import streamlit as st
import ai_agent
import email_sender
import time

# --- Page Config ---
st.set_page_config(page_title="Ghostwriter AI", page_icon="✉️")

st.title("✉️ Ghostwriter AI")
st.markdown("### Your Professional Email Assistant")

# --- SECTION 0: State & Reset Logic (THE FIX) ---
# We handle the reset here, BEFORE any widgets are drawn on the screen.

if 'email_sent_trigger' not in st.session_state:
    st.session_state.email_sent_trigger = False

# If the flag is set to True (from the previous run), we clear everything now
if st.session_state.email_sent_trigger:
    # 1. Show the success message
    st.toast("✅ Mail sent successfully!", icon="🚀")
    
    # 2. Reset all the inputs
    st.session_state.recipient_input = ""
    st.session_state.context_input = ""
    
    # 3. Clear the internal logic state
    st.session_state.draft_subject = ""
    st.session_state.draft_body = ""
    st.session_state.recipient_email = ""
    
    # 4. Turn off the trigger so it doesn't happen again next time
    st.session_state.email_sent_trigger = False

# Initialize state variables if they don't exist
if 'draft_subject' not in st.session_state:
    st.session_state.draft_subject = ""
if 'draft_body' not in st.session_state:
    st.session_state.draft_body = ""
if 'recipient_email' not in st.session_state:
    st.session_state.recipient_email = ""

# --- SECTION 1: User Input ---
with st.container():
    col1, col2 = st.columns([1, 2])
    
    with col1:
        recipient_name = st.text_input("Who is this for?", placeholder="e.g. Alice", key="recipient_input")
    
    with col2:
        if recipient_name:
            found_email = ai_agent.get_recipient_email(recipient_name)
            if found_email:
                st.success(f"Found: {found_email}")
                st.session_state.recipient_email = found_email
            else:
                st.error("Contact not found.")
                st.session_state.recipient_email = ""

    email_context = st.text_area("What do you want to say?", height=100, 
                                 placeholder="e.g. Tell Bob I need the report...", 
                                 key="context_input")

    email_tone = st.selectbox("Tone", ["Formal", "Casual", "Urgent", "Friendly"], key="tone_input")

    if st.button("✨ Generate Draft"):
        if not st.session_state.recipient_email:
            st.error("Please enter a valid contact name first.")
        elif not email_context:
            st.warning("Please provide some context.")
        else:
            with st.spinner("Drafting your email..."):
                subject, body = ai_agent.generate_email_draft(recipient_name, email_context, email_tone)
                st.session_state.draft_subject = subject
                st.session_state.draft_body = body
                st.rerun()

# --- SECTION 2: Human Review ---
if st.session_state.draft_body:
    st.markdown("---")
    st.subheader("📝 Review & Edit")
    
    final_subject = st.text_input("Subject Line", value=st.session_state.draft_subject)
    final_body = st.text_area("Email Body", value=st.session_state.draft_body, height=300)

    col_send, col_cancel = st.columns([1, 4])
    
    with col_send:
        if st.button("🚀 Send Email", type="primary"):
            with st.spinner("Sending..."):
                success, message = email_sender.send_email(
                    st.session_state.recipient_email, 
                    final_subject, 
                    final_body
                )
                
                if success:
                    # THE CHANGE: Instead of clearing here, we flip the switch and rerun.
                    st.session_state.email_sent_trigger = True
                    st.rerun()
                else:
                    st.error(f"Failed to send: {message}")
    
    with col_cancel:
        if st.button("❌ Discard"):
            st.session_state.draft_subject = ""
            st.session_state.draft_body = ""
            st.rerun()