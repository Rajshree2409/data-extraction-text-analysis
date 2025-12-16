import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize

# NLTK
nltk.download("punkt")

# PATHS 
INPUT_FILE = "Input.xlsx"
OUTPUT_FILE = "Output.csv"
ARTICLE_DIR = "data/extracted_articles"

STOPWORDS_DIR = "StopWords"
MASTER_DICT_DIR = "MasterDictionary"

# Creating output directory 
os.makedirs(ARTICLE_DIR, exist_ok=True)

# load all stopwords files from a folder then cleans each word and stores every unique stopwords in a single set for text processing
stopwords = set() 
for file in os.listdir(STOPWORDS_DIR):
    with open(os.path.join(STOPWORDS_DIR, file), "r", encoding="latin-1") as f:
        stopwords.update(word.strip().lower() for word in f if word.strip())

# load positive and negative sentiment words from dictionary files, cleans and normalize them, and remove any stopwords so only meaningful sentiment-carrying words
def load_words(filepath):
    with open(filepath, "r", encoding="latin-1") as f:
        return set(word.strip().lower() for word in f if word.strip())

positive_words = load_words(os.path.join(MASTER_DICT_DIR, "positive-words.txt")) - stopwords  # remove common non-sentiment words that may appear in the dictionary
negative_words = load_words(os.path.join(MASTER_DICT_DIR, "negative-words.txt")) - stopwords  # doing the same work but for negative sentiment words


# Fetches a webpage, extracts the article title and main text from HTML, and returns them for NLP analysis
def extract_article(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"  # Implement HTTP headers for the request
    }

    response = None
    for _ in range(2):  # retry once
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            break
        except requests.exceptions.RequestException:
            response = None

    if response is None:
        raise Exception("Request failed after retries")

    soup = BeautifulSoup(response.content, "html.parser") 

    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else ""

    article_text = " ".join(p.get_text(strip=True) for p in soup.find_all("p"))

    return title, article_text

# Funtion used to estimeate how many syllables a word has using vowel patterns, which is required for readability and complexity metrices
def syllable_count(word):
    word = word.lower()
    vowels = "aeiou"
    count = 0

    if word and word[0] in vowels:
        count += 1

    for i in range(1, len(word)):
        if word[i] in vowels and word[i - 1] not in vowels:
            count += 1

    if word.endswith(("es", "ed")):
        count -= 1

    return max(count, 1)

# -function counts how many first-person personal pronouns appear in a text
def count_pronouns(text):
    # breaking the regex down 
    pattern = r"\b(I|we|my|ours|us)\b"
    matches = re.findall(pattern, text, flags=re.I)
    return len(matches)

# Main Pipeline, It basically read each URL from the input file, extracts the article, cleans and analyze the text, and use NLP metrics and store the result
df_input = pd.read_excel(INPUT_FILE)
results = []

for _, row in df_input.iterrows():
    url_id = row["URL_ID"]
    url = row["URL"]

    try:
        title, article = extract_article(url)

        
        file_path = os.path.join(ARTICLE_DIR, f"{url_id}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(title + "\n\n" + article)

        text = article.lower()

        sentences = sent_tokenize(text)
        words = word_tokenize(text)

        cleaned_words = []
        for word in words:
            word = re.sub(r"[^a-z]", "", word.lower())
            if word and word not in stopwords:
                cleaned_words.append(word)

        word_count = len(cleaned_words)
        sentence_count = len(sentences)

        positive_score = sum(1 for w in cleaned_words if w in positive_words)
        negative_score = sum(1 for w in cleaned_words if w in negative_words)

        polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) + 1e-6)
        subjectivity_score = (positive_score + negative_score) / (word_count + 1e-6)

        avg_sentence_length = word_count / sentence_count if sentence_count else 0

        complex_words = [w for w in cleaned_words if syllable_count(w) > 2]
        complex_word_count = len(complex_words)

        percentage_complex_words = complex_word_count / word_count if word_count else 0
        fog_index = 0.4 * (avg_sentence_length + percentage_complex_words)

        avg_words_per_sentence = avg_sentence_length
        syllables_per_word = (
            sum(syllable_count(w) for w in cleaned_words) / word_count if word_count else 0
        )

        pronouns = count_pronouns(article)
        avg_word_length = (
            sum(len(w) for w in cleaned_words) / word_count if word_count else 0
        )


        # Stores all coumputed metrics in a structured row
        results.append([
            row["URL_ID"], row["URL"],
            positive_score, negative_score, polarity_score, subjectivity_score,
            avg_sentence_length, percentage_complex_words, fog_index,
            avg_words_per_sentence, complex_word_count, word_count,
            syllables_per_word, pronouns, avg_word_length
        ])

    except Exception as e:
        print(f"Error processing {url_id}: {e}")

# The final output structure and convert all computed results into a table ans saves it as a CSV file
columns = [
    "URL_ID", "URL",
    "POSITIVE SCORE", "NEGATIVE SCORE", "POLARITY SCORE", "SUBJECTIVITY SCORE",
    "AVG SENTENCE LENGTH", "PERCENTAGE OF COMPLEX WORDS", "FOG INDEX",
    "AVG NUMBER OF WORDS PER SENTENCE", "COMPLEX WORD COUNT", "WORD COUNT",
    "SYLLABLE PER WORD", "PERSONAL PRONOUNS", "AVG WORD LENGTH"
]

df_output = pd.DataFrame(results, columns=columns)
df_output.to_csv(OUTPUT_FILE, index=False)

print("Processing complete. Output saved to Output.csv")
