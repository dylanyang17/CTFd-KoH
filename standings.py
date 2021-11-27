from sqlalchemy.sql.expression import union_all

from CTFd.cache import cache
from CTFd.models import Challenges, Teams, Users, db
from CTFd.utils import get_config
from CTFd.utils.dates import unix_time_to_utc
from CTFd.utils.modes import get_model


from .models import KoHSolves


@cache.memoize(timeout=60)
def get_koh_standings(challenge_id, count=None, admin=False, fields=None):
    """
    Get standings as a list of tuples containing account_id, name, and score e.g. [(account_id, team_name, score)].

    Ties are broken by who reached a given score first based on the solve ID. Two users can have the same score but one
    user will have a solve ID that is before the others. That user will be considered the tie-winner.

    Challenges & Awards with a value of zero are filtered out of the calculations to avoid incorrect tie breaks.
    """
    if fields is None:
        fields = []

    Model = get_model()

    scores = (
        db.session.query(
            KoHSolves.account_id.label("account_id"),
            db.func.max(KoHSolves.score).label("score"),
            db.func.max(KoHSolves.id).label("id"),
            db.func.max(KoHSolves.date).label("date"),
        )
        .join(Challenges)
        .filter(KoHSolves.challenge_id == challenge_id)
        .group_by(KoHSolves.account_id)
    )

    """
    Filter out solves and awards that are before a specific time point.
    """
    freeze = get_config("freeze")
    if not admin and freeze:
        scores = scores.filter(KoHSolves.date < unix_time_to_utc(freeze))

    """
    Admins can see scores for all users but the public cannot see banned users.

    Filters out banned users.
    Properly resolves value ties by ID.

    Different databases treat time precision differently so resolve by the row ID instead.
    """
    scores = scores.subquery()
    if admin:
        standings_query = (
            db.session.query(
                Model.id.label("account_id"),
                Model.oauth_id.label("oauth_id"),
                Model.name.label("name"),
                Model.hidden,
                Model.banned,
                scores.columns.score,
                *fields,
            )
            .join(scores, Model.id == scores.columns.account_id)
            .order_by(scores.columns.score.desc(), scores.columns.id)
        )
    else:
        standings_query = (
            db.session.query(
                Model.id.label("account_id"),
                Model.oauth_id.label("oauth_id"),
                Model.name.label("name"),
                scores.columns.score,
                *fields,
            )
            .join(scores, Model.id == scores.columns.account_id)
            .filter(Model.banned == False, Model.hidden == False)
            .order_by(scores.columns.score.desc(), scores.columns.id)
        )

    """
    Only select a certain amount of users if asked.
    """
    if count is None:
        standings = standings_query.all()
    else:
        standings = standings_query.limit(count).all()

    return standings


@cache.memoize(timeout=60)
def get_koh_team_standings(challenge_id, count=None, admin=False, fields=None):
    if fields is None:
        fields = []
    scores = (
        db.session.query(
            KoHSolves.account_id.label("account_id"),
            db.func.max(KoHSolves.score).label("score"),
            db.func.max(KoHSolves.id).label("id"),
            db.func.max(KoHSolves.date).label("date"),
        )
        .join(Challenges)
        .filter(KoHSolves.challenge_id == challenge_id)
        .group_by(KoHSolves.team_id)
    )

    freeze = get_config("freeze")
    if not admin and freeze:
        scores = scores.filter(KoHSolves.date < unix_time_to_utc(freeze))

    scores = scores.subquery()
    if admin:
        standings_query = (
            db.session.query(
                Teams.id.label("team_id"),
                Teams.oauth_id.label("oauth_id"),
                Teams.name.label("name"),
                Teams.hidden,
                Teams.banned,
                scores.columns.score,
                *fields,
            )
            .join(scores, Teams.id == scores.columns.team_id)
            .order_by(scores.columns.score.desc(), scores.columns.id)
        )
    else:
        standings_query = (
            db.session.query(
                Teams.id.label("team_id"),
                Teams.oauth_id.label("oauth_id"),
                Teams.name.label("name"),
                scores.columns.score,
                *fields,
            )
            .join(scores, Teams.id == scores.columns.team_id)
            .filter(Teams.banned == False)
            .filter(Teams.hidden == False)
            .order_by(scores.columns.score.desc(), scores.columns.id)
        )

    if count is None:
        standings = standings_query.all()
    else:
        standings = standings_query.limit(count).all()

    return standings


@cache.memoize(timeout=60)
def get_koh_user_standings(challenge_id, count=None, admin=False, fields=None):
    if fields is None:
        fields = []
    scores = (
        db.session.query(
            KoHSolves.account_id.label("account_id"),
            db.func.max(KoHSolves.score).label("score"),
            db.func.max(KoHSolves.id).label("id"),
            db.func.max(KoHSolves.date).label("date"),
        )
        .join(Challenges)
        .filter(KoHSolves.challenge_id == challenge_id)
        .group_by(KoHSolves.user_id)
    )

    freeze = get_config("freeze")
    if not admin and freeze:
        scores = scores.filter(KoHSolves.date < unix_time_to_utc(freeze))

    scores = scores.subquery()
    if admin:
        standings_query = (
            db.session.query(
                Users.id.label("user_id"),
                Users.oauth_id.label("oauth_id"),
                Users.name.label("name"),
                Users.team_id.label("team_id"),
                Users.hidden,
                Users.banned,
                scores.columns.score,
                *fields,
            )
            .join(scores, Users.id == scores.columns.user_id)
            .order_by(scores.columns.score.desc(), scores.columns.id)
        )
    else:
        standings_query = (
            db.session.query(
                Users.id.label("user_id"),
                Users.oauth_id.label("oauth_id"),
                Users.name.label("name"),
                Users.team_id.label("team_id"),
                scores.columns.score,
                *fields,
            )
            .join(scores, Users.id == scores.columns.user_id)
            .filter(Users.banned == False, Users.hidden == False)
            .order_by(scores.columns.score.desc(), scores.columns.id)
        )

    if count is None:
        standings = standings_query.all()
    else:
        standings = standings_query.limit(count).all()

    return standings


def clear_koh_standings():
    # Clear out the bulk standings functions
    cache.delete_memoized(get_koh_standings)
    cache.delete_memoized(get_koh_team_standings)
    cache.delete_memoized(get_koh_user_standings)
