from elevenlabs import set_api_key, History, voices, generate, HistoryItem
import time
from pydub import AudioSegment
import os
from io import BytesIO

import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TTS:
    def __init__(
        self,
        api_key: str,
        custom_voice_id: str,
    ) -> None:
        """_summary_

        Args:
            api_key (str): _description_
            custom_voice_id (str): _description_
        """
        self.api_key = api_key
        set_api_key(api_key)
        self.custom_voice_id = custom_voice_id
        self.paragraph_text_list = []

    def set_custom_voice_id(self, new_custom_voice_id: str) -> None:
        self.custom_voice_id = new_custom_voice_id

    def set_new_api_key(self, new_api_key):
        self.api_key = new_api_key
        set_api_key(new_api_key)

    def find_in_history(self, text, voice_id=None):
        """_summary_

        Args:
            text (_type_): _description_
            voice_id (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        logger.info("find_in_history(): Enter Function.")
        history = History.from_api()
        if not text:
            logger.info("find_in_history(): Text not in history")
            return None
        for item in history:
            if (
                text in item.text
                or item.text in text
                and (item.voice_id == voice_id or item.voice_id == None)
            ):
                return item
        logger.info("find_in_history(): Text not in history")
        return None

    def get_custom_voices_list(self) -> list[dict]:
        """_summary_

        Returns:
            list[dict]: _description_
        """
        logger.info(
            "get_custom_voices(): getting all custom voices from api and printing them"
        )
        custom_voices = []
        all_voices = voices()
        for voice in all_voices.voices:
            if voice.category == "cloned":
                custom_voices.append({voice.name, voice.voice_id})
        print(custom_voices)

    def set_paragraph_list_from_file(self, file_path: str) -> None:
        """_summary_

        Args:
            file_path (str): _description_
        """
        logger.info("set_paragraph_list_from_file(): enter function.")
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                self.paragraph_text_list = file.read().split("\n")

    def set_paragraphs_list_from_text(self, text: str) -> None:
        """_summary_

        Args:
            text (str): _description_
        """
        logger.info("set_paragraphs_list_from_text(): enter function.")
        self.paragraph_text_list = (
            text.split("\n") if text else self.paragraph_text_list
        )

    def does_generated_text_exist(self, text: str, voice_id: str):
        """_summary_

        Args:
            text (str): _description_
            voice_id (str): _description_

        Returns:
            _type_: _description_
        """
        logger.info("does_generated_text_exist(): enter function.")
        history_item = self.find_in_history(text)
        if not history_item:
            logger.info(
                "does_generated_text_exist(): returning false, history_item = None."
            )
            return False
        logger.info(
            f"does_generated_text_exist(): same text:{history_item.text == text}"
        )
        logger.info(
            f"does_generated_text_exist(): same voice_id: {history_item.voice_id == voice_id}"
        )

        return (
            history_item.text == text
            and history_item.voice_id == voice_id
            and text != ""
        )

    def generate_remaining_text(
        self,
        api_key,
        input_text,
        existing_text,
        voice_id=None,
        model="eleven_monolingual_v1",
    ):
        """_summary_

        Args:
            api_key (_type_): _description_
            input_text (_type_): _description_
            existing_text (_type_): _description_
            voice_id (_type_, optional): _description_. Defaults to None.
            model (str, optional): _description_. Defaults to "eleven_monolingual_v1".

        Returns:
            _type_: _description_
        """
        logger.info("generate_remaining_text(): enter function.")
        remaining_text = input_text.replace(existing_text, "").strip()
        if remaining_text:
            logger.info(f"Generating remaining text: {remaining_text}")
            audio = generate(
                text=remaining_text, api_key=api_key, voice=voice_id, model=model
            )
            return audio
        logger.info(
            "generate_remaining_text(): All text already generated no remaining text to generate"
        )
        return None

    def generate_paragraph_audio(self, text, voice_id, model="eleven_monolingual_v1"):
        """_summary_

        Args:
            text (_type_): _description_
            voice_id (_type_): _description_
            model (str, optional): _description_. Defaults to "eleven_monolingual_v1".

        Returns:
            _type_: _description_
        """
        logger.info("generate_paragraph_audio():enter function.")
        if voice_id == None:
            logger.info(
                "generate_paragraph_audio(): setting voice_id = self.custom_voice_id"
            )
            voice_id = self.custom_voice_id
        if not self.does_generated_text_exist(text, voice_id):
            logger.info(
                f"generate_paragraph_audio(): Generating new audio.\n Truncated text(first 30 chars): {text[:30]}..."
            )
            return generate(
                text=text, api_key=self.api_key, voice=voice_id, model=model
            )
        else:
            logger.info("generate_paragraph_audio(): Found existing audio in history.")

            return self.find_in_history(text, voice_id)

    def generate_paragraph_list_audio(
        self, paragraphs: list[str], voice_id: str, model="eleven_monolingual_v1"
    ) -> None:
        """_summary_

        Args:
            paragraphs (list[str]): _description_
            voice_id (str): _description_
            model (str, optional): _description_. Defaults to "eleven_monolingual_v1".
        """
        logger.info("generate_paragraph_list_audio(): enter function.")
        for paragraph in paragraphs:
            if paragraph:  # Checks if the paragraph is not empty
                self.generate_paragraph_audio(paragraph, voice_id, model)

    def save_item_audio_to_file(self, item: HistoryItem, folder_path: str) -> str:
        """_summary_

        Args:
            item (HistoryItem): _description_
            folder_path (str): _description_

        Returns:
            str: _description_
        """
        logger.info("save_item_audio_to_file(): enter function.")
        saved_file_path = os.path.join(
            folder_path, f"paragraph_{item.history_item_id}_time_{time.time()}.mp3"
        )
        logger.info(
            "save_item_audio_to_file():saving audio bytes for item at: {saved_file_path}"
        )
        if not os.path.exists(os.path.normpath(folder_path)):
            logger.info(
                "save_item_audio_to_file(): creating {os.path.normpath(folder_path)}"
            )
            os.makedirs(os.path.normpath(folder_path))
        with open(saved_file_path, "wb") as f:
            f.write(item.audio)
        return saved_file_path

    def save_and_combine_paragraph_list(
        self, paragraph_list: list[str], combined_audio_file_path: str, name=None
    ):
        """_summary_

        Args:
            paragraph_list (list[str]): _description_
            combined_audio_file_path (str): _description_
            name (_type_, optional): _description_. Defaults to None.
        """
        logger.info("save_and_combine_paragraph_list(): enter function.")
        combined = AudioSegment.empty()
        for paragraph in paragraph_list:
            logger.info("save_and_combine_paragraph_list(): finding item in history")
            existing_item = self.find_in_history(paragraph)
            if existing_item:
                logger.info(
                    "save_and_combine_paragraph_list():appending item to comined audio segment"
                )
                segment = AudioSegment.from_file(
                    BytesIO(existing_item.audio), format="mp3"
                )
                # segment = AudioSegment(BytesIO(existing_item.audio))
                combined += segment
            # Export the combined audio as an MP3 file

        logger.info(
            "save_and_combine_paragraph_list():exporting combined audio segement to file"
        )
        if not os.path.exists(os.path.normpath(combined_audio_file_path)):
            logger.info(
                f"save_and_combine_paragraph_list(): creating {os.path.normpath(combined_audio_file_path)}"
            )
            os.makedirs(os.path.normpath(combined_audio_file_path))
        combined.export(
            os.path.join(
                combined_audio_file_path, f"combined_{name}_time_{time.time()}.mp3"
            )
        )

    def generate_and_save_from_file(
        self,
        file_path_to_generate: str = None,
        voice_id: str = None,
        text_name: str = None,
        model: str = "eleven_monolingual_v1",
    ) -> None:
        """_summary_

        Args:
            file_path_to_generate (_type_, optional): _description_. Defaults to None.
            voice_id (_type_, optional): _description_. Defaults to None.
            text_name (_type_, optional): _description_. Defaults to None.
            model (str, optional): _description_. Defaults to "eleven_monolingual_v1".
        """
        logger.info(
            "generate_and_save_from_file(): save_and_combine_paragraph_list(): enter function."
        )
        self.set_paragraph_list_from_file(file_path_to_generate)
        paragraph_list = self.paragraph_text_list
        self.generate_paragraph_list_audio(paragraph_list, voice_id)
        audio_folder_path = ".//audio_files//"

        self.save_and_combine_paragraph_list(
            paragraph_list, audio_folder_path, name=text_name
        )
        logger.info("generate_and_save_from_file(): completed generating and saving")

    def generate_and_save_from_text(
        self,
        folder_path_to_save: str,
        text: str = None,
        voice_id: str = None,
        text_name: str = None,
        model: str = "eleven_monolingual_v1",
    ) -> None:
        """_summary_

        Args:
            folder_path_to_save (str): _description_
            text (str, optional): _description_. Defaults to None.
            voice_id (str, optional): _description_. Defaults to None.
            text_name (str, optional): _description_. Defaults to None.
            model (str, optional): _description_. Defaults to "eleven_monolingual_v1".
        """
        logger.info(
            "generate_and_save_from_text(): save_and_combine_paragraph_list(): enter function."
        )
        self.set_paragraph_list_from_text(text)
        paragraph_list = self.paragraph_text_list
        self.generate_paragraph_list_audio(paragraph_list, voice_id)
        audio_folder_path = folder_path_to_save

        self.save_and_combine_paragraph_list(
            paragraph_list, audio_folder_path, name=text_name
        )
        logger.info("generate_and_save_from_text(): completed generating and saving")


file_path = "text_samples/human_text.txt"


if __name__ == "__main__":
    tts_instance = TTS(api_key, custom_voice_id)
    tts_instance.generate_and_save_from_file(
        file_path_to_generate=file_path, text_name="human_text"
    )

    # change
    """from elevenlabs.api import Models
    models = Models.from_api()
    print(models[0])
    print(models)"""
