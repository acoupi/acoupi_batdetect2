"""# Batdetect2 Program.

This module builds the BatDetect2 Program to record, detect and classify, as well as
manage and send messages of UK bat calls. The program extends the `DetectionProgram`
and `MessagingProgram` from the _acoupi_ package by adding the BatDetect2 model
and integrating users' custom configuration schema.

### Key Elements:

- __BatDetect2_ConfigSchema__: Defines the configuration for the BatDetect2
program, including the audio recording, model setup, file management, messaging,
and summariser settings.

### Program Tasks:

- __recording_task__: Records audio from a microphone and saves the audio files
in a temporary directory until they have been processed by the `detection`
and `management` tasks. Based on the `SavingFilters` configuration, recordings
will either saved or deleted.
- __detection_task__: Runs the BatDetect2 model on the audio recordings, processes
the detections, and can use a custom `ModelOutputCleaner` to filter out unwanted
detections (e.g., low-confidence results). The filtered detections are saved in
a `metadata.db` file.
- __management_task__: Performs periodically file management operations,
such as moving recording to permanent storage, or deleting unnecessary ones.
- __messaging_task__: Send messages stored in the message store using a
configured protocol (HTTP or MQTT).
- __summary_task__: Periodically creates summaries of the detections.

### Customisation Options:

- __ModelConfig__: Set the `detection_threshold` to clean out the output of the
BatDetect2 model. Detections with a confidence score below this threshold
will be excluded from the store and from the message content.

- __SaveRecordingManager__: Define where recordings are stored, the naming format, and
the minimum confidence score for saving recordings. Recordings with confidence
scores below the `saving_threshold` will not be saved. The `saving_threshold`
can be set lower than the `detection_threshold` to save recordings with uncertain
detections. Recordings with detections above the `detection_threshold` will be
saved in the `true_dir` directory, while recordings with detections below
the `detection_threshold` but above the `saving_threshold` will be saved in
the `false_dir` directory.

- __SaveRecordingFilter__: Define additional saving filters for saving recordings.
    1. A timeinterval interval fitler that saves recordings whthin a specific time
     window, set by the `starttime` and `endtime` parameters.
    2. A frequency filter that saves recordings for a specific duration
     (in minutes) at defined interval (in minutes), set by the `frequency_duration`
     and `frequency_interval` parameters.
    3. A before dawn/dusk filter to save recording for a defined duration
     (in minutes) before dawn and dusk, set by the `before_dawndusk_duration`.
    4. An after dawn/dusk filter to save recording for a defined duration
     (in minutes) after dawn and dusk, set by the `after_dawndusk_duration`.
    5. A saving threshold filter to save recording with detection above a specific 
    treshold, set by the `saving_filter` parameter. 

- __SummariserConfig__: Define the interval for summarising detections.
By default, the summariser calculates the minimum, maximum, and average
confidence scores of the total number of detections for each time interval.
If the `low_band_threshold`, `mid_band_threshold`, and `high_band_threshold` are
set to values greater than 0.0, it also summarises the number of detections in
each band (low, mid, high).
"""

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
    """BatDetect2 Program Configuration."""

    config_schema = BatDetect2_ConfigSchema

    def setup(self, config):
        """Set up the BatDetect2 Program.

        This method initialises the batdetect2 program, registers the
        recording, detection, management, messaging, and summariser tasks,
        and performs any necessary setup for the program to run.
        """
        # Setup all the elements from the DetectionProgram
        super().setup(config)

        # Create the summariser task
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
        """Configure the BatDetect2 model.

        Returns
        -------
        BatDetect2
            The BatDetect2 model instance.
        """
        return BatDetect2()

    def get_summarisers(self, config) -> list[types.Summariser]:
        """Get the summarisers for the BatDetect2 Program.

        Parameters
        ----------
        config : BatDetect2_ConfigSchema
            The configuration schema for the _acoupi_batdetect2_ program defined in
            the configuration.py file and configured by a user via the CLI.

        Returns
        -------
        list[types.Summariser]
            A list of summarisers for the batdetect2 program. By default,
            the summariser will use the `summariser_config.interval` parameter for summarising
            the detections and calculating the minimum, maximum, and average
            confidence scores of the detections in each interval.
        """
        # Check if there is any summariser configuration
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
        """Get the file managers for the BatDetect2 Program.

        Parameters
        ----------
        config : BatDetect2_ConfigSchema
            The configuration schema for the _acoupi_batdetect2_ program defined in
            the configuration.py file and configured by a user via the CLI.

        Returns
        -------
        list[types.RecordingSavingManager]
            A list of file managers for the batdetect2 program.
        """
        return [
            components.SaveRecordingManager(
                dirpath=config.paths.recordings,
                dirpath_true=config.paths.recordings
                / config.saving_managers.true_dir,
                dirpath_false=config.paths.recordings
                / config.saving_managers.false_dir,
                timeformat=config.saving_managers.timeformat,
                detection_threshold=config.model.detection_threshold,
                saving_threshold=config.saving_managers.bat_threshold,
            )
        ]

    def get_message_factories(self, config) -> list[types.MessageBuilder]:
        """Get the message factories for the BatDetect2 Program.

        Parameters
        ----------
        config : BatDetect2_ConfigSchema
            The configuration schema for the _acoupi_batdetect2_ program defined in
            the configuration.py file and configured by a user via the CLI.

        Returns
        -------
        list[types.MessageBuilder]
            A list of message factories for the batdetect2 program. By default,
            the message factory will use the `detection_threshold` parameter for
            buildling messages.
        """
        return [
            components.DetectionThresholdMessageBuilder(
                detection_threshold=config.model.detection_threshold
            )
        ]

    def get_recording_filters(
        self, config
    ) -> list[types.RecordingSavingFilter]:
        """Get the recording filters for the BatDetect2 Program.

        Parameters
        ----------
        config : BatDetect2_ConfigSchema
            The configuration schema for the _acoupi_batdetect2_ program defined in
            the configuration.py file and configured by a user via the CLI.

        Returns
        -------
        list[types.RecordingSavingFilter]
            A list of recording filters for the batdetect2 program. If no
            saving filters are defined, the method will not save any recordings.
        """
        if not config.saving_filters:
            # No saving filters defined
            return []

        saving_filters = []
        timezone = pytz.timezone(config.timezone)
        recording_saving = config.saving_filters

        # Main filter
        # Will only save recordings if the recording time is in the
        # interval defined by the start and end time.
        if (
            recording_saving is not None
            and recording_saving.starttime is not None
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
            recording_saving is not None
            and recording_saving.frequency_duration != 0
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

        if (
            recording_saving is not None
            and recording_saving.before_dawndusk_duration != 0
        ):
            # This filter will only save recordings if the recording time
            # is before dawn or dusk.
            saving_filters.append(
                components.Before_DawnDuskTimeInterval(
                    duration=recording_saving.before_dawndusk_duration,
                    timezone=timezone,
                )
            )

        if (
            recording_saving is not None
            and recording_saving.after_dawndusk_duration != 0
        ):
            # This filter will only save recordings if the recording time
            # is after dawn or dusk.
            saving_filters.append(
                components.After_DawnDuskTimeInterval(
                    duration=recording_saving.after_dawndusk_duration,
                    timezone=timezone,
                )
            )

        if recording_saving is not None and recording_saving.saving_threshold:
            # This filter will only save recordings if the recording has
            # detections above the saving threshold.
            saving_filters.append(
                components.SavingThreshold(recording_saving.saving_threshold)
            )

        return saving_filters
