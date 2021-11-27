from __future__ import division  # Use floating point for math calculations

from flask import render_template, Blueprint

from CTFd.models import db
from CTFd.plugins import register_plugin_assets_directory, register_user_page_menu_bar
from CTFd.plugins.challenges import CHALLENGE_CLASSES
from CTFd.plugins.migrations import upgrade
from CTFd.api import CTFd_API_v1
from CTFd.utils.decorators.visibility import check_account_visibility, check_score_visibility
from CTFd.utils.helpers import get_infos
from CTFd.utils.logging import log

from .challenge_type import KoHChallengeType
from .standings import get_koh_standings
from .api import koh_scoreboard_namespace
from .models import Challenges


def load(app):
    app.db.create_all()
    upgrade()
    CHALLENGE_CLASSES["koh"] = KoHChallengeType
    register_plugin_assets_directory(
        app, base_path="/plugins/CTFd-KoH/assets/", endpoint='plugins.koh.assets'
    )

    koh_blueprint = Blueprint(
        "koh",
        __name__,
        template_folder="templates",
        static_folder="assets",
    )

    @koh_blueprint.route("/koh-scoreboard/<int:challenge_id>")
    def koh_scoreboard(challenge_id):
        standings = get_koh_standings(challenge_id)
        return render_template('koh-scoreboard.html', standings=standings, infos=get_infos())

    @koh_blueprint.route("/koh-scoreboard")
    @check_account_visibility
    @check_score_visibility
    def koh_scoreboard_index():
        koh_challenges = db.session.query(Challenges.id.label("challenge_id"), Challenges.name.label("challenge_name"), Challenges.description.label("description")) \
                        .filter(Challenges.type == 'koh', Challenges.state == 'visible').all()
        koh_challenges_list = []
        for challenge in koh_challenges:
            koh_challenges_list.append({
                'challenge_id': challenge.challenge_id,
                'challenge_name': challenge.challenge_name,
                'description': challenge.description,
            })
        return render_template('koh-scoreboard-index.html', koh_challenges_list=koh_challenges_list, infos=get_infos())

    app.register_blueprint(koh_blueprint)
    register_user_page_menu_bar('KoH', '/koh-scoreboard')
    CTFd_API_v1.add_namespace(koh_scoreboard_namespace, path="/plugins/CTFd-KoH/scoreboard")
