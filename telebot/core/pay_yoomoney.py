from yoomoney import Client, Quickpay
from uuid import uuid4

from core.settings import YOOMONEY_ACCESS_TOKEN, YOOMONEY_WALLET_ID

client : Client = Client(token=YOOMONEY_ACCESS_TOKEN)

# label : str = "testwfwfwf"
# quickpay : Quickpay = Quickpay(
#     receiver=YOOMONEY_WALLET_ID,
#     quickpay_form="shop",
#     targets="Тестовая покупка",
#     paymentType="SB",
#     sum=2,
#     label=label
# )
# print(quickpay.base_url)
# print(quickpay.redirected_url)

# history = client.operation_history(label=label)
# print(history.operations)
# for operation in history.operations:
#     print(operation.status)


def get_ticket() -> tuple:
    label : str = str(uuid4())
    quickpay : Quickpay = Quickpay(
        receiver=YOOMONEY_WALLET_ID,
        quickpay_form="shop",
        targets="Плагин",
        paymentType="SB",
        sum=2,
        label=label
    )

    return label, quickpay.redirected_url

def check_payment(uuid : str) -> bool:
    history = client.operation_history(
        label=uuid
    )
    for operation in history.operations:
        if operation.status == "succeded":
            return True
    
    return False
