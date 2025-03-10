from enum import Enum

from ..constants.computer_part_categories import *

class ComputerPartType(Enum):
    CASE = "CASE",
    GPU = "GPU",
    CPU = "CPU",
    SSD = "SSD",
    COOLER = "COOLER",
    PSU = "PSU",
    MOTHERBOARD = "MOTHERBOARD",
    RAM = "RAM",
    OTHER = "OTHER"

    @staticmethod
    def from_str(category: str):
        if category in CASE_CATEGORIES:
            return ComputerPartType.CASE
        elif category in GPU_CATEGORIES:
            return ComputerPartType.GPU
        elif category in CPU_CATEGORIES:
            return ComputerPartType.CPU
        elif category in SSD_CATEGORIES:
            return ComputerPartType.SSD
        elif category in COOLER_CATEGORIES:
            return ComputerPartType.COOLER
        elif category in PSU_CATEGORIES:
            return ComputerPartType.PSU
        elif category in MOTHERBOARD_CATEGORIES:
            return ComputerPartType.MOTHERBOARD
        elif category in MOTHERBOARD_CATEGORIES:
            return ComputerPartType.MOTHERBOARD
        else:
            return ComputerPartType.OTHER