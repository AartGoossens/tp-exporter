# TrainingPeaks Exporter

Please note that using this tool for anything else than personal use will violate the TrainingPeaks terms and conditions.
Use at your own risk, the author cannot be held liable.


## Usage
The easiest way to use this script is to use docker (installation instructions here):
```bash
docker run -it -v $(pwd)/downloaddir/:/data/ aartgoossens/tp-exporter:latest
```

...and follow the prompts.

You will be prompted for:
- Your username and password. These will only be stored in memory while the script is running.
- Whether you are a coach or not.
- If you are a coach: The TrainingPeaks ID you want to run the script for. If you go to one of you coachees calendar the url will look something like: `https://app.trainingpeaks.com/#calendar/athletes/1234567`. The last bit (`1234567`) is the TrainingPeaks ID of this athlete.
- The number of days back the data should be downloaded.

The `$(pwd)/downloaddir/:/data/` argument in the docker command specifies which local directory should be mounted in the docker container and where the downloaded data should be stored.
In this case the data will be downloaded in the `downloaddir/` directory relative to the directory from which you are running the script.

## Alternative usage
If you cannot or do not want to use docker, you can in theory use the scripts without it by installing the requirments in the Pipfile and by installing Google Chrome (or Chromium) and the Chromedriver on your system.
For this to work you probably also need to change the paths to Chrome/Chromium and Chromedriver in the `website.py` file.
