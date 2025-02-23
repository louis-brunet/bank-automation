import asyncio
from typing import Callable

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By, ByType
from selenium.webdriver.remote.webelement import WebElement

from bank_automation.errors.browser_errors import MaxRetriesExceededError
from bank_automation.services.base_service import BaseService


class BrowserService(BaseService):
    def __init__(self, web_driver: WebDriver) -> None:
        self.web_driver = web_driver
        self.web_driver.implicitly_wait(0.5)
        super().__init__()

    def get(self, url: str):
        self.web_driver.get(url)

    def find_element_by_id_optional(self, id: str) -> WebElement | None:
        return self._find_element_optional(by=By.ID, value=id)

    def find_element_by_id(self, id: str) -> WebElement:
        return self._find_element(by=By.ID, value=id)

    def find_elements_by_css_selector(self, selector: str) -> list[WebElement]:
        return self._find_elements(by=By.CSS_SELECTOR, value=selector)

    def get_current_url(self) -> str:
        return self.web_driver.current_url

    async def wait_for_element_to_disappear(
        self,
        by: ByType,
        value: str,
        max_try_count: int = 30,
        sleep_delay_in_seconds: float = 2.0,
    ):
        logger = self.logger.getChild(self.wait_for_element_to_disappear.__name__)

        def stop_condition() -> bool:
            element = self._find_element_optional(by=by, value=value)
            if element is None:
                return True
            logger.error("Found MFA dialog, waiting for human MFA approval...")
            return False

        return await self._wait_for(
            is_stop_condition_reached=stop_condition,
            max_try_count=max_try_count,
            sleep_delay_in_seconds=sleep_delay_in_seconds,
        )

    async def wait_for_elements(
        self,
        by: ByType,
        value: str,
        max_try_count: int = 5,
        sleep_delay_in_seconds: float = 1.0,
    ) -> list[WebElement]:
        logger = self.logger.getChild(self.wait_for_elements.__name__)
        elements: list[WebElement] = []

        def stop_condition():
            nonlocal elements
            elements = self._find_elements(by=by, value=value)
            if len(elements) > 0:
                return True
            logger.error(f"No elements found (by='{by}', value='{value}')")
            return False

        await self._wait_for(
            is_stop_condition_reached=stop_condition,
            max_try_count=max_try_count,
            sleep_delay_in_seconds=sleep_delay_in_seconds,
        )

        return elements

    async def _wait_for(
        self,
        is_stop_condition_reached: Callable[[], bool],
        max_try_count: int = 30,
        sleep_delay_in_seconds: float = 2.0,
    ):
        logger = self.logger.getChild(self._wait_for.__name__)

        for try_index in range(max_try_count):
            if is_stop_condition_reached():
                return
            await asyncio.sleep(sleep_delay_in_seconds)
            logger.info(f"Waiting... ({try_index + 1}/{max_try_count})")
        raise MaxRetriesExceededError(try_count=max_try_count)

    def _find_element(self, by: ByType, value: str | None) -> WebElement:
        return self.web_driver.find_element(by=by, value=value)

    def _find_element_optional(
        self, by: ByType, value: str | None
    ) -> WebElement | None:
        try:
            return self._find_element(by=by, value=value)
        except NoSuchElementException:
            return None

    def _find_elements(
        self,
        by: ByType,
        value: str | None,
    ) -> list[WebElement]:
        return self.web_driver.find_elements(by=by, value=value)
