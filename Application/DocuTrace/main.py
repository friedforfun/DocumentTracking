#!/usr/bin/env python
import sys, argparse
from threading import Thread
from DocuTrace.Analysis.ComputeData import ComputeData
from DocuTrace.Analysis.DataCollector import DataCollector
from DocuTrace.Utils.Logging import logger
from DocuTrace.Utils.Validation import is_pathname_valid, InvalidPathError

def main():
    run(parse_args())


def run(args):
    try:
        verbosity = args.verbose
        logger.setLevel(verbosity)
        logger.info('Verbosity set to display info messages.')
        logger.debug('Verbosity set to display debug messages.')

        path = validate_path(args.filepath)

        data_collector = DataCollector(path)
        load = Thread(target=process_file, args=(data_collector,), daemon=True)
        load.start()

        user_uuid = args.user_uuid
        doc_uuid = args.doc_uuid
        tast_id = args.task_id

        print('Sucess!')
        print('User_uuid: {}'.format(user_uuid))
        print('doc_uuid: {}'.format(doc_uuid))
        print('tast_id: {}'.format(tast_id))
        # Step 2. Load data

    except InvalidPathError as e:
        logger.exception(e)
        sys.exit(1)

    except Exception as e:
        logger.exception(e)
        sys.exit(1)



def parse_args():
    """Parse the args provided to this namespace

    Returns:
        ArgumentParser: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Command line interface for DocuTrace.')
    args = parser.add_argument_group('Core parameters')
    args.add_argument('-u', '--user_uuid', help='Specifies the user uuid', required=False, type=str)
    args.add_argument('-d', '--doc_uuid',help='Specifies the document uuid', required=False, type=str)
    # Task id is mandatory for command line usage
    args.add_argument('-t', '--task_id', help='Specifies the task id', required=True, type=int)
    args.add_argument('-f', '--filepath', help='Specifies the file name', required=True, type=str)
    args.add_argument('-v', '--verbose', type=int, required=False, default=30, nargs='?', const=20, help='Set the verbosity level, 20 for INFO, 10 for DEBUG')
    return parser.parse_args()


def validate_path(path: str) -> str:
    """Validate the path string

    Args:
        path (str): A path provided by the user

    Raises:
        InvalidPathError: Invalid path was provided too many times

    Returns:
        str: A valid path
    """
    tries = 0
    if not is_pathname_valid(path) or not path.lower().endswith('.json'):
        while (not is_pathname_valid(path) or not path.lower().endswith('.json')) and tries < 4:
            logger.warning('Invalid path to file detected. Please check and try again. If all else fails try and absolute path.')
            path = input('Please enter a valid path: ')
            tries += 1

        if tries > 4 or not is_pathname_valid(path):
            raise InvalidPathError('Invalid path enterred too many times.')

    return path


def process_file(data_collector):
    """Begin processing this file.
    """
    data_collector.gather_data()


def task_1():
    logger.info('Task 1: The core functionality of this application is written in python.')

def task_2a():
    logger.info('Task 2a. Specifies a document UUID, and return a histogram of countries of the viewers.')

def task_2b():
    logger.info('Task 2b. Group the countries by continent, and generate a histogram of the continents of the viewers.')

def task_3a():
    logger.info('Task 3a: Histogram of verbose views by browser.')

def task_3b():
    logger.info('Task 3b: Histogram of views by browser, with processed browser names.')

def task_4d():
    logger.info('Task 4d: 10 most avid readers.')

def task_5():
    logger.info('Task 5: Also likes top n documents.')

def task_6():
    logger.info('Task 6: Also likes graph, inside GUI.')

def task_7():
    logger.info('Task 7: Open the GUI')

def task_8():
    logger.info('Task 8: Command line, This is it!')


task_picker = {
    '1': task_1,
    '2a': task_2a,
    '2b': task_2b,
    '3a': task_3a,
    '3b': task_3b,
    '4d': task_4d,
    '5': task_5,
    '6': task_6,
    '7': task_7,
    '8': task_8
}

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



def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


if __name__ == "__main__":
    sys.exit(main() or 0)
