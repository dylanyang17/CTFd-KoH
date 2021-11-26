from CTFd.models import Challenges, Solves, db


class KoHChallengeModel(Challenges):
    __mapper_args__ = {"polymorphic_identity": "koh"}
    id = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"), primary_key=True
    )
    checker_url = db.Column(db.Text)
    allowed_suffixes = db.Column(db.Text)
    filesize_limit = db.Column(db.Integer)

    def __init__(self, *args, **kwargs):
        super(KoHChallengeModel, self).__init__(**kwargs)
        # self.value = kwargs["initial"]


class KoHSolves(Solves):
    score = db.Column(db.Integer)
