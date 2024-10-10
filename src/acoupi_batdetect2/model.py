"""Acoupi detection and classification Models."""

from acoupi import data
from acoupi.components import types


class BatDetect2(types.Model):
    """BatDetect2 Model to analyse the audio recording.

    This model uses the BatDetect2 library to detect bat calls in audio
    recordings and classify them into one of the 18 UK bat species.

    Attributes
    ----------
    name : str
        The name of the model, by default "BatDetect2".
    """

    name: str = "BatDetect2"

    def __init__(self):
        """Initialise the BatDetect2 model."""
        from batdetect2 import api

        self.api = api

    def run(self, recording: data.Recording) -> data.ModelOutput:
        """Run the model on the recording.

        Parameters
        ----------
        recording : data.Recording
            The audio recording to process.

        Returns
        -------
        data.ModelOutput
            The model output containing the detections.
        """
        # Get the audio path of the recorded file
        audio_file_path = recording.path

        if not audio_file_path:
            return data.ModelOutput(
                name_model="BatDetect2",
                recording=recording,
            )

        # Load the audio file and compute spectrograms
        audio = self.api.load_audio(str(audio_file_path))
        spec = self.api.generate_spectrogram(audio)

        # Process the audio or the spectrogram with the model
        raw_detections, _ = self.api.process_spectrogram(spec)

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
