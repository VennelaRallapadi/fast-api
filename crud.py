from fastapi import FastAPI,HTTPException, status

from pydantic import BaseModel

Books = [
    {
        "id":1,
        "title":"The Python",
        "Author":"Vennela",
        "Publish_date":"25-10-2002",
    },
    {
        "id":2,
        "title":"The java",
        "Author": "Siva",
        "Publish_date":"25-10-2003",
    },
    {
        "id":3,
        "title":"The C",
        "Author": "Vanaja",
        "Publish_date":"25-10-2004",
    },
    {
       "id":4,
        "title":"The C#",
        "Author": "Pranav",
        "Publish_date":"25-10-2005",
    },
    
    
]

app = FastAPI()
@app.get("/book")
def get_book():
    return Books

class Book(BaseModel):
    id:int
    title:str
    author:str
    publish_date:str
    

@app.get("/book/{book_id}")
def get_book_by_id(book_id: int):
    for book in Books:
        if book["id"] == book_id:
            return book

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Book not found"
    )

    
    
@app.post("/book")
def create_book(book: Book):
    new_book = book.model_dump()
    Books.append(new_book)
    return new_book
    

class BookUpdate(BaseModel):
    title:str
    author:str
    publish_date:str
    
@app.put("/book/{book_id}")
def update_book(book_id: int, book_update: BookUpdate):
    for book in Books:
        if book['id']==book_id:
            book['title']=book_update.title
            book['author']=book_update.author
            book['publish_date']=book_update.publish_date
            
            return book
        
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Book not found"
    )
        

@app.delete("/book/{book_id}")
def delete_book(book_id: int):
    for book in Books:
        if book["id"] == book_id:
            Books.remove(book)
            return {"message": "Book deleted successfully"}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Book not found"
    )