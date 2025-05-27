import json
import re
import smtplib
from email.mime.text import MIMEText

def extract_first_json(response_text: str):
    """
    Extracts the first valid JSON object from the response string.

    Args:
        response_text (str): The raw response from the Groq API.

    Returns:
        dict or None: The parsed JSON object or None if no valid JSON could be extracted.
    """
    try:
        # Use regex to extract the actual JSON portion of the response
        json_text = re.search(r'```json\s*(\{.*\})\s*```', response_text, re.DOTALL)
        if json_text:
            cleaned_json = json_text.group(1).strip()  # Extract and clean the JSON text
            parsed_json = json.loads(cleaned_json)  # Parse the JSON
            return parsed_json
        else:
            print("No valid JSON found in the response.")
            return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from the response: {e}")
        return None

def send_email(to: str, subject: str, body: str):
    sender = "your-email@example.com"
    password = "your-password"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, to, msg.as_string())