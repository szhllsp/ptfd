from datetime import datetime
from pydantic import BaseModel


class Message(BaseModel):
    id: str
    from_user: str
    content: str
    time: datetime
    platform: str


class Comment(BaseModel):
    id: str
    post_id: str
    author: str
    content: str
    time: datetime
    reply_count: int


class Stats(BaseModel):
    post_id: str
    title: str = ""
    views: int = 0
    reads: int = 0
    comments: int = 0
    likes: int = 0
    shares: int = 0
    platform: str = ""
