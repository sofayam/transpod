from transformers import pipeline
import torch

# Set random seed for reproducibility
torch.manual_seed(42)

# Load model
model_name = "rinna/japanese-gpt2-medium"
generator = pipeline("text-generation", model=model_name)

# Input text
unpunctuated_text = "こんにちは元気ですか私は学生です学校に行きます"

# Generate with more controlled parameters
punctuated_text = generator(
    unpunctuated_text,
    max_length=len(unpunctuated_text) + 10,  # Limit length to avoid extra generation
    temperature=0.1,  # Lower temperature for more focused outputs
    top_p=0.9,
    num_return_sequences=1
)[0]['generated_text']

print(punctuated_text)