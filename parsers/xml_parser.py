from bs4 import BeautifulSoup

class XMLParser():

    def read(self, filePath):
        with open(filePath, 'r') as f:
            data = f.read() 

        bs_data = BeautifulSoup(data, 'xml') 

        raw_sentences = bs_data.find_all('S') 
        data =' '.join(map(lambda x: x.text, raw_sentences))
        return data