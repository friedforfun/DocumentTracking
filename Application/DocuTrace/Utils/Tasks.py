import sys
from threading import Thread
from collections import OrderedDict
from argparse import ArgumentTypeError
from time import sleep
from threading import Thread, Event
from alive_progress import alive_bar

from DocuTrace.Analysis.DataCollector import DataCollector
from DocuTrace.Analysis.ComputeData import ComputeData, top_n_sorted
from DocuTrace.Utils.Logging import debug, logger
from DocuTrace.Utils.Validation import validate_user_uuid, str2bool, validate_task, validate_doc_uuid
from DocuTrace.Utils.Exceptions import InvalidTaskIDError
from DocuTrace.Gui import main as gui

"""Provides functions to begin each task
"""

def task_1(data_collector: DataCollector, args):
    logger.info(
        'Task 1: The core functionality of this application is written in python.')


def task_2a(data_collector: DataCollector, args):
    logger.info(
        'Task 2a. Specifiy a document UUID, and return a histogram of countries of the viewers.')
    #! Render histogram inside gui
    #! Supply n_countries modification logic
    try:
        doc_uuid = get_doc_uuid(args)
        n = get_n(args)
        compute = ComputeData(data_collector)
        compute.construct_document_counts_figure(doc_uuid, show_continents=False, n_countries=n)
        gui.open(compute, doc_uuid=doc_uuid, n=n, start_tab='Task 2a')

    except Exception as e:
        logger.exception('Exception encountered during Task 2a')

def task_2b(data_collector: DataCollector, args):
    logger.info(
        'Task 2b. Group the countries by continent, and generate a histogram of the continents of the viewers.')
    #! Render histogram inside gui
    try:
        doc_uuid = get_doc_uuid(args)
        n = get_n(args)
        compute = ComputeData(data_collector)
        compute.construct_document_counts_figure(
            doc_uuid, show_countries=False, n_countries=n)
        gui.open(compute, doc_uuid=doc_uuid, n=n, start_tab='Task 2b')

    except Exception as e:
        logger.exception('Exception encountered during Task 2a')


def task_3a(data_collector: DataCollector, args):
    logger.info('Task 3a: Histogram of verbose views by browser.')
    try:
        n = get_n(args)
        compute = ComputeData(data_collector)
        compute.construct_counts_figure(show_continents=False, show_countries=False, n_browsers=n, clean_browser_names=False)
        gui.open(compute, n=n, start_tab='Task 3a')

    except Exception as e:
        logger.exception('Exception encountered during Task 3a')


def task_3b(data_collector: DataCollector, args):
    logger.info(
        'Task 3b: Histogram of views by browser, with processed browser names.')
    #! Render histogram inside gui
    #! Supply n_browsers modification logic
    try:
        n = get_n(args)
        compute = ComputeData(data_collector)
        compute.construct_counts_figure(show_continents=False, show_countries=False, n_browsers=n, clean_browser_names=True)
        gui.open(compute, n=n, start_tab='Task 3b')

    except Exception as e:
        logger.exception('Exception encountered during Task 3b')

def task_4(data_collector: DataCollector, args):
    logger.info('Task 4d: 10 most avid readers.')
    try:
        n = get_n(args)
        compute = ComputeData(data_collector)
        compute.sort(sort_countries=False,
                    sort_continents=False, sort_browsers=False)
        gui.open(compute, n=n, start_tab='Task 4')
        # for i, profile in enumerate(compute.reader_profiles.values()):
        #     if i < 10:
        #         print('{:{width}} | {}'.format(i, profile, width=4))

    except Exception as e:
        logger.exception('Exception encountered during Task 4')
    

def task_5d(data_collector: DataCollector, args):
    logger.info('Task 5d: Also likes top n documents.')
    #! Dont forget to catch key errors
    try:
        doc_uuid = get_doc_uuid(args)
        user_uuid = get_user_uuid(args)
        n = get_n(args)
        compute = ComputeData(data_collector)
        also_likes = compute.also_likes(doc_uuid, user_uuid, sort_fn=top_n_sorted, n=n)
        gui.open(compute, doc_uuid, user_uuid, n, start_tab='Task 5d')
        # for i, doc in enumerate(also_likes):
        #     print(i+1, ' | ', doc)

    except Exception as e:
        logger.exception('Exception encountered during Task 5d')

def task_6(data_collector: DataCollector, args):
    logger.info('Task 6: Also likes graph, inside GUI.')
    #! Dont forget to catch key errors
    try:
        doc_uuid = get_doc_uuid(args)
        user_uuid = get_user_uuid(args)
        n = get_n(args)
        compute = ComputeData(data_collector)
        also_likes = compute.also_likes(doc_uuid, user_uuid, sort_fn=top_n_sorted, n=n)
        gui.open(compute, doc_uuid, user_uuid, n, start_tab='Task 6')
        # for i, doc in enumerate(also_likes):
        #     print(i+1, ' | ', doc)

    except Exception as e:
        logger.exception('Exception encountered during Task 6')


