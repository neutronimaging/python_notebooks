class FileErrorException(Exception):

    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}"


class NoFilesFound(FileErrorException):
    pass
