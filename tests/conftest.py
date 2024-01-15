"""Common testing fixtures."""

import datetime
from pathlib import Path

import pytest
from acoupi import data

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
