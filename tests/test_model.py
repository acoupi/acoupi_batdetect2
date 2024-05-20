"""Test Suite for Acoupi BatDetect2 Model."""

from acoupi import data

from acoupi_batdetect2.model import BatDetect2


def test_batdetect2(recording: data.Recording):
    model = BatDetect2()
    detections = model.run(recording)

    assert isinstance(detections, data.ModelOutput)
    assert detections.name_model == "BatDetect2"
    assert len(detections.detections) == 51
