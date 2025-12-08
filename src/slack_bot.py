import os
import logging
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Import your existing modules
import ai_agent
import email_sender

# Load environment variables
load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

# Initialize the Slack App
app = App(token=SLACK_BOT_TOKEN)

# Simple in-memory storage to remember drafts (Dictionary keyed by user_id)
# In production, use a real database (Redis/SQL)
user_sessions = {}

@app.event("app_mention")
def handle_mention(event, say):
    """Triggered when you type @Ghostwriter in Slack"""
    user_id = event["user"]
    text = event["text"]
    
    # Remove the "@Ghostwriter" part from the text to get the clean prompt
    # Format usually looks like "<@U12345> email bob..."
    clean_text = text.split(">", 1)[1].strip() if ">" in text else text

    # Check if user actually typed a command
    if not clean_text:
        say(f"Hi <@{user_id}>! Please mention me with a command. Example:\n`@Ghostwriter Email Alice regarding the project update.`")
        return

    # 1. Parsing Phase (Simplified)
    # In a real app, you might want a clearer way to separate Name vs Context.
    # For now, we assume the first word is the name if the user follows "Email [Name] [Context]"
    parts = clean_text.split(" ", 1)
    if len(parts) < 2:
        say("Please provide a name and some context. e.g., 'Email Bob I am late'.")
        return
        
    target_name = parts[0] # e.g. "Bob" (or "Email Bob" - this logic is naive but works for demos)
    if target_name.lower() == "email": # Handle "Email Bob..." vs "Bob..."
        target_name = parts[1].split(" ", 1)[0]
        context_text = parts[1].split(" ", 1)[1]
    else:
        context_text = parts[1]

    # 2. Lookup Contact
    recipient_email = ai_agent.get_recipient_email(target_name)
    
    if not recipient_email:
        say(f"❌ I couldn't find '{target_name}' in your contacts.json.")
        return

    # 3. Generate Draft
    msg = say(f"⏳ Working on it, <@{user_id}>...") # feedback message
    
    subject, body = ai_agent.generate_email_draft(target_name, context_text, tone="Formal")

    # Store in session so the button knows what to send
    user_sessions[user_id] = {
        "email": recipient_email,
        "subject": subject,
        "body": body
    }

    # 4. Send Interactive Block (The "GUI")
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Draft for {target_name}* ({recipient_email})"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Subject:* {subject}\n\n{body}"}
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "🚀 Send Email"},
                        "style": "primary", # Green button
                        "action_id": "button_send"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "❌ Cancel"},
                        "style": "danger", # Red button
                        "action_id": "button_cancel"
                    }
                ]
            }
        ],
        text="Draft ready for review" # Fallback for notifications
    )

@app.action("button_send")
def handle_send_click(ack, body, say):
    """Triggered when the green button is clicked"""
    ack() # Acknowledge the click immediately
    user_id = body["user"]["id"]
    
    if user_id not in user_sessions:
        say("⚠️ Session expired. Please try again.")
        return

    draft = user_sessions[user_id]
    
    # Execute Send
    success, msg = email_sender.send_email(draft["email"], draft["subject"], draft["body"])
    
    if success:
        # Update the original message to remove buttons and show success
        # We assume 'say' posts a new message. To update, you'd use client.chat_update (advanced).
        # For now, just posting a new success message is fine.
        say(f"✅ Email sent successfully to {draft['email']}!")
        del user_sessions[user_id] # Clear session
    else:
        say(f"❌ Failed to send: {msg}")

@app.action("button_cancel")
def handle_cancel_click(ack, body, say):
    """Triggered when the red button is clicked"""
    ack()
    user_id = body["user"]["id"]
    
    if user_id in user_sessions:
        del user_sessions[user_id]
    
    say("🚫 Draft discarded.")

if __name__ == "__main__":
    if not SLACK_APP_TOKEN:
        print("Error: SLACK_APP_TOKEN not found in .env")
        exit(1)
        
    print("⚡️ Ghostwriter Slack Bot is running...")
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()