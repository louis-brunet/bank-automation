from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from bank_automation import CurrencyType


class DigitRecognitionSettings(BaseSettings):
    model_config = SettingsConfigDict(
        # env_prefix="caisse_d_epargne_",
        # env_file=".env",
        # env_file_encoding="utf-8",
    )
    languages: list[str] = Field(
        # default=None,
        default_factory=lambda: ["en"],
        frozen=True,
        validate_default=True,
        strict=True,
        init=False,
    )
    text_threshold: float = Field(
        default=0.0,
        frozen=True,
        validate_default=True,
        strict=True,
        init=False,
    )
    low_text: float = Field(
        default=0.0,
        frozen=True,
        validate_default=True,
        strict=True,
        init=False,
    )
    iend_chunk: bytes = Field(
        default=b"\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82",
        description="In decoded PNG files, truncate every byte after this IEND chunk.",
        frozen=True,
        validate_default=True,
        strict=True,
        init=False,
    )


# class CaisseDEpargneAccount(BaseModel):
#     current: CurrencyType = Field(
#         frozen=True,
#         validate_default=True,
#         strict=True,
#         init=False,
#     )


class CaisseDEpargneSettings(BaseSettings):
    model_config = SettingsConfigDict(
        # env_prefix="caisse_d_epargne_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    account_id: str = Field(
        alias="caisse_d_epargne_account_id",
        # validation_alias='caisse_d_epargne_account_id',
        frozen=True,
        validate_default=True,
        strict=True,
        init=False,
    )
    account_password: str = Field(
        alias="caisse_d_epargne_account_password",
        # validation_alias='caisse_d_epargne_account_password',
        frozen=True,
        validate_default=True,
        strict=True,
        init=False,
    )
    checking_account: str = Field(
        alias="caisse_d_epargne_checking_account",
        frozen=True,
        validate_default=True,
        strict=True,
        init=False,
    )
    # accounts: dict[str, Cai]


class LoggingSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="log_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    level: str = Field(
        default="INFO",
        frozen=True,
        validate_default=True,
        strict=True,
        init=False,
    )
    format: str = Field(
        default="[%(asctime)s] %(levelname)s %(name)s:%(lineno)d - %(message)s",
        frozen=True,
        validate_default=True,
        strict=True,
        init=False,
    )


# class ApplicationSettings(BaseSettings):
#     model_config = SettingsConfigDict(
#         # env_file=".env",
#         # env_file_encoding="utf-8",
#     )
#
#     caisse_d_epargne: CaisseDEpargneSettings = CaisseDEpargneSettings()
