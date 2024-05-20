"""Common testing fixtures."""

import datetime
from pathlib import Path

import pyaudio
import pytest
from acoupi import components, data
from acoupi.devices.audio import get_input_devices
from acoupi.system.configs import CeleryConfig
from celery import Celery
from celery.worker import WorkController

from acoupi_batdetect2.configuration import (
    AudioDirectories,
    BatDetect2_ConfigSchema,
    SaveRecordingFilter,
)
from acoupi_batdetect2.program import BatDetect2_Program

pytest_plugins = ("celery.contrib.pytest",)

TEST_RECORDING: Path = (
    Path(__file__).parent / "data" / "audiofile_test1_myomys.wav"
)
TEST_RECORDING_NOBAT: Path = (
    Path(__file__).parent / "data" / "audiofile_test3_nobats.wav"
)


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
        datetime=datetime.datetime.now(),
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
        datetime=datetime.datetime.now(),
        deployment=data.Deployment(
            name="test_nobats",
        ),
    )


@pytest.fixture
def microphone_config() -> components.MicrophoneConfig:
    p = pyaudio.PyAudio()
    devices = get_input_devices(p)

    p.terminate()
    assert len(devices) > 0

    device = devices[0]
    return components.MicrophoneConfig(
        device_name=device.name,
        samplerate=int(device.default_samplerate),
        audio_channels=device.max_input_channels,
    )


@pytest.fixture
def program_config(
    tmp_path: Path,
    microphone_config: components.MicrophoneConfig,
) -> BatDetect2_ConfigSchema:
    audio_temp_path = tmp_path / "temp_audio"
    audio_temp_path.mkdir(exist_ok=True, parents=True)
    return BatDetect2_ConfigSchema(
        tmp_path=audio_temp_path,
        dbpath=tmp_path / "test.db",
        dbpath_messages=tmp_path / "test_messages.db",
        microphone_config=microphone_config,
        audio_directories=AudioDirectories(
            audio_dir=tmp_path / "audio",
            audio_dir_true=tmp_path / "audio_true",
            audio_dir_false=tmp_path / "audio_false",
        ),
        recording_saving=SaveRecordingFilter(
            saving_threshold=None,
        ),
    )


@pytest.fixture(scope="session")
def celery_config():
    return CeleryConfig().model_dump()


@pytest.fixture
def program(
    program_config: BatDetect2_ConfigSchema,
    celery_app: Celery,
    celery_config: dict,
    celery_worker: WorkController,
) -> BatDetect2_Program:
    program = BatDetect2_Program(
        program_config=program_config,
        celery_config=CeleryConfig.model_validate(celery_config),
        app=celery_app,
    )
    program.logger.setLevel("DEBUG")
    assert celery_app.conf["accept_content"] == ["pickle"]
    celery_worker.reload()
    return program
