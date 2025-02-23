import logging
import base64


module_logger = logging.getLogger("TestDigitRecognitionService")


class TestDigitRecognitionService:
    # def test_recognize_image_from_base64(self):
    #     recognizer = DigitRecognitionService()
    #
    #     base64_images = [
    #         self._convert_file_to_base64(
    #             os.path.join(
    #                 os.path.join(os.path.dirname(__file__), "images"),
    #                 f"digit_{digit}.png",
    #             )
    #         )
    #         for digit in range(10)
    #     ]
    #
    #     for index, base64_image in enumerate(base64_images):
    #         expected_digit = index
    #         digit = recognizer.recognize_digit_from_base64(base64_image)
    #
    #         assert digit == expected_digit

    def _convert_file_to_base64(self, file_path: str) -> str:
        logger = module_logger.getChild(self._convert_file_to_base64.__name__)

        with open(file_path, "br") as file:
            file_content = file.read()

            logger.debug(f"{file_path} file_content:\n{file_content}")

            base64_bytes = base64.b64encode(file_content)
            return base64_bytes.decode(encoding="ascii")
