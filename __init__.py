from __future__ import division  # Use floating point for math calculations

from flask import render_template, Blueprint, redirect, request, url_for

from CTFd.constants.config import ChallengeVisibilityTypes, Configs
from CTFd.models import db
from CTFd.plugins import register_plugin_assets_directory, register_user_page_menu_bar, register_admin_plugin_menu_bar
from CTFd.plugins.challenges import CHALLENGE_CLASSES
from CTFd.plugins.migrations import upgrade
from CTFd.api import CTFd_API_v1
from CTFd.utils import config
from CTFd.utils.config import is_teams_mode
from CTFd.utils.config.visibility import scores_visible
from CTFd.utils.decorators import (
    during_ctf_time_only,
    require_complete_profile,
    require_verified_emails, admins_only,
)
from CTFd.utils.dates import ctf_ended, ctf_paused, ctf_started
from CTFd.utils.decorators.visibility import (
    check_challenge_visibility,
    check_score_visibility,
)
from CTFd.utils.helpers import get_infos, get_errors
from CTFd.utils.user import authed, get_current_team, is_admin

from .challenge_type import KoHChallengeType
from .standings import get_koh_standings
from .api import koh_scoreboard_namespace


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

    @koh_blueprint.route("/koh-scoreboard/<int:challenge_id>", methods=["GET"])
    @during_ctf_time_only
    @check_score_visibility
    def koh_scoreboard(challenge_id):
        infos = get_infos()

        if config.is_scoreboard_frozen():
            infos.append("Scoreboard has been frozen")

        if is_admin() is True and scores_visible() is False:
            infos.append("Scores are not currently visible to users")
        
        standings = get_koh_standings(challenge_id)
        return render_template('user/koh-scoreboard.html', standings=standings, infos=infos, errors=get_errors())

    @koh_blueprint.route("/koh-scoreboard", methods=["GET"])
    @during_ctf_time_only
    @check_challenge_visibility
    def koh_scoreboard_index():
        if (
            Configs.challenge_visibility == ChallengeVisibilityTypes.PUBLIC
            and authed() is False
        ):
            pass
        else:
            if is_teams_mode() and get_current_team() is None:
                return redirect(url_for("teams.private", next=request.full_path))

        infos = get_infos()
        errors = get_errors()

        if ctf_started() is False:
            errors.append(f"{Configs.ctf_name} has not started yet")

        if ctf_paused() is True:
            infos.append(f"{Configs.ctf_name} is paused")

        if ctf_ended() is True:
            infos.append(f"{Configs.ctf_name} has ended")

        return render_template('user/koh-scoreboard-index.html', infos=infos, errors=errors)

    @koh_blueprint.route("/admin/koh-scoreboard/<int:challenge_id>", methods=["GET"])
    @admins_only
    def admin_koh_scoreboard(challenge_id):
        standings = get_koh_standings(challenge_id, admin=True)
        return render_template('user/koh-scoreboard.html', standings=standings, infos=get_infos(), errors=get_errors())

    @koh_blueprint.route("/admin/koh-scoreboard", methods=["GET"])
    @admins_only
    def admin_koh_scoreboard_index():
        db.session.query()
        return render_template('admin/koh-scoreboard-index.html', infos=get_infos(), errors=get_errors())

    app.register_blueprint(koh_blueprint)
    register_user_page_menu_bar('KoH', '/koh-scoreboard')
    register_admin_plugin_menu_bar('KoH', '/admin/koh-scoreboard')
    CTFd_API_v1.add_namespace(koh_scoreboard_namespace, path="/plugins/CTFd-KoH/scoreboard")
