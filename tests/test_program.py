from pathlib import Path

from acoupi import components, data
from acoupi.system.configs import CeleryConfig
from celery import Celery
from celery.worker import WorkController

from acoupi_batdetect2.configuration import (
    AudioDirectories,
    BatDetect2_ConfigSchema,
)
from acoupi_batdetect2.program import BatDetect2_Program


def test_can_run_detection_program(
    tmp_path: Path,
    recording: data.Recording,
    celery_app: Celery,
    celery_worker: WorkController,
):
    """Test can run detection program."""
    config = BatDetect2_ConfigSchema(
        dbpath=tmp_path / "test.db",
        dbpath_messages=tmp_path / "test_messages.db",
        audio_directories=AudioDirectories(
            audio_dir=tmp_path / "audio",
            audio_dir_true=tmp_path / "audio_true",
            audio_dir_false=tmp_path / "audio_false",
        ),
    )
    store = components.SqliteStore(config.dbpath)

    # Store test recording in the database to test the program.
    store.store_recording(recording)

    # Instantiate the BatDetect2 program.
    celery_config = CeleryConfig()
    program = BatDetect2_Program(
        program_config=config,
        celery_config=celery_config,
        app=celery_app,
    )
    assert celery_app.conf["accept_content"] == ["pickle"]
    celery_worker.reload()

    # Check that the program has a detection task.
    assert "detection_task" in program.tasks

    # Run the detection task on the test recording.
    program.tasks["detection_task"].delay(recording)

    # Retrieve the recording from the database.
    recordings, model_outputs = store.get_recordings(
        ids=[recording.id],
    )

    # Check that the recording was stored in the database.
    assert len(recordings) == 1
    assert len(model_outputs) == 1
    assert recordings[0] == recording

    # Check that the detections were stored in the database.
    detections = model_outputs[0]
    assert isinstance(detections, data.ModelOutput)

    # This test recording has 51 detections with the default BatDetect2
    assert len(detections.detections) == 51
