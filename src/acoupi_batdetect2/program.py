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
    """BatDetect2 Program Configuration

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
                schedule=datetime.timedelta(
                    minutes=config.summariser_config.interval
                ),
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
                dirpath_true=config.paths.recordings / config.saving.true_dir,
                dirpath_false=config.paths.recordings
                / config.saving.false_dir,
                timeformat=config.saving.timeformat,
                detection_threshold=config.model.detection_threshold,
                saving_threshold=config.saving.saving_threshold,
            )
        ]

    def get_message_factories(self, config) -> list[types.MessageBuilder]:
        return [
            components.DetectionThresholdMessageBuilder(
                detection_threshold=config.model.detection_threshold
            )
        ]

    def get_recording_filters(
        self, config
    ) -> list[types.RecordingSavingFilter]:
        if not config.saving.filters:
            # No saving filters defined
            return []

        recording_filters = []

        timezone = pytz.timezone(config.timezone)
        saving_filters = config.saving.filters

        # Main saving_filters for processed recrodings
        # Will only save recordings if the recording time is in the
        # interval defined by the start and end time.
        if (
            saving_filters.starttime is not None
            and saving_filters.endtime is not None
        ):
            recording_filters.append(
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
            saving_filters.frequency_duration
            and saving_filters.frequency_interval
        ):
            # This filter will only save recordings at a frequency defined
            # by the duration (length of time in which files are saved) and
            # interval (period of time between each duration in which files are not saved).
            recording_filters.append(
                components.FrequencySchedule(
                    duration=saving_filters.frequency_duration,
                    frequency=saving_filters.frequency_interval,
                )
            )

        if saving_filters.before_dawndusk_duration:
            # This filter will only save recordings if the recording time is
            # within the duration (lenght of time in minutes) before dawn and dusk.
            recording_filters.append(
                components.Before_DawnDuskTimeInterval(
                    duration=saving_filters.before_dawndusk_duration,
                    timezone=timezone,
                )
            )

        if saving_filters.after_dawndusk_duration:
            # This filter will only save recordings if the recording time is
            # within the duration (lenght of time in minutes) after dawn and dusk.
            recording_filters.append(
                components.After_DawnDuskTimeInterval(
                    duration=saving_filters.after_dawndusk_duration,
                    timezone=timezone,
                )
            )

        if config.saving.saving_threshold:
            # This filter will only save recordings if the recording files
            # have a positive detection above the threshold.
            recording_filters.append(
                components.SavingThreshold(
                    saving_threshold=config.saving.saving_threshold,
                )
            )

        return recording_filters
