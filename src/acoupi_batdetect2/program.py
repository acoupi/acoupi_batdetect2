"""Batdetect2 Program."""

import datetime

import pytz
from acoupi import components, data, tasks
from acoupi.components import types
from acoupi.programs.templates import DetectionProgram

from acoupi_batdetect2.configuration import (
    BatDetect2_ConfigSchema,
)
from acoupi_batdetect2.model import BatDetect2


class BatDetect2_Program(DetectionProgram[BatDetect2_ConfigSchema]):
    """BatDetect2 Program Configuration.

    Section 1. Get configuration schema
        - Get the specific configuration parameters for the batdetect2 program.

    Section 2. Inherit template program from acoupi
        - Get the functionality and structure of the `DetectionProgram`

    Section 3. Define and configure supplementary tasks
        - Implement the customised program configuration.
    """

    config_schema = BatDetect2_ConfigSchema

    def setup(self, config):
        super().setup(config)

        if config.summariser_config and config.summariser_config.interval:
            summary_task = tasks.generate_summariser_task(
                summarisers=self.get_summarisers(config),
                message_store=self.message_store,
                logger=self.logger.getChild("summary"),
            )

            self.add_task(
                function=summary_task,
                schedule=datetime.timedelta(minutes=config.summariser_config.interval),
            )

    def configure_model(self, config):
        return BatDetect2()

    def get_summarisers(self, config) -> list[types.Summariser]:
        if not config.summariser_config:
            return []

        summarisers = []
        summariser_config = config.summariser_config

        if summariser_config.interval != 0.0:
            summarisers.append(
                components.StatisticsDetectionsSummariser(
                    store=self.store,  # type: ignore
                    interval=summariser_config.interval,
                )
            )

        if (
            summariser_config.interval != 0.0
            and summariser_config.low_band_threshold != 0.0
            and summariser_config.mid_band_threshold != 0.0
            and summariser_config.high_band_threshold != 0.0
        ):
            summarisers.append(
                components.ThresholdsDetectionsSummariser(
                    store=self.store,  # type: ignore
                    interval=summariser_config.interval,
                    low_band_threshold=summariser_config.low_band_threshold,
                    mid_band_threshold=summariser_config.mid_band_threshold,
                    high_band_threshold=summariser_config.high_band_threshold,
                )
            )

        return summarisers

    def get_file_managers(self, config) -> list[types.RecordingSavingManager]:
        return [
            components.SaveRecordingManager(
                dirpath=config.paths.recordings,
                dirpath_true=config.paths.recordings / config.recording_saving.true_dir,
                dirpath_false=config.paths.recordings
                / config.recording_saving.false_dir,
                timeformat=config.recording_saving.timeformat,
                detection_threshold=config.model.detection_threshold,
                saving_threshold=config.recording_saving.saving_threshold,
            )
        ]

    def get_message_factories(self, config) -> list[types.MessageBuilder]:
        return [
            components.DetectionThresholdMessageBuilder(
                detection_threshold=config.model.detection_threshold
            )
        ]

    def get_recording_filters(self, config) -> list[types.RecordingSavingFilter]:
        if not config.recording_saving:
            # No saving filters defined
            return []

        saving_filters = []
        timezone = pytz.timezone(config.timezone)
        recording_saving = config.recording_saving

        # Main filter
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

        # Additional filters
        if (
            recording_saving.frequency_duration != 0
            and recording_saving.frequency_interval != 0
        ):
            # This filter will only save recordings at a frequency defined
            # by the duration and interval.
            saving_filters.append(
                components.FrequencySchedule(
                    duration=recording_saving.frequency_duration,
                    frequency=recording_saving.frequency_interval,
                )
            )

        if recording_saving.before_dawndusk_duration != 0:
            # This filter will only save recordings if the recording time
            # is before dawn or dusk.
            saving_filters.append(
                components.Before_DawnDuskTimeInterval(
                    duration=recording_saving.before_dawndusk_duration,
                    timezone=timezone,
                )
            )

        if recording_saving.after_dawndusk_duration != 0:
            # This filter will only save recordings if the recording time
            # is after dawn or dusk.
            saving_filters.append(
                components.After_DawnDuskTimeInterval(
                    duration=recording_saving.after_dawndusk_duration,
                    timezone=timezone,
                )
            )

        return saving_filters
