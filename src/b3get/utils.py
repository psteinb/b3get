import tempfile
import os

def tmp_location():
    """ return a folder under /tmp or similar,
    If something exists that matches the name '.*-b3get', use this.
    If nothing is found, a new folder under /tmp is created and returned
    """
    tmp = tempfile.gettempdir()
    folders = [ subdir[0] for subdir in os.walk(tmp) if subdir[0].endswith('-b3get') ]
    if len(folders) > 0:
        return folders[0]
    else:
        return tempfile.mkdtemp(suffix='-b3get')
