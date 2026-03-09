def calculate_xp(
    ds_hours: float,
    diploma_hours: float,
    workout_done: bool,
    university_done: bool,
) -> int:
    xp = 0
    xp += int(ds_hours * 10)
    xp += int(diploma_hours * 10)
    if workout_done:
        xp += 20
    if university_done:
        xp += 10
    if ds_hours > 0 and diploma_hours > 0 and workout_done:
        xp += 10
    return xp


def calculate_level(total_xp: int) -> int:
    level = 1
    while total_xp >= 50 * level * level:
        level += 1
    return level