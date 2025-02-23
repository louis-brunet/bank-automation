import dataclasses
from bank_automation.adapters.caisse_d_epargne_adapter import CaisseDEpargneAdapter
from bank_automation.services.base_service import BaseService


@dataclasses.dataclass
class GetAccountBalanceResult:
    checking: float


class BankingService(BaseService):
    def __init__(
        self,
        caisse_d_epargne_adapter: CaisseDEpargneAdapter,
    ) -> None:
        self.caisse_d_epargne_adapter = caisse_d_epargne_adapter
        super().__init__()

    async def get_all_account_balances(self):
        logger = self.logger.getChild(self.get_all_account_balances.__name__)
        checking_balance = (
            await self.caisse_d_epargne_adapter.get_checking_account_balance()
        )
        logger.info(f"fetched checking account balance: {checking_balance}")

        return GetAccountBalanceResult(checking=checking_balance)
