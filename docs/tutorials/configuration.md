# Configuration

#### Configuration Parameters

| __Model (Optional)__| | | Configuration related to running a model. | Will require an acoupi program to integrate the detection task. |
| `model.detection_threshold` | float | 0.4 | The detection threshold is used to determine if a model detect a species call with confidence. | A float value between 0 and 1. Each model will have a different threshold that can be used to determine if a species call is detected with high or low confidence score. |
| __Saving (Optional)__| | | Configuration to store recordings when a model is used. | Additional parameters for saving recording after they have been processed by a model. |
| `saving.true_dir` | str | "storages/confident_recordings" | Path to the directory storing recorded audio files that held __confident__ detections (i.e., detections that are greater or equal than the `detection_treshold` parameter) after processing. | |
| `saving.fasle_dir` | str | "storages/nonconfident_recordings" | Path to the directory storing recorded audio files that held __non-confident__ detections (i.e., detections that are smaller than the `detection_treshold` parameter) after processing. | |
| `saving.timeformat` | str | "%Y%m%d_%H%M%S" | The saving.timeformat defines how to name the recording audio file. The default value capture the date and time of when the recording stated.  | A recording with name 20241004_183040.wav means that the recording file started on 4th October 2024 at 18:30:40. |
| `saving.saving_threshold` | float | 0.2 | The saving threshold is used to determine which files to save. It allows to save files that have been classified as having _non-confident_ detections by a model. | A float value between 0 and 1. |
| __Summariser (Optional)__| | | Configuration to store recordings when a model is used. | Additional parameters for saving recording after they have been processed by a model. |
| `saving.true_dir` | str | "storages/confident_recordings" | Path to the directory storing recorded audio files that held __confident__ detections (i.e., detections that are greater or equal than the `detection_treshold` parameter) after processing. | |
| `saving.fasle_dir` | str | "storages/nonconfident_recordings" | Path to the directory storing recorded audio files that held __non-confident__ detections (i.e., detections that are smaller than the `detection_treshold` parameter) after processing. | |
| `saving.timeformat` | str | "%Y%m%d_%H%M%S" | The saving.timeformat defines how to name the recording audio file. The default value capture the date and time of when the recording stated.  | A recording with name 20241004_183040.wav means that the recording file started on 4th October 2024 at 18:30:40. |
| `saving.saving_threshold` | float | 0.2 | The saving threshold is used to determine which files to save. It allows to save files that have been classified as having _non-confident_ detections by a model. | A float value between 0 and 1. |