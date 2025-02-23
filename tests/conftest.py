import pytest
import unittest.mock
import selenium.webdriver
from selenium.webdriver.chrome.webdriver import WebDriver

from bank_automation.containers import ApplicationContainer


@pytest.fixture
def application() -> ApplicationContainer:
    application = ApplicationContainer()
    application.wire(modules=[__name__])
    application.logging.container.init_resources()
    return application


@pytest.fixture
def web_driver_mock() -> unittest.mock.Mock:
    mock = unittest.mock.Mock(selenium.webdriver.Chrome)
    return mock
