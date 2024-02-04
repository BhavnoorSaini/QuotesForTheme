import requests
from bs4 import BeautifulSoup
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer, util
import torch

class QuoteMatcherClass:
    def __init__(self, url, theme):
        # Initialize the URL and theme
        self.url = url
        self.theme = theme
        # Initialize the model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def get_quotes(self):
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, 'html.parser')
        # Extract all text from paragraph tags
        quotes = [p.text for p in soup.find_all('p')]
        return quotes

    def process_quotes(self, quotes):
        processed_quotes = []
        # List of words which don't carry much meaning
        stop_words = set(stopwords.words('english')) 
        # Reduces words to their base form
        lemmatizer = WordNetLemmatizer()
    
        for quote in quotes:
            # Remove non-alphanumeric characters and convert to lowercase
            quote = re.sub(r'[^a-zA-Z0-9\s]', '', quote)
            # Splits sentence (quotes) into words
            tokens = word_tokenize(quote)
            # Remove stop words
            tokens = [word for word in tokens if word not in stop_words]
            # Lemmatize
            tokens = [lemmatizer.lemmatize(word) for word in tokens]
            # Join words back into sentence
            processed_quote = ' '.join(tokens)
            processed_quotes.append(processed_quote)
        
        return processed_quotes

    def match_quotes(self, original_quotes, processed_quotes):
        # Check if there are no quotes or theme
        if not processed_quotes or not self.theme:
            return None
    
        # Convert sentences to embeddings which can be used for similarity comparison
        quote_embeddings = self.model.encode(processed_quotes, convert_to_tensor=True)
        # Convert theme to embedding
        theme_embedding = self.model.encode([self.theme], convert_to_tensor=True)
        # Compute cosine similarity between theme and processed quotes
        similarities = util.pytorch_cos_sim(theme_embedding, quote_embeddings)[0]
        # Get the index of the processed quote that is most similar to the theme
        related_quote_index = torch.argmax(similarities)
        # Get the original quote that corresponds to the best matching processed quote
        matched_quote = original_quotes[related_quote_index]
    
        return matched_quote

    def run(self):
        quotes = self.get_quotes()
        processed_quotes = self.process_quotes(quotes)
        matched_quote = self.match_quotes(quotes, processed_quotes)
        return matched_quote