"""Batdetect2 Program."""
import datetime
from celery.schedules import crontab
from acoupi import components, data, tasks
from acoupi.programs.base import AcoupiProgram
from acoupi_batdetect2.configuration import BatDetect2_ConfigSchema
from acoupi_batdetect2.model import BatDetect2


class BatDetect2_Program(AcoupiProgram):
    """BatDetect2 Program."""

    config: BatDetect2_ConfigSchema

    def setup(self, config: BatDetect2_ConfigSchema):
        """Setup.

        1. Create Audio Recording Task
        2. Create Detection Task
        3. Create Saving Recording Filter and Management Task
        4. Create Message Task

        """

        # Step 1 - Audio Recordings Task
        recording_task = tasks.generate_recording_task(
            recorder=components.PyAudioRecorder(
                duration=config.audio_config.audio_duration,
                samplerate=config.audio_config.samplerate,
                audio_channels=config.audio_config.audio_channels,
                chunksize=config.audio_config.chunksize,
                device_index=config.audio_config.device_index,
            ),
            store=components.SqliteStore(config.dbpath),
            # logger
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
                    timezone=config.timezone,
                )
            ],
        )

        # Step 2 - Model Detections Task
        detection_task = tasks.generate_detection_task(
            store=components.SqliteStore(config.dbpath),
            model=BatDetect2(),
            message_store=components.SqliteMessageStore(db_path=config.dbpath_messages),
            # logger
            output_cleaners=[
                components.ThresholdDetectionFilter(
                    threshold=config.detection_threshold
                )
            ],
            message_factories=[components.FullModelOutputMessageBuilder()],
        )

        # Step 3 - Files Management Task
        def create_file_filters():
            saving_filters = []

            if components.SaveIfInInterval is not None:
                saving_filters.add(
                    components.SaveIfInInterval(
                        interval=data.TimeInterval(
                            start=config.recording_saving.starttime,
                            end=config.recording_saving.endtime,
                        ),
                        timezone=config.timezone,
                    )
                )
            elif components.FrequencySchedule is not None:
                saving_filters.add(
                    components.FrequencySchedule(
                        duration=config.recording_saving.frequency_duration,
                        frequency=config.recording_saving.frequency_interval,
                    )
                )
            elif components.Before_DawnDuskTimeInterval is not None:
                saving_filters.add(
                    components.Before_DawnDuskTimeInterval(
                        duration=config.recording_saving.before_dawndusk_duration,
                        timezone=config.timezone,
                    )
                )
            elif components.After_DawnDuskTimeInterval is not None:
                saving_filters.add(
                    components.After_DawnDuskTimeInterval(
                        duration=config.recording_saving.after_dawndusk_duration,
                        timezone=config.timezone,
                    )
                )
            elif components.ThresholdRecordingFilter is not None:
                saving_filters.add(
                    components.ThresholdRecordingFilter(
                        threshold=config.recording_saving.saving_threshold,
                    )
                )
            else:
                raise UserWarning("No saving filters defined - no files will be saved.")

            return saving_filters

        file_management_task = (
            tasks.generate_file_management_task(
                store=components.SqliteStore(config.dbpath),
                file_manager=components.SaveRecordingManager(
                    dirpath_true=config.audio_directories.audio_dir_true,
                    dirpath_false=config.audio_directories.audio_dir_false,
                    timeformat=config.timeformat,
                    threshold=config.threshold,
                ),
                file_filters=create_file_filters(),
            ),
        )

        # Step 4 - Send Data Task
        def create_messenger():
            data_messengers = []

            if components.HTTPMessenger is not None:
                data_messengers.add(
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
            elif components.MQTTMessenger is not None:
                data_messengers.add(
                    components.MQTTMessenger(
                        host=config.mqtt_message_config.host,
                        port=config.mqtt_message_config.port,
                        password=config.mqtt_message_config.client_password,
                        username=config.mqtt_message_config.client_username,
                        topic=config.mqtt_message_config.topic,
                        clientid=config.mqtt_message_config.clientid,
                    )
                )
            else:
                raise UserWarning(
                    "No Messenger defined - no data will be communicated."
                )

            return data_messengers

        send_data_task = tasks.generate_send_data_task(
            message_store=components.SqliteMessageStore(db_path=config.dbpath_messages),
            messenger=create_messenger(),
        )

        # Final Step - Add Tasks to Program
        self.add_task(
            function=recording_task,
            callbacks=[detection_task],
            schedule=datetime.timedelta(seconds=10),
        )

        self.add_task(
            function=file_management_task,
            schedule=datetime.timedelta(minutes=10),
        )

        self.add_task(
            function=send_data_task,
            schedule=crontab(minute="*/1"),
        )
