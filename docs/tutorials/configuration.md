# Configuration

Once *acoupi_batdetect2* has been installed on a device, users can configure it. This setup determines how the device records audio, classifies it, and sends information over a network.

To **accept** the default settings, press the keyboard letter __`y`__ or the key __`Enter`__. 
To **reject and modify** a setting, press the keyboard letter __`n`__ and input a new value when prompted.

The video shows the configuration process for the _acoupi_batdetect2_ program via the CLI.

![type:video](../img/acoupi_batdetect2_configuration.mp4){: style='width: 100%'}

### Configuration Parameters

The following is an example of how an _acoupi_batdetect2_ program can be configured, shown in JSON format.

In this setup, the device records audio in 3 second clips every 12 seconds, from 7pm to 7am. However, the device only saves recordings between 9pm (__`saving_filters.starttime`__) and 11pm  (__`saving_filters.endttime`__). Several parameters control how and when recordings are saved. 

- __`saving_managers.true_dir`__ and __`saving_managers.false_dir`__ specify the folders where recordings are saved. These paramenters are complementary to the __`paths.recordings`__ parameter. Recordings with "true" detections (i.e., where the detection confidence score is greater or equal to the __`model.detection_threshold`__ parameter) are saved in the `true_dir` folder, while those with "false" detections (i.e., where the confidence score is lower than the __`model.detection_threshold`__ but higher than the __`saving_managers.bat_threshold`__) are saved in the `false_dir` folder. This aims at helping capturing possible false negatives.
- __`saving_managers.timeformat`__ determines the naming format for saved recordings. The timestamp in the filename reflects the starting time of a recording (i.e., the exact time the recording started).


Detections made by the BatDetect2 model are transmitted to a remote server using the MQTT communication protocol. The following parameters manage how and where this information is sent. 

- __`mqtt.host`__ and __`mqtt.topic`__ specify the destination (i.e., the server address and the topic) to which messages are sent. Messages contain information about the recording file, and the detection and classification found in the file. 
- __`messaging.messages_db`__ sets the location of the local database on the device. This database stores outgoing messages and tracks their status - whether they are waiting to be sent, have been sent successfully or failed. 
- __`messaging.message_send_interval`__ controls how often the system checks for new messages to be sent. This interval can be reduced for near real-time updates, or lengthen to minutes or even hours if network connectivity is limited. 

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
            "interval": 10,
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
        "saving_filters": {
          "starttime": "21:00:00",
          "endtime": "23:00:00",
          "before_dawndusk_duration": 0,
          "after_dawndusk_duration": 0,
          "frequency_duration": 0,
          "frequency_interval": 0
          "saving_threshold": '0.3,
        },
        "saving_managers": {
          "true_dir": "bats",
          "false_dir": "no_bats",
          "timeformat": "%Y%m%d_%H%M%S",
          "bat_threshold": 0.5,
        },
        "summariser_config": {
          "interval": 3600.0,
          "low_band_threshold": 0.0,
          "mid_band_threshold": 0.0,
          "high_band_threshold": 0.0
        }
    }
    ```

!!! Tip "How to define the `detection_threhold` value?"

    The `detection_threshold` selects detections based on their confidence scores. Detections below this value will be disregarded, while those above or equal to this threshold will be saved. 

    The confidence score obtained from running the BatDetect2 model on your audio recordings depends on the model's prediction accuracy and recall, as 
    well as factors like your audio recording device, 
    recorder location, and environmenal conditions. 

    We recommend familiarising yourself with the BatDetect2 model's precision and recall values for each of the UK bat species. Refer to the 
    publication by [Mac Aodha O., et al., (2002) _Towards a General Approach for Bat Echolocation Detection and Classification_](https://doi.org/10.1101/2022.12.14.520490) for more details. 

??? Tip "How to modify a value after setup?"
    
    You can modify a parameter's value after the _acoupi_batdetect2_ program has been set up. This can be necessary due to a misconfiguration or to make changes to the current program. To modify a parameter, use the command:


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
| __Microphone__| | | Microphone configuration.| |
| `microphone.device_name`| str | - | The name of the microphone to use for recording.| Ensure it matches the device in use.|
| `microphone.samplerate`| int (Hz) | - | Sampling rate of the microphone in Hz. | Set the sampling rate according to the microphone's specifications, however keep in mind that `batdetect2` natively processes recordings at 256 kHz and resamples all non-matching recordings. |
|`microphone.audio_channels`| int | - | Number of audio channels (i.e., 1 for mono).| Configure according to the microphone's capabilities, however keep in mind that `batdetect2` only uses the first audio channel.|
| __Recording__| | | Configuration regarding the recording process.| |
| `recording.duration`| int (sec.) | 3 | Duration in seconds for each audio recording. | The `batdetect2` model is able to process recordings of variable duration, however processing long recordings might lead to failure due to increased memory usage. Keep the duration between 1 and 3 seconds for optimal performance.|
| `recording.interval`| int (sec.) | 10 | Interval in seconds between recordings. | The `batdetect2` model requires some processing time. This interval helps maintain good performance. |
| `recording.chunksize`| int | 8192 | Chunksize of the audio recording.| An error will occur if the chunksize is too small for the audio device. |
| `schedule_start`| time (HH:MM:SS)| 19:00:00 | Time of day when recordings will start (24-hour format).| Adjust according to specific monitoring needs (e.g., nightime hours). |
| `schedule_end`| time (HH:MM:SS)| 07:00:00 | Time of day when recordings will end (24-hour format). | Adjust according to specific monitoring needs (e.g., nightime hours). |
| `timezone`| string | "Europe/London" | Timezone of the sensor location. | Configure this according to your deployment region.|
| __Paths__| | | Configuration for file paths.| |
| `paths.tmp_audio`| string | "/run/shm" | Temporary storage path for audio recordings. | Temporary in-memory path. Do not modify. |
| `paths.recordings`| string | "/home/pi/storages/recordings" | Path to directory for permanent storing of recorded audio files. | Modify accordingly. With default paths, recordings are stored on the SDCard, modify if using external usb hardrive. |
| `paths.db_metadata`| string | "/home/pi/storages/metadata.db" | Path to the database file for storing the metadata. | This database keeps track of recorded files, ML detection results, and system information. |
| __Messaging (Optional)__| | | Configuration for sending messages to remote server.| Will require access to network connectivity at the location of your device deployment. |
| `messaging.messages_db`| str | "/home/pi/storages/messages.db" | Path to the database file for storing messages. | This database keeps track of the messages to be sent to a remote server and their sent/received status. |
| `messaging.message_send_interval`| int (sec.) | 120 | Interval in seconds between attempts to send messages to a remote server. | Adjust for network performance and data bandwidth. |
| `messaging.heartbeat_interval` | int (sec.) | 3600 | Interval in seconds for sending heartbeat messages to the server. | Heartbeat message provides information about the device status (i.e., the correct functioning of the device). |
| __Messaging HTTP (Optional)__| | | Configuration for sending messages via HTTP.| |
| `messaging.http.base_url` | str | - | URL of the HTTP server to which messages are sent. | Configure according to your server setup. |
| `messaging.http.content_type` | str | application/json | Content type of the HTTP messages. | Messages to be sent are formated into a `json` object. |
| `messaging.http.timeout` | int (sec) | - | Timeout for HTTP requests in seconds. | |
| __Messaging MQTT (Optional)__| | | Configuration for sending messages via MQTT.| |
| `messaging.mqtt.host` | string | - | MQTT server hostname for message transmission. | Configure according to your server setup. |
| `messaging.mqtt.username` | str | - | Username for authentication with the MQTT broker. | Replace with your server username. |
| `messaging.mqtt.password` | str | - | Password for authentication with the MQTT broker. | Replace with your server password. |
| `messaging.mqtt.topic` | str | "acoupi" | Topic on the MQTT broker to publish messages | Replace with your server setup. |
| `messaging.mqtt.port`| int | 1884 |  Port number of the MQTT broker. | Default port is usually fine unless other setup on your server. |
| `messaging.mqtt.timeout` | int (sec) | 5 | Timeout for connecting to the MQTT broker in seconds. | |
| __Model__| | | Configuration related to running the BatDetect2 model. | |
| `model.detection_threshold` | float | 0.4 | Defines the threshold for filtering the detections obtained by the model. | A float value between 0.01 and 0.99. |
| __Recording Saving Filters (Optional)__ | N/A | - | Additional configurations for filtering the recordings to save. | |
| `saving_filters.starttime`| time (HH:MM:SS)| "21:00:00"| Start time for saving recorded audio files (24-hour format).| Insert 00:00:00 to not use this parameter to save audio recordings.|
| `saving_filters.endtime`| time (HH:MM:SS)| "23:00:00"| End time for saving recorded audio files (24-hour format)| Insert 00:00:00 to not use this parameter to save audio recordings. |
| `saving_filters.before_dawndusk_duration` | int (min.) | 0 | Additional duration (in minutes) to save recordings __before__ the dawn/dusk time.| Ensure recording interval covers the dawn and dusk time if using this parameter. |
| `saving_filters.after_dawndusk_duration`  | int (min.) | 0 |  Additional duration (in minutes) to save recordings __after__ the dawn/dusk time.| Ensure recording interval covers the dawn and dusk time if using this parameter. |
| `saving_filters.frequency_duration` | int (min.) | 0 | Duration in minutes for storing recordings when using the frequency filter. | Set to zero if not using this parameter.|
| `saving_filters.frequency_interval` | int (min.) | 0 | Periodic interval in minutes between two periods of storing recordings. | Set to zero if not using this parameter. |
| `saving_filters.saving_threshold` | float | 0.2 | Defines the threshold for saving files containing detections. | A float value between 0.01 and 0.99. |
| __Recording Saving Managers (Optional)__| | | Additional configurations for managing recordings processed by the model. | |
| `saving_managers.true_dir` | str | "bats" | Path to the directory storing audio files with _confident_ detections (i.e., recordings with detection score greater or equal than the `detection_threshold`). | Folder located in the folder defined by the `path.recordings` parameter. |
| `saving_managers.false_dir` | str | "no_bats" | Path to the directory storing audio files with _non-confident_ detections (i.e., recordings with detection score smaller than the `detection_threshold`). | Folder located in the folder defined by the `path.recordings` parameter. |
| `saving_managers.timeformat` | str | "%Y%m%d_%H%M%S" | Defines how to name recording files. The default value capture the date and time when the recording stated. | A recording with name 20241004_183040.wav indicates that the recording started on October 4, 2024 at 18:30:40. |
| `saving_managers.bat_threshold` | float | 0.5 | Defines the threshold for saving files in folders based on confident and non-confident detections. | A float value between 0.01 and 0.99. |
| __Summariser (Optional)__| | | Configuration for creating summary messages of the detections. | |
| `summariser.interval` | float | 3600 | Interval for which detections will be summarised. | In minutes. |
| `summariser.low_band_threshold` | float | 0.0 | Count the number of bat calls for each species that have a classification score lower or equal to the threshold. | A float value between 0.01 and 0.99 |
| `summariser.mid_band_threshold` | float | 0.0 | Count the number of bat calls for each species that have a classification score lower or equal to the mid_band value but higher than the low_band value. | A float value between 0.01 and 0.99 |
| `summariser.high_band_threshold` | float | 0.0 | Count the number of bat calls for each species that have a classification score lower or equal to the high_band value but higher than the high_band value. | A float value between 0.01 and 0.99 |
