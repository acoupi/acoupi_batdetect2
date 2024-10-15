import datetime

from acoupi import components
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
