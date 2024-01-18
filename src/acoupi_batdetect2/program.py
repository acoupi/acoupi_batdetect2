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
                name="recording_worker",
                queues=["recording"],
                concurrency=1,
            ),
            # AcoupiWorker(
            #    name="detection_worker",
            #    queues=["detection"],
            #    concurrency=1,
            # ),
            AcoupiWorker(
                name="default_worker",
                queues=["default"],
            ),
        ],
    )

    def setup(self, config: BatDetect2_ConfigSchema):
        """Setup.

        1. Create Audio Recording Task
        2. Create Detection Task
        3. Create Saving Recording Filter and Management Task
        4. Create Message Task
        """
        timezone = pytz.timezone(config.timezone)

        if not config.dbpath.parent.exists():
            config.dbpath.parent.touch()

        if not config.dbpath.exists():
            config.dbpath.touch()

        if not config.dbpath_messages.exists():
            config.dbpath_messages.touch()

        if not config.audio_directories.audio_dir.exists():
            config.audio_directories.audio_dir.mkdir(parents=True)

        if not config.audio_directories.audio_dir_true.exists():
            config.audio_directories.audio_dir_true.mkdir(parents=True)

        if not config.audio_directories.audio_dir_false.exists():
            config.audio_directories.audio_dir_false.mkdir(parents=True)

        self.store = components.SqliteStore(config.dbpath)
        self.message_store = components.SqliteMessageStore(
            config.dbpath_messages
        )
        self.recorder = components.PyAudioRecorder(
            duration=config.audio_config.audio_duration,
            samplerate=config.microphone.samplerate,
            audio_channels=config.microphone.audio_channels,
            chunksize=config.audio_config.chunksize,
            device_index=config.microphone.device_index,
        )
        self.model = BatDetect2()

        # Step 1 - Audio Recordings Task
        recording_task = tasks.generate_recording_task(
            recorder=self.recorder,
            store=self.store,
            logger=self.logger.getChild("recording"),
            recording_conditions=[
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
            ],
        )

        # Step 2 - Model Detections Task
        detection_task = tasks.generate_detection_task(
            store=self.store,
            model=self.model,
            message_store=self.message_store,
            logger=self.logger.getChild("detection"),
            output_cleaners=[
                components.ThresholdDetectionFilter(
                    threshold=config.detection_threshold
                )
            ],
            message_factories=[components.FullModelOutputMessageBuilder()],
        )

        # Step 3 - Files Management Task
        def create_file_filters():
            recording_saving = config.recording_saving

            if recording_saving is None:
                return []

            saving_filters = []
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

            elif (
                recording_saving.frequency_duration is not None
                and recording_saving.frequency_interval is not None
            ):
                saving_filters.append(
                    components.FrequencySchedule(
                        duration=recording_saving.frequency_duration,
                        frequency=recording_saving.frequency_interval,
                    )
                )

            elif recording_saving.before_dawndusk_duration is not None:
                saving_filters.append(
                    components.Before_DawnDuskTimeInterval(
                        duration=recording_saving.before_dawndusk_duration,
                        timezone=timezone,
                    )
                )

            elif recording_saving.after_dawndusk_duration is not None:
                saving_filters.append(
                    components.After_DawnDuskTimeInterval(
                        duration=recording_saving.after_dawndusk_duration,
                        timezone=timezone,
                    )
                )
            elif recording_saving.saving_threshold is not None:
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

        file_management_task = tasks.generate_file_management_task(
            store=self.store,
            file_manager=components.SaveRecordingManager(
                dirpath=config.audio_directories.audio_dir,
                dirpath_true=config.audio_directories.audio_dir_true,
                dirpath_false=config.audio_directories.audio_dir_false,
                timeformat=config.timeformat,
                threshold=config.detection_threshold,
            ),
            file_filters=create_file_filters(),
        )

        # Step 4 - Send Data Task
        def create_messenger():
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

        self.messenger = create_messenger()

        send_data_task = tasks.generate_send_data_task(
            message_store=self.message_store,
            messenger=self.messenger,
        )

        # Final Step - Add Tasks to Program
        self.add_task(
            function=recording_task,
            callbacks=[detection_task],
            schedule=datetime.timedelta(seconds=10),
            queue="recording",
        )

        # self.add_task(
        #    function=detection_task,
        #    schedule=datetime.timedelta(seconds=5),
        #    queue="detection",
        # )

        self.add_task(
            function=file_management_task,
            schedule=datetime.timedelta(seconds=30),
            queue="default",
        )

        self.add_task(
            function=send_data_task,
            schedule=crontab(minute="*/1"),
            queue="default",
        )
