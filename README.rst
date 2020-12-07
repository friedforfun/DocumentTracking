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
- regex==2020.11.13
- alive-progress==1.6.1
- python-decouple=3.3

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
2. Install the dependencies from ``requirements.txt``:
    ``$ pip install -r requirements.txt``
3. Install the DocuTrace module:
    ``$ pip install -e Application/DocuTrace``


Command line usage
==================
Ensure your current shell is in the correct environment.

The best way to start the application is via the provided shell script within the Application directory (needs executable permissions):
``$ ./docutrace -h``

Alternatively you must create a .env file and specify the full path to the location of your current shell (the shell script will automate this):
``WORK_DIR=<path to shell>``

Now the application can be run directly on the python entry point:
``<Path to repository>/Application$ python DocuTrace/main.py -h``





usage: ``main.py [-h] [-u USER_UUID] [-d DOC_UUID] [-t TASK_ID] -f FILEPATH [-n [LIMIT_DATA]] [-v [VERBOSE]] [-e [EXIT_EARLY]]``

Command line interface for DocuTrace.
-------------------------------------

*optional arguments*:

-h, --help            show this help message and exit

*Core parameters*:

-u USER_UUID, --user_uuid USER_UUID         Specifies the user uuid
                        
-d DOC_UUID, --doc_uuid DOC_UUID            Specifies the document uuid
                        
-t TASK_ID, --task_id TASK_ID               Specifies the task id
                        
-f FILEPATH, --filepath FILEPATH            Specifies the file name
                        

*Secondary parameters*:

-n LIMIT_DATA, --limit_data LIMIT_DATA          Limits the number of displayed data points for tasks 2a, 2b, 3a, 3b, 4d, and 5.
                        
-v VERBOSE, --verbose VERBOSE                   Set the verbosity level, 20 for INFO, 10 for DEBUG. Default is 30: WARN
                        
-e EXIT_EARLY, --exit_early EXIT_EARLY          Continue the program after running only the specified task.
                        
