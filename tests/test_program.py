from acoupi import components, data

from acoupi_batdetect2.configuration import (
    BatDetect2_ConfigSchema,
)
from acoupi_batdetect2.program import BatDetect2_Program


def test_can_run_detection_program(
    recording: data.Recording,
    program: BatDetect2_Program,
    program_config: BatDetect2_ConfigSchema,
):
    """Test can run detection program."""
    store = components.SqliteStore(program_config.paths.db_metadata)

    # Store test recording in the database to test the program.
    store.store_recording(recording)

    # Check that the program has a detection task.
    assert "detection_task" in program.tasks

    # Run the detection task on the test recording.
    model_output = program.tasks["detection_task"].delay(recording)
    model_output.get()

    # Retrieve the recording from the database.
    recordings, model_outputs = zip(
        *store.get_recordings(
            ids=[recording.id],
        )
    )

    # Check that the recording was stored in the database.
    assert len(recordings) == 1
    assert len(model_outputs) == 1
    assert recordings[0] == recording

    # Check that the detections were stored in the database.
    detections = model_outputs[0][0]
    assert isinstance(detections, data.ModelOutput)
    assert len(detections.detections) > 0

    # Check that messages were stored in the database.
    messages = program.message_store.get_unsent_messages()
    assert len(messages) > 0
