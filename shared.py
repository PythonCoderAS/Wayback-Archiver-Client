from uuid import UUID, getnode

from requests import Session

from config import SERVER_BASE

session = Session()


def get_session_id() -> int:
    r = session.post(f"{SERVER_BASE}/api/session", json={"hostname": str(UUID(int=getnode()))})
    r.raise_for_status()
    return r.json()["id"]


def add_url(session_id: int, url: str):
    r = session.post(f"{SERVER_BASE}/api/item", json={"session_id": session_id, "url": url})
    r.raise_for_status()
    return r.json()["id"]
