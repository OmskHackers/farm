import importlib
import os
import threading

from server import app, config as config_module


_config_mtime = None
_reload_lock = threading.RLock()
_cur_config = config_module.CONFIG


def get_config():
    global _config_mtime, _cur_config

    cur_mtime = os.stat(os.path.join(app.root_path, 'config.py')).st_mtime_ns
    if cur_mtime != _config_mtime:
        with _reload_lock:
            if cur_mtime != _config_mtime:
                try:
                    importlib.reload(config_module)
                    _cur_config = config_module.CONFIG
                    app.logger.info('New config loaded')
                except Exception as e:
                    app.logger.error('Failed to reload config: %s', e)

                _config_mtime = cur_mtime

    return _cur_config

