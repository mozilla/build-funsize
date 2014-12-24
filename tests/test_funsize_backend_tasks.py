import os


def test_configs():
    """ Ensure we can load the configs to avoid runtime errors """
    for cfg in ("dev", "staging", "production", "test"):
        os.environ["FUNSIZE_CELERY_CONFIG"] = "funsize.backend.config.%s" % cfg
        import funsize.backend.tasks
        reload(funsize.backend.tasks)
        assert funsize.backend.tasks.app.conf.FUNSIZE_CONF_NAME == cfg
