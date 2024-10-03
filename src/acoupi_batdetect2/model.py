"""Acoupi detection and classification Models."""

from acoupi import data
from acoupi.components import types
from batdetect2 import api


class BatDetect2(types.Model):
    """BatDetect2 Model to analyse the audio recording."""

    name: str = "BatDetect2"

    def run(self, recording: data.Recording) -> data.ModelOutput:
        """Run the model on the recording."""
        # Get the audio path of the recorded file
        audio_file_path = recording.path

        if not audio_file_path:
            return data.ModelOutput(
                name_model="BatDetect2",
                recording=recording,
            )

        # Load the audio file and compute spectrograms
        audio = api.load_audio(str(audio_file_path))
        spec = api.generate_spectrogram(audio)

        # Process the audio or the spectrogram with the model
        raw_detections, _ = api.process_spectrogram(spec)

        # Convert the raw detections to a list of detections
        detections = [
            data.Detection(
                detection_score=detection["det_prob"],
                location=data.BoundingBox.from_coordinates(
                    detection["start_time"],
                    detection["low_freq"],
                    detection["end_time"],
                    detection["high_freq"],
                ),
                tags=[
                    data.PredictedTag(
                        tag=data.Tag(
                            key="species",
                            value=detection["class"],
                        ),
                        confidence_score=detection["class_prob"],
                    ),
                ],
            )
            for detection in raw_detections
        ]

        return data.ModelOutput(
            name_model="BatDetect2",
            recording=recording,
            detections=detections,
        )
