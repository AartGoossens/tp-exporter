import gzip
import zipfile
from io import BytesIO
from pathlib import Path


def merge_workout_files(exported_zip, destination):
    with zipfile.ZipFile(exported_zip, 'r') as zip_ref:
        for file_in_zip in zip_ref.namelist():
            gzip_bytes_io = BytesIO(zip_ref.read(name=file_in_zip))
            with gzip.open(gzip_bytes_io, 'rb') as f:
                with Path(destination, Path(file_in_zip).stem).open('wb') as fit_file:
                    fit_file.write(f.read())

def merge_workout_summaries(exported_zip, destination):
    with zipfile.ZipFile(exported_zip) as zip_ref:
        zip_ref.extract('workouts.csv', Path(destination))


def merge_custom_metrics(exported_zip, destination):
    with zipfile.ZipFile(exported_zip) as zip_ref:
        zip_ref.extract('metrics.csv', Path(destination))
