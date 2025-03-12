from dataclasses import dataclass

@dataclass
class ComputerPart:
    barcode: str
    partName: str
    partType: str
    price: float
    imageUrl: str
    storeUrl: str
    storeName: str

    def __init__(
        self, 
        barcode: str, 
        part_name: str, 
        part_type: str, 
        price: float, 
        image_url: str, 
        store_url: str, 
        store_name: str
    ):
        self.barcode = barcode
        self.partName = part_name
        self.partType = part_type
        self.price = price
        self.imageUrl = image_url
        self.storeUrl = store_url
        self.storeName = store_name
