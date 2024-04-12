"""Batdetect2 Program."""

import datetime
from typing import Optional
import pytz

from acoupi import components, data, tasks
from acoupi.programs.base import AcoupiProgram
from acoupi.programs.workers import AcoupiWorker, WorkerConfig
from celery.schedules import crontab

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
                queues=["default", "celery"],
            ),
        ],
    )

    def setup(self, config: BatDetect2_ConfigSchema):
        """Setup.

        Section 1 - Define Tasks for the BatDetect2 Program
            1. Create Recording Task
            2. Create Detection Task
            3. Create Fine Management Task
            4. Create Message Task
        Section 2 - Add Tasks to BatDetect2 Program
        Section 3 - Configure Tasks based on BatDetect2 Configurations & User Inputs
            1. Store Directories
            2. Recording Conditions
            3. File Filters
            4. Messengers
        """

        self.validate_dirs(config)
        microphone = config.microphone_config
        self.recorder = components.PyAudioRecorder(
            duration=config.audio_config.audio_duration,
            chunksize=config.audio_config.chunksize,
            samplerate=microphone.samplerate,
            audio_channels=microphone.audio_channels,
            device_name=microphone.device_name,
        )

        self.model = BatDetect2()
        self.file_manager = components.SaveRecordingManager(
            dirpath=config.audio_directories.audio_dir,
            dirpath_true=config.audio_directories.audio_dir_true,
            dirpath_false=config.audio_directories.audio_dir_false,
            timeformat=config.timeformat,
            threshold=config.detection_threshold,
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
        detection_task = tasks.generate_detection_task(
            store=self.store,
            model=self.model,
            message_store=self.message_store,
            logger=self.logger.getChild("detection"),
            output_cleaners=self.create_detection_cleaners(config),
            message_factories=[components.FullModelOutputMessageBuilder()],
        )

        # Step 3 - Files Management Task
        file_management_task = tasks.generate_file_management_task(
            store=self.store,
            logger=self.logger.getChild("file_management"),
            file_manager=self.file_manager,
            file_filters=self.create_file_filters(config),
        )

        # Step 4 - Send Data Task
        send_data_task = tasks.generate_send_data_task(
            message_store=self.message_store,
            messenger=self.create_messenger(config),
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
            schedule=datetime.timedelta(seconds=30),
            queue="default",
            # delay_seconds=60,
        )

        self.add_task(
            function=send_data_task,
            schedule=crontab(minute="*/1"),
            queue="default",
            # delay_seconds=60,
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

    def create_detection_cleaners(self, config: BatDetect2_ConfigSchema):
        """Create Detection Cleaners."""

        detection_cleaners = []

        # Main detection_cleaner
        # Will clean the model outputs by removing any detections that are
        # below the threshold.
        detection_cleaners.append(
            components.ThresholdDetectionFilter(
                threshold=config.detection_threshold,
            ),
        )

        return detection_cleaners

    def create_file_filters(self, config: BatDetect2_ConfigSchema):
        """Create File Filters."""
        if not config.recording_saving:
            # No saving filters defined
            return []

        saving_filters = []
        timezone = pytz.timezone(config.timezone)
        recording_saving = config.recording_saving

        # Main saving_file filter
        # Will only save recordings if the recording time is in the
        # interval defined by the start and end time.
        if (
            recording_saving.starttime is not None
            and recording_saving.endtime is not None
        ):
            saving_filters.append(
                components.SaveIfInInterval(
                    interval=data.TimeInterval(
                        start=recording_saving.starttime,
                        end=recording_saving.endtime,
                    ),
                    timezone=timezone,
                )
            )

        # Additional saving_file filters
        if (
            recording_saving.frequency_duration != 0
            and recording_saving.frequency_interval != 0
        ):
            # This filter will only save recordings at a frequency defined
            # by the duration (length of time in which files are saved) and
            # interval (period of time between each duration in which files are not saved).
            saving_filters.append(
                components.FrequencySchedule(
                    duration=recording_saving.frequency_duration,
                    frequency=recording_saving.frequency_interval,
                )
            )

        # if recording_saving.before_dawndusk_duration is not None:
        if recording_saving.before_dawndusk_duration != 0:
            # This filter will only save recordings if the recording time is
            # within the duration (lenght of time in minutes) before dawn and dusk.
            saving_filters.append(
                components.Before_DawnDuskTimeInterval(
                    duration=recording_saving.before_dawndusk_duration,
                    timezone=timezone,
                )
            )

        # if recording_saving.after_dawndusk_duration is not None:
        if recording_saving.after_dawndusk_duration != 0:
            # This filter will only save recordings if the recording time is
            # within the duration (lenght of time in minutes) after dawn and dusk.
            saving_filters.append(
                components.After_DawnDuskTimeInterval(
                    duration=recording_saving.after_dawndusk_duration,
                    timezone=timezone,
                )
            )

        # if recording_saving.saving_threshold is not None:
        if recording_saving.saving_threshold != 0:
            # This filter will only save recordings if the recording files
            # have a positive detection above the threshold.
            saving_filters.append(
                components.ThresholdRecordingFilter(
                    threshold=recording_saving.saving_threshold,
                )
            )
        else:
            raise UserWarning(
                "No saving filters defined - no files will be saved."
            )

        return saving_filters

    def create_messenger(self, config: BatDetect2_ConfigSchema):
        """Create Messengers - Send Detection Results."""

        # HTTP Messenger
        # This messenger will send detection results to a web server.
        if config.http_message_config is not None:
            return components.HTTPMessenger(
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

        # MQTT Messenger
        # This messenger will send detection results to a MQTT broker.
        if config.mqtt_message_config is not None:
            return components.MQTTMessenger(
                host=config.mqtt_message_config.host,
                port=config.mqtt_message_config.port,
                password=config.mqtt_message_config.client_password,
                username=config.mqtt_message_config.client_username,
                topic=config.mqtt_message_config.topic,
                clientid=config.mqtt_message_config.clientid,
            )

        raise UserWarning(
            "No Messenger defined - no data will be communicated."
        )
