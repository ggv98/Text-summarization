from lsa_summarizer import LsaSummarizer
import nltk
import os
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)

from nltk.corpus import stopwords
from rouge import Rouge

summarizator = LsaSummarizer() 
stopwords = stopwords.words('english')
summarizator.stop_words = stopwords


dir = "../Textrank-Summarization/textrank_implementation/top1000_complete"
def evaluate():
    original_summaries = []
    generated_summaries = []
    for index, filename in enumerate(os.listdir(dir)):
        if index == 100: break
        print(index, filename)
        summarizator.set_filepath(dir+'/{0}/Documents_xml/{0}.xml'.format(filename))
        f = open(dir+'/{0}/summary/{0}.gold.txt'.format(filename), "r", encoding="utf8")
        # try:
        original_summaries.append(f.read())
        print(original_summaries[-1].count('\n')+5)
        summary = summarizator(original_summaries[-1].count('\n')+5)

        generated_summaries.append(''.join(summary))


    rouge = Rouge()
    print(rouge.get_scores(original_summaries, generated_summaries, avg=True))
    print('\n')

evaluate()