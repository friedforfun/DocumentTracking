import sys
from threading import Thread
from collections import OrderedDict
from argparse import ArgumentTypeError
from time import sleep
from threading import Thread, Event
from alive_progress import alive_bar

from DocuTrace.Analysis.DataCollector import DataCollector
from DocuTrace.Analysis.ComputeData import ComputeData, top_n_sorted
from DocuTrace.Utils.Logging import logger
from DocuTrace.Utils.Validation import validate_user_uuid, str2bool, validate_task, validate_doc_uuid
from DocuTrace.Utils.Exceptions import InvalidTaskIDError
from DocuTrace.Gui import main as gui


def task_1(data_collector: DataCollector, args):
    logger.info(
        'Task 1: The core functionality of this application is written in python.')


def task_2a(data_collector: DataCollector, args):
    logger.info(
        'Task 2a. Specifies a document UUID, and return a histogram of countries of the viewers.')
    #! Render histogram inside gui
    #! Supply n_countries modification logic
    compute = ComputeData(data_collector)
    compute.configure_figure(show_continents=False, show_browsers=False, n_countries=20)
    compute.histogram()

def task_2b(data_collector: DataCollector, args):
    logger.info(
        'Task 2b. Group the countries by continent, and generate a histogram of the continents of the viewers.')
    #! Render histogram inside gui
    compute = ComputeData(data_collector)
    compute.configure_figure(show_countries=False, show_browsers=False)
    compute.histogram()


def task_3a(data_collector: DataCollector, args):
    logger.info('Task 3a: Histogram of verbose views by browser.')


def task_3b(data_collector: DataCollector, args):
    logger.info(
        'Task 3b: Histogram of views by browser, with processed browser names.')
    #! Render histogram inside gui
    #! Supply n_browsers modification logic
    compute = ComputeData(data_collector)
    compute.configure_figure(show_countries=False, show_continents=False, n_browsers=20)
    compute.histogram()

def task_4d(data_collector: DataCollector, args):
    logger.info('Task 4d: 10 most avid readers.')
    compute = ComputeData(data_collector)
    compute.sort(sort_countries=False, sort_continents=False, sort_browsers=False)
    for i, profile in enumerate(compute.reader_profiles.values()):
        if i < 10:
            print('{:{width}} | {}'.format(i, profile, width=4))

def task_5(data_collector: DataCollector, args):
    logger.info('Task 5: Also likes top n documents.')
    #! Dont forget to catch key errors
    try:
        doc_uuid = get_doc_uuid(args)
        user_uuid = get_user_uuid(args)
        n = get_n(args)
        compute = ComputeData(data_collector)
        compute.also_likes(doc_uuid, user_uuid, sort_fn=top_n_sorted, n=n)
    except Exception as e:
        logger.exception('Exception encountered during Task 5')

def task_6(data_collector: DataCollector, args):
    logger.info('Task 6: Also likes graph, inside GUI.')
    #! Dont forget to catch key errors
    user_uuid = get_user_uuid(args)


def task_7(data_collector: DataCollector, args):
    logger.info('Task 7: Open the GUI')
    gui.open()

def task_8(data_collector: DataCollector, args):
    logger.info('Task 8: Command line, This is it!')


task_picker = OrderedDict()
task_picker['1'] = task_1
task_picker['2a'] = task_2a
task_picker['2b'] = task_2b
task_picker['3a'] = task_3a
task_picker['3b'] = task_3b
task_picker['4d'] = task_4d
task_picker['5'] = task_5
task_picker['6'] = task_6
task_picker['7'] = task_7
task_picker['8'] = task_8


def next_item(key) -> str:
    try:
        return list(task_picker)[list(task_picker.keys()).index(key) + 1]
    except IndexError as e:
        return '1'

def raise_invalid_task(*args, **kwargs):
    raise InvalidTaskIDError


def tasks(data_collector: DataCollector, thread: Thread, task_id: str, args) -> None:
    finished = False
    loading_event = Event()
    loading_bar = Thread(target=loading_data, args=(loading_event,), daemon=True)
    loading_bar.start()
    thread.join()
    loading_event.set()
    loading_bar.join()

    while not finished:
        finished, task_id, args = begin_task(data_collector, task_id, args)


def begin_task(data_collector: DataCollector, task_id, args) -> bool:
    run_task = task_picker.get(task_id, raise_invalid_task)
    print('------------------ Task: {} ------------------'.format(task_id))
    run_task(data_collector, args)


    print()
    next_task = next_item(task_id)
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


def get_doc_uuid(args) -> str:
    if args is None or not hasattr(args, 'doc_uuid'):
        doc_uuid = input('Doc UUID: ')
    else:
        doc_uuid = args.doc_uuid


    doc_uuid = validate_doc_uuid(doc_uuid)

    return doc_uuid


def get_user_uuid(args) -> str:
    if args is None or not hasattr(args, 'user_uuid'):
        user_uuid = input('User UUID: ')
    else:
        user_uuid = args.user_uuid  

    if user_uuid is not None:
        user_uuid = validate_user_uuid(user_uuid)
    return user_uuid


def get_n(args) -> int:
    if args is None or not hasattr(args, 'limit_data'):
        return 10
    else:
        return args.limit_data


def loading_data(done_event: Event) -> None:
    with alive_bar(title='Processing data file...', total=None) as bar:
        while not done_event.is_set():
            bar()
            sleep(0.1)
            


def check_exit(string: str) -> str:
    if string.lower() == 'e':
        sys.exit(0)
    return string

def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate


@static_vars(step_id=0)
def next_step(additional_info='', step_id=0):
    step_names = {
        1: '1',
        2: '2'
    }

    if step_id != 0:
        next_step.step_id = step_id
    else:
        next_step.step_id += 1

    if next_step.step_id not in step_names.keys():
        raise Exception('Step ID {} is out of total steps number '.format(
            next_step.step_id, str(len(step_names))))

    step_info_template = '[Step {}/{}] {}'
    step_name = step_names[next_step.step_id] + \
        (' ({})'.format(additional_info) if additional_info else '')
    step_info_template = step_info_template.format(
        next_step.step_id, len(step_names), step_name)
    print(step_info_template)

