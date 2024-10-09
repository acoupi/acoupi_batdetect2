"""Batdetect2 Program Configuration Options."""

import datetime
from typing import Optional

from acoupi.programs.templates import (
    AudioConfiguration,
    DetectionProgramConfiguration,
)
from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """Model output configuration."""

    detection_threshold: float = 0.4


class SavingFiltersConfig(BaseModel):
    """Saving Filters for audio recordings configuration."""

    starttime: datetime.time = datetime.time(hour=19, minute=0, second=0)

    endtime: datetime.time = datetime.time(hour=7, minute=0, second=0)

    before_dawndusk_duration: int = 0

    after_dawndusk_duration: int = 0

    frequency_duration: int = 0

    frequency_interval: int = 0


class SavingConfig(BaseModel):
    """Saving configuration for audio recordings.

    (path to storage, name of files, saving threshold).
    """

    true_dir: str = "bats"

    false_dir: str = "no_bats"

    timeformat: str = "%Y%m%d_%H%M%S"

    saving_threshold: float = 0.2

    filters: Optional[SavingFiltersConfig] = Field(
        default_factory=SavingFiltersConfig,
    )


class Summariser(BaseModel):
    """Summariser configuration."""

    interval: Optional[float] = 3600  # interval in seconds

    low_band_threshold: Optional[float] = 0.0

    mid_band_threshold: Optional[float] = 0.0

    high_band_threshold: Optional[float] = 0.0


class BatDetect2_AudioConfig(AudioConfiguration):
    schedule_start: datetime.time = Field(
        default=datetime.time(hour=21, minute=0, second=0),
    )

    schedule_end: datetime.time = Field(
        default=datetime.time(hour=23, minute=0, second=0),
    )


class BatDetect2_ConfigSchema(DetectionProgramConfiguration):
    """Configuration for the batdetct2 program."""

    recording: BatDetect2_AudioConfig = Field(  # type: ignore
        default_factory=BatDetect2_AudioConfig,
    )

    model: ModelConfig = Field(
        default_factory=ModelConfig,
    )

    recording_saving: SavingConfig = Field(default_factory=SavingConfig)

    summariser_config: Optional[Summariser] = Field(
        default_factory=Summariser,
    )
