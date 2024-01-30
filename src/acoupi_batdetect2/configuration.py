"""Batdetect2 Program Configuration Options."""
import datetime
from pathlib import Path
from typing import Optional

from acoupi.components.audio_recorder import MicrophoneConfig
from pydantic import BaseModel, Field, model_validator

"""Default paramaters for Batdetect2 Program"""


class AudioConfig(BaseModel):
    """Audio recording configuration parameters."""

    audio_duration: int = 3
    """Duration of each audio recording in seconds."""

    recording_interval: int = 10
    """Interval between each audio recording in seconds."""

    chunksize: int = 8192

    # @model_validator(mode="after")
    # def validate_audio_duration(cls, value):
    #     """Validate audio duration."""
    #
    #     if value.audio_duration > value.recording_interval:
    #         raise ValueError(
    #             "Audio duration cannot be greater than recording interval."
    #         )
    #
    #     return value


class RecordingSchedule(BaseModel):
    """Recording schedule config."""

    start_recording: datetime.time = datetime.time(hour=5, minute=30, second=0)

    end_recording: datetime.time = datetime.time(hour=20, minute=0, second=0)


class SaveRecordingFilter(BaseModel):
    """Recording saving options configuration."""

    starttime: datetime.time = datetime.time(hour=9, minute=30, second=0)

    endtime: datetime.time = datetime.time(hour=20, minute=30, second=0)

    before_dawndusk_duration: Optional[int] = 0

    after_dawndusk_duration: Optional[int] = 0

    frequency_duration: Optional[int] = 0

    frequency_interval: Optional[int] = 0

    saving_threshold: float = 0.4


class AudioDirectories(BaseModel):
    """Audio Recording Directories configuration."""

    audio_dir: Path = Path.home() / "storages" / "recordings"

    audio_dir_true: Path = Path.home() / "storages" / "recordings" / "bats"

    audio_dir_false: Path = Path.home() / "storages" / "recordings" / "no_bats"


class MQTT_MessageConfig(BaseModel):
    """MQTT configuration to send messages."""

    host: str = "localhost"

    port: int = 1884

    client_password: str = "guest"

    client_username: str = "guest"

    topic: str = "mqtt-topic"

    clientid: str = "mqtt-clientid"


class HTTP_MessageConfig(BaseModel):
    """MQTT configuration to send messages."""

    deviceid: str = "device-id"

    baseurl: str = "base-url"

    client_password: str = "guest"

    client_id: str = "guest"

    api_key: str = "guest"

    content_type: str = "application-json"


# class CleanDetectionFilter(BaseModel):
#     """Detection cleaning options configuration."""
#
#     detection_threshold: float = 0.2

#     species_list: Optional[str] = None


class BatDetect2_ConfigSchema(BaseModel):
    """BatDetect2 Configuration Schematic."""

    name: str = "batdetect2"

    detection_threshold: float = 0.2

    dbpath: Path = Path.home() / "storages" / "acoupi.db"

    dbpath_messages: Path = Path.home() / "storages" / "acoupi_messages.db"

    timeformat: str = "%Y%m%d_%H%M%S"

    timezone: str = "Europe/London"

    microphone_config: MicrophoneConfig

    audio_config: AudioConfig = Field(
        default_factory=AudioConfig,
    )

    recording_schedule: RecordingSchedule = Field(
        default_factory=RecordingSchedule,
    )

    recording_saving: Optional[SaveRecordingFilter] = Field(
        default_factory=SaveRecordingFilter,
    )

    audio_directories: AudioDirectories = Field(
        default_factory=AudioDirectories,
    )

    mqtt_message_config: Optional[MQTT_MessageConfig] = Field(
        default_factory=MQTT_MessageConfig,
    )
    http_message_config: Optional[HTTP_MessageConfig] = Field(
        default_factory=HTTP_MessageConfig,
    )

    # clean_detection: Optional[CleanDetectionFilter] = Field(
    #     default_factory=CleanDetectionFilter,
    # )
