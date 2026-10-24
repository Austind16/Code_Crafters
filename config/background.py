import logging
import os
import sys
import threading
import time

import requests
from django.db import close_old_connections

logger = logging.getLogger(__name__)
_started = False


def _env_bool(name, default):
    return os.environ.get(name, default).strip().lower() in {'1', 'true', 'yes'}


def _keepalive_loop(url, interval):
    while True:
        time.sleep(interval)
        try:
            response = requests.get(url, timeout=15)
            logger.info('Keep-alive ping %s -> %s', url, response.status_code)
        except requests.RequestException as exc:
            logger.warning('Keep-alive ping failed: %s', exc)


def _grader_loop(poll_seconds):
    from submissions.management.commands.check_submissions import Command

    command = Command()
    options = {'max_submissions': 25, 'max_attempts': 3}
    while True:
        try:
            processed = command.process_batch(options)
        except Exception:
            logger.exception('Grader batch crashed; will retry.')
            processed = 0
        finally:
            close_old_connections()
        if processed == 0:
            time.sleep(poll_seconds)


def start_background_threads():
    global _started
    if _started or 'test' in sys.argv:
        return
    _started = True

    base_url = os.environ.get('KEEPALIVE_URL') or os.environ.get('RENDER_EXTERNAL_URL', '')
    if base_url:
        url = base_url.rstrip('/')
        if not url.endswith('/healthz'):
            url += '/healthz'
        interval = int(os.environ.get('KEEPALIVE_INTERVAL', '300'))  # 300 s = 5 min
        threading.Thread(
            target=_keepalive_loop, args=(url, interval), daemon=True, name='keepalive'
        ).start()

    if _env_bool('RUN_GRADER_THREAD', 'true'):
        poll = int(os.environ.get('GRADER_POLL_SECONDS', '10'))
        threading.Thread(
            target=_grader_loop, args=(poll,), daemon=True, name='grader'
        ).start()