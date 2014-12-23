# import os
# import shutil
# import tempfile

from funsize.cache import LocalCache, CacheBase


def test_cache_base_cache_path():
    cb = CacheBase()
    assert cb.get_cache_path("a", "b") == "files/a/b"


def test_local_cache_abspath():
    lc = LocalCache("/tmp")
    assert lc.abspath("a", "b") == "/tmp/files/a/b"
    # tmpdir = tempfile.mkdtemp()
