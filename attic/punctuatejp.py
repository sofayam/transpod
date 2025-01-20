from transformers import pipeline

model_name = "rinna/japanese-gpt2-medium"  # Pre-trained Japanese GPT model
generator = pipeline("text-generation", model=model_name)

unpunctuated_text = "こんにちは元気ですか私は学生です学校に行きます"
punctuated_text = generator(unpunctuated_text, max_length=100)[0]['generated_text']
print(punctuated_text)