import pytest
from pathlib import Path
import datetime
import shutil

from acoupi import components, data

from acoupi.files import TEMP_PATH
from acoupi.system.configs import CeleryConfig
from celery import Celery
from celery.worker import WorkController

from acoupi.files import get_temp_files

from acoupi_batdetect2.configuration import (
    AudioDirectories,
    BatDetect2_ConfigSchema,
)
from acoupi_batdetect2.program import BatDetect2_Program

# TEMP_PATH = Path("Users/audevuilliomenet/Documents")


@pytest.fixture
def temp_recording(
    recording: data.Recording,
) -> data.Recording:
    """Create a temporary recording."""
    assert recording.path is not None
    temp_recording_path = TEMP_PATH / recording.path.name
    shutil.copy(recording.path, temp_recording_path)
    return data.Recording(
        path=temp_recording_path,
        duration=3,
        samplerate=192000,
        datetime=datetime.datetime.now(),
        deployment=data.Deployment(
            name="test",
        ),
    )


@pytest.fixture
def nobat_temp_recording(
    notbat_recording: data.Recording,
) -> data.Recording:
    """Create a temporary recording."""
    assert notbat_recording.path is not None
    temp_recording_path_nobat = TEMP_PATH / notbat_recording.path.name
    shutil.copy(notbat_recording.path, temp_recording_path_nobat)
    return data.Recording(
        path=temp_recording_path_nobat,
        duration=3,
        samplerate=192000,
        datetime=datetime.datetime.now(),
        deployment=data.Deployment(
            name="test",
        ),
    )


@pytest.fixture
def config(
    tmp_path: Path,
):
    config = BatDetect2_ConfigSchema(
        dbpath=tmp_path / "test.db",
        dbpath_messages=tmp_path / "test_messages.db",
        audio_directories=AudioDirectories(
            audio_dir=tmp_path / "audio",
            audio_dir_true=tmp_path / "audio_true",
            audio_dir_false=tmp_path / "audio_false",
        ),
    )

    return config


@pytest.fixture
def program(
    tmp_path: Path,
    config: BatDetect2_ConfigSchema,
    celery_app: Celery,
    celery_worker: WorkController,
):
    """Test can run detection program."""
    # Instantiate the BatDetect2 program.
    celery_config = CeleryConfig()
    program = BatDetect2_Program(
        program_config=config,
        celery_config=celery_config,
        app=celery_app,
    )
    program.logger.setLevel("DEBUG")
    assert celery_app.conf["accept_content"] == ["pickle"]
    celery_worker.reload()

    return program


def test_management_notempfiles(
    config: BatDetect2_ConfigSchema,
    program: BatDetect2_Program,
):
    assert len(get_temp_files()) == 0
    assert config.audio_directories.audio_dir.exists()
    assert len(list(config.audio_directories.audio_dir.glob("*.wav"))) == 0

    assert "file_management_task" in program.tasks

    output_file_task = program.tasks["file_management_task"].delay()
    output_file_task.get()


def test_management_tempfile_notindb(
    config: BatDetect2_ConfigSchema,
    program: BatDetect2_Program,
    temp_recording: data.Recording,
):
    """Test that a recording file exists in the temporary directory but not in the database."""
    assert len(get_temp_files()) != 0
    assert config.audio_directories.audio_dir.exists()
    assert len(list(config.audio_directories.audio_dir.glob("*.wav"))) == 0

    assert (
        program.store.get_recordings_temp_path(
            temp_paths=[str(temp_recording.path)]
        )
        == []
    )

    assert "file_management_task" in program.tasks
    output_file_task = program.tasks["file_management_task"].delay()
    output_file_task.get()

    assert temp_recording.path is not None
    assert temp_recording.path.exists()


def test_management_tempfiles_notprocess(
    config: BatDetect2_ConfigSchema,
    program: BatDetect2_Program,
    temp_recording: data.Recording,
):
    """Test that a recording file exists in the temporary directory
    and that the recording file is in the database but not processed."""
    assert len(get_temp_files()) != 0
    assert config.audio_directories.audio_dir.exists()
    assert len(list(config.audio_directories.audio_dir.glob("*.wav"))) == 0

    # Store test recording in the database to test the test.
    program.store.store_recording(temp_recording)

    # Check that the recording was stored in the database.
    assert (
        program.store.get_recordings_temp_path(
            temp_paths=[str(temp_recording.path)]
        )
        != []
    )

    # Retrieve the recording from the database.
    recordings = program.store.get_recordings_temp_path(
        temp_paths=[str(temp_recording.path)],
    )

    # Check that the recording was stored in the database but no detection exists.
    assert len(recordings) >= 1

    assert "file_management_task" in program.tasks
    output_file_task = program.tasks["file_management_task"].delay()
    output_file_task.get()

    assert temp_recording.path is not None
    assert temp_recording.path.exists()


def test_management_tempfile_positive_detection(
    config: BatDetect2_ConfigSchema,
    program: BatDetect2_Program,
    temp_recording: data.Recording,
    celery_app: Celery,
    celery_worker: WorkController,
):
    assert len(get_temp_files()) != 0
    assert config.audio_directories.audio_dir.exists()
    assert config.audio_directories.audio_dir_true.exists()
    assert len(list(config.audio_directories.audio_dir.glob("*.wav"))) == 0
    assert (
        len(list(config.audio_directories.audio_dir_true.glob("*.wav"))) == 0
    )

    # Store test recording in the database to test the test.
    program.store.store_recording(temp_recording)

    # Instantiate the BatDetect2 program.
    celery_config = CeleryConfig()
    program = BatDetect2_Program(
        program_config=config,
        celery_config=celery_config,
        app=celery_app,
    )

    # Check that the program has a detection and file_management task.
    assert "detection_task" in program.tasks
    assert "file_management_task" in program.tasks

    # Run the detection task on the test recording.
    model_output = program.tasks["detection_task"].delay(temp_recording)
    model_output.get()

    # Run the file_management task on the test detection.
    output_file_task = program.tasks["file_management_task"].delay()
    output_file_task.get()

    # Check that the file was moved.
    assert len(get_temp_files()) == 0
    assert (
        len(list(config.audio_directories.audio_dir_true.glob("*.wav"))) != 0
    )


def test_management_tempfile_negative_detection(
    config: BatDetect2_ConfigSchema,
    program: BatDetect2_Program,
    nobat_temp_recording: data.Recording,
    celery_app: Celery,
    celery_worker: WorkController,
):
    assert len(get_temp_files()) != 0
    assert config.audio_directories.audio_dir.exists()
    assert config.audio_directories.audio_dir_true.exists()
    assert config.audio_directories.audio_dir_false.exists()
    assert (
        len(list(config.audio_directories.audio_dir_false.glob("*.wav"))) == 0
    )

    # Store test recording in the database to test the test.
    program.store.store_recording(nobat_temp_recording)

    # Instantiate the BatDetect2 program.
    celery_config = CeleryConfig()
    program = BatDetect2_Program(
        program_config=config,
        celery_config=celery_config,
        app=celery_app,
    )

    # Check that the program has a detection and file_management task.
    assert "detection_task" in program.tasks
    assert "file_management_task" in program.tasks

    # Run the detection task on the test recording.
    model_output = program.tasks["detection_task"].delay(nobat_temp_recording)
    model_output.get()

    # Run the file_management task on the test detection.
    output_file_task = program.tasks["file_management_task"].delay()
    output_file_task.get()

    # Check that the file was moved.
    assert len(get_temp_files()) == 0
    assert (
        len(list(config.audio_directories.audio_dir_false.glob("*.wav"))) != 0
    )

    return
