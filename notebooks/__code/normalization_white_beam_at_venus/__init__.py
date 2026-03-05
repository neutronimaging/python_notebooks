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
    
    
class DataDict:
    full_path = None
    nexus_path = None
    data = None
    acquisition_time = None
    proton_charge = None
    
    def __str__(self):
        return f"DataDict(full_path={self.full_path}, nexus_path={self.nexus_path}, acquisition_time={self.acquisition_time}, proton_charge={self.proton_charge})"
    
    def __repr__(self):
        return self.__str__()
    
    
class FolderPath:
    sample = None
    ob = None
    dc = None
    output = None
    shared = None
    nexus = None
    ipts = None