from CTFd.models import db, Challenges


def get_koh_challenges(admin=False):
    koh_challenges = db.session.query(Challenges.id.label("challenge_id"), Challenges.name.label("challenge_name"),
                                      Challenges.description.label("description")).filter(Challenges.type == 'koh')
    if not admin:
        koh_challenges = koh_challenges.filter(Challenges.state == 'visible').all()
    return koh_challenges


def get_koh_challenges_attrs(admin=False):
    koh_challenges = get_koh_challenges(admin)
    koh_challenges_attrs = []
    for challenge in koh_challenges:
        koh_challenges_attrs.append({
            'challenge_id': challenge.challenge_id,
            'challenge_name': challenge.challenge_name,
            'description': challenge.description,
        })
    return koh_challenges_attrs
