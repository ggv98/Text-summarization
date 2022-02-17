# Text-summarization
This repository contain to sumarization algorithms:
- TextRank (Algorithm based on PageRank)
- Latent semantic analysis (**LSA**)

We also created a corpus of Bulgarian scientific articles and their summaries and related keywords. 
These texts can be found in: **bg_articles**.

Each of articles contain 3 files:
- **text.txt**   (original article text)
- **summary.txt**   (short human created summary)
- **keywords.txt**   (human selected keywords which describe article content)

This article are extracted from: [ANNUAL SCIENTIFIC CONFERENCE
of Angel Kanchev University of Ruse and Union of Scientists - Ruse](http://conf.uni-ruse.bg/en/?cmd=dPage&pid=index)
## Setup 

### Python version

    python 3.8.5

### Virtual environment
#### Create virtual environment

    python -m venv venv

or

    py -m venv venv


#### Enter virtual environment

##### Windows (powershell): 

    . venv\Scripts\activate

##### Unix or MacOS : 

    source venv/bin/activate

### Installing packages

     pip install -r .\requirements.txt 

  Make sure you are inside venv first.

  #### Important

  There is a bug in google_trans_new library, so if you want to use pdf-reader.py to parse a new pdf document need to make the following:
  ##### Steps:
  
  1. Goto           
  
    venv\Lib\site-packages\google_trans_new\google_trans_new.py
  2. Update line 151:

    response = (decoded_line + ']') ---> response = decoded_line

### Adding a new package.
After adding a new package, make sure to update the *requirements.txt*.

    pip freeze > requirements.txt 
