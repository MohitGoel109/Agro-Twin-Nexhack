"""In-memory store (latest check-up per machine). Resets on restart. Bounded size. No personal data."""
import threading
import time

_LOCK = threading.Lock()
_DATA = {}
MAX_ITEMS = 200


def save(machine_id, record):
    with _LOCK:
        record = dict(record, saved_at=time.time())
        _DATA[machine_id] = record
        if len(_DATA) > MAX_ITEMS:
            oldest = min(_DATA, key=lambda k: _DATA[k]["saved_at"])
            _DATA.pop(oldest, None)
        return record


def get(machine_id):
    with _LOCK:
        return _DATA.get(machine_id)


def all_ids():
    with _LOCK:
        return list(_DATA.keys())


def clear():
    with _LOCK:
        _DATA.clear()
        _OWNER.clear()


# ---- owner profile (saved separately so it can be edited without redoing the check-up) ----
_OWNER = {}


def save_owner(machine_id, profile):
    with _LOCK:
        _OWNER[machine_id] = {"profile": profile, "saved_at": time.time()}
        if len(_OWNER) > MAX_ITEMS:
            oldest = min(_OWNER, key=lambda k: _OWNER[k]["saved_at"])
            _OWNER.pop(oldest, None)
        return _OWNER[machine_id]


def get_owner(machine_id):
    with _LOCK:
        return _OWNER.get(machine_id)
