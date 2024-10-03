"""Batdetect2 Program Configuration Options."""

import datetime
from typing import Optional

from acoupi.programs.templates import DetectionProgramConfiguration
from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """Model output configuration."""

    detection_threshold: float = 0.4


class SavingFiltersConfig(BaseModel):
    """Saving Filters for audio recordings configuration."""

    starttime: datetime.time = datetime.time(hour=20, minute=0, second=0)

    endtime: datetime.time = datetime.time(hour=6, minute=0, second=0)

    before_dawndusk_duration: Optional[int] = 0

    after_dawndusk_duration: Optional[int] = 0

    frequency_duration: Optional[int] = 0

    frequency_interval: Optional[int] = 0


class SavingConfig(BaseModel):
    """Saving configuration for audio recordings (path to storage, name of files, saving threshold)."""

    true_dir: str = "bats"

    false_dir: str = "no_bats"

    timeformat: str = "%Y%m%d_%H%M%S"

    saving_threshold: float = 0.2

    saving_filters: Optional[SavingFiltersConfig] = Field(
        default_factory=SavingFiltersConfig,
    )


class Summariser(BaseModel):
    """Summariser configuration."""

    interval: Optional[float] = 60  # interval in minutes

    low_band_threshold: Optional[float] = 0.0

    mid_band_threshold: Optional[float] = 0.0

    high_band_threshold: Optional[float] = 0.0


class BatDetect2_ConfigSchema(DetectionProgramConfiguration):
    """Configuration for the batdetct2 program."""

    model: ModelConfig = Field(
        default_factory=ModelConfig,
    )

    saving: SavingConfig = Field(default_factory=SavingConfig)

    summariser_config: Optional[Summariser] = Field(
        default_factory=Summariser,
    )
