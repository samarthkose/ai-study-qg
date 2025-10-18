import datetime

def update_sm2(progress: 'Progress', quality: int):
    if quality < 3:
        progress.repetition = 0
        progress.interval = 1
    else:
        progress.repetition += 1
        if progress.repetition == 1:
            progress.interval = 1
        elif progress.repetition == 2:
            progress.interval = 6
        else:
            progress.interval = int(progress.interval * progress.ease)
        progress.ease = max(1.3, progress.ease + 0.1 - (5-quality)*(0.08 + (5-quality)*0.02))
    progress.due = datetime.datetime.utcnow() + datetime.timedelta(days=progress.interval)
    return progress
