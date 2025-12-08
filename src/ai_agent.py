import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load the API key from .env
load_dotenv()

client = OpenAI(
    # This is the default and can be omitted if the env var is named OPENAI_API_KEY
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def get_recipient_email(name):
    """Looks up a name in contacts.json"""
    try:
        # Go up one level to find contacts.json
        file_path = os.path.join(os.path.dirname(__file__), '..', 'contacts.json')
        with open(file_path, 'r') as f:
            contacts = json.load(f)
            
        # Case-insensitive search
        name_lower = name.lower()
        # Create a dictionary where keys are lowercase for searching
        contacts_lower = {k.lower(): v for k, v in contacts.items()}
        
        return contacts_lower.get(name_lower)
    except Exception as e:
        return None

def generate_email_draft(recipient_name, short_context, tone="Formal"):
    """Uses OpenAI to draft an email with a specific tone."""
    
    prompt = f"""
    You are a professional email assistant.
    
    Task: Write an email based on the context below.
    Recipient Name: {recipient_name}
    Context/Intent: {short_context}
    
    Requirements:
    - Tone: {tone}
    - Structure: Valid JSON format with two keys: "subject" and "body".
    - The "body" should be the email content only (no subject in the body).
    - Sign off as "Best regards, Shramanth".
    """

    try:
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-3.5-turbo",
            response_format={ "type": "json_object" } # Crucial: forces valid JSON back
        )
        
        # Parse the JSON response
        response_content = completion.choices[0].message.content
        email_data = json.loads(response_content)
        
        return email_data['subject'], email_data['body']
    
    except Exception as e:
        return "Error", f"Failed to generate draft: {str(e)}"

# --- TEST BLOCK ---
if __name__ == "__main__":
    print("Testing AI Agent...")
    # Test with a different tone to see if it works
    subj, body = generate_email_draft("Alice", "Lets grab lunch tomorrow", tone="Casual")
    print(f"Subject: {subj}")
    print(f"Body:\n{body}")