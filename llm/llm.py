from transformers import AutoTokenizer, AutoModelForCausalLM
from openai import OpenAI

# The ideal solution would use a self-hosted LLM due to security and sensitive data concerns.
# The OpenAI API is used as a temporary solution just to demonstrate the concept.
# For production, a self-hosted solution is recommended, such as Hugging Face's transformers library.
# Ideally this model would be hosted in another API acessible only by the main API.
# This would allow for better security and control over the model.

class OpenAILLM:
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.openai = OpenAI()
        self.model = model

    def generate_text(self, prompt: str, max_length: int = 300):
        return self.openai.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=max_length,
            temperature=0.5
        )
    
class HuggingFaceLM:
    def __init__(self, model: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.model = AutoModelForCausalLM.from_pretrained(model)
    
    def generate_text(self, prompt: str, max_length: int = 50):
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_length=max_length)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

class LLM:
    def __init__(self, model_name: str = "gpt3.5"):
        self.model = {
            "gpt3.5" : OpenAILLM(model="gpt-3.5-turbo"),
            "gpt4" : OpenAILLM(model="gpt-4"),
        }[model_name]

    def generate_text(self, prompt: str, max_length: int = 300):
        return self.model.generate_text(prompt, max_length)