import datetime

from acoupi_batdetect2.configuration import (
    BatDetect2_ConfigSchema,
)


def test_audio_config_defaults_have_been_overwriten(
    microphone_config,
    messaging_config,
):
    config = BatDetect2_ConfigSchema(
        microphone=microphone_config,
        messaging=messaging_config,
    )

    assert config.recording.schedule_start == datetime.time(hour=19)
    assert config.recording.schedule_end == datetime.time(hour=7)
