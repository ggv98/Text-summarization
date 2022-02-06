import pdfplumber
from langdetect import detect
from typing import List
from google_trans_new import google_translator 
import os

class PDFReader():
    def __init__(self, fileName):
            self.fileName = fileName

    def extract_article_names(self, startPage, endPage) -> List[str]:
        articleIndex = 1
        self.articleNames = []
        with pdfplumber.open(self.fileName) as pdf:
            for pageIndex in range(startPage, endPage):
                page = pdf.pages[pageIndex]
                text = page.extract_text().split('\n')
                for line in text:
                    words =  line.replace('  ', ' ').split(' ')
                    if words[0].startswith('{}.'.format(articleIndex)):
                        self.articleNames.append(words[1])
                        articleIndex += 1

    def extract_article_text(self, startPage, endPage):
        currentArticle = 0
        text = []
        articles = {}
        start = False
        summary = ''
        keywords = ''
        articleText = ''
        with pdfplumber.open(self.fileName) as pdf:
            for pageIndex in range(startPage, endPage):
                page = pdf.pages[pageIndex]
                text.extend(page.extract_text().split('\n'))

        lineIndex = 0
        while lineIndex < len(text) and currentArticle < len(self.articleNames) :
            if text[lineIndex].replace(' ', '') == self.articleNames[currentArticle]:
                start = True
            elif text[lineIndex].replace(' ', '') == 'REFERENCES':
                keywords = keywords.replace('Key words', '').replace('Keywords', '').replace(':', '')
                summary = summary.replace('Abstract', '').replace(':', '')
                articles[self.articleNames[currentArticle]] = (keywords, summary, articleText)
                start = False
                summary = ''
                keywords = ''
                articleText = ''
                currentArticle += 1
            elif start == True:
                if text[lineIndex].startswith('Abstract'):
                    while lineIndex < len(text) and not text[lineIndex].lstrip().startswith('Key words')and not text[lineIndex].lstrip().startswith('Keywords') and  text[lineIndex].replace(' ', '') != '':
                        summary += text[lineIndex]
                        lineIndex += 1
                    continue
                if text[lineIndex].lstrip().startswith('Key words') or text[lineIndex].lstrip().startswith('Keywords') :
                    while lineIndex < len(text)  and  text[lineIndex].replace(' ', '') != '' and 'ВЪВЕДЕНИЕ' not in text[lineIndex] and 'INTRODUCTION ' not in text[lineIndex]:
                        keywords += text[lineIndex]
                        lineIndex += 1
                    while lineIndex < len(text)  and  text[lineIndex].replace(' ', '') != 'REFERENCES':
                        articleText += text[lineIndex]
                        lineIndex += 1
                    continue
            lineIndex += 1

        self.articles = articles

    def filter_bulgarian_articles(self):
        filtered_articles = {}
        for key, article in self.articles.items():
            if article[2] and  detect(article[2]) == 'bg':
                filtered_articles[key] = article
        self.articles = filtered_articles


    def translate_summaries(self):
        translator = google_translator()
        for key, article in self.articles.items():
            self.articles[key] = (translator.translate(article[0], lang_tgt='bg'), translator.translate(article[1], lang_tgt='bg'), article[2])
                
    def get_articles(self, contentStartPage, contentEndPage, articlesStartPage, articlesEndPage):
        self.extract_article_names(contentStartPage, contentEndPage)
        self.extract_article_text(articlesStartPage, articlesEndPage)
        self.filter_bulgarian_articles()
        self.translate_summaries()

        return self.articles

                
def file_or_directory_exists(entityPath: str) -> bool:
    return os.path.exists(entityPath)

def make_directory(dirName: str):
    os.makedirs(dirName)

def save_data(articles):
    if not file_or_directory_exists('./bg_articles'):
        make_directory('./bg_articles')
    
    for key, article in articles.items():
        if not file_or_directory_exists('./bg_articles/{}'.format(key)):
            make_directory('./bg_articles/{}'.format(key))
        else:
            os.remove('./bg_articles/{}'.format(key))
            make_directory('./bg_articles/{}'.format(key))

        with open('./bg_articles/{}/text.txt'.format(key), 'w', encoding="utf-8") as f:
            f.write(article[2])
        with open('./bg_articles/{}/keywords.txt'.format(key), 'w', encoding="utf-8") as f:
            f.write(article[0])
        with open('./bg_articles/{}/summary.txt'.format(key), 'w', encoding="utf-8") as f:
            f.write(article[1])


# reader = PDFReader('.\Textrank-Summarization\\textrank_implementation\\FPNO-FMI.pdf')
# articles = reader.get_articles(7, 9, 9, 108)
# save_data(articles)

# reader = PDFReader('.\Textrank-Summarization\\textrank_implementation\\FR.pdf')
# articles = reader.get_articles(7, 9, 9, 88)
# save_data(articles)

# reader = PDFReader('.\Textrank-Summarization\\textrank_implementation\\TF.pdf')
# articles = reader.get_articles(7, 8, 9, 92)
# save_data(articles)

# reader = PDFReader('.\Textrank-Summarization\\textrank_implementation\\FBM.pdf')
# articles = reader.get_articles(7, 8, 8, 58)
# save_data(articles)

# reader = PDFReader('.\Textrank-Summarization\\textrank_implementation\\EEA.pdf')
# articles = reader.get_articles(7, 8, 10, 50)
# save_data(articles)

reader = PDFReader('.\Textrank-Summarization\\textrank_implementation\\EEA.pdf')
articles = reader.get_articles(8, 10, 53, 159)
save_data(articles)