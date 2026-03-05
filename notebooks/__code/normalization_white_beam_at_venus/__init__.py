class DataType:
    sample = "sample"
    ob = "ob"
    dc = "dc"

class Roi:

    def __init__(self, left: int = 0, top: int = 0, width: int = 1, height: int = 1):
        self.left: int = left
        self.top: int = top
        self.width: int = width
        self.height: int = height

    def __repr__(self):
        return f"Roi(left={self.left}, top={self.top}, width={self.width}, height={self.height})"



class DetectorType:
    ikonxl = "ikonxl"
    qhy600 = "qhy600"
    