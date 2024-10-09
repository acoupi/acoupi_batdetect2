# Configuration acoupi-batdetect2

acoupi-batdetect2 is built using the acoupi Python toolkit. acoupi-batdetect2 is made of three main parts: the batdetect2 model, a configuation schema, and a program, which is a collection of acoupi components.

Here we are only discussing the configuration options for acoupi-batdetect2. If you want to learn more about the [acoupi](https://pypi.org/project/batdetect2/) framework, please refer to the developer guide available in the [acoupi documentation](https://pypi.org/project/acoupi/).


## Getting Started

Configuring acoupi-batdetect2 is an extremely quick and easy task. To customise acoupi-batdetect2 configuration, you first need to intall acoupi-batdetect2 on your Raspberry Pi. 

>[!Important]
> If you have not installed acoupi-batdetect2 on your Rapspberry Pi, go to the [installation guide](/docs/user_guide/installation.md) and follow the instructions. Once you are done, come back here. 

When running the initial command `acoupi setup --program acoupi_batdetect2.program`, you will be prompted with a serie of questions. By entering **Y** for Yes and **n** for No, you will tailor the program to your needs. 

The configurations can be grouped as follows: 

- [Program Setup](#program-setup-parameters)
- [Audio and Microphone](#audio-and-microphone-parameters)
- [Recording Schedule](#recording-schedule-parameters)
- [Saving Recordings](#saving-recordings-parameters)
- [Remote Messaging](#remote-messaging)
    - [MQTT](#mqtt-parameters)
    - [HTTP](#http-parameters)


### Program Setup Parameters
There are a few parameters the user must configure so the program can start working. 

1. **name**: the name associated with the program installed on the Raspberry Pi. For clarity, we are using the name of the bioacoustic classifiers model. 

    Default value: batdetect2

2. **detection_threshold**: the threshold that will be used to detect bat species in audio recordings. Any detection under the threshold will be disregarded, any detection above the threshold will be saved. Values >0.9 are conservative and might missed some true positive, values <0.5 will contain false positive. 

    Default value: 0.7

    Acceptable value range: [0.01 to 0.99]

3. **dbpath and dbpath_messages**: the path to the sqlite3 database file where detections results and remote messaging messages are saved. 

4. **timeformat**: the timeformat used to name the audio recordings files. An example of the default timeformat value '%Y%m%d_%H%M%S' is as follows: 20240128_223045 which equals to the 28th January 2024 at 22:40:45.

5. **timezone**: the timezone in which the device is deployed. See the [timezone database on Wikipedia](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) to find the TZ identifier of your timezone. 

    Default value: Europe/London

    Acceptable value: TZ Identifier

### Audio and Microphone Parameters
There are multiple parameters used to configure the audio recordings. Some of these parameters can be modified, others are best not to. 

1. **audio_duration**: the length of an audio recording file that will serve as input to the batdetect2 model. 

    Default value in seconds: 3 

    Acceptable value range: [1 to 3]

2. **samplerate**: the sample rate used by the microphone to record audio. You will need to be modified this value depending on the microphone you are using. 

    Default value in Hz: 192000
    
    Acceptable value range: [96000 to 384000]

3. **audio_channels**: the number of channels your microphone has. *The BatDetect2 model was trained with audio recordings from 1 channel microphone.* Most popular microphone have 1 audio channel. It is unlikely you need to change this value. 

    Default value: 1
    
    Acceptable value range:

4. **chunksize**: the arbitrarily number of frames the audio signals are split into. Chunksize are mutilple of 2**n. 

    Default value: 8192
    
    Acceptable value range: [1024 to 8192]

5. **device index**: Ignore.

6. **recording interval**: the time in seconds between two audio recordings.

    Default value in seconds: 10

    Acceptable value range: [0 to 60]

### Recording Schedule Parameters
1. **recording_schedule**: this parameters enables the users to set specific time to record audio files. If nothing is set by the user the default recording schedule parameters are used. 

2. **start_recording**: the time of the day when the device starts to record audio.  

    Default value: 19:00:00

    Acceptable value: *What value to input??*

3. **end_recording**: the time of the day when the device stops to record audio.  

    Default value: 07:00:00

    Acceptable value: *What value to input??*

### Saving Recordings Parameters
There are multiple parameters available for saving audio recordings on the device. Some of these parameters work in pair and the users will need to configure the pair. These are starttime and endtime, and frequency duration and frequency interval. In the case of before dawndusk and after dawndusk, the user can use them separately.

1. **recording_saving**: this parameters enables the users to save audio recordings on the device. If nothing is set by the users NO audio recordings will be saved. 

2. **starttime**: the time of the day when the device will start saving audio recordings.

    Default value: 21:30:00

    Acceptable value: *What value to input??*

3. **endtime**: the time of the day when the device will stop saving audio recordings.  

    Default value: 23:30:00

    Acceptable value: *What value to input??*

4. **before_dawndusk_duration**: the duration in minutes **before** the time of dawn and dusk the device will save audio recordings.  

    Default value in minutes: 10

    Acceptable value: [0-120]

5. **after_dawndusk_duration**: the duration in minutes **after** the time of dawn and dusk the device will save audio recordings.  

    Default value in minutes: 10

    Acceptable value: [0-120]

6. **frequency_duration**: the duration in minutes the device will save audio recordings. This parameter goes hand in hand with the following parameter: *frequency_interval*. 

    Default value in minutes: 0

    Acceptable value: [0-30]

7. **frequency_interval**: the interval in minutes that the device will wait before saving again audio recordings. This parameter goes hand in hand with the above parameter: *frequency_duration*. 

    Default value in minutes: 0

    Acceptable value: [30-120]

8. **saving_threshold**: the detection treshold for which audio files will be saved. Only audio files with a detection **above** the saving_threshold will be saved. The other files will be disregarded.  

    Default value: 0.8

    Acceptable value: [0.01-0.99]

9. **audio_directories**: this parameters enables the users to define the paths where the audio recordings will be saved on the device. If nothing is set by the users the default value will be saved. 

10. **audio_dir_true**: the path to which audio files containing a positive detection will be saved. 

    Default value: Path('/home/pi/.acoupi/storages/recordings/bats')

11. **audio_dir_false**: the path to which audio files with no detections will be saved. 

    Default value: Path('/home/pi/.acoupi/storages/recordings/no_bats')

### Remote Messaging

The acoupi-batdetect2 program comes with the optionality to send detection results back to a remote server. We  have pre-configured two messaging optionalities: MQTT and HTPP. 

#### MQTT Parameters
1. **host**: the hostname or IP address of the target MQTT broker. 

    Default value: localhost

2. **port**: the port to use for connecting to the borker. Default ports are 1883/1884 for MQTT and 8883/8884 for secure MQTT (MQTTS).

    Default value: 1884

3. **client_password**: the password used to authenticate with the broker. 

4. **client_username**: the username used to authenticate with the broker. 

5. **topic**: the topic the message will be sent to. 

6. **clientid**: the client id for the connection. 

#### HTTP Parameters
1. **base_url**: the URL to send messages to. This should include the protocol (e.g. http:// or https://) and the hostname (e.g. localhost) and the path (e.g. /api/endpoint).

2. **client_password**: the password to use when authenticating with the target server. 

3. **client_username**: the username to use when authenticating with the target server. 

4. **api_key**: the api key for authorisation that is sent as a request header. 

5. **content_type**: the content type to send with each request, by default "application/json".