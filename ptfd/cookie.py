import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def get_cookie_path(platform: str) -> str:
    cookie_dir = os.path.join(DATA_DIR, "cookies")
    os.makedirs(cookie_dir, exist_ok=True)
    return os.path.join(cookie_dir, f"{platform}.json")


def has_cookie(platform: str) -> bool:
    return os.path.exists(get_cookie_path(platform))
