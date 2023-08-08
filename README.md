# The AST wrapper module for the Elevenlabs API

A module wrapper for the Elevenlabs API. I need a to generate large texts and to be able to regenrate them without costing tokens for parts and paragraphs which stay the same. So this generates per paragraph then combines them all and spits out an .mp3 file.

## How it works rundown

1. **Find Existing Audio in History**: Check and retrieve previously generated audio from the API's history.

2. **Generate using your own custom voices** Along side the API key provide a custom/default voice id.

3. **Generate Remaining Audio from Text**: Convert text paragraphs into audio using your custom voice.

4. **Combine Audio Segments**: Combine separate audio segments into a single file.

5. **Save Audio Files**: Save generated audio files to a specified folder.

## Installation

See requirments.txt for full list of dependencies.

## Usage

### Initialization

```python
from tts_module import TTS

api_key = "your_api_key"
custom_voice_id = "your_custom_voice_id"
tts = TTS(api_key, custom_voice_id)
```

### Generate and Save Audio from Text

```python
text = "Your text here..."
folder_path_to_save = "./audio_files"
tts.generate_and_save_from_text(folder_path_to_save, text, custom_voice_id, text_name="example")
```

### Generate and Save Audio from File

```python
file_path_to_generate = "path/to/your/textfile.txt"
tts.generate_and_save_from_file(file_path_to_generate, custom_voice_id, text_name="example")
```

## Contributing

If I fucked up somewhere or for some resean you want to help that'd be lovely.
