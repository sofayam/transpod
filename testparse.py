from fugashi import Tagger
from jamdict import Jamdict

tagger = Tagger()
jam = Jamdict()

text = "昨日は寿司を食べました。"

# Only look up content words (e.g., nouns, verbs, adjectives)
content_pos_prefixes = ('名詞', '動詞', '形容詞')  # noun, verb, i-adjective

for word in tagger(text):
    pos = word.feature.pos1
    lemma = word.feature.lemma

    # Skip non-content words (particles, auxiliary verbs, etc.)
    if not pos.startswith(content_pos_prefixes):
        continue

    if not lemma or lemma == "*":
        continue

    print(f"--- {lemma} ({pos}) ---")
    result = jam.lookup(lemma)
    for entry in result.entries:
        print(entry)
