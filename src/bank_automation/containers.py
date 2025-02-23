import logging
from typing import Generator
from dependency_injector import containers, providers
import selenium.webdriver
import easyocr
from selenium.webdriver.chrome.webdriver import WebDriver

from bank_automation.adapters.caisse_d_epargne_adapter import (
    CaisseDEpargneAdapter,
)
from bank_automation.services.banking_service import BankingService
from bank_automation.infra.browser_service import BrowserService
from bank_automation.services.digit_recognition_service import DigitRecognitionService
from bank_automation.settings import (
    CaisseDEpargneSettings,
    DigitRecognitionSettings,
    LoggingSettings,
)


def init_web_driver() -> Generator[WebDriver, None, None]:
    logger = logging.getLogger(init_web_driver.__name__)
    logger.info("Initializing Chrome web driver")
    with selenium.webdriver.Chrome() as web_driver:
        logger.info("Created Chrome web driver")
        yield web_driver
        logger.info("Destroying Chrome web driver")
        web_driver.quit()
    logger.info("Destroyed Chrome web driver")


class LoggingContainer(containers.DeclarativeContainer):
    config = providers.Singleton(LoggingSettings)

    basic_config = providers.Resource(
        logging.basicConfig,
        level=config().level,
        format=config().format,
    )
    color_debug = providers.Resource(
        logging.addLevelName,
        logging.DEBUG,
        "\033[1;35m%s\033[1;0m" % logging.getLevelName(logging.DEBUG),
    )
    color_info = providers.Resource(
        logging.addLevelName,
        logging.INFO,
        "\033[1;34m%s\033[1;0m" % logging.getLevelName(logging.INFO),
    )
    color_warning = providers.Resource(
        logging.addLevelName,
        logging.WARN,
        "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.WARN),
    )
    color_error = providers.Resource(
        logging.addLevelName,
        logging.ERROR,
        "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.ERROR),
    )


class ApplicationContainer(containers.DeclarativeContainer):
    logging = providers.Container(LoggingContainer)

    digit_recognition_settings = providers.Singleton(DigitRecognitionSettings)
    digit_recognition_reader = providers.Singleton(
        easyocr.Reader, digit_recognition_settings().languages
    )
    digit_recognition_service = providers.Singleton(
        DigitRecognitionService,
        reader=digit_recognition_reader,
        config=digit_recognition_settings,
    )

    web_driver = providers.Resource(init_web_driver)
    browser_service = providers.Singleton(BrowserService, web_driver=web_driver)

    caisse_d_epargne_config = providers.Singleton(CaisseDEpargneSettings)
    caisse_d_epargne_adapter = providers.Singleton(
        CaisseDEpargneAdapter,
        config=caisse_d_epargne_config,
        digit_recognition_service=digit_recognition_service,
        browser_service=browser_service,
    )

    banking_service = providers.Singleton(
        BankingService, caisse_d_epargne_adapter=caisse_d_epargne_adapter
    )