def task_7(data_collector: DataCollector, args):
    logger.info('Task 7: Open the GUI')
    try:
        doc_uuid = get_doc_uuid(args)
        user_uuid = get_user_uuid(args)
        n = get_n(args)
        compute = ComputeData(data_collector)
        also_likes = compute.also_likes(
            doc_uuid, user_uuid, sort_fn=top_n_sorted, n=n)
        gui.open(compute, doc_uuid, user_uuid, n, start_tab='Task 6')
        # for i, doc in enumerate(also_likes):
        #     print(i+1, ' | ', doc)

    except Exception as e:
        logger.exception('Exception encountered during Task 7')

def task_8(data_collector: DataCollector, args):
    logger.info('Task 8: Command line, This is it!')


task_picker = OrderedDict()
task_picker['1'] = task_1
task_picker['2a'] = task_2a
task_picker['2b'] = task_2b
task_picker['3a'] = task_3a
task_picker['3b'] = task_3b
task_picker['4'] = task_4
task_picker['5d'] = task_5d
task_picker['6'] = task_6
task_picker['7'] = task_7
task_picker['8'] = task_8


def next_item(key, task_dict=task_picker) -> str:
    """Get the item after the key given to the function

    Args:
        key (str): A valid key from task_dict

    Returns:
        str: The next key, or if the final key is given return the first key.
    """
    try:
        return list(task_dict)[list(task_dict.keys()).index(key) + 1]
    except IndexError as e:
        return '1'

def raise_invalid_task(*args, **kwargs):
    """Function that raises error, used when accessing the task_picker dict

    Raises:
        InvalidTaskIDError: Raised when the task is invalid
    """
    raise InvalidTaskIDError


def tasks(data_collector: DataCollector, thread: Thread, task_id: str, args) -> None:
    """Display a loading bar for the data processing, once processing is complete start the task based on the ArgParse parameters.

    Args:
        data_collector (DataCollector): Instance of the DataCollector class used to process the file.
        thread (Thread): The thread currently processing the file
        task_id (str): The validated identifier of the task to begin running
        args (Namespace): The CLI arguments
    """
    finished = False
    loading_event = Event()
    loading_bar = Thread(target=loading_data, args=(loading_event,), daemon=True)
    loading_bar.start()
    thread.join()
    loading_event.set()
    loading_bar.join()

    if args.exit_early:
        finished, task_id, args = begin_task(data_collector, task_id, args)
    else:
        while not finished:
            finished, task_id, args = begin_task(data_collector, task_id, args)


def begin_task(data_collector: DataCollector, task_id: str, args) -> bool:
    """Function to handle task selection and the flow of the program

    Args:
        data_collector (DataCollector): Instance of the DataCollector class used to process the file.
        task_id (str): The validated identifier of the task to begin running
        args (Namespace): The CLI arguments

    Returns:
        bool: Indicates if the program is complete
    """
    run_task = task_picker.get(task_id, raise_invalid_task)
    print('------------------ Task: {} ------------------'.format(task_id))
    run_task(data_collector, args)


    print()
    next_task = next_item(task_id)
    
    finished = None

    if args is not None:
        finished = not args.exit_early
        if finished is True:
            finished = None

    while finished is None:
        try:
            finished = str2bool(check_exit(input('Continue to task {} [Y/n] (e for exit)? '.format(next_task))))
            if finished is False:
                finished = str2bool(check_exit(input('Jump to new task [Y/n] (e for exit)? ')))
                if finished is False:
                    break
                next_task = validate_task(input('Enter task to run {}: '.format(task_picker.keys())))

        except ArgumentTypeError as e:
            logger.warning('Invalid argument provided, expecting a boolean value')
            finished = None
            continue
        except InvalidTaskIDError as e:
            logger.warning('Invalid task ID entered')
            finished = None
            continue
    
    args = None
    return not finished, next_task, args

#@debug
def get_doc_uuid(args) -> str:
    """Helper function to get the document UUID

    Args:
        args (Namespace): The CLI arguments

    Returns:
        str: Document UUID
    """
    if args is None or not hasattr(args, 'doc_uuid'):
        doc_uuid = input('Doc UUID must be specified: ')
    else:
        if args.doc_uuid is None:
            doc_uuid = input('Doc UUID must be specified: ')
        else:
            doc_uuid = args.doc_uuid


    doc_uuid = validate_doc_uuid(doc_uuid)

    return doc_uuid


def get_user_uuid(args) -> str:
    """Helper function to get the user UUID

    Args:
        args (Namespace): The CLI arguments

    Returns:
        str: User UUID
    """
    if args is None or not hasattr(args, 'user_uuid'):
        user_uuid = input('User UUID: ')
    else:
        user_uuid = args.user_uuid  

    if user_uuid is not None:
        user_uuid = validate_user_uuid(user_uuid)
    return user_uuid


def get_n(args) -> int:
    """Helper function to get the n parameter

    Args:
        args (Namespace): The CLI arguments

    Returns:
        int: n
    """
    if args is None or not hasattr(args, 'limit_data'):
        return None
    else:
        return args.limit_data


def loading_data(done_event: Event) -> None:
    """Display a loading bar while the data is being loaded

    Args:
        done_event (Event): An event that gets set when the loading bar finishes
    """
    with alive_bar(title='Processing data file...', total=None) as bar:
        while not done_event.is_set():
            bar()
            sleep(0.1)       


def check_exit(string: str) -> str:
    """Verify if the exit flag has been entered by the user

    Args:
        string (str): String entered by the user

    Returns:
        str: returns the unmodified string
    """
    if string.lower() == 'e':
        sys.exit(0)
    return string


