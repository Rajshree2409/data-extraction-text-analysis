# Data-extraction-text-analysis

This project implements an end-to-end Natural Language Processing (NLP) pipeline to extract articles from given URLs and compute sentiment and readability metrics.

---

## Objectives

- Extract article text from URLs provided in an Excel file  
- Clean and preprocess textual data  
- Perform sentiment analysis using a lexicon-based approach  
- Compute readability and linguistic metrics  
- Store extracted articles and generate a final output CSV  

---

<h2>Project Structure</h2>

<pre>
.
├── Input.xlsx
├── Output.csv
├── main.py
├── StopWords/
│   ├── StopWords_Auditor.txt
│   ├── StopWords_Currencies.txt
│   └── ...
├── MasterDictionary/
│   ├── positive-words.txt
│   └── negative-words.txt
├── data/
│   └── extracted_articles/
│       ├── URL_ID_1.txt
│       └── URL_ID_2.txt
└── README.md
</pre>





---

## Input

### Input.xlsx
Contains:
- `URL_ID` – unique identifier for each article  
- `URL` – web link to the article  

---

## Output

### Output.csv
Contains the following metrics:

| Column Name                      |
|----------------------------------|
| URL_ID                           |
| URL                              |
| POSITIVE SCORE                   |
| NEGATIVE SCORE                   |
| POLARITY SCORE                   |
| SUBJECTIVITY SCORE               |
| AVG SENTENCE LENGTH              |
| PERCENTAGE OF COMPLEX WORDS      |
| FOG INDEX                        |
| AVG NUMBER OF WORDS PER SENTENCE |
| COMPLEX WORD COUNT               |
| WORD COUNT                       |
| SYLLABLE PER WORD                |
| PERSONAL PRONOUNS                |
| AVG WORD LENGTH                  |

---

## Methodology:
### 1) Article Extraction
- Uses HTTP requests with proper headers  
- Parses HTML using BeautifulSoup  
- Extracts `<h1>` as title and `<p>` tags as content  
- Stores extracted text locally for traceability  

### 2️) Text Preprocessing
- Lowercasing  
- Tokenization (sentence & word level)  
- Stopword removal  
- Punctuation and symbol cleaning  

### 3️) Sentiment Analysis
- Lexicon-based approach  
- Uses predefined positive and negative word lists  
- Computes polarity and subjectivity scores  

### 4️) Readability Analysis
- Syllable counting (heuristic method)  
- Complex word detection (> 2 syllables)  
- Gunning Fog Index calculation  

### 5️) Linguistic Metrics
- Personal pronoun count  
- Average word length  
- Syllables per word  

---

## Dependencies
Install required libraries:
pip install pandas requests beautifulsoup4 nltk openpyxl

Download NLTK tokenizer:
import nltk
nltk.download("punkt")

# To run the script:
python main.py
