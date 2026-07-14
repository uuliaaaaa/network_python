"""
01_bookstore — CRUD API для книжного магазина 📚
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import Optional


# ============================================================
# МОДЕЛИ
# ============================================================

class Category(BaseModel):
    id: int
    name: str = Field(min_length=1, max_length=50)


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    model_config = {"extra": "forbid"}


class Book(BaseModel):
    id: int
    title: str = Field(min_length=1, max_length=100)
    author: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=1900, le=2025)
    isbn: str
    price: float = Field(gt=0)
    category_id: Optional[int] = None


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    author: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=1900, le=2025)
    isbn: str
    price: float = Field(gt=0)
    category_id: Optional[int] = None

    @field_validator('isbn')
    @classmethod
    def validate_isbn(cls, v: str) -> str:
        return v.strip()


# ============================================================
# ПРИЛОЖЕНИЕ И ХРАНИЛИЩЕ
# ============================================================

app = FastAPI(title="Bookstore API")

BOOKS: list[dict] = []
CATEGORIES: list[dict] = []


# ============================================================
# КАТЕГОРИИ
# ============================================================

@app.get("/categories")
def list_categories():
    return CATEGORIES


@app.post("/categories", status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate):
    new_id = len(CATEGORIES) + 1
    new_cat = category.model_dump()
    new_cat["id"] = new_id
    CATEGORIES.append(new_cat)
    return new_cat


# ============================================================
# КНИГИ
# ============================================================

@app.get("/books")
def list_books(category_id: Optional[int] = None, year: Optional[int] = None):
    result = BOOKS.copy()
    if category_id is not None:
        result = [b for b in result if b.get("category_id") == category_id]
    if year is not None:
        result = [b for b in result if b.get("year") == year]
    return result


@app.get("/books/search")
def search_books(query: str):
    if not query:
        return []
    q = query.lower()
    result = []
    for b in BOOKS:
        if q in b["title"].lower() or q in b["author"].lower():
            result.append(b)
    return result


@app.get("/books/{book_id}")
def get_book(book_id: int):
    for b in BOOKS:
        if b["id"] == book_id:
            return b
    return JSONResponse(
        status_code=404,
        content={"detail": "Book not found", "code": "NOT_FOUND"}
    )


@app.post("/books", status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate):
    for b in BOOKS:
        if b["isbn"] == book.isbn:
            raise HTTPException(status_code=409, detail={"detail": "ISBN already exists", "code": "DUPLICATE_ISBN"})

    new_id = len(BOOKS) + 1
    new_book = book.model_dump()
    new_book["id"] = new_id
    BOOKS.append(new_book)
    return new_book


@app.put("/books/{book_id}")
def update_book(book_id: int, book: BookCreate):
    for idx, b in enumerate(BOOKS):
        if b["id"] == book_id:
            if b["isbn"] != book.isbn:
                for other in BOOKS:
                    if other["id"] != book_id and other["isbn"] == book.isbn:
                        return JSONResponse(
                            status_code=409,
                            content={"detail": "ISBN already exists", "code": "DUPLICATE_ISBN"}
                        )

            updated = book.model_dump()
            updated["id"] = book_id
            BOOKS[idx] = updated
            return updated
    return JSONResponse(
        status_code=404,
        content={"detail": "Book not found", "code": "NOT_FOUND"}
    )


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int):
    for idx, b in enumerate(BOOKS):
        if b["id"] == book_id:
            del BOOKS[idx]
            return
    return JSONResponse(
        status_code=404,
        content={"detail": "Book not found", "code": "NOT_FOUND"}
    )
