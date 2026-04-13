# accounts/points.py

POINT_RULES = {
    "login": 1,
    "quest_complete": 3,
}

def add_point(user, action: str, save=True) -> int:
    p = POINT_RULES.get(action, 0)
    if p <= 0:
        return 0

    user.point = (user.point or 0) + p
    if save:
        user.save(update_fields=["point"])
        user.recalc_grade(save=True)
    return p
