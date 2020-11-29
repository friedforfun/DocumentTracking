#!/usr/bin/env python
import sys, argparse
from threading import Thread
from DocuTrace.Analysis.ComputeData import ComputeData
from DocuTrace.Analysis.DataCollector import DataCollector
from DocuTrace.Utils.Logging import logger
from DocuTrace.Utils.Validation import validate_path, validate_task
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

    Returns:
        ArgumentParser: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Command line interface for DocuTrace.')
    args = parser.add_argument_group('Core parameters')
    args.add_argument('-u', '--user_uuid', help='Specifies the user uuid', required=False, default=None, type=str)
    args.add_argument('-d', '--doc_uuid',help='Specifies the document uuid', required=False, default=None, type=str)
    # Task id is mandatory for command line usage
    args.add_argument('-t', '--task_id', help='Specifies the task id', required=False, type=str)
    args.add_argument('-f', '--filepath', help='Specifies the file name', required=False, type=str)
    args.add_argument('-v', '--verbose', type=int, required=False, default=30, nargs='?', const=20, help='Set the verbosity level, 20 for INFO, 10 for DEBUG. Default is 30: WARN')
    return parser.parse_args()


def process_file(data_collector):
    """Begin processing this file.
    """
    data_collector.gather_data()


if __name__ == "__main__":
    sys.exit(main() or 0)
