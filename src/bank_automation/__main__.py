#!/usr/bin/env python

import logging
import asyncio

from dependency_injector.wiring import Provide, inject

from .containers import ApplicationContainer
from .services.banking_service import BankingService


@inject
async def main(
    banking_service: BankingService = Provide[ApplicationContainer.banking_service],
):
    logger = module_logger.getChild(main.__name__)
    balances = await banking_service.get_all_account_balances()
    logger.info(f"balances: {balances}")


if __name__ == "__main__":
    application = ApplicationContainer()
    application.wire(modules=[__name__])

    application.logging.container.init_resources()
    module_logger = logging.getLogger(__name__)

    # adapter_mock = unittest.mock.Mock(CaisseDEpargneAdapter)
    # adapter_mock.configure_mock(login=lambda: print("MOCKED LOGIN"))
    # with application.caisse_d_epargne_adapter.override(adapter_mock):
    #     main()
    event_loop = asyncio.get_event_loop()
    try:
        event_loop.run_until_complete(main())
    except Exception as e:
        module_logger.error(f"Error running main function: {str(e)}")
        raise e
    finally:
        application.shutdown_resources()
