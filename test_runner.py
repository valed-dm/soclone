"""Non-interactive test runner for soclone"""
import contextlib

from django.test.runner import DiscoverRunner


class NonInteractiveTestRunner(DiscoverRunner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interactive = False

    def teardown_databases(self, old_config, **kwargs):
        try:
            super().teardown_databases(old_config, **kwargs)
        except RuntimeError:
            contextlib.suppress(RuntimeError)
