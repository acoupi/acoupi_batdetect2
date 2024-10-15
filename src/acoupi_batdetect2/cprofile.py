import datetime

import pytz
from acoupi import components, data
from acoupi.components import types
from acoupi.programs.templates import (
    AudioConfiguration,
    cProfileProgram,
    cProfileProgram_Configuration,
)
from pydantic import BaseModel, Field

from acoupi_batdetect2.model import BatDetect2


## ---------- Step 1 - Components Configuration ---------- ##
## Define the configuration schema for the program, which
## include configuration for compoment setup and task creation.
## ------------------------------------------------------- ##
class AudioConfig(AudioConfiguration):
    """Audio recording configuration schema."""

    schedule_start: datetime.time = Field(
        default=datetime.time(hour=8, minute=0, second=0)
    )
    schedule_end: datetime.time = Field(
        default=datetime.time(hour=20, minute=0, second=0)
    )


class SaveRecordingFilter(BaseModel):
    """Recording saving options configuration."""

    starttime: datetime.time = datetime.time(hour=8, minute=0, second=0)
    endtime: datetime.time = datetime.time(hour=20, minute=0, second=0)
    before_dawndusk_duration: int = 0
    after_dawndusk_duration: int = 0
    frequency_duration: int = 0
    frequency_interval: int = 0


class SaveRecordingManager(BaseModel):
    """Configruation options to manage saving recordings."""

    true_dir: str = "true_detections"
    false_dir: str = "false_detections"
    timeformat: str = "%Y%m%d_%H%M%S"
    saving_threshold: float = 0.2


class ModelConfig(BaseModel):
    """Model configuration schema."""

    detection_threshold: float = 0.3


class BatDetect2_ConfigSchema(cProfileProgram_Configuration):

    recording: AudioConfig = Field(  # type: ignore
        default_factory=AudioConfig,
    )
    model: ModelConfig = Field(
        default_factory=ModelConfig,
    )
    saving_filters: SaveRecordingFilter = Field(
        default_factory=SaveRecordingFilter,
    )
    saving_managers: SaveRecordingManager = Field(
        default_factory=SaveRecordingManager,
    )


class BatDetect2_Program(cProfileProgram[BatDetect2_ConfigSchema]):

    config_schema = BatDetect2_ConfigSchema

    def setup(self, config):
        super().setup(config)

    def configure_model(self, config):
        return BatDetect2()

    def get_message_factories(self, config) -> list[types.MessageBuilder]:
        return [
            components.DetectionThresholdMessageBuilder(
                detection_threshold=config.model.detection_threshold
            )
        ]

    def get_recording_saving_filters(self, config) -> list[types.RecordingSavingFilter]:
        if not config.saving_filters:
            # No saving filters defined
            return []

        saving_filters = []
        timezone = pytz.timezone(config.timezone)
        recording_saving_filters = config.saving_filters

        # Main filter
        # Will only save recordings if the recording time is in the
        # interval defined by the start and end time.
        if (
            recording_saving_filters.starttime is not None
            and recording_saving_filters.endtime is not None
        ):
            saving_filters.append(
                components.SaveIfInInterval(
                    interval=data.TimeInterval(
                        start=recording_saving_filters.starttime,
                        end=recording_saving_filters.endtime,
                    ),
                    timezone=timezone,
                )
            )

        # Additional filters
        if (
            recording_saving_filters.frequency_duration != 0
            and recording_saving_filters.frequency_interval != 0
        ):
            # This filter will only save recordings at a frequency defined
            # by the duration and interval.
            saving_filters.append(
                components.FrequencySchedule(
                    duration=recording_saving_filters.frequency_duration,
                    frequency=recording_saving_filters.frequency_interval,
                )
            )

        if recording_saving_filters.before_dawndusk_duration != 0:
            # This filter will only save recordings if the recording time
            # is before dawn or dusk.
            saving_filters.append(
                components.Before_DawnDuskTimeInterval(
                    duration=recording_saving_filters.before_dawndusk_duration,
                    timezone=timezone,
                )
            )

        if recording_saving_filters.after_dawndusk_duration != 0:
            # This filter will only save recordings if the recording time
            # is after dawn or dusk.
            saving_filters.append(
                components.After_DawnDuskTimeInterval(
                    duration=recording_saving_filters.after_dawndusk_duration,
                    timezone=timezone,
                )
            )

        return saving_filters

    def get_recording_saving_managers(self, config):
        if not config.saving_managers:
            return []
        return [
            components.SaveRecordingManager(
                dirpath=config.paths.recordings,
                dirpath_true=config.paths.recordings / config.saving_managers.true_dir,
                dirpath_false=config.paths.recordings
                / config.saving_managers.false_dir,
                timeformat=config.saving_managers.timeformat,
                detection_threshold=config.model.detection_threshold,
                saving_threshold=config.saving_managers.saving_threshold,
            )
        ]
