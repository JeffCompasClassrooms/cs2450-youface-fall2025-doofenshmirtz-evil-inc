import tinydb

def load_db():
    return tinydb.TinyDB('db.json', sort_keys=True, indent=4, separators=(',', ': '))

def save_db(*args, **kwargs):
    """Gracefully handle extra args when saving the DB."""
    if args:
        db = args[0]
        try:
            db.close()
        except Exception:
            pass