def get_adapter(platform: str):
    if platform == "toutiao":
        from .toutiao import ToutiaoAdapter
        return ToutiaoAdapter()
    raise ValueError(f"Unsupported platform: {platform}")
