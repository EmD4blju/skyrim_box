from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    comments: list["Comment"] = Relationship(back_populates="user")
    
class Item(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: str
    comments: list["Comment"] = Relationship(back_populates="item")
    
class Comment(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    content: str
    user_id: int = Field(foreign_key="user.id")
    item_id: int = Field(foreign_key="item.id")
    created_at: datetime = Field(default_factory=datetime.today, nullable=True)
    user: User = Relationship(back_populates="comments")
    item: Item = Relationship(back_populates="comments")