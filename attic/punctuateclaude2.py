from transformers import AutoTokenizer, AutoModelForCausalLM

# Load tokenizer and model separately
tokenizer = AutoTokenizer.from_pretrained("rinna/japanese-gpt2-medium", use_fast=False)
model = AutoModelForCausalLM.from_pretrained("rinna/japanese-gpt2-medium")

# Input text
unpunctuated_text = "こんにちは元気ですか私は学生です学校に行きます"

# Tokenize and generate
inputs = tokenizer(unpunctuated_text, return_tensors="pt")
outputs = model.generate(
    inputs['input_ids'],
    max_length=len(unpunctuated_text) + 20,
    temperature=0.1,
    top_p=0.9,
    num_return_sequences=1
)

# Decode the output
punctuated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(punctuated_text)