from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import CRUD

app = FastAPI(title="Igam Article API - Backend")

# Schema buat POST /article/
class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=20, description="Minimal 20 karakter")
    content: str = Field(..., min_length=200, description="Minimal 200 karakter")
    category: str = Field(..., min_length=3, description="Minimal 3 karakter")
    status: str = Field(default="publish", description="publish / draft / thrash")

@app.get("/")
def root():
    return {"message": "API jalan! Buka /docs untuk test"}

@app.post("/article/")
def create_article(payload: ArticleCreate):
    try:
        # validasi extra biar sama kayak di Flet
        data = payload.model_dump()
        new_id = CRUD.insert_article(data)
        article = CRUD.get_article(new_id)
        return {"message": "Article berhasil ditambahkan", "data": article}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

@app.get("/article/")
def get_all_articles(status: str = None):
    try:
        rows = CRUD.list_articles(status)
        return {"count": len(rows), "data": rows}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

@app.get("/article/{article_id}")
def get_one_article(article_id: int):
    row = CRUD.get_article(article_id)
    if not row:
        raise HTTPException(status_code=404, detail="Article tidak ditemukan")
    return row

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)