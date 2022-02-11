"# Text-summarization" 
## Setup 

### Python version
[Find and download](https://www.python.org/downloads/) the python version of the pipeline docker image.  

    python 3.7.9

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
  
  1. Goto venv\Lib\site-packages\google_trans_new\google_trans_new.py
  2. Update line 151:
        response = (decoded_line + ']') -> response = decoded_line

### Adding a new package.
After adding a new package, make sure to update the *requirements.txt*.

     pip freeze > requirements.txt 