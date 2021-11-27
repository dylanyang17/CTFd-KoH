from __future__ import division  # Use floating point for math calculations

from flask import render_template, Blueprint

from CTFd.plugins import register_plugin_assets_directory, register_user_page_menu_bar
from CTFd.plugins.challenges import CHALLENGE_CLASSES
from CTFd.plugins.migrations import upgrade
from CTFd.api import CTFd_API_v1
from CTFd.utils.logging import log

from .challenge_type import KoHChallengeType
from .api import koh_scoreboard_namespace


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
    register_user_page_menu_bar('KoH', '/koh-scoreboard')
    CTFd_API_v1.add_namespace(koh_scoreboard_namespace, path="/plugins/koh/scoreboard")
