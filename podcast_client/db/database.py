import os

from json_database import JsonStorage

from mycroft.util import LOG


class Database:
    """Abstracted interface for communicating with the chosen database."""

    def __init__(self, config={}):
        db_path = os.path.join(config["storage_dir"], config["db_filename"])
        self.data = JsonStorage(db_path)

    @property
    def entries(self):
        return self.data.values()

    def add_entry(self, key, value):
        """Add an entry to the database."""
        if key in self.data:
            LOG.error(f"Entry already exists in database: {key}")
            return False
        # Add a reference to the entries own key to make it easy to find
        value['self'] = key
        self.data[key] = value
        self.data.store()
        return True

    def remove_entry(self, key):
        """Remove an entry from the database."""
        if key in self.data:
            del self.data[key]
            self.data.store()
            return True
        else:
            LOG.error(f"Entry not found in database: {key}")
            return False

    def replace_entry(self, key, value):
        """Replace all data for an entry"""
        if key not in self.data:
            LOG.error(f"Entry not found in database: {key}")
            return False
        # Add a reference to the entries own key to make it easy to find
        value['self'] = key
        self.data[key] = value
        self.data.store()
        return True
