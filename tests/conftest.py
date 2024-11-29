"""Common testing fixtures."""

import datetime
from pathlib import Path

import pytest
from acoupi import data
from acoupi.components import HTTPConfig, MicrophoneConfig
from acoupi.programs.templates import (
    MessagingConfig,
    PathsConfiguration,
)
from acoupi.system.constants import CeleryConfig
from celery import Celery
from celery.worker import WorkController

from acoupi_batdetect2.configuration import (
    BatDetect2_AudioConfig,
    BatDetect2_ConfigSchema,
)
from acoupi_batdetect2.program import BatDetect2_Program

pytest_plugins = ("celery.contrib.pytest",)

TESTS_DIR = Path(__file__).parent
TEST_RECORDING = TESTS_DIR / "data" / "audiofile_test1_myomys.wav"
TEST_RECORDING_NOBAT = TESTS_DIR / "data" / "audiofile_test3_nobats.wav"


@pytest.fixture(autouse=True)
def setup_logging(caplog):
    caplog.set_level("WARNING", logger="numba")
    caplog.set_level("INFO", logger="celery")
    caplog.set_level("WARNING", logger="amqp")


@pytest.fixture
def recording() -> data.Recording:
    return data.Recording(
        path=TEST_RECORDING,
        duration=3,
        samplerate=192000,
        created_on=datetime.datetime.now(),
        deployment=data.Deployment(
            name="test",
        ),
    )


@pytest.fixture
def notbat_recording() -> data.Recording:
    return data.Recording(
        path=TEST_RECORDING_NOBAT,
        duration=3,
        samplerate=192000,
        created_on=datetime.datetime.now(),
        deployment=data.Deployment(
            name="test_nobats",
        ),
    )


@pytest.fixture
def paths_config(tmp_path: Path) -> PathsConfiguration:
    tmp_audio = tmp_path / "tmp"
    recordings = tmp_path / "audio"
    tmp_audio.mkdir(parents=True, exist_ok=True)
    recordings.mkdir(parents=True, exist_ok=True)
    return PathsConfiguration(
        tmp_audio=tmp_path / "tmp",
        recordings=tmp_path / "audio",
        db_metadata=tmp_path / "metadata.db",
    )


@pytest.fixture
def audio_config() -> BatDetect2_AudioConfig:
    return BatDetect2_AudioConfig(duration=1, interval=2)


@pytest.fixture
def microphone_config() -> MicrophoneConfig:
    return MicrophoneConfig(
        samplerate=44100,
        audio_channels=1,
        device_name="default",
    )


@pytest.fixture
def messaging_config(tmp_path: Path) -> MessagingConfig:
    return MessagingConfig(
        messages_db=tmp_path / "messages.db",
        http=HTTPConfig(
            base_url="http://localhost:8000",
        ),
    )


@pytest.fixture
def program_config(
    messaging_config: MessagingConfig,
    paths_config: PathsConfiguration,
    audio_config: BatDetect2_AudioConfig,
    microphone_config: MicrophoneConfig,
) -> BatDetect2_ConfigSchema:
    return BatDetect2_ConfigSchema(
        paths=paths_config,
        messaging=messaging_config,
        recording=audio_config,
        microphone=microphone_config,
        saving_filters=None,
    )


@pytest.fixture(scope="session")
def celery_config():
    return CeleryConfig().model_dump()


@pytest.fixture
def program(
    program_config: BatDetect2_ConfigSchema,
    celery_app: Celery,
    celery_worker: WorkController,
) -> BatDetect2_Program:
    program = BatDetect2_Program(
        program_config=program_config,
        app=celery_app,
    )
    program.logger.setLevel("DEBUG")
    assert celery_app.conf["accept_content"] == ["pickle"]
    celery_worker.reload()
    return program
