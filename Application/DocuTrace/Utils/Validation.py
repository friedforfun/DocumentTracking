import errno
import os
import sys
import argparse
import regex

from DocuTrace.Utils.Logging import logger
from DocuTrace.Utils.Exceptions import InvalidPathError, InvalidTaskIDError, InvalidUserUUIDError, InvalidDocUUIDError

"""Entertaining stack overflow post by Cecil Curry. Path validity checks use this. 
https://stackoverflow.com/questions/9532499/check-whether-a-path-is-valid-in-python-without-creating-a-file-at-the-paths-ta
"""

MAX_TRIES = 3
user_regex = regex.compile(r"^[\da-fA-F]{16}$")
doc_regex = regex.compile(r"^\d{12}-[\da-zA-Z]{32}$")

# Sadly, Python fails to provide the following magic number for us.
ERROR_INVALID_NAME = 123
'''
Windows-specific error code indicating an invalid pathname.

See Also
----------
https://docs.microsoft.com/en-us/windows/win32/debug/system-error-codes--0-499-
    Official listing of all such codes.
'''


def is_pathname_valid(pathname: str) -> bool:
    '''
    `True` if the passed pathname is a valid pathname for the current OS;
    `False` otherwise.
    '''
    # If this pathname is either not a string or is but is empty, this pathname
    # is invalid.
    try:
        if not isinstance(pathname, str) or not pathname:
            return False

        # Strip this pathname's Windows-specific drive specifier (e.g., `C:\`)
        # if any. Since Windows prohibits path components from containing `:`
        # characters, failing to strip this `:`-suffixed prefix would
        # erroneously invalidate all valid absolute Windows pathnames.
        _, pathname = os.path.splitdrive(pathname)

        # Directory guaranteed to exist. If the current OS is Windows, this is
        # the drive to which Windows was installed (e.g., the "%HOMEDRIVE%"
        # environment variable); else, the typical root directory.
        root_dirname = os.environ.get('HOMEDRIVE', 'C:') \
            if sys.platform == 'win32' else os.path.sep
        assert os.path.isdir(root_dirname)   # ...Murphy and her ironclad Law

        # Append a path separator to this directory if needed.
        root_dirname = root_dirname.rstrip(os.path.sep) + os.path.sep

        # Test whether each path component split from this pathname is valid or
        # not, ignoring non-existent and non-readable path components.
        for pathname_part in pathname.split(os.path.sep):
            try:
                os.lstat(root_dirname + pathname_part)
            # If an OS-specific exception is raised, its error code
            # indicates whether this pathname is valid or not. Unless this
            # is the case, this exception implies an ignorable kernel or
            # filesystem complaint (e.g., path not found or inaccessible).
            #
            # Only the following exceptions indicate invalid pathnames:
            #
            # * Instances of the Windows-specific "WindowsError" class
            #   defining the "winerror" attribute whose value is
            #   "ERROR_INVALID_NAME". Under Windows, "winerror" is more
            #   fine-grained and hence useful than the generic "errno"
            #   attribute. When a too-long pathname is passed, for example,
            #   "errno" is "ENOENT" (i.e., no such file or directory) rather
            #   than "ENAMETOOLONG" (i.e., file name too long).
            # * Instances of the cross-platform "OSError" class defining the
            #   generic "errno" attribute whose value is either:
            #   * Under most POSIX-compatible OSes, "ENAMETOOLONG".
            #   * Under some edge-case OSes (e.g., SunOS, *BSD), "ERANGE".
            except OSError as exc:
                if hasattr(exc, 'winerror'):
                    if exc.winerror == ERROR_INVALID_NAME:
                        return False
                elif exc.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                    return False
    # If a "TypeError" exception was raised, it almost certainly has the
    # error message "embedded NUL character" indicating an invalid pathname.
    except TypeError as exc:
        return False
    # If no exception was raised, all path components and hence this
    # pathname itself are valid. (Praise be to the curmudgeonly python.)
    else:
        return True
    # If any other exception was raised, this is an unrelated fatal issue
    # (e.g., a bug). Permit this exception to unwind the call stack.
    #
    # Did we mention this should be shipped with Python already?


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def validate_path(path: str) -> str:
    """Validate the path string

    Args:
        path (str): A path provided by the user

    Raises:
        InvalidPathError: Invalid path was provided too many times

    Returns:
        str: A valid path
    """
    attempts = 1
    if not is_pathname_valid(path) or not path.lower().endswith('.json'):
        while (not is_pathname_valid(path) or not path.lower().endswith('.json')) and attempts < MAX_TRIES:
            logger.warning('Invalid path to file detected. Please check and try again. If all else fails try and absolute path.')
            path = input('Please enter a valid path: ')
            attempts += 1

        if attempts > attempts:
            raise InvalidPathError('Invalid path entered too many times.')
    return path


def validate_task(task: str) -> str:
    """Validate the task identifying string

    Args:
        task (str): A task id

    Raises:
        InvalidTaskIDError: Invalid task id entered too many times

    Returns:
        str: A valid task id
    """
    # Handle circular import
    from DocuTrace.Utils.Tasks import task_picker

    attempts = 1
    if not task in task_picker.keys():
        while not task in task_picker.keys() and attempts < MAX_TRIES:
            logger.warning('Invalid task identifier has been provided, please provide one of {}'.format(list(task_picker.keys())))
            task = input('Please enter a valid task id: ')
            attempts += 1
        
        if attempts > 4:
            raise InvalidTaskIDError('Invalid task id entered too many times')
    return task


def validate_user_uuid(user_uuid: str) -> str:
    """Validate a user uuid string

    Args:
        user_uuid (str): A user uuid, should be 16 hexadecimal characters.
    Raises:
        InvalidUserUUIDError: Invalid user UUID id entered too many times

    Returns:
        str: A valid user UUID
    """
    attempts = 1
    if not user_regex.fullmatch(user_uuid):
        while not user_regex.fullmatch(user_uuid) and attempts < MAX_TRIES:
            if user_uuid is '' or None:
                return None
                
            logger.warning('Invalid user UUID detected. Please try again.')
            user_uuid = input('Please enter a valid user UUID: ')
            attempts += 1

        if attempts >= 4:
            raise InvalidUserUUIDError('Invalid user UUID entered too many times')

    return user_uuid.lower()


def validate_doc_uuid(doc_uuid: str) -> str:

    attempts = 1
    if not doc_regex.fullmatch(doc_uuid):
        while not doc_regex.fullmatch(doc_uuid) and attempts < MAX_TRIES:
            logger.warning('Invalid doc UUID detected. Please try again.')
            doc_uuid = input('Please enter a valid doc UUID: ')
            attempts += 1
        
        if attempts >= 4:
            raise InvalidDocUUIDError('Invalid doc UUID entered too many times')

    return doc_uuid