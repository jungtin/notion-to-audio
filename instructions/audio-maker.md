# Audio Generator Script Creation

## Task Description
Create a script that reads transcript files from the transcript folder and converts them to audio using a text-to-speech model. The audio files should be saved to a local folder.

## Requirements
1. Read all transcript files from the transcript directory
2. Use the [Kokoro-82M text-to-speech model](https://huggingface.co/hexgrad/Kokoro-82M) from Hugging Face
3. Generate audio files from each transcript 
4. Save the generated audio files to a designated output folder

## Implementation Notes
- Use appropriate error handling for file operations
- Consider adding command line arguments for input/output directories
- Ensure proper audio format and quality settings