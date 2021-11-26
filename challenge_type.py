import math

from flask import Blueprint

from CTFd.models import Challenges, Solves, db
from CTFd.plugins.challenges import CHALLENGE_CLASSES, BaseChallenge
from CTFd.utils.modes import get_model

from .models import KoHChallengeModel


class KoHChallengeType(BaseChallenge):
    id = "koh"  # Unique identifier used to register challenges
    name = "koh"  # Name of a challenge type
    templates = {  # Handlebars templates used for each aspect of challenge editing & viewing
        "create": "/plugins/CTFd-KoH/assets/create.html",
        "update": "/plugins/CTFd-KoH/assets/update.html",
        "view": "/plugins/CTFd-KoH/assets/view.html",
    }
    scripts = {  # Scripts that are loaded when a template is loaded
        "create": "/plugins/CTFd-KoH/assets/create.js",
        "update": "/plugins/CTFd-KoH/assets/update.js",
        "view": "/plugins/CTFd-KoH/assets/view.js",
    }
    # Route at which files are accessible. This must be registered using register_plugin_assets_directory()
    route = "/plugins/CTFd-KoH/assets/"
    # Blueprint used to access the static_folder directory.
    blueprint = Blueprint(
        "CTFd-KoH",
        __name__,
        template_folder="templates",
        static_folder="assets",
    )
    challenge_model = KoHChallengeModel

    @classmethod
    def get_score_from_checker(cls, challenge, request):
        return challenge

    @classmethod
    def read(cls, challenge):
        """
        This method is in used to access the data of a challenge in a format processable by the front end.

        :param challenge:
        :return: Challenge object, data dictionary to be returned to the user
        """
        challenge = KoHChallengeModel.query.filter_by(id=challenge.id).first()
        data = {
            "id": challenge.id,
            "name": challenge.name,
            "value": challenge.value,
            "checker_url": challenge.checker_url,
            "allowed_suffixes": challenge.allowed_suffixes,
            "description": challenge.description,
            "connection_info": challenge.connection_info,
            "category": challenge.category,
            "state": challenge.state,
            "max_attempts": challenge.max_attempts,
            "type": challenge.type,
            "type_data": {
                "id": cls.id,
                "name": cls.name,
                "templates": cls.templates,
                "scripts": cls.scripts,
            },
        }
        return data

    @classmethod
    def update(cls, challenge, request):
        """
        This method is used to update the information associated with a challenge. This should be kept strictly to the
        Challenges table and any child tables.

        :param challenge:
        :param request:
        :return:
        """
        data = request.form or request.get_json()
        for attr, value in data.items():
            setattr(challenge, attr, value)
        db.session.commit()
        return challenge
        # return KoHChallengeType.calculate_value(challenge)

    @classmethod
    def attempt(cls, challenge, request):
        return True, 'Running checker...'

    @classmethod
    def solve(cls, user, team, challenge, request):
        pass
        # super().solve(user, team, challenge, request)

        # KoHChallengeType.calculate_value(challenge)