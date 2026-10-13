# my-api-fetcher/src/api_client.py
"""
APIClient - sends HTTP GET requests to JSONPlaceholder and returns parsed JSON.

Every public method returns Python data (dict / list) on success, or None on failure.
The reason for the last failure is kept in `self.last_error` so the CLI can show it.
"""
import requests


class APIClient:
    BASE_URL = "https://jsonplaceholder.typicode.com"

    def __init__(self, base_url=None, timeout=10):
        self.base_url = (base_url or self.BASE_URL).rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()          # reuses the connection between calls
        self.session.headers.update({"Accept": "application/json"})
        self.last_error = None
        self.last_status = None

    def _get(self, endpoint, params=None):
        """GET {base_url}{endpoint}?params and return the decoded JSON (or None)."""
        url = f"{self.base_url}{endpoint}"
        self.last_error, self.last_status = None, None
        query = "&".join(f"{k}={v}" for k, v in (params or {}).items())
        print(f"[INFO] GET {url}{'?' + query if query else ''}")
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            self.last_status = response.status_code
            response.raise_for_status()               # 4xx / 5xx -> HTTPError
            return response.json()
        except requests.exceptions.HTTPError:
            if self.last_status == 404:
                self.last_error = "ไม่พบข้อมูล (404 Not Found)"
            else:
                self.last_error = f"เซิร์ฟเวอร์ตอบกลับผิดพลาด (HTTP {self.last_status})"
        except requests.exceptions.ConnectionError:
            self.last_error = "เชื่อมต่อเซิร์ฟเวอร์ไม่ได้ - ตรวจสอบอินเทอร์เน็ต"
        except requests.exceptions.Timeout:
            self.last_error = f"เซิร์ฟเวอร์ไม่ตอบกลับภายใน {self.timeout} วินาที (Timeout)"
        except requests.exceptions.RequestException as e:
            self.last_error = f"เกิดข้อผิดพลาดของคำขอ: {e}"
        except ValueError:                            # response.json() failed
            self.last_error = "ข้อมูลที่ได้รับไม่ใช่ JSON ที่ถูกต้อง"
        print(f"[ERROR] {self.last_error}")
        return None

    # ---------- endpoints ----------
    def fetch_single_todo(self, todo_id):
        """GET /todos/{id} -> dict"""
        return self._get(f"/todos/{todo_id}")

    def fetch_all_posts(self):
        """GET /posts -> list of dicts"""
        return self._get("/posts")

    def fetch_user_todos(self, user_id):
        """GET /todos?userId={id} -> list of dicts (empty list if the user has none)"""
        return self._get("/todos", params={"userId": user_id})

    def fetch_user(self, user_id):
        """GET /users/{id} -> dict (used to show the user's name next to their TODOs)"""
        return self._get(f"/users/{user_id}")


# ---------- pure helpers (no network - easy to test) ----------
def summarize_todos(todos):
    """Returns counts and completion percentage for a list of TODO dicts."""
    total = len(todos)
    done = sum(1 for t in todos if t.get("completed"))
    return {
        "total": total,
        "completed": done,
        "pending": total - done,
        "percent": round(done * 100 / total, 1) if total else 0.0,
    }


def shorten(text, width):
    """Puts text on one line and cuts it to `width` characters with '...'."""
    text = " ".join(str(text or "").split())
    return text if len(text) <= width else text[: width - 3] + "..."
