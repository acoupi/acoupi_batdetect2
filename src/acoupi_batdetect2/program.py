"""Batdetect2 Program."""

import datetime
from typing import Optional

import pytz
from acoupi import components, data, tasks
from acoupi.programs.core.base import AcoupiProgram
from acoupi.programs.core.workers import AcoupiWorker, WorkerConfig

from acoupi_batdetect2.configuration import BatDetect2_ConfigSchema
from acoupi_batdetect2.model import BatDetect2


class BatDetect2_Program(AcoupiProgram):
    """BatDetect2 Program."""

    config: BatDetect2_ConfigSchema

    worker_config: Optional[WorkerConfig] = WorkerConfig(
        workers=[
            AcoupiWorker(
                name="recording",
                queues=["recording"],
                concurrency=1,
            ),
            AcoupiWorker(
                name="default",
                queues=["celery"],
            ),
        ],
    )

    def setup(self, config: BatDetect2_ConfigSchema):
        """Set up the batdetect2 program.

        Section 1 - Define Tasks for the BatDetect2 Program
            1. Create Recording Task
            2. Create Detection Task
            3. Create File Management Task
            4. Create Summary Task
            5. Create Message Task
        Section 2 - Add Tasks to BatDetect2 Program
        Section 3 - Configure Tasks based on BatDetect2 Configurations & User Inputs
            1. Store Directories
            2. Recording Conditions
            3. File Filters
            4. Summarisers
            5. Messengers
        """
        self.validate_dirs(config)
        microphone = config.microphone_config
        self.recorder = components.PyAudioRecorder(
            duration=config.audio_config.audio_duration,
            chunksize=config.audio_config.chunksize,
            samplerate=microphone.samplerate,
            audio_channels=microphone.audio_channels,
            device_name=microphone.device_name,
            audio_dir=config.tmp_path,
        )

        self.model = BatDetect2()
        self.saving_manager = components.SaveRecordingManager(
            dirpath=config.audio_directories.audio_dir,
            dirpath_true=config.audio_directories.audio_dir_true,
            dirpath_false=config.audio_directories.audio_dir_false,
            timeformat=config.timeformat,
            detection_threshold=config.detection_threshold,
            saving_threshold=config.saving_filters.saving_threshold,
        )
        self.store = components.SqliteStore(config.dbpath)
        self.message_store = components.SqliteMessageStore(
            config.dbpath_messages
        )

        """ Section 1 - Define Tasks for the BatDetect2 Program """
        # Step 1 - Audio Recordings Task
        recording_task = tasks.generate_recording_task(
            recorder=self.recorder,
            store=self.store,
            logger=self.logger.getChild("recording"),
            recording_conditions=self.create_recording_conditions(config),
        )

        # Step 2 - Model Detections Task
        #detection_task = tasks.generate_detection_task(
        #detection_task = tasks.generate_pyinstrument_task(
        detection_task = tasks.generate_cprofile_task(
            store=self.store,
            model=self.model,
            message_store=self.message_store,
            logger=self.logger.getChild("detection"),
            output_cleaners=self.create_modeloutput_cleaners(config),
            message_factories=[
                components.DetectionThresholdMessageBuilder(
                    detection_threshold=config.detection_threshold
                )
            ],
            profile_output="fulloutput.prof",
        )

        # Step 3 - Files Management Task
        file_management_task = tasks.generate_file_management_task(
            store=self.store,
            file_managers=[self.saving_manager],
            logger=self.logger.getChild("file_management"),
            file_filters=self.create_file_filters(config),
            temp_path=config.tmp_path,
        )

        # Step 4 - Summariser Task
        summary_task = tasks.generate_summariser_task(
            summarisers=self.create_summariser(config),
            message_store=self.message_store,
            logger=self.logger.getChild("summary"),
        )

        # Step 5 - Send Data Task
        send_data_task = tasks.generate_send_data_task(
            message_store=self.message_store,
            messengers=self.create_messenger(config),
            logger=self.logger.getChild("messaging"),
        )

        """ Section 2 - Add Tasks to BatDetect2 Program """
        self.add_task(
            function=recording_task,
            schedule=datetime.timedelta(
                seconds=config.audio_config.recording_interval
            ),
            callbacks=[detection_task],
            queue="recording",
        )

        self.add_task(
            function=file_management_task,
            schedule=datetime.timedelta(seconds=120),
        )

        if (
            config.summariser_config is not None
            and config.summariser_config.interval != 0.0
        ):
            self.add_task(
                function=summary_task,
                schedule=datetime.timedelta(
                    minutes=config.summariser_config.interval
                ),
            )

        self.add_task(
            function=send_data_task,
            schedule=datetime.timedelta(seconds=10),
        )

    """ Section 3 - Configure Tasks based on BatDetect2 Configurations & User Inputs """

    def validate_dirs(self, config: BatDetect2_ConfigSchema):
        """Validate Stores Directories."""
        # Check that directories to store audio files exists.
        if not config.audio_directories.audio_dir.exists():
            config.audio_directories.audio_dir.mkdir(parents=True)
        # Check directory to store audio files with positive detections.
        if not config.audio_directories.audio_dir_true.exists():
            config.audio_directories.audio_dir_true.mkdir(parents=True)
        # Check directory to store audio files with negative detections.
        if not config.audio_directories.audio_dir_false.exists():
            config.audio_directories.audio_dir_false.mkdir(parents=True)
        # Check directory to store database.
        if not config.dbpath.parent.exists():
            config.dbpath.parent.mkdir(parents=True)
        if not config.dbpath.exists():
            config.dbpath.touch()
        if not config.dbpath_messages.exists():
            config.dbpath_messages.touch()

    def create_recording_conditions(self, config: BatDetect2_ConfigSchema):
        """Create Recording Conditions."""
        timezone = pytz.timezone(config.timezone)
        return [
            components.IsInIntervals(
                intervals=[
                    data.TimeInterval(
                        start=config.recording_schedule.start_recording,
                        end=datetime.datetime.strptime(
                            "23:59:59", "%H:%M:%S"
                        ).time(),
                    ),
                    data.TimeInterval(
                        start=datetime.datetime.strptime(
                            "00:00:00", "%H:%M:%S"
                        ).time(),
                        end=config.recording_schedule.end_recording,
                    ),
                ],
                timezone=timezone,
            )
        ]

    def create_modeloutput_cleaners(self, config: BatDetect2_ConfigSchema):
        """Create Detection Cleaners."""
        detection_cleaners = []
        # No OutputCleaner Defined.
        return detection_cleaners

    def create_file_filters(self, config: BatDetect2_ConfigSchema):
        """Create File Filters."""
        if not config.saving_filters:
            # No saving filters defined
            return []

        file_filters = []
        timezone = pytz.timezone(config.timezone)
        saving_filters = config.saving_filters

        # Main saving_filters for processed recrodings
        # Will only save recordings if the recording time is in the
        # interval defined by the start and end time.
        if (
            saving_filters.starttime is not None
            and saving_filters.endtime is not None
        ):
            file_filters.append(
                components.SaveIfInInterval(
                    interval=data.TimeInterval(
                        start=saving_filters.starttime,
                        end=saving_filters.endtime,
                    ),
                    timezone=timezone,
                )
            )

        # Additional saving_file filters
        if (
            saving_filters.frequency_duration != 0
            and saving_filters.frequency_interval != 0
        ):
            # This filter will only save recordings at a frequency defined
            # by the duration (length of time in which files are saved) and
            # interval (period of time between each duration in which files are not saved).
            file_filters.append(
                components.FrequencySchedule(
                    duration=saving_filters.frequency_duration,
                    frequency=saving_filters.frequency_interval,
                )
            )

        if saving_filters.before_dawndusk_duration != 0:
            # This filter will only save recordings if the recording time is
            # within the duration (lenght of time in minutes) before dawn and dusk.
            file_filters.append(
                components.Before_DawnDuskTimeInterval(
                    duration=saving_filters.before_dawndusk_duration,
                    timezone=timezone,
                )
            )

        if saving_filters.after_dawndusk_duration != 0:
            # This filter will only save recordings if the recording time is
            # within the duration (lenght of time in minutes) after dawn and dusk.
            file_filters.append(
                components.After_DawnDuskTimeInterval(
                    duration=saving_filters.after_dawndusk_duration,
                    timezone=timezone,
                )
            )

        if saving_filters.saving_threshold != 0.0:
            # This filter will only save recordings if the recording files
            # have a positive detection above the threshold.
            file_filters.append(
                components.SavingThreshold(
                    saving_threshold=saving_filters.saving_threshold,
                )
            )

        return file_filters

    def create_summariser(self, config: BatDetect2_ConfigSchema):
        """Create Summariser."""
        # Main Summariser will send summary of detections at regular intervals.
        if not config.summariser_config:
            raise UserWarning(
                "No saving filters defined - no files will be saved."
            )

        summarisers = []
        summariser_config = config.summariser_config

        """Default Summariser: Return mean, max, min and count of detections of a time interval."""
        if summariser_config.interval != 0.0:
            summarisers.append(
                components.StatisticsDetectionsSummariser(
                    store=self.store,
                    interval=summariser_config.interval,
                )
            )

        """Threshold Summariser: Return count and mean of detections in threshold bands 
        for a specific time interval, if users set values for threshold bands."""
        if (
            summariser_config.interval != 0.0
            and summariser_config.low_band_threshold != 0.0
            and summariser_config.mid_band_threshold != 0.0
            and summariser_config.high_band_threshold != 0.0
        ):
            summarisers.append(
                components.ThresholdsDetectionsSummariser(
                    store=self.store,
                    interval=summariser_config.interval,
                    low_band_threshold=summariser_config.low_band_threshold,
                    mid_band_threshold=summariser_config.mid_band_threshold,
                    high_band_threshold=summariser_config.high_band_threshold,
                )
            )

        return summarisers

    def create_messenger(self, config: BatDetect2_ConfigSchema):
        """Create Messengers - Send Detection Results."""
        # Main Messenger will send messages to remote server.
        if not config.mqtt_message_config and not config.http_message_config:
            raise UserWarning(
                "No messengers defined - no messages will be sent."
            )

        messengers = []

        """MQTT Messenger - Will send messages to a MQTT broker."""
        if (
            config.mqtt_message_config is not None
            and config.mqtt_message_config.client_password != "guest_password"
        ):
            messengers.append(
                components.MQTTMessenger(
                    host=config.mqtt_message_config.host,
                    port=config.mqtt_message_config.port,
                    password=config.mqtt_message_config.client_password,
                    username=config.mqtt_message_config.client_username,
                    topic=config.mqtt_message_config.topic,
                    clientid=config.mqtt_message_config.clientid,
                )
            )

        if (
            config.http_message_config is not None
            and config.http_message_config.client_password != "guest_password"
        ):
            messengers.append(
                components.HTTPMessenger(
                    base_url=config.http_message_config.baseurl,
                    base_params={
                        "client-id": config.http_message_config.client_id,
                        "password": config.http_message_config.client_password,
                    },
                    headers={
                        "Accept": config.http_message_config.content_type,
                        "Authorization": config.http_message_config.api_key,
                    },
                )
            )

        return messengers
