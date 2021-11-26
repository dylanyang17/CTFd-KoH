from __future__ import division  # Use floating point for math calculations

from flask import render_template, Blueprint

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

    koh_blueprint = Blueprint(
        "koh",
        __name__,
        template_folder="templates",
        static_folder="assets",
    )

    @koh_blueprint.route("/koh-scoreboard")
    def koh_scoreboard():
        return render_template('koh-scoreboard.html')

    app.register_blueprint(koh_blueprint)
