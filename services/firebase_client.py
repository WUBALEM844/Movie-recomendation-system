import os
import json
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

LOCAL_DB = "user_data.json"


class FirebaseClient:
    """Minimal Firebase client wrapper with local fallback.

    - If `pyrebase` and a `firebase_config.json` file are available, uses Pyrebase for auth + database.
    - Otherwise falls back to a local JSON file for favorites/watchlist.
    """

    def __init__(self, config_path: str = "firebase_config.json"):
        self.config_path = config_path
        self.use_firebase = False
        self.use_firestore = False
        self.firebase = None
        self.auth = None
        self.db = None
        self.firestore = None

        # Try to load Firebase config. Prefer firebase_admin (Firestore) if available,
        # otherwise fall back to Pyrebase (Realtime DB) when web config exists.
        if os.path.exists(self.config_path):
            # First, try to initialize firebase_admin for Firestore using a service account
            try:
                try:
                    from firebase_admin import credentials, initialize_app, firestore as _firestore
                except Exception:
                    _firestore = None

                # If config file appears to be a service account JSON (has private_key), use it
                with open(self.config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)

                # Detect service account by presence of private_key or client_email
                if isinstance(cfg, dict) and ("private_key" in cfg or "client_email" in cfg):
                    try:
                        from firebase_admin import credentials, initialize_app, firestore as _firestore

                        cred = credentials.Certificate(self.config_path)
                        initialize_app(cred)
                        self.firestore = _firestore.client()
                        self.use_firestore = True
                        logger.info("Initialized firebase_admin Firestore client using service account config")
                    except Exception as e:
                        logger.warning(f"firebase_admin init failed: {e}")

                # If firebase_admin not used, try Pyrebase (web config) for Realtime DB / Auth
                if not self.use_firestore:
                    try:
                        import pyrebase

                        self.firebase = pyrebase.initialize_app(cfg)
                        self.auth = self.firebase.auth()
                        try:
                            self.db = self.firebase.database()
                        except Exception:
                            self.db = None
                        self.use_firebase = True
                        logger.info("Firebase client initialized using pyrebase (Realtime DB)")
                    except Exception as e:
                        logger.warning(f"pyrebase not available or failed to init: {e}. Falling back to local storage.")
                        self.use_firebase = False
            except Exception as e:
                logger.warning(f"Failed to parse firebase_config.json: {e}. Using local JSON fallback")
                self.use_firebase = False
        else:
            logger.info("No firebase_config.json found — using local JSON fallback")

        # Ensure local DB exists
        if not os.path.exists(LOCAL_DB):
            with open(LOCAL_DB, "w", encoding="utf-8") as f:
                json.dump({"users": {}}, f)

    # ------------------
    # Authentication (pyrebase only)
    # ------------------
    def signup(self, email: str, password: str, display_name: Optional[str] = None) -> Dict[str, Any]:
        if not self.use_firebase or not self.auth:
            # Local signup: create a user id and store in local DB
            uid = f"local_{email}"
            self._ensure_user(uid, email=email, display_name=display_name)
            return {"localId": uid, "email": email}

        user = self.auth.create_user_with_email_and_password(email, password)
        if display_name:
            try:
                self.auth.send_email_verification(user['idToken'])
            except Exception:
                pass
        return user

    def login(self, email: str, password: str) -> Dict[str, Any]:
        if not self.use_firebase or not self.auth:
            uid = f"local_{email}"
            self._ensure_user(uid, email=email)
            return {"localId": uid, "email": email}

        user = self.auth.sign_in_with_email_and_password(email, password)
        return user

    # ------------------
    # Local JSON helpers
    # ------------------
    def _read_local(self) -> Dict[str, Any]:
        with open(LOCAL_DB, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_local(self, data: Dict[str, Any]):
        with open(LOCAL_DB, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _ensure_user(self, uid: str, email: Optional[str] = None, display_name: Optional[str] = None):
        data = self._read_local()
        users = data.setdefault("users", {})
        if uid not in users:
            users[uid] = {"email": email, "display_name": display_name, "favorites": [], "watchlist": []}
            self._write_local(data)

    # ------------------
    # Favorites / Watchlist
    # ------------------
    def add_favorite(self, uid: str, movie: Dict[str, Any]):
        # Prefer Firestore when available
        if self.use_firestore and self.firestore:
            try:
                col = self.firestore.collection("users").document(uid).collection("favorites")
                # Use movie_id as document id when available
                doc_id = str(movie.get("movie_id")) if movie.get("movie_id") is not None else None
                if doc_id:
                    col.document(doc_id).set(movie)
                else:
                    col.add(movie)
                return True
            except Exception as e:
                logger.error(f"Firestore add_favorite failed: {e}")
                # fall through to local

        if self.use_firebase and self.db:
            try:
                path = f"users/{uid}/favorites"
                self.db.push(movie, path)
                return True
            except Exception as e:
                logger.error(f"Firebase add_favorite failed: {e}")
                return False

        data = self._read_local()
        users = data.setdefault("users", {})
        self._ensure_user(uid)
        favs = users[uid].setdefault("favorites", [])
        # avoid duplicates by movie_id
        if not any(f.get("movie_id") == movie.get("movie_id") for f in favs):
            favs.append(movie)
            self._write_local(data)
        return True

    def remove_favorite(self, uid: str, movie_id: int):
        if self.use_firestore and self.firestore:
            try:
                doc = self.firestore.collection("users").document(uid).collection("favorites").document(str(movie_id))
                doc.delete()
                return True
            except Exception as e:
                logger.error(f"Firestore remove_favorite failed: {e}")
                return False

        if self.use_firebase and self.db:
            logger.warning("remove_favorite via realtime DB not implemented")
            return False

        data = self._read_local()
        users = data.setdefault("users", {})
        if uid in users:
            favs = users[uid].get("favorites", [])
            favs = [f for f in favs if f.get("movie_id") != movie_id]
            users[uid]["favorites"] = favs
            self._write_local(data)
        return True

    def list_favorites(self, uid: str) -> List[Dict[str, Any]]:
        if self.use_firestore and self.firestore:
            try:
                col = self.firestore.collection("users").document(uid).collection("favorites")
                docs = col.stream()
                items = [d.to_dict() for d in docs]
                return items
            except Exception as e:
                logger.error(f"Firestore list_favorites failed: {e}")
                return []

        if self.use_firebase and self.db:
            try:
                path = f"users/{uid}/favorites"
                res = self.db.child(path).get()
                items = []
                if res.each():
                    for it in res.each():
                        items.append(it.val())
                return items
            except Exception as e:
                logger.error(f"Firebase list_favorites failed: {e}")
                return []

        data = self._read_local()
        users = data.get("users", {})
        return users.get(uid, {}).get("favorites", [])

    def add_watchlist(self, uid: str, movie: Dict[str, Any]):
        if self.use_firestore and self.firestore:
            try:
                col = self.firestore.collection("users").document(uid).collection("watchlist")
                doc_id = str(movie.get("movie_id")) if movie.get("movie_id") is not None else None
                if doc_id:
                    col.document(doc_id).set(movie)
                else:
                    col.add(movie)
                return True
            except Exception as e:
                logger.error(f"Firestore add_watchlist failed: {e}")
                # fall through to local

        if self.use_firebase and self.db:
            try:
                path = f"users/{uid}/watchlist"
                self.db.push(movie, path)
                return True
            except Exception as e:
                logger.error(f"Firebase add_watchlist failed: {e}")
                return False

        data = self._read_local()
        users = data.setdefault("users", {})
        self._ensure_user(uid)
        wl = users[uid].setdefault("watchlist", [])
        if not any(w.get("movie_id") == movie.get("movie_id") for w in wl):
            wl.append(movie)
            self._write_local(data)
        return True

    def list_watchlist(self, uid: str) -> List[Dict[str, Any]]:
        if self.use_firestore and self.firestore:
            try:
                col = self.firestore.collection("users").document(uid).collection("watchlist")
                docs = col.stream()
                items = [d.to_dict() for d in docs]
                return items
            except Exception as e:
                logger.error(f"Firestore list_watchlist failed: {e}")
                return []

        if self.use_firebase and self.db:
            try:
                path = f"users/{uid}/watchlist"
                res = self.db.child(path).get()
                items = []
                if res.each():
                    for it in res.each():
                        items.append(it.val())
                return items
            except Exception as e:
                logger.error(f"Firebase list_watchlist failed: {e}")
                return []

        data = self._read_local()
        users = data.get("users", {})
        return users.get(uid, {}).get("watchlist", [])


# Simple helper to get a default client
_client: Optional[FirebaseClient] = None


def get_client() -> FirebaseClient:
    global _client
    if _client is None:
        _client = FirebaseClient()
    return _client
