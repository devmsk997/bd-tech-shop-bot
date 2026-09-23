import time
from google import genai

def generate_content_with_gemini(client, prompt):
    model_name = "gemini-3.6-flash"
    max_retries = 5
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"🤖 Generating content with model: {model_name} (Attempt {attempt}/{max_retries})")
            chat = client.chats.create(model=model_name)
            response = chat.send_message(prompt)
            if response and response.text:
                return response.text
        except Exception as e:
            err_msg = str(e)
            print(f"⚠️ Error: {err_msg}")
            if "503" in err_msg or "UNAVAILABLE" in err_msg or "429" in err_msg:
                wait_time = attempt * 10
                print(f"⏳ Waiting {wait_time} seconds before retrying...")
                time.sleep(wait_time)
            else:
                time.sleep(5)
                
    raise Exception("❌ Gemini API failed after multiple attempts.")
