
class InvalidArgument(Exception):
    """Raised when an invalid argument has been provided.
    """


class InvalidPathError(InvalidArgument):
    """Raised when an invalid path has been entered.
    """

    def __init__(self, message='Invalid path provided as an argument'):
        self.message = message
        super().__init__(self.message)

class InvalidTaskIDError(InvalidArgument):
    """Raised when an invalid task id has been entered.
    """
    def __init__(self, message='Invalid Task id provided as an argument'):
        self.message = message
        super().__init__(self.message)

class InvalidUserUUIDError(InvalidArgument):
    """Raised when an invaid user UUID has been entered.
    """
    def __init__(self, message='Invalid user UUID provided as an argument'):
        self.message = message
        super().__init__(self.message)
