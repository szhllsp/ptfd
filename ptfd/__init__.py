from typing import Optional


class PTFD:
    def __init__(self):
        self._adapters = {}

    def _get_adapter(self, platform: str):
        if platform not in self._adapters:
            if platform == "toutiao":
                from .adapters.toutiao import ToutiaoAdapter
                self._adapters[platform] = ToutiaoAdapter()
            else:
                raise ValueError(f"Unsupported platform: {platform}")
        return self._adapters[platform]

    def login(self, platform: str):
        return self._get_adapter(platform).login()

    def check_login(self, platform: str) -> bool:
        return self._get_adapter(platform).check_login()

    def list_articles(self, platform: str, page=None):
        return self._get_adapter(platform).list_articles(page=page)

    def publish(self, platform: str, title: str, content: str, images: Optional[list] = None):
        return self._get_adapter(platform).publish(title, content, images or [])

    def publish_micro(
        self,
        platform: str,
        content: str,
        images: Optional[list] = None,
        topics: Optional[list] = None,
        declare_first: bool = False,
        source_network: bool = False,
        source_internal: bool = False,
        personal_view: bool = False,
    ):
        return self._get_adapter(platform).publish_micro(
            content=content,
            images=images or [],
            topics=topics or [],
            declare_first=declare_first,
            source_network=source_network,
            source_internal=source_internal,
            personal_view=personal_view,
        )

    def delete(self, platform: str, post_id: str, page=None):
        return self._get_adapter(platform).delete(post_id, page=page)

    def get_messages(self, platform: str):
        return self._get_adapter(platform).get_messages()

    def get_comments(self, platform: str, post_id: str):
        return self._get_adapter(platform).get_comments(post_id)

    def reply_comment(self, platform: str, comment_id: str, text: str):
        return self._get_adapter(platform).reply_comment(comment_id, text)

    def get_stats(self, platform: str, post_id: str):
        return self._get_adapter(platform).get_stats(post_id)
