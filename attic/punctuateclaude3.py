from transformers import AutoTokenizer, AutoModelForCausalLM

# Load tokenizer and model separately
tokenizer = AutoTokenizer.from_pretrained("rinna/japanese-gpt2-medium", use_fast=False)
model = AutoModelForCausalLM.from_pretrained("rinna/japanese-gpt2-medium")

# Input text
unpunctuated_text = "こんにちは元気ですか私は学生です学校に行きます"

# Tokenize and generate
inputs = tokenizer(unpunctuated_text, return_tensors="pt", padding=True)
outputs = model.generate(
    inputs['input_ids'],
    attention_mask=inputs['attention_mask'],
    max_length=100,
    do_sample=True,
    temperature=0.7,
    top_p=0.95,
    num_return_sequences=1,
    pad_token_id=tokenizer.eos_token_id,
    repetition_penalty=1.2,
    no_repeat_ngram_size=2,
    early_stopping=True
)

# Decode the output
punctuated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(punctuated_text)