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
                # i = 0
                # while 'Content' not in text[i]:
                #     text.pop(i)
                # text.pop(i)
                
                # while 'Content' not in text[i]:
                #     text.pop(i)
                    
                for line in text:
                    words =  line.replace('  ', ' ').replace(' – ', '-').replace(' - ', '-').split(' ')
                    if len(words)>1 and words[0] == ' ':
                        words.pop(0)
                    if len(words) == 5:
                        words[1] = words[1] + words[2]
                    if words[0].startswith('{}.'.format(articleIndex)) or words[0].startswith(str(articleIndex)) :
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
            if text[lineIndex].replace(' ', '').replace('–', '-').split('-')[-1] == self.articleNames[currentArticle].replace('–', '-').split('-')[-1]:
                start = True
            elif text[lineIndex].replace(' ', '').replace(':', '') in ('REFERENCES', 'REFERENCE', 'REFERENSES'):
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
                    while lineIndex < len(text)  and  text[lineIndex].replace(' ', '').replace(':', '') not in ('REFERENCES', 'REFERENCE', 'REFERENSES'):
                        articleText += text[lineIndex]
                        lineIndex += 1
                    continue
                if 'ВЪВЕДЕНИЕ' in text[lineIndex] or 'INTRODUCTION ' in text[lineIndex]:
                    while lineIndex < len(text)  and  text[lineIndex].replace(' ', '').replace(':', '') not in ('REFERENCES', 'REFERENCE', 'REFERENSES'):
                        articleText += text[lineIndex]
                        lineIndex += 1
                    continue
            lineIndex += 1

        self.articles = articles

    def filter_bulgarian_articles(self):
        filtered_articles = {}
        for key, article in self.articles.items():
            if len(article[2]) > 1000 and  detect(article[2]) == 'bg':
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

def save_data(articles, nameAddition=''):
    if not file_or_directory_exists('./bg_articles'):
        make_directory('./bg_articles')
    
    for key, article in articles.items():
        key += nameAddition
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


# reader = PDFReader('.\\bg-articles-pdf\\FPNO-FMI.pdf')
# articles = reader.get_articles(7, 9, 9, 108)
# save_data(articles)

# reader = PDFReader('.\\bg-articles-pdf\\FR.pdf')
# articles = reader.get_articles(7, 9, 9, 88)
# save_data(articles)

# reader = PDFReader('.\\bg-articles-pdf\\TF.pdf')
# articles = reader.get_articles(7, 8, 9, 92)
# save_data(articles)

# reader = PDFReader('.\\bg-articles-pdf\\FBM.pdf')
# articles = reader.get_articles(7, 8, 8, 58)
# save_data(articles)

# reader = PDFReader('.\\bg-articles-pdf\\EEA.pdf')
# articles = reader.get_articles(7, 8, 10, 50)
#  save_data(articles)

# reader = PDFReader('.\\bg-articles-pdf\\EEA.pdf')
# articles = reader.get_articles(8, 10, 53, 159)
# save_data(articles)

# reader = PDFReader('bg-articles-pdf\FPNO-LLAS_HEF.pdf')
# articles = reader.get_articles(9, 10, 10, 28)
# save_data(articles)

# reader = PDFReader('bg-articles-pdf\FOZZG.pdf')
# articles = reader.get_articles(8, 10, 14, 94)
# save_data(articles)

# reader = PDFReader('bg-articles-pdf\FOZZG.pdf')
# articles = reader.get_articles(11, 13, 96, 211)
# save_data(articles)

# reader = PDFReader('bg-articles-pdf\FOZZG.pdf')
# articles = reader.get_articles(13, 14, 212, 250)
# save_data(articles)

# reader = PDFReader('bg-articles-pdf\FOZZG_2020.pdf')
# articles = reader.get_articles(8, 10, 14, 140)
# save_data(articles, '_2020')

# reader = PDFReader('bg-articles-pdf\FOZZG_2020.pdf')
# articles = reader.get_articles(10, 11, 140, 171)
# save_data(articles, '_2020')

# reader = PDFReader('bg-articles-pdf\FOZZG_2020.pdf')
# articles = reader.get_articles(11, 14, 171, 328)
# save_data(articles, '_2020')

# reader = PDFReader('bg-articles-pdf\FOZZG_2019.pdf')
# articles = reader.get_articles(7, 8, 11, 50)
# save_data(articles, '_2019')

# reader = PDFReader('bg-articles-pdf\FOZZG_2019.pdf')
# articles = reader.get_articles(8, 10, 81, 217)
# save_data(articles, '_2019')

# reader = PDFReader('bg-articles-pdf\FS.pdf')
# articles = reader.get_articles(6, 7, 8, 90)
# save_data(articles, '_2019')

# reader = PDFReader('bg-articles-pdf\FS_2021.pdf')
# articles = reader.get_articles(9, 10, 11, 52)
# save_data(articles, '_2021')

# reader = PDFReader('bg-articles-pdf\FS_2021.pdf')
# articles = reader.get_articles(10, 11, 52, 71)
# save_data(articles, '_2021')

# reader = PDFReader('bg-articles-pdf\FS_2021.pdf')
# articles = reader.get_articles(10, 11, 75, 96)
# save_data(articles, '_2021')

# reader = PDFReader('bg-articles-pdf\FPNO-PP.pdf')
# articles = reader.get_articles(9, 11, 11, 86)
# save_data(articles, '_2021')

reader = PDFReader('bg-articles-pdf\FPNO-FMI&PP.pdf')
articles = reader.get_articles(10, 11, 51, 135)
save_data(articles, '_2021')