import dataclasses
import logging
import re
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from bank_automation import Currency, CurrencyType
from bank_automation.errors.banking_errors import PasswordOcrError, PasswordParseError
from bank_automation.services.browser_service import BrowserService
from bank_automation.services.digit_recognition_service import DigitRecognitionService
from bank_automation.settings import CaisseDEpargneSettings


@dataclasses.dataclass
class CaisseDEpargneGetAccountBalanceAccountOptions:
    currency: CurrencyType


class CaisseDEpargneAccountNotFoundError(ValueError):
    def __init__(self, account_id: str) -> None:
        super().__init__(f"Account not found: {account_id}")


class CaisseDEpargneAdapter:
    def __init__(
        self,
        config: CaisseDEpargneSettings,
        digit_recognition_service: DigitRecognitionService,
        browser_service: BrowserService,
    ) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

        self.digit_recognition_service = digit_recognition_service
        assert self.digit_recognition_service is not None

        self.browser_service = browser_service
        assert self.browser_service is not None

        self.config = config
        assert self.config is not None

        self.logger.debug(f"config: {config}")
        assert config.account_id is not None
        assert isinstance(config.account_id, str)
        assert len(config.account_id) > 0

        assert config.account_password is not None
        assert isinstance(config.account_password, str)
        assert len(config.account_password) > 0

    def _get_base64_from_background_image(self, background_image: str) -> str:
        matched = re.search(r'url\("data:image/png;base64,(.*)"\)', background_image)
        if matched:
            return matched.group(1)
        raise ValueError(
            f"could not get base64 from background image value: {background_image}"
        )

    def _get_button_value(self, background_image: str) -> int | None:
        image_base64 = self._get_base64_from_background_image(background_image)
        button_value = self.digit_recognition_service.recognize_digit_from_base64(
            image_base64
        )
        return button_value

    def _sort_buttons(self, buttons: list[WebElement]) -> list[WebElement]:
        button_values: list[tuple[int, WebElement]] = []

        for button in buttons:
            background_image = button.value_of_css_property("background-image")
            button_value = self._get_button_value(background_image)
            if button_value is None:
                raise PasswordOcrError(background_image)
            button_values.append((button_value, button))

        ordered_buttons = [
            button for _, button in sorted(button_values, key=lambda x: x[0])
        ]
        return ordered_buttons

    async def get_checking_account_balance(self) -> float:
        account_id = self.config.checking_account
        balances = await self.get_account_balance(
            {
                account_id: CaisseDEpargneGetAccountBalanceAccountOptions(
                    currency=Currency.EURO
                ),
            }
        )
        balance = balances[account_id]
        if not isinstance(balance, float):
            raise ValueError(f"Expected float, got {balance}")
        return balance

    async def get_account_balance(
        self,
        accounts: dict[str, CaisseDEpargneGetAccountBalanceAccountOptions],
    ) -> dict[str, float]:
        """Get account balance for each of the given accounts

        Args:
            account_ids: map of account ID to its expected currency suffix

        Returns:
            map of account ID to its account balance

        Raises:
            PasswordParseError:
            NoSuchElementException:
        """
        # accounts = request.accounts

        logger = self.logger.getChild(self.get_account_balance.__name__)
        logger.debug(f"starting login flow for account ids: {accounts}")

        self.browser_service.get(
            "https://www.caisse-epargne.fr/banque-a-distance/acceder-compte/"
        )
        no_consent = self.browser_service.find_element_by_id(id="no_consent_btn")
        no_consent.click()
        self.browser_service.get(
            "https://www.caisse-epargne.fr/se-connecter/sso?service=dei"
        )
        identifier_input = self.browser_service.find_element_by_id(
            id="input-identifier"
        )
        identifier_input.send_keys(self.config.account_id)
        identifier_input.send_keys("\n")

        time.sleep(2)  # TODO: remove sleep

        logger.debug("sort password buttons")
        buttons = self.browser_service.find_elements_by_css_selector(
            selector="button.keyboard-button"
        )
        ordered_buttons = self._sort_buttons(buttons)

        logger.debug("input configured password using sorted numeric buttons")
        remaining_password = self.config.account_password

        while remaining_password != "":
            try:
                next_char = int(remaining_password[0])
            except ValueError:
                raise PasswordParseError()
            if next_char < 0 or next_char > 9:
                raise PasswordParseError()

            button = ordered_buttons[next_char]
            button.click()
            remaining_password = remaining_password[1:]

        logger.debug("submit password")
        password_submit_button = self.browser_service.find_element_by_id(
            id="p-password-btn-submit"
        )
        password_submit_button.click()

        time.sleep(2)  # TODO: remove sleep

        logger.debug(f"URL: {self.browser_service.get_current_url()}")

        await self.browser_service.wait_for_element_to_disappear(
            by=By.ID, value="m-identifier-cloudcard-btn-fallback"
        )

        logger.info("Could not find MFA dialog button, continuing")

        account_tiles = await self.browser_service.wait_for_elements(
            by=By.CSS_SELECTOR,
            value="compte-contract-tile",
        )

        logger.debug(f"found account labels: {account_tiles}")

        account_balances = {}

        for account_tile in account_tiles:
            account_tile_id_p = account_tile.find_element(
                by=By.CSS_SELECTOR,
                value="p[data-e2e=account-label]+p",
            )
            account_tile_id = account_tile_id_p.text.strip()
            if account_tile_id in accounts.keys():
                logger.debug(
                    f"found account tile for account with id: {account_tile_id}"
                )
                balance_spans = account_tile.find_elements(
                    by=By.CSS_SELECTOR,
                    value="compte-ui-balance[data-e2e=compte-balance-contract] .balance span",
                )
                expected_currency_suffix = accounts[account_tile_id].currency
                assert len(balance_spans) == 2
                assert balance_spans[1].text.strip()[-1] == expected_currency_suffix

                balance = self._get_balance_from_raw_parts(
                    [span.text for span in balance_spans]
                )
                logger.debug(
                    f"account balance for account ID {account_tile_id} is: {balance}"
                )

                account_balances[account_tile_id] = balance

        for expected_key in accounts.keys():
            if expected_key not in account_balances:
                raise CaisseDEpargneAccountNotFoundError(expected_key)

        return account_balances

    def _get_balance_from_raw_parts(self, balance_span_contents: list[str]) -> float:
        logger = self.logger.getChild(self._get_balance_from_raw_parts.__name__)
        [whole_part, decimal_part] = [
            re.sub(r"[^0-9,.-]", "", text) for text in balance_span_contents
        ]
        logger.debug(f"whole_part='{whole_part}', decimal_part='{decimal_part}'")

        balance = float(f"{whole_part}{decimal_part.replace(',', '.')}")
        return balance
