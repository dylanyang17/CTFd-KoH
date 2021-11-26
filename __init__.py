from __future__ import division  # Use floating point for math calculations

from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES
from CTFd.plugins.migrations import upgrade
from CTFd.utils.logging import log

from .challenge_type import KoHChallengeType


def load(app):
    app.db.create_all()
    upgrade()
    CHALLENGE_CLASSES["koh"] = KoHChallengeType
    register_plugin_assets_directory(
        app, base_path="/plugins/CTFd-KoH/assets/"
    )
