from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, create_engine, select
from typing import List
from pydantic import BaseModel

from models import Item, Comment, User

# Database connection
DATABASE_URL = "postgresql+psycopg2://skyrim_user:skyrim_password@localhost:5432/skyrim_db"
engine = create_engine(DATABASE_URL)

# Initialize FastAPI Fast App
app = FastAPI(title="Skyrim Box API", description="Big Data Engineering Flow Playground")

# Enable CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_session():
    with Session(engine) as session:
        yield session

# Schema for incoming comment request
class CommentCreate(BaseModel):
    content: str
    user_id: int = 1 # Hardcoded to "Dragonborn" from our seed data for now

# 0. Health-check
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Skyrim Box API is active."}

# 1. Get Items
@app.get("/items", response_model=List[Item])
def get_items(session: Session = Depends(get_session)):
    items = session.exec(select(Item)).all()
    return items

# 2. Get Item Comments (Optional but helpful extra endpoint!)
@app.get("/items/{item_id}/comments", response_model=List[Comment])
def get_item_comments(item_id: int, session: Session = Depends(get_session)):
    # Verify the item exists first
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    # Sort placing newest first, but ensuring NULLs (old migrations) gracefully fall to the bottom instead of top
    comments = session.exec(
        select(Comment)
        .where(Comment.item_id == item_id)
        .order_by(Comment.created_at.desc().nulls_last())
    ).all()
    return comments

# 3. Post Comment
@app.post("/items/{item_id}/comments", response_model=Comment)
def post_comment(item_id: int, comment: CommentCreate, session: Session = Depends(get_session)):
    # Verify the item exists
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    # Build the new model object
    new_comment = Comment(
        content=comment.content,
        user_id=comment.user_id,
        item_id=item_id
    )
    
    # Save to db
    session.add(new_comment)
    session.commit()
    session.refresh(new_comment)
    
    return new_comment

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
