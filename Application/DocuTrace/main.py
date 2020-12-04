#!/usr/bin/env python
import sys, argparse
from threading import Thread
from DocuTrace.Analysis.ComputeData import ComputeData
from DocuTrace.Analysis.DataCollector import DataCollector
from DocuTrace.Utils.Logging import logger
from DocuTrace.Utils.Validation import str2bool, validate_path, validate_task
from DocuTrace.Utils.Exceptions import InvalidPathError, InvalidTaskIDError
from DocuTrace.Utils.Tasks import tasks


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

        task = validate_task(args.task_id)
        tasks(data_collector, load, task, args)



        print('Sucess!')
        # Step 2. Load data

    except InvalidPathError as e:
        logger.exception(e)
        sys.exit(1)

    except InvalidTaskIDError as e:
        logger.exception(e)
        sys.exit(1)

    except Exception as e:
        logger.exception(e)
        sys.exit(1)



def parse_args():
    """Parse the args provided to this namespace

    usage: ``main.py [-h] [-u USER_UUID] [-d DOC_UUID] [-t TASK_ID] -f FILEPATH [-n [LIMIT_DATA]] [-v [VERBOSE]] [-e [EXIT_EARLY]]``

    **Command line interface for DocuTrace.**
    

    optional arguments:

    -h, --help            show this help message and exit

    Core parameters:

    -u USER_UUID, --user_uuid USER_UUID         Specifies the user uuid
                            
    -d DOC_UUID, --doc_uuid DOC_UUID            Specifies the document uuid
                            
    -t TASK_ID, --task_id TASK_ID               Specifies the task id
                            
    -f FILEPATH, --filepath FILEPATH            Specifies the file name
                            

    Secondary parameters:

    -n LIMIT_DATA, --limit_data LIMIT_DATA      Limits the number of displayed data points for tasks 2a, 2b, 3a, 3b, 4d, and 5.
                            
    -v VERBOSE, --verbose VERBOSE               Set the verbosity level, 20 for INFO, 10 for DEBUG. Default is 30: WARN
                            
    -e EXIT_EARLY, --exit_early EXIT_EARLY      Exit the program after running only the specified task.

    Returns:
        ArgumentParser: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Command line interface for DocuTrace.')
    args = parser.add_argument_group('Core parameters')
    args.add_argument('-u', '--user_uuid', help='Specifies the user uuid', required=False, default=None, type=str)
    args.add_argument('-d', '--doc_uuid',help='Specifies the document uuid', required=False, default=None, type=str)
    args.add_argument('-t', '--task_id', help='Specifies the task id', required=False, type=str)
    args.add_argument('-f', '--filepath', help='Specifies the file name', required=True, type=str)

    secondary_args = parser.add_argument_group('Secondary parameters')
    secondary_args.add_argument('-n', '--limit_data', help='Limits the number of displayed data points for tasks 2a, 2b, 3a, 3b, 4d, and 5.', type=int, required=False, default=None, const=20, nargs='?')
    secondary_args.add_argument('-v', '--verbose', type=int, required=False, default=30, nargs='?',
                                const=20, help='Set the verbosity level, 20 for INFO, 10 for DEBUG. Default is 30: WARN')
    secondary_args.add_argument('-e', '--exit_early', type=str2bool, default=False, const=True,
                                nargs='?', help='Exit the program after running only the specified task.')
    return parser.parse_args()


def process_file(data_collector):
    """Begin processing this file.
    """
    data_collector.gather_data()


if __name__ == "__main__":
    sys.exit(main() or 0)
