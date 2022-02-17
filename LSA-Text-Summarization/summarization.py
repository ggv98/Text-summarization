from lsa_summarizer import LsaSummarizer
import nltk
import os
import sys
from pathlib import Path
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)

from nltk.corpus import stopwords
from rouge import Rouge
from stop_words import safe_get_stop_words

summarizator = LsaSummarizer() 
#stopwords = stopwords.words('english')
stopwords = safe_get_stop_words('bulgarian')
summarizator.stop_words = stopwords
print(sys.getrecursionlimit())
sys.setrecursionlimit(1500)

dir = "top1000-complete"
def evaluate():
    original_summaries = []
    generated_summaries = []
    for index, filename in enumerate(os.listdir(Path(dir))):
        if index == 100: break
        print(index, filename)
        summarizator.set_filepath(dir+'/{0}/Documents_xml/{0}.xml'.format(filename))
        f = open(dir+'/{0}/summary/{0}.gold.txt'.format(filename), "r", encoding="utf8")
        # try:
        original_summaries.append(f.read())
        summary = summarizator(original_summaries[-1].count('\n')+5)

        generated_summaries.append(''.join(summary))


    rouge = Rouge()
    print(rouge.get_scores(original_summaries, generated_summaries, avg=True))
    print('\n')
def evaluteSimpleText():
    source_file = "LSA-Text-Summarization/original_text.txt"
    f = open(source_file,"r", encoding="utf8")
    summarizator.set_filepath(source_file)
    summary = summarizator(8)
    print("\n------- Orginal text -------")
    print(f.read())
    print("------- End of original text -------")
    print("\n------- Summary -------")
    print(" ".join(summary))
    print("------- End of summary -------")
def evaluate_bg():
    rouge = Rouge()
    results = {}

    original_summaries = []
    generated_summaries = [] 
    cwd = Path.cwd()
    main_dir = Path.joinpath(cwd, 'bg_articles')
    for index, filename in enumerate(os.listdir(main_dir)):
        if index == 230: break
        print(index, filename)
        summarizator.set_filepath("bg_articles/"+filename+'/text.txt')
        f = open("bg_articles/"+filename+'/summary.txt', "r", encoding="utf8")
        # try:
        original = f.read()
        original_summaries.append(original)
        summary = summarizator(original_summaries[-1].count('\n')+5)

        generated_summaries.append(''.join(summary))

    print(rouge.get_scores(original_summaries, generated_summaries, avg=True))
    print('\n')
def summarizeByKeyword():
    # try:
    summarizator.set_filepath("LSA-Text-Summarization/original_text.txt")
    summary = summarizator(4,True,["математика","математиците","доказателство"])

    print(''.join(summary))

evaluate_bg()