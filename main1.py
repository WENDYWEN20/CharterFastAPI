from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
app = FastAPI()
class Item(BaseModel):
    name: str=None
    is_done: bool=False
    
items=[]

@app.get("/")
def read_root():
    return {"Hello": "World"}
@app.post("/items")
def create_item(item: Item):
    items.append(item)
    return items
@app.get("/items/{itemId}", response_model=Item)
def read_item(itemId: int) -> Item:
    if( itemId>=len(items) or itemId<0):
        raise HTTPException(status_code=404, detail=f"Item {itemId} not found")
    return items[itemId]
@app.get("/items", response_model=list[Item])
def list_items(limit: int = 1):
    return items[0:limit]
@app.get("/get-by-name")
def get_item_by_name(name: str):
    for item in items:
        if item.name == name:
            return item
    raise HTTPException(status_code=404, detail=f"Item with name {name} not found")