import mock
from StringIO import StringIO
import os

# Fake celery before importing app
os.environ["CELERY_BROKER"] = "fake"
from funsize.frontend.api import app
import funsize.cache


def test_index():
    c = app.test_client()
    rv = c.get("/")
    assert rv.status_code == 200


def test_caching_localhost_only():
    c = app.test_client()
    rv = c.post("/cache", environ_overrides={"REMOTE_ADDR": "192.168.1.1"})
    assert rv.status_code == 403


def test_caching_required_params():
    c = app.test_client()
    rv = c.post("/cache", environ_overrides={"REMOTE_ADDR": "127.0.0.1"})
    assert rv.status_code == 400


def test_caching_required_file():
    c = app.test_client()
    data = {"sha_from": "xx", "sha_to": "yy"}
    rv = c.post("/cache", environ_overrides={"REMOTE_ADDR": "127.0.0.1"},
                data=data)
    assert rv.status_code == 400


@mock.patch("funsize.cache.Cache")
def test_caching(m_cache):
    cacheo = mock.Mock()
    m_cache.return_value = cacheo
    c = app.test_client()
    data = {"sha_from": "xx", "sha_to": "yy",
            "patch_file": (StringIO('Foo bar baz'), "patch")}
    rv = c.post("/cache", environ_overrides={"REMOTE_ADDR": "127.0.0.1"},
                data=data)
    assert rv.status_code == 200
    cacheo.save.assert_called_once()


def test_trigger_partial_missing_params():
    c = app.test_client()
    rv = c.post("/partial")
    assert rv.status_code == 400


@mock.patch("funsize.cache.Cache")
def test_trigger_partial_existing(m_cache):
    cacheo = mock.Mock()
    cacheo.find.return_value = True
    m_cache.return_value = cacheo
    c = app.test_client()
    data = {'mar_from': 'mf', 'sha_from': 'hf', 'mar_to': 'mt', 'sha_to': 'st',
            'channel_id': 'ci', 'product_version': 'pv'}
    rv = c.post("/partial", data=data)
    assert rv.status_code == 201
    cacheo.find.assert_called_once()


@mock.patch("funsize.backend.tasks.build_partial_mar")
@mock.patch("funsize.cache.Cache")
def test_trigger_partial_new(m_cache, m_task):
    cacheo = mock.Mock()
    cacheo.find.return_value = False
    m_cache.return_value = cacheo
    c = app.test_client()
    data = {'mar_from': 'mf', 'sha_from': 'hf', 'mar_to': 'mt', 'sha_to': 'st',
            'channel_id': 'ci', 'product_version': 'pv'}
    rv = c.post("/partial", data=data)
    cacheo.save_blank_file.assert_called_once()
    m_task.delay.assert_called_once()
    assert rv.status_code == 202


@mock.patch("funsize.cache.Cache")
def test_trigger_partial_cache_error(m_cache):
    cacheo = mock.Mock()
    cacheo.find.return_value = False
    cacheo.save_blank_file.side_effect = funsize.cache.CacheError("oops")
    m_cache.return_value = cacheo
    c = app.test_client()
    data = {'mar_from': 'mf', 'sha_from': 'hf', 'mar_to': 'mt', 'sha_to': 'st',
            'channel_id': 'ci', 'product_version': 'pv'}
    rv = c.post("/partial", data=data)
    cacheo.save_blank_file.assert_called_once()
    assert rv.status_code == 500


def test_get_patch_missing_params():
    c = app.test_client()
    rv = c.get("/cache")
    assert rv.status_code == 400


@mock.patch("funsize.cache.Cache")
def test_get_patch_cache_miss(m_cache):
    cacheo = mock.Mock()
    cacheo.find.return_value = False
    m_cache.return_value = cacheo
    c = app.test_client()
    # data = {"sha_from": "sf", "sha_to": "st"}
    rv = c.get("/cache?sha_from=a&sha_to=b")
    assert rv.status_code == 400
    cacheo.find.assert_called_once()


@mock.patch("funsize.cache.Cache")
def test_get_patch_cache_hit(m_cache):
    cacheo = mock.Mock()
    cacheo.find.return_value = True
    m_cache.return_value = cacheo
    c = app.test_client()
    # data = {"sha_from": "sf", "sha_to": "st"}
    rv = c.get("/cache?sha_from=a&sha_to=b")
    assert rv.status_code == 200
    cacheo.find.assert_called_once()
    cacheo.retrieve.assert_called_once()


@mock.patch("funsize.cache.Cache")
def test_get_partial_404(m_cache):
    cacheo = mock.Mock()
    cacheo.find.return_value = False
    m_cache.return_value = cacheo
    c = app.test_client()
    rv = c.get("/partial/123")
    assert rv.status_code == 404
    cacheo.find.assert_called_once()


@mock.patch("funsize.cache.Cache")
def test_get_partial_in_progress(m_cache):
    cacheo = mock.Mock()
    cacheo.find.return_value = True
    cacheo.is_blank_file.return_value = True
    m_cache.return_value = cacheo
    c = app.test_client()
    rv = c.get("/partial/123")
    assert rv.status_code == 202
    cacheo.find.assert_called_once()


@mock.patch("funsize.cache.Cache")
def test_get_partial_completed_head(m_cache):
    cacheo = mock.Mock()
    cacheo.find.return_value = True
    cacheo.is_blank_file.return_value = False
    m_cache.return_value = cacheo
    c = app.test_client()
    rv = c.head("/partial/123")
    assert rv.status_code == 200
    assert rv.content_type == "application/json"
    cacheo.find.assert_called_once()


@mock.patch("funsize.cache.Cache")
def test_get_partial_completed_get(m_cache):
    cacheo = mock.Mock()
    cacheo.find.return_value = True
    cacheo.is_blank_file.return_value = False
    m_cache.return_value = cacheo
    c = app.test_client()
    rv = c.get("/partial/123")
    assert rv.status_code == 200
    assert rv.content_type == "application/octet-stream"
    cacheo.find.assert_called_once()
