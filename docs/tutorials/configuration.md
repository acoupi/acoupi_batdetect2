# Configuration

Once *acoupi_batdetect2* has been installed on a device, users can configure it.

To **accept** the default values, press the keyboard letter `y` or the key `Enter`. 
To **reject and modify** a setting, press the keyboard letter `n` and input a new value.

The video shows the configuration process for the _acoupi default_ program via the CLI.  

### Configuration Parameters

!!! Example "CLI Output: _acoupi config get_"

    ```json
    {
        "timezone": "Europe/London",
        "microphone": {
            "device_name": "UltraMic 250K 16 bit r4",
            "samplerate": 250000,
            "audio_channels": 1
        },
        "recording": {
            "duration": 3,
            "interval": 12,
            "chunksize": 8192,
            "schedule_start": "19:00:00",
            "schedule_end": "07:00:00"
        },
        "paths": {
            "tmp_audio": "/run/shm",
            "recordings": "/home/pi/storages/recordings",
            "db_metadata": "/home/pi/storages/metadata.db"
        },
        "messaging": {
            "messages_db": "/home/pi/storages/messages.db",
            "message_send_interval": 120,
            "heartbeat_interval": 3600,
            "http": null,
            "mqtt": {
                "host": "your-mqtt-broker.org",
                "username": "mqtt_username",
                "password": "mqtt_password",
                "topic": "mytopic/acoupi",
                "port": 1884,
                "timeout": 5
            }
        },
        "model": {
            "detection_threshold": 0.4
        },
        "recording_saving": {
            "true_dir": "bats",
            "false_dir": "no_bats",
            "timeformat": "%Y%m%d_%H%M%S",
            "saving_threshold": 0.2,
            "filters": {
                "starttime": "21:00:00",
                "endtime": "23:00:00",
                "before_dawndusk_duration": 0,
                "after_dawndusk_duration": 0,
                "frequency_duration": 0,
                "frequency_interval": 0
            }
        },
        "summariser_config": {
            "interval": 3600.0,
            "low_band_threshold": 0.0,
            "mid_band_threshold": 0.0,
            "high_band_threshold": 0.0
        }
    }
    ```

!!! Tip "How to modify a value after setup?"
    
    You can modify the value of a parameter after an _acoupi_ program has been set up. This can be necessary either due to
    a misconfiguration or to make changes to the current program. To modify a parameter, use the command:


    !!! Example "CLI Command: modify a configuration parameter after setup"

          ```bash
          acoupi config set --field <parameter_name> <new_value>
          ```

      Replace the _`parameter_name`_ with the full name of the parameter to modified. For example, to update the recording saving filters start time to 7pm, the CLI command would be as follow:

    !!! Example "CLI Command: modify recording_saving filter start time"

          ```bash
          acoupi config set --field recording_saving.filters.starttime 19:00:00
          ```

The table below provides detailed information about the parameters available when setting up *acoupi_batdetect2* program.

| Parameter | Type | Default Value | Definition | Comment |
|---|---|---|---|---|
| __Model (Optional)__| | | Configuration related to running a model. | Will require an acoupi program to integrate the detection task. |
| `model.detection_threshold` | float | 0.4 | The detection threshold is used to determine if a model detect a species call with confidence. | A float value between 0 and 1. Each model will have a different threshold that can be used to determine if a species call is detected with high or low confidence score. |
| __Saving (Optional)__| | | Configuration to store recordings when a model is used. | Additional parameters for saving recording after they have been processed by a model. |
| `recording_saving.true_dir` | str | "/home/pi/storages/recordings/bats" | Path to the directory storing recorded audio files that held __confident__ detections (i.e., detections that are greater or equal than the `detection_treshold` parameter) after processing. | |
| `recording_saving.fasle_dir` | str | "/home/pi/storages/recordings/no_bats" | Path to the directory storing recorded audio files that held __non-confident__ detections (i.e., detections that are smaller than the `detection_treshold` parameter) after processing. | |
| `recording_saving.timeformat` | str | "%Y%m%d_%H%M%S" | The saving.timeformat defines how to name the recording audio file. The default value capture the date and time of when the recording stated.  | A recording with name 20241004_183040.wav means that the recording file started on 4th October 2024 at 18:30:40. |
| `recording_saving.saving_threshold` | float | 0.2 | The saving threshold is used to determine which files to save. It allows to save files that have been classified as having _non-confident_ detections by a model. | A float value between 0 and 1. |
| __Summariser (Optional)__| | | Configuration to store recordings when a model is used. | Additional parameters for saving recording after they have been processed by a model. |
| `summariser.interval` | float | 3600 |  | |
| `summariser.low_band_threshold` | float | 0.0 | | |
| `summariser.mid_band_threshold` | float | 0.0 | | |
| `summariser.high_band_threshold` | float | 0.0 | | |