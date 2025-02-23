from typing import Literal


class Currency:
    EURO = "€"


CurrencyType = Literal["€"]


GetAccountBalanceResponse = dict[str, float]
