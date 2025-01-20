import spacy
import numpy as np
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class TranscriptFormatter:
    def __init__(self, language: str = "en"):
        """
        Initialize the formatter with specified language.
        
        Args:
            language (str): Language code ('en' for English, 'ja' for Japanese)
        """
        self.language = language
        # Load appropriate language model with word vectors
        if language == "ja":
            self.nlp = spacy.load("ja_core_news_lg")  # Large model for better vectors
        else:
            self.nlp = spacy.load("en_core_web_lg")  # Large model for better vectors
            
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english' if language == 'en' else None
        )
        
    def format_transcript(self, text: str) -> str:
        """Format transcript text using semantic analysis."""
        # Process the text
        doc = self.nlp(text)
        
        # Split into sentences
        sentences = list(doc.sents)
        
        # Group sentences into paragraphs
        paragraphs = self.group_into_paragraphs(sentences)
        
        # Format the final text
        formatted_text = self.format_paragraphs(paragraphs)
        
        return formatted_text

    def calculate_semantic_similarity(self, sent1: spacy.tokens.Span, sent2: spacy.tokens.Span) -> float:
        """
        Calculate semantic similarity between two sentences using multiple methods.
        """
        # Method 1: Word vector similarity
        if sent1.vector_norm and sent2.vector_norm:  # Check if vectors exist
            vector_similarity = sent1.similarity(sent2)
        else:
            vector_similarity = 0.5  # Default if no vectors
            
        # Method 2: TF-IDF similarity
        try:
            tfidf = self.vectorizer.fit_transform([str(sent1), str(sent2)])
            tfidf_similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        except:
            tfidf_similarity = 0.5  # Default if TF-IDF fails
            
        # Method 3: Named entity and key phrase overlap
        ents1 = set([ent.text.lower() for ent in sent1.ents])
        ents2 = set([ent.text.lower() for ent in sent2.ents])
        if ents1 and ents2:  # If both sentences have entities
            entity_similarity = len(ents1.intersection(ents2)) / len(ents1.union(ents2))
        else:
            entity_similarity = 0.5  # Default if no entities
            
        # Weight and combine similarities
        weighted_similarity = (
            0.4 * vector_similarity +
            0.4 * tfidf_similarity +
            0.2 * entity_similarity
        )
        
        return weighted_similarity

    def detect_topic_change(self, current_window: List[spacy.tokens.Span], 
                          next_sentence: spacy.tokens.Span,
                          threshold: float = 0.3) -> bool:
        """
        Detect if there's a significant topic change by comparing the next sentence
        to a window of previous sentences.
        """
        if not next_sentence:
            return True
            
        # Calculate average similarity with previous context window
        similarities = [
            self.calculate_semantic_similarity(prev_sent, next_sentence)
            for prev_sent in current_window
        ]
        avg_similarity = np.mean(similarities) if similarities else 0
        
        # Check for topic change
        return avg_similarity < threshold

    def group_into_paragraphs(self, sentences: List[spacy.tokens.Span]) -> List[List[str]]:
        """Group sentences into paragraphs based on semantic similarity."""
        paragraphs = []
        current_paragraph = []
        context_window = []  # Keep track of recent sentences for context
        window_size = 3  # Number of sentences to consider for context
        
        for i, sentence in enumerate(sentences):
            current_paragraph.append(str(sentence))
            context_window.append(sentence)
            
            # Maintain fixed window size
            if len(context_window) > window_size:
                context_window.pop(0)
            
            # Check for paragraph break
            if i < len(sentences) - 1:  # If not the last sentence
                next_sentence = sentences[i + 1]
                
                # Detect topic change using semantic analysis
                if self.detect_topic_change(context_window, next_sentence):
                    if current_paragraph:
                        paragraphs.append(current_paragraph)
                        current_paragraph = []
                        # Keep last sentence in context window for smooth transition
                        context_window = context_window[-1:]
            
        # Add the last paragraph
        if current_paragraph:
            paragraphs.append(current_paragraph)
        
        return paragraphs

    def format_paragraphs(self, paragraphs: List[List[str]]) -> str:
        """Format paragraphs with appropriate spacing."""
        formatted_paragraphs = []
        
        for paragraph in paragraphs:
            if self.language == "ja":
                # For Japanese, don't add spaces between sentences
                formatted_paragraph = ''.join(paragraph)
            else:
                # For English and others, join with spaces
                formatted_paragraph = ' '.join(paragraph)
                
            formatted_paragraphs.append(formatted_paragraph)
        
        # Join paragraphs with double newlines
        return '\n\n'.join(formatted_paragraphs)

# Example usage
if __name__ == "__main__":
    # "content/hotcast/AirPods_Pro_2_に感動しました！#984.json.txt"
    # Example text (English)
    en_formatter = TranscriptFormatter(language="en")
    en_text = """
    Machine learning is transforming the tech industry. It's being used in everything 
    from recommendation systems to self-driving cars. The basic principle is that 
    computers can learn from data without explicit programming. This has led to 
    breakthrough applications in many fields. Speaking of applications, let me tell 
    you about my recent experience with a chatbot. I was trying to get customer 
    service help and was amazed by how well it understood my questions. The technology 
    has come so far in recent years. Of course, there are still challenges to overcome. 
    Privacy concerns are a major issue in AI development. We need to ensure that 
    personal data is protected while still advancing the technology. By the way I bought a Nintendo switch yesterday and I love it!
    """
    print(en_formatter.format_transcript(en_text))