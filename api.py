from collections import defaultdict

from flask_restx import Namespace, Resource
from sqlalchemy import select

from CTFd.cache import cache, make_cache_key
from CTFd.models import Users, db
from CTFd.utils import get_config
from CTFd.utils.dates import isoformat, unix_time_to_utc
from CTFd.utils.decorators.visibility import (
    check_account_visibility,
    check_score_visibility,
)
from CTFd.utils.modes import TEAMS_MODE, generate_account_url, get_mode_as_word

from .standings import get_koh_standings, get_koh_user_standings
from .models import KoHSolves

koh_scoreboard_namespace = Namespace(
    "koh_scoreboard", description="Endpoint to retrieve scores"
)


@koh_scoreboard_namespace.route("/<challenge_id>/standings")
@koh_scoreboard_namespace.param("challenge_id", "The KoH challenge's id")
class KoHScoreboardList(Resource):
    @check_account_visibility
    @check_score_visibility
    @cache.cached(timeout=60)
    def get(self, challenge_id):
        standings = get_koh_standings(challenge_id=challenge_id)
        response = []
        mode = get_config("user_mode")
        account_type = get_mode_as_word()

        if mode == TEAMS_MODE:
            r = db.session.execute(
                select(
                    [
                        Users.id,
                        Users.name,
                        Users.oauth_id,
                        Users.team_id,
                        Users.hidden,
                        Users.banned,
                    ]
                ).where(Users.team_id.isnot(None))
            )
            users = r.fetchall()
            membership = defaultdict(dict)
            for u in users:
                if u.hidden is False and u.banned is False:
                    membership[u.team_id][u.id] = {
                        "id": u.id,
                        "oauth_id": u.oauth_id,
                        "name": u.name,
                        "score": 0,
                    }

            # Get user_standings as a dict so that we can more quickly get member scores
            user_standings = get_koh_user_standings(challenge_id)
            for u in user_standings:
                membership[u.team_id][u.user_id]["score"] = int(u.score)

        for i, x in enumerate(standings):
            entry = {
                "pos": i + 1,
                "account_id": x.account_id,
                "account_url": generate_account_url(account_id=x.account_id),
                "account_type": account_type,
                "oauth_id": x.oauth_id,
                "name": x.name,
                "score": int(x.score),
            }

            if mode == TEAMS_MODE:
                entry["members"] = list(membership[x.account_id].values())

            response.append(entry)
        return {"success": True, "data": response}


@koh_scoreboard_namespace.route("/<challenge_id>/top/<count>")
@koh_scoreboard_namespace.param("challenge_id", "The KoH challenge's id")
@koh_scoreboard_namespace.param("count", "How many top teams to return")
class KoHScoreboardDetailTop(Resource):
    @check_account_visibility
    @check_score_visibility
    @cache.cached(timeout=60)
    def get(self, challenge_id, count):
        response = {}

        standings = get_koh_standings(challenge_id=challenge_id, count=count)

        team_ids = [team.account_id for team in standings]

        koh_solves = KoHSolves.query.filter(KoHSolves.account_id.in_(team_ids))

        freeze = get_config("freeze")

        if freeze:
            koh_solves = koh_solves.filter(KoHSolves.date < unix_time_to_utc(freeze))

        koh_solves = koh_solves.all()

        # Build a mapping of accounts to their solves and awards
        solves_mapper = defaultdict(list)
        for solve in koh_solves:
            solves_mapper[solve.account_id].append(
                {
                    "challenge_id": solve.challenge_id,
                    "account_id": solve.account_id,
                    "team_id": solve.team_id,
                    "user_id": solve.user_id,
                    "value": solve.score,
                    "date": isoformat(solve.date),
                }
            )

        # Sort all solves by date
        for team_id in solves_mapper:
            solves_mapper[team_id] = sorted(
                solves_mapper[team_id], key=lambda k: k["date"]
            )

        for i, _team in enumerate(team_ids):
            response[i + 1] = {
                "id": standings[i].account_id,
                "name": standings[i].name,
                "solves": solves_mapper.get(standings[i].account_id, []),
            }
        return {"success": True, "data": response}


@koh_scoreboard_namespace.route("/<challenge_id>/account/<account_id>")
@koh_scoreboard_namespace.param("challenge_id", "The KoH challenge's id")
@koh_scoreboard_namespace.param("account_id", "The target account's id")
class KoHScoreboardDetailAccount(Resource):
    @check_account_visibility
    @check_score_visibility
    @cache.cached(timeout=60)
    def get(self, challenge_id, account_id):
        koh_solves = KoHSolves.query.filter(KoHSolves.account_id == account_id and KoHSolves.challenge_id == challenge_id)
        freeze = get_config("freeze")
        if freeze:
            koh_solves = koh_solves.filter(KoHSolves.date < unix_time_to_utc(freeze))
        koh_solves = koh_solves.all()
        response = {'solves': []}
        for solve in koh_solves:
            response['solves'].append(
                {
                    "challenge_id": solve.challenge_id,
                    "account_id": solve.account_id,
                    "team_id": solve.team_id,
                    "user_id": solve.user_id,
                    "value": solve.score,
                    "date": isoformat(solve.date),
                }
            )
        return {"success": True, "data": response}
