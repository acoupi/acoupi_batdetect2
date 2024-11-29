"""Batdetect2 Program Configuration Options."""

import datetime
from typing import Optional

from acoupi.programs.templates import (
    AudioConfiguration,
    DetectionProgramConfiguration,
)
from pydantic import BaseModel, Field


class BatDetect2_AudioConfig(AudioConfiguration):
    """Audio Configuration schema."""

    schedule_start: datetime.time = Field(
        default=datetime.time(hour=19, minute=0, second=0),
    )
    """Start time for recording schedule."""

    schedule_end: datetime.time = Field(
        default=datetime.time(hour=7, minute=0, second=0),
    )
    """End time for recording schedule."""


class ModelConfig(BaseModel):
    """Model output configuration."""

    detection_threshold: float = 0.4
    """Detection threshold for filtering model outputs."""


class SaveRecordingFilter(BaseModel):
    """Saving Filters for audio recordings configuration."""

    starttime: datetime.time = datetime.time(hour=19, minute=0, second=0)
    """Start time of the interval for which to save recordings."""

    endtime: datetime.time = datetime.time(hour=7, minute=0, second=0)
    """End time of the interval for which to save recordings."""

    before_dawndusk_duration: int = 0
    """Optional duration in minutes before dawn/dusk to save recordings."""

    after_dawndusk_duration: int = 0
    """Optional duration in minutes after dawn/dusk to save recordings."""

    frequency_duration: int = 0
    """Optional duration in minutes to save recordings using the frequency filter."""

    frequency_interval: int = 0
    """Optional periodic interval in minutes to save recordings."""

    saving_threshold: float = 0.3
    """Minimum threshold of detections from a recording to save it."""


class SaveRecordingManager(BaseModel):
    """Saving configuration for audio recordings.

    (path to storage, name of files, saving threshold).
    """

    true_dir: str = "bats"
    """Directory for saving recordings with confident detections."""

    false_dir: str = "no_bats"
    """Directory for saving recordings with uncertain detections."""

    timeformat: str = "%Y%m%d_%H%M%S"
    """Time format for naming the audio recording files."""

    bat_threshold: float = 0.5
    """Minimum threshold of detections from a recording to save it."""


class Summariser(BaseModel):
    """Summariser configuration."""

    interval: Optional[float] = 3600  # interval in seconds
    """Interval (in seconds) for summarising detections."""

    low_band_threshold: Optional[float] = 0.0
    """Optional low band threshold to summarise detections."""

    mid_band_threshold: Optional[float] = 0.0
    """Optional mid band threshold to summarise detections."""

    high_band_threshold: Optional[float] = 0.0
    """Optional high band threshold to summarise detections."""


class BatDetect2_ConfigSchema(DetectionProgramConfiguration):
    """BatDetect2 Program Configuration schema.

    This schema extends the _acoupi_ `DetectionProgramConfiguration` to
    include settings for the BatDetect2 program, such as custom audio recording,
    model setup, file management, messaging, and summarisation.
    """

    recording: BatDetect2_AudioConfig = Field(  # type: ignore
        default_factory=BatDetect2_AudioConfig,
    )
    """Audio recording configuration."""

    model: ModelConfig = Field(
        default_factory=ModelConfig,
    )
    """Model output configuration."""

    saving_filters: Optional[SaveRecordingFilter] = Field(
        default_factory=SaveRecordingFilter,
    )
    """Recording Saving Filters configuration for audio recordings."""

    saving_managers: SaveRecordingManager = Field(
        default_factory=SaveRecordingManager,
    )
    """Recording Saving Managers configuration for audio recordings."""

    summariser_config: Optional[Summariser] = Field(
        default_factory=Summariser,
    )
    """Summariser configuration."""
