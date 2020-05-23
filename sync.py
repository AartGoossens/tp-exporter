from datetime import date, timedelta
from getpass import getpass
from pathlib import Path

import storage
from website import TrainingPeaks


def sync():
    print('TrainingPeaks credentials:')
    username = input('Username: ')
    password = getpass(prompt='Password: ')

    coach = input("Are you a coach? (yes/NO): ")
    if coach == "yes":
        coach = True
    else:
        coach = False

    if coach:
        trainingpeaks_id = input("TrainingPeaks ID for which you want to fetch data: ")

    offset = int(input("How many days back should I fetch data?: "))

    if not coach:
        with TrainingPeaks(username, password) as tp:
            trainingpeaks_id = tp.get_athlete_id()

    athlete_dir = Path("/data/", trainingpeaks_id)
    try:
        athlete_dir.mkdir()
    except FileExistsError:
        raise FileExistsError(f"Directory {athlete_dir} already exists. Aborting to prevent loss of data...")


    with TrainingPeaks(username, password, download_dir=athlete_dir) as tp:
        print(f"Downloading athlete {trainingpeaks_id}...")

        workout_files_zip = tp.download_workout_files(
                athlete_id=trainingpeaks_id,
                start_date=date.today() - timedelta(days=offset),
                end_date=date.today())
        if workout_files_zip is not None:
            workout_file_dir = Path(athlete_dir, "workouts")
            workout_file_dir.mkdir(parents=True, exist_ok=True)
            storage.merge_workout_files(workout_files_zip, workout_file_dir)

        workout_summaries_zip = tp.download_workout_summaries(
            athlete_id=trainingpeaks_id,
            start_date=date.today() - timedelta(days=365),
            end_date=date.today())
        if workout_summaries_zip is not None:
            storage.merge_workout_summaries(workout_summaries_zip, athlete_dir)

        custom_metrics_zip = tp.download_custom_metrics(
            athlete_id=trainingpeaks_id,
            start_date=date.today() - timedelta(days=365),
            end_date=date.today())
        if custom_metrics_zip is not None:
            storage.merge_custom_metrics(custom_metrics_zip, athlete_dir)


if __name__ == "__main__":
    print("""This tool let's you export all your data from TrainingPeaks.""")
    sync()
