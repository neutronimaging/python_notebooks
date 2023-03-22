from __code.timepix3_histo_hdf5_mcp_detector import FittingRegions


class FittingErrorException(Exception):

    def __init__(self, fitting_region=FittingRegions.high_lambda, message=""):
        self.message = message
        self.fitting_region = fitting_region
        super().__init__(self.message)

    def __str__(self):
        return f"{self.fitting_region} -> {self.message}!"


class HighLambdaFittingError(FittingErrorException):
    pass


class LowLambdaFittingError(FittingErrorException):
    pass


class BraggPeakFittingError(FittingErrorException):
    pass
