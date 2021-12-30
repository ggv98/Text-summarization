from lsa_summarizer import LsaSummarizer
import nltk
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)

from nltk.corpus import stopwords

source_file = "original_text.txt"

with open(source_file, "r", encoding='utf-8') as file:
    lines = file.readlines()

    text = ""
    for line in lines:
        text += line.replace("\n", " ")


summarizer = LsaSummarizer()

# stopwords = stopwords.words('english')
# summarizer.stop_words = stopwords

# TODO make summary_sentences_count to be sqrt(len(input_text))
summary_sentences_count = 5
summary = summarizer(text, summary_sentences_count)

print("------- Original text -------")
print(text)
print("------- End of original text -------")



print("\n------- Summary -------")

print(" ".join(summary))
print("------- End of summary -------")
