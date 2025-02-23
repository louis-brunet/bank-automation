import unittest.mock

from bank_automation.containers import ApplicationContainer


class TestCaisseDEpargneAdapter:
    @staticmethod
    def test_exists(
        application: ApplicationContainer, web_driver_mock: unittest.mock.Mock
    ):
        with application.web_driver.override(web_driver_mock):
            assert not not application.caisse_d_epargne_adapter()

    @staticmethod
    def test_get_balance_from_raw_parts(
        application: ApplicationContainer, web_driver_mock: unittest.mock.Mock
    ):
        with application.web_driver.override(web_driver_mock):
            adapter = application.caisse_d_epargne_adapter()
            assert adapter._get_balance_from_raw_parts(["+ 123", ",45€"]) == 123.45
            assert adapter._get_balance_from_raw_parts(["- 123", ",45 €"]) == -123.45
            assert adapter._get_balance_from_raw_parts(["123", ",45 €"]) == 123.45
            assert adapter._get_balance_from_raw_parts(["123", ".45 €"]) == 123.45
            assert (
                adapter._get_balance_from_raw_parts([" abc  -  123", "  , 45   €  "])
                == -123.45
            )
            assert adapter._get_balance_from_raw_parts(["+123", ",45 €"]) == 123.45
