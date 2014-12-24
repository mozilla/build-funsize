import mock
from StringIO import StringIO
import os

# Fake celery before importing app
os.environ["FUNSIZE_CELERY_CONFIG"] = "funsize.backend.config.test"
from funsize.frontend.api import app


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


@mock.patch("funsize.frontend.api.cache")
def test_caching(m_cache):
    c = app.test_client()
    data = {"sha_from": "xx", "sha_to": "yy",
            "patch_file": (StringIO('Foo bar baz'), "patch")}
    rv = c.post("/cache", environ_overrides={"REMOTE_ADDR": "127.0.0.1"},
                data=data)
    assert rv.status_code == 200
    assert m_cache.save.call_count == 1


def test_trigger_partial_missing_params():
    c = app.test_client()
    rv = c.post("/partial")
    assert rv.status_code == 400


@mock.patch("funsize.frontend.api.cache")
def test_trigger_partial_existing(m_cache):
    m_cache.exists.return_value = True
    c = app.test_client()
    data = {'mar_from': 'mf', 'sha_from': 'hf', 'mar_to': 'mt', 'sha_to': 'st',
            'channel_id': 'ci', 'product_version': 'pv'}
    rv = c.post("/partial", data=data)
    assert rv.status_code == 201
    assert m_cache.exists.call_count == 1


@mock.patch("funsize.backend.tasks.build_partial_mar")
@mock.patch("funsize.frontend.api.cache")
def test_trigger_partial_new(m_cache, m_task):
    m_cache.exists.return_value = False
    c = app.test_client()
    data = {'mar_from': 'mf', 'sha_from': 'hf', 'mar_to': 'mt', 'sha_to': 'st',
            'channel_id': 'ci', 'product_version': 'pv'}
    rv = c.post("/partial", data=data)
    print dir(m_cache)
    assert m_cache.exists.call_count == 1
    assert m_cache.save_blank_file.call_count == 1
    assert m_task.delay.call_count == 1
    assert rv.status_code == 202


@mock.patch("funsize.frontend.api.cache")
def test_trigger_partial_cache_error(m_cache):
    m_cache.exists.return_value = False
    m_cache.save_blank_file.side_effect = Exception("oops")
    c = app.test_client()
    data = {'mar_from': 'mf', 'sha_from': 'hf', 'mar_to': 'mt', 'sha_to': 'st',
            'channel_id': 'ci', 'product_version': 'pv'}
    rv = c.post("/partial", data=data)
    assert m_cache.save_blank_file.call_count == 1
    assert rv.status_code == 500


def test_get_patch_no_direct_access():
    c = app.test_client()
    rv = c.get("/cache")
    assert rv.status_code == 405


@mock.patch("funsize.frontend.api.cache")
def test_get_patch_cache_miss(m_cache):
    m_cache.exists.return_value = False
    c = app.test_client()
    rv = c.get("/cache/a/b")
    assert rv.status_code == 400
    assert m_cache.exists.call_count == 1


@mock.patch("funsize.frontend.api.cache")
def test_get_patch_cache_hit(m_cache):
    m_cache.exists.return_value = True
    c = app.test_client()
    rv = c.get("/cache/a/b")
    assert rv.status_code == 200
    assert m_cache.exists.call_count == 1
    assert m_cache.retrieve.call_count == 1


@mock.patch("funsize.frontend.api.cache")
def test_get_partial_404(m_cache):
    m_cache.exists.return_value = False
    c = app.test_client()
    rv = c.get("/partial/123")
    assert rv.status_code == 404
    assert m_cache.exists.call_count == 1


@mock.patch("funsize.frontend.api.cache")
def test_get_partial_in_progress(m_cache):
    m_cache.exists.return_value = True
    m_cache.is_blank_file.return_value = True
    c = app.test_client()
    rv = c.get("/partial/123")
    assert rv.status_code == 202
    assert m_cache.exists.call_count == 1


@mock.patch("funsize.frontend.api.cache")
def test_get_partial_completed_head(m_cache):
    m_cache.exists.return_value = True
    m_cache.is_blank_file.return_value = False
    c = app.test_client()
    rv = c.head("/partial/123")
    assert rv.status_code == 200
    assert rv.content_type == "application/json"
    assert m_cache.exists.call_count == 1


@mock.patch("funsize.frontend.api.cache")
def test_get_partial_completed_get(m_cache):
    m_cache.exists.return_value = True
    m_cache.is_blank_file.return_value = False
    c = app.test_client()
    rv = c.get("/partial/123")
    assert rv.status_code == 200
    assert rv.content_type == "application/octet-stream"
    assert m_cache.exists.call_count == 1
