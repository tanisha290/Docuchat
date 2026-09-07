"""
Wraps Gemini's generation API for producing the final chat answer.
"""
import time
import google.generativeai as genai

from config import GEMINI_API_KEY, GEMINI_GENERATION_MODEL

genai.configure(api_key=GEMINI_API_KEY)

MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2

SYSTEM_INSTRUCTION = (
    "You are DocuChat, an assistant that answers questions strictly using the "
    "provided document context and prior conversation. If the answer is not "
    "contained in the context, say clearly that the document doesn't seem to "
    "cover that, rather than guessing. Be concise and direct."
)


def generate_answer(context_text, history_text, question):
    prompt = (
        f"Relevant document context:\n{context_text}\n\n"
        f"Conversation so far:\n{history_text}\n\n"
        f"Current question:\n{question}\n\n"
        "Answer using only the context above."
    )

    model = genai.GenerativeModel(
        model_name=GEMINI_GENERATION_MODEL,
        system_instruction=SYSTEM_INSTRUCTION,
    )

    last_err = None
    for attempt in range(MAX_RETRIES):
        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:  # noqa: BLE001 - retry on any transient error
            last_err = e
            time.sleep(RETRY_BACKOFF_SECONDS * (attempt + 1))

    raise RuntimeError(f"Gemini generation call failed after {MAX_RETRIES} attempts: {last_err}")
