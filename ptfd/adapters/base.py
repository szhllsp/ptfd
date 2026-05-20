from abc import ABC, abstractmethod
from typing import Optional
from ptfd.models.schemas import Message, Comment, Stats


class BaseAdapter(ABC):

    @abstractmethod
    def login(self):
        """打开浏览器让用户手动登录，保存 Cookie"""
        pass

    @abstractmethod
    def check_login(self) -> bool:
        """检查 Cookie 是否有效"""
        pass

    @abstractmethod
    def list_articles(self) -> list[Stats]:
        """获取文章列表及统计数据"""
        pass

    @abstractmethod
    def publish(self, title: str, content: str, images: Optional[list] = None) -> str:
        """发布内容，返回 post_id"""
        pass

    @abstractmethod
    def delete(self, post_id: str) -> bool:
        """删除文章"""
        pass

    @abstractmethod
    def get_messages(self) -> list[Message]:
        """获取消息列表"""
        pass

    @abstractmethod
    def get_comments(self, post_id: str) -> list[Comment]:
        """获取评论列表"""
        pass

    @abstractmethod
    def reply_comment(self, comment_id: str, text: str) -> bool:
        """回复评论"""
        pass

    @abstractmethod
    def get_stats(self, post_id: str) -> Stats:
        """获取展示量/阅读量"""
        pass
