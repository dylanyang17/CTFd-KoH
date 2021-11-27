import datetime

from sqlalchemy.ext.hybrid import hybrid_property

from CTFd.models import Challenges, Solves, db, Submissions


class KoHChallengeModel(Challenges):
    __tablename__ = "koh_challenge_model"
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


class KoHSolves(db.Model):
    __tablename__ = "koh_solves"
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE")
    )
    score = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id", ondelete="CASCADE"))
    ip = db.Column(db.String(46))
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, *args, **kwargs):
        super(KoHSolves, self).__init__(**kwargs)

    def __repr__(self):
        return f"<Submission id={self.id}, challenge_id={self.challenge_id}, ip={self.ip}, provided={self.provided}>"

    @hybrid_property
    def account_id(self):
        from CTFd.utils import get_config

        user_mode = get_config("user_mode")
        if user_mode == "teams":
            return self.team_id
        elif user_mode == "users":
            return self.user_id

    @staticmethod
    def get_child(type):
        child_classes = {
            x.polymorphic_identity: x.class_
            for x in Submissions.__mapper__.self_and_descendants
        }
        return child_classes[type]
