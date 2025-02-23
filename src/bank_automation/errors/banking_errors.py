class PasswordParseError(ValueError):
    def __init__(self) -> None:
        super().__init__("Could not parse password")


class PasswordOcrError(ValueError):
    def __init__(self, cssBackgroundImage: str) -> None:
        super().__init__(
            f"Could not recognize password button image digit with OCR from the following value: {cssBackgroundImage}"
        )
