from fastapi import FastAPI, APIRouter
from dataclasses import dataclass

user_router = APIRouter()

@dataclass
class Item():
    name : str
    description : str
    
@user_router.get("/items/{item_id}", response_model=Item)
def read_item(item_id: str, q: str = None):
    item = Item(
        name="Foo",
        description="A very nice Item"
    )
    return item
    
