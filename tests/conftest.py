"""Common testing fixtures."""

import datetime
from pathlib import Path

import pytest
from acoupi import data
from acoupi.system.configs import CeleryConfig

TEST_RECORDING = Path(__file__).parent / "data" / "audiofile_test1_myomys.wav"


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


@pytest.fixture(scope="session")
def celery_config():
    return CeleryConfig().model_dump()


@pytest.fixture(autouse=True)
def setup_logging(caplog):
    caplog.set_level("WARNING", logger="numba")
    caplog.set_level("INFO", logger="celery")
    caplog.set_level("WARNING", logger="amqp")
