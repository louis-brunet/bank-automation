import base64

import easyocr

from bank_automation.services.base_service import BaseService
from bank_automation.settings import DigitRecognitionSettings


class DigitRecognitionService(BaseService):
    def __init__(self, reader: easyocr.Reader, config: DigitRecognitionSettings) -> None:
        self.reader = reader
        self.config = config
        super().__init__()

    def recognize_digit_from_base64(self, base64_string: str) -> int | None:
        logger = self.logger.getChild("recognize_digits_from_base64")

        image_bytes = base64.b64decode(base64_string)
        fixed_bytes = self._remove_bytes_after_iend_chunk(image_bytes)

        candidates = self.reader.readtext(
            fixed_bytes,
            detail=0,
            allowlist="0123456789",
            # max_candidates=1,
            text_threshold=self.config.text_threshold,
            low_text=self.config.low_text,
        )

        logger.debug(f"candidates {candidates}")

        if len(candidates) == 0:
            return None

        result: int
        first_candidate = candidates[0]
        if type(first_candidate) is str:
            result = int(first_candidate)
        # elif type(first_candidate) is list:
        #     raise NotImplementedError(f"not implemented for type {type(first_candidate)}")
        # elif type(first_candidate) is dict:
        #     raise NotImplementedError(f"not implemented for type {type(first_candidate)}")
        else:
            error_message = f"Unexpected type: {type(first_candidate)}"
            raise ValueError(error_message)

        return result

    def _remove_bytes_after_iend_chunk(self, input_bytes: bytes) -> bytes:
        logger = self.logger.getChild(self._remove_bytes_after_iend_chunk.__name__)

        logger.debug(f"input_bytes: {input_bytes}")

        # iend_chunk = b"\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82"
        iend_chunk = self.config.iend_chunk
        iend_chunk_index = input_bytes.index(iend_chunk)
        logger.debug(f"found index {iend_chunk_index}")

        output_bytes = input_bytes[: iend_chunk_index + len(iend_chunk)]
        logger.debug(f"removed {len(input_bytes) - len(output_bytes)} bytes")

        return output_bytes

