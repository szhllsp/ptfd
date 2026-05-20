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
    views: int
    reads: int
    likes: int
    shares: int
    platform: str
