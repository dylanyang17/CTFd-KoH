from CTFd.models import Challenges, Solves, db


class KoHChallengeModel(Challenges):
    __mapper_args__ = {"polymorphic_identity": "koh"}
    id = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"), primary_key=True
    )
    initial = db.Column(db.Integer, default=0)
    minimum = db.Column(db.Integer, default=0)
    decay = db.Column(db.Integer, default=0)

    def __init__(self, *args, **kwargs):
        super(KoHChallengeModel, self).__init__(**kwargs)
        self.value = kwargs["initial"]
