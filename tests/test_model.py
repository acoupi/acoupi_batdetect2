"""Test Suite for Acoupi BatDetect2 Model."""
import datetime
from pathlib import Path

from acoupi import data

from acoupi_batdetect2.model import BatDetect2

TEST_RECORDING = Path(__file__).parent / "data" / "audiofile_test1_myomys.wav"


def test_batdetect2():
    recording = data.Recording(
        path=TEST_RECORDING,
        duration=3,
        samplerate=192000,
        datetime=datetime.datetime.now(),
        deployment=data.Deployment(
            name="test",
        ),
    )

    model = BatDetect2()
    detections = model.run(recording)

    assert isinstance(detections, data.ModelOutput)
    assert detections.name_model == "BatDetect2"
    assert len(detections.detections) == 51
