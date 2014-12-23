# import os
# import shutil
# import tempfile

from funsize.cache import LocalCache, CacheBase
from funsize.utils.checksum import get_hash


def test_cache_base_cache_path():
    cb = CacheBase()
    assert cb.get_cache_path("a", "b") == "files/a/b"


def test_local_cache_abspath():
    lc = LocalCache("/tmp")
    assert lc.abspath("a", "b") == "/tmp/files/a/{}".format(
        get_hash("sha1", "b"))
    # tmpdir = tempfile.mkdtemp()
