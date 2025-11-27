# llm_gemini_api.py
import os
import google.generativeai as genai
from dotenv import load_dotenv
# Make sure to import the specific exceptions
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable, InternalServerError

# Load your API key from opapi.env file
load_dotenv("opapi.env")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize the client
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

def generate_financial_advice(prompt, persona):
    """
    Generates personalized financial advice using only the
    Gemini 2.5 Flash model.
    """
    if not GOOGLE_API_KEY:
        return "⚠️ Missing Google API key. Please add GOOGLE_API_KEY to your opapi.env file."

    try:
        # System instructions for the bot's behavior
        system_instruction = (
            "You are FinBot, an intelligent and friendly AI financial advisor.\n"
            "Provide practical and trustworthy financial guidance. "
            "Include actionable steps, keep it concise, and explain why each suggestion helps. "
            "Use a polite and supportive tone."
        )
        
        # The user's specific request
        user_prompt = (
            f"Persona: {persona}\n"
            f"User Question: {prompt}"
        )

        # --- Initialize the single model: Gemini 2.5 Flash ---
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",  # <-- Only using this model
            system_instruction=system_instruction,
            generation_config={
                # --- 'max_output_tokens' line REMOVED ---
                "temperature": 0.7
            }
        )

        # Generate the content
        response = model.generate_content(user_prompt)

        # --- Robustness Check (Handles Safety Blocks) ---
        
        if not response.candidates:
            return f"❌ Error: Generation failed. The prompt was likely blocked. Feedback: {response.prompt_feedback}"

        finish_reason = response.candidates[0].finish_reason
        
        if finish_reason.value != 1: # 1 = STOP
            return (
                f"❌ Error: Response was blocked by the API.\n"
                f"Reason: **{finish_reason.name}** (Code: {finish_reason.value})"
            )

        return response.text.strip()

    # --- Catch API errors or other problems ---
    except (ResourceExhausted, ServiceUnavailable, InternalServerError) as e1:
        # This is the "offline" fallback message
        return (
            "⚠️ FinBot is currently offline (API quota exceeded or unavailable).\n\n"
            "Here are some general money-saving strategies:\n"
            "• Track expenses weekly to identify unnecessary spending.\n"
            "• Apply the 50-30-20 rule: 50% needs, 30% wants, 20% savings.\n"
            "• Automate savings transfers at the start of each month.\n"
            "• Cook at home and limit take-outs.\n"
            "• Avoid impulse purchases — wait 24 hrs before buying.\n"
            "• Set a specific monthly savings goal and monitor progress."
        )

    except Exception as e:
        return f"❌ Error generating advice: {repr(e)}"

# --- Example of how to run it (optional) ---
if __name__ == "__main__":
    test_persona = "A 25-year-old software developer with some student debt."
    test_prompt = "How can I start investing while still paying off my loans?"
    
    print("--- Generating Advice ---")
    advice = generate_financial_advice(test_prompt, test_persona)
    print(advice)