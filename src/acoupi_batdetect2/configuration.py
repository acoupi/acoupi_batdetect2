"""Batdetect2 Program Configuration Options."""
import datetime
from pathlib import Path
from typing import Optional

from acoupi.system.constants import ACOUPI_HOME
from pydantic import BaseModel, Field

"""Default paramaters for Batdetect2 Program"""


class AudioConfig(BaseModel):
    """Audio and microphone configuration parameters."""

    audio_duration: int = 3

    samplerate: int = 250_000

    audio_channels: int = 1

    chunksize: int = 8192

    device_index: int = 1

    recording_interval: int = 10


class RecordingSchedule(BaseModel):
    """Recording schedule config."""

    start_recording: datetime.time = datetime.time(hour=10, minute=0, second=0)

    end_recording: datetime.time = datetime.time(hour=20, minute=0, second=0)


# class RecordingSaving(BaseModel):
class SaveRecordingFilter(BaseModel):
    """Recording saving options configuration."""

    starttime: datetime.time = datetime.time(hour=9, minute=30, second=0)

    endtime: datetime.time = datetime.time(hour=20, minute=30, second=0)

    before_dawndusk_duration: int = 0

    after_dawndusk_duration: int = 0

    frequency_duration: Optional[int] = None

    frequency_interval: Optional[int] = None

    saving_threshold: float = 0.8


class AudioDirectories(BaseModel):
    """Audio Recording Directories configuration."""

    audio_dir_true: Path = ACOUPI_HOME / "storages" / "recordings" / "bats"

    audio_dir_false: Path = ACOUPI_HOME / "storages" / "recordings" / "no_bats"


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


class BatDetect2_ConfigSchema(BaseModel):
    """BatDetect2 Configuration Schematic."""

    name: str = "batdetect2"

    detection_threshold: float = 0.2

    dbpath: Path = ACOUPI_HOME / "storages" / "acoupi.db"

    dbpath_messages: Path = ACOUPI_HOME / "storages" / "acoupi_messages.db"

    timeformat: str = "%Y%m%d_%H%M%S"

    timezone: str = "Europe/London"

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