import pytest
import unittest.mock
import selenium.webdriver

from bank_automation.containers import ApplicationContainer
from bank_automation.settings import CaisseDEpargneSettings


@pytest.fixture
def application() -> ApplicationContainer:
    application = ApplicationContainer()
    application.wire(modules=[__name__])
    application.logging.container.init_resources()

    mocked_ce_settings = unittest.mock.Mock(CaisseDEpargneSettings)
    mocked_ce_settings.account_id = "mocked id"
    mocked_ce_settings.account_password = "mocked password"
    mocked_ce_settings.checking_account = "mocked checking account"
    application.caisse_d_epargne_config.override(mocked_ce_settings)

    mocked_web_driver = unittest.mock.Mock(selenium.webdriver.Chrome)
    application.web_driver.override(mocked_web_driver)

    return application
