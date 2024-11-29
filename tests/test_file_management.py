import datetime
import shutil
from typing import Generator

import pytest
from acoupi import data
from acoupi.system.files import get_temp_files

from acoupi_batdetect2.configuration import (
    BatDetect2_ConfigSchema,
)
from acoupi_batdetect2.program import BatDetect2_Program


@pytest.fixture
def temp_recording(
    program_config: BatDetect2_ConfigSchema,
    recording: data.Recording,
) -> Generator[data.Recording, None, None]:
    """Create a temporary recording."""
    assert recording.path is not None
    temp_recording_path = program_config.paths.tmp_audio / recording.path.name
    shutil.copyfile(recording.path, temp_recording_path)
    yield data.Recording(
        path=temp_recording_path,
        duration=3,
        samplerate=192000,
        created_on=datetime.datetime.now(),
        deployment=data.Deployment(
            name="test",
        ),
    )

    if temp_recording_path.exists():
        temp_recording_path.unlink()


@pytest.fixture
def nobat_temp_recording(
    program_config: BatDetect2_ConfigSchema,
    notbat_recording: data.Recording,
) -> Generator[data.Recording, None, None]:
    """Create a temporary recording."""
    assert notbat_recording.path is not None

    temp_recording_path_nobat = (
        program_config.paths.tmp_audio / notbat_recording.path.name
    )

    shutil.copyfile(notbat_recording.path, temp_recording_path_nobat)
    yield data.Recording(
        path=temp_recording_path_nobat,
        duration=3,
        samplerate=192000,
        created_on=datetime.datetime.now(),
        deployment=data.Deployment(
            name="test",
        ),
    )
    if temp_recording_path_nobat.exists():
        temp_recording_path_nobat.unlink()


def test_management_notempfiles(
    program_config: BatDetect2_ConfigSchema,
    program: BatDetect2_Program,
):
    assert len(get_temp_files(path=program_config.paths.tmp_audio)) == 0
    assert program_config.paths.recordings.exists()
    assert len(list(program_config.paths.recordings.glob("*.wav"))) == 0

    assert "file_management_task" in program.tasks

    output_file_task = program.tasks["file_management_task"].delay()
    output_file_task.get()


def test_management_tempfile_notindb(
    program_config: BatDetect2_ConfigSchema,
    program: BatDetect2_Program,
    temp_recording: data.Recording,
):
    """Test that a recording file exists in the temporary directory but not in the database."""
    assert len(get_temp_files(path=program_config.paths.tmp_audio)) != 0
    assert program_config.paths.recordings.exists()
    assert len(list(program_config.paths.recordings.glob("*.wav"))) == 0
    assert temp_recording.path is not None

    assert program.store.get_recordings_by_path([temp_recording.path]) == []

    assert "file_management_task" in program.tasks
    output_file_task = program.tasks["file_management_task"].delay()
    output_file_task.get()

    assert temp_recording.path is not None
    assert temp_recording.path.exists()


def test_management_tempfiles_notprocess(
    program_config: BatDetect2_ConfigSchema,
    program: BatDetect2_Program,
    temp_recording: data.Recording,
):
    assert len(get_temp_files(path=program_config.paths.tmp_audio)) != 0
    assert program_config.paths.recordings.exists()
    assert len(list(program_config.paths.recordings.glob("*.wav"))) == 0
    assert temp_recording.path is not None

    # Store test recording in the database to test the test.
    program.store.store_recording(temp_recording)

    # Check that the recording was stored in the database.
    assert program.store.get_recordings_by_path([temp_recording.path]) != []

    # Retrieve the recording from the database.
    results = program.store.get_recordings_by_path([temp_recording.path])

    # Check that the recording was stored in the database but no detection exists.
    assert len(results) == 1
    _, model_outputs = results[0]
    assert len(model_outputs) == 0

    assert "file_management_task" in program.tasks
    output_file_task = program.tasks["file_management_task"].delay()
    output_file_task.get()

    assert temp_recording.path is not None
    assert temp_recording.path.exists()


def test_management_tempfile_positive_detection(
    program_config: BatDetect2_ConfigSchema,
    program: BatDetect2_Program,
    temp_recording: data.Recording,
):
    audio_dir = program_config.paths.recordings
    true_dir = audio_dir / program_config.saving_managers.true_dir

    assert len(get_temp_files(path=program_config.paths.tmp_audio)) != 0
    assert audio_dir.exists()
    assert (audio_dir / program_config.saving_managers.true_dir).exists()
    assert len(list(audio_dir.glob("*.wav"))) == 0
    assert len(list(true_dir.glob("*.wav"))) == 0

    # Store test recording in the database to test the test.
    program.store.store_recording(temp_recording)

    # Run the detection task on the test recording.
    model_output = program.tasks["detection_task"].delay(temp_recording)
    model_output.get()

    print(model_output)

    # Check the recording is in the temporary folder before running the
    # file management task
    assert len(get_temp_files(path=program_config.paths.tmp_audio)) == 1

    # Run the file_management task on the test detection.
    output_file_task = program.tasks["file_management_task"].delay()
    output_file_task.get()

    # Check that the file was moved.
    assert len(get_temp_files(path=program_config.paths.tmp_audio)) == 0
    assert len(list(true_dir.glob("*.wav"))) != 0


def test_management_tempfile_negative_detection(
    program_config: BatDetect2_ConfigSchema,
    program: BatDetect2_Program,
    nobat_temp_recording: data.Recording,
):
    assert nobat_temp_recording.path is not None

    # Make sure there is a single file in the temporary audio folder but
    # the audio directories are empty.
    audio_dir = program_config.paths.recordings
    true_dir = audio_dir / program_config.saving_managers.true_dir
    false_dir = audio_dir / program_config.saving_managers.false_dir
    assert len(get_temp_files(path=program_config.paths.tmp_audio)) != 0
    assert audio_dir.exists()
    assert true_dir.exists()
    assert false_dir.exists()
    assert len(list(false_dir.glob("*.wav"))) == 0

    # Store test recording in the database to test the test.
    program.store.store_recording(nobat_temp_recording)

    # Check that the program has a detection and file_management task.
    assert "detection_task" in program.tasks
    assert "file_management_task" in program.tasks

    # Run the detection task on the test recording.
    model_output = program.tasks["detection_task"].delay(nobat_temp_recording)
    model_output.get()

    _, outputs = program.store.get_recordings_by_path(
        [nobat_temp_recording.path]
    )[0]

    assert len(outputs) == 1

    # Run the file_management task on the test detection.
    output_file_task = program.tasks["file_management_task"].delay()
    output_file_task.get()

    # Check that the file was moved.
    assert len(get_temp_files(path=program_config.paths.tmp_audio)) == 0
    assert len(list(false_dir.glob("*.wav"))) == 0
