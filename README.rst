###########################################
DocuTrace
###########################################

Industrial Programming coursework: Data analysis of a document tracker.


Requirements
============
The **DocuTrace** module has the following dependencies:

- Python==3.8
- numpy==1.18.5
- matplotlib==3.3.3
- PyYAML==5.3.1
- ua-parser==0.10.0
- user-agents==2.2.0
- pycountry==20.7.3
- pycountry-convert==0.7.2
- graphviz==0.15

**Test** requirements:
- pytest==6.1.2

For **Jupyter notebooks** these requirements must additionally be installed:

- ipython==7.19.0
- notebook==6.1.5

To build the **Docs** the following must be installed:

- Sphinx==3.3.1
- sphinx-rtd-theme==0.5.0

Installation
============
1. Create a Python 3.8 environment
2. Install the dependencies from `requirements.txt`:
    ``$ pip install -r requirements.txt``
3. Install the DocuTrace module:
    ``$ pip install -e Application/DocuTrace``


Command line usage
==================
Ensure your current shell is in the correct environment.

This application can either be run directly on the python entry point:
``<Path to repository>/Application$ python DocuTrace/main.py -h``

Alternatively a shell script has been provided within the Application directory (needs executable permissions):
``$ ./docutrace -h``


usage: ``main.py [-h] [-u USER_UUID] [-d DOC_UUID] -t TASK_ID [-f FILEPATH] [-v [VERBOSE]]``

optional arguments:
  -h, --help            show this help message and exit

Params:
  -u USER_UUID, --user_uuid USER_UUID
                        Specifies the user uuid
  -d DOC_UUID, --doc_uuid DOC_UUID
                        Specifies the document uuid
  -t TASK_ID, --task_id TASK_ID
                        Specifies the task id
  -f FILEPATH, --filepath FILEPATH
                        Specifies the file name
  -v [VERBOSE], --verbose [VERBOSE]
                        Set a verbose output
