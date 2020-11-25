#!/usr/bin/env python
import sys, argparse
from DocuTrace.Utils.Logging import logger

def main():
    next_step()
    run(parse_args())


def run(args):
    try:
        # Step 1. Parse and validate arguments
        user_uuid = args.user_uuid
        doc_uuid = args.doc_uuid
        tast_id = args.task_id
        filename = args.filename
        print('Sucess!')
        # Step 2. Load data
        next_step(step_id=2)

    except Exception as e:
        logger.exception(e)
        sys.exit(1)



def parse_args():
    parser = argparse.ArgumentParser()
    args = parser.add_argument_group('Params')
    args.add_argument('-u', '--user_uuid', nargs=1, help='Specifies the user uuid', required=True)
    args.add_argument('-d', '--doc_uuid', nargs=1, help='Specifies the document uuid', required=True)
    args.add_argument('-t', '--task_id', nargs=1, help='Specifies the task id', required=True)
    args.add_argument('-f', '--filepath', nargs=1, help='Specifies the file name', required=True)
    args.add_argument('-v', '--verbose', type=str2bool, required=False, default=False, nargs='?', const=True, help='Set a verbose output')
    return parser.parse_args()


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
