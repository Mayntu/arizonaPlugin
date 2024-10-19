from yoomoney import Client, Quickpay
from uuid import UUID, uuid4
from datetime import datetime

from core.settings import YOOMONEY_ACCESS_TOKEN, YOOMONEY_WALLET_ID
from database.schemas.buy_schema import BuySchema
from database.settings import buys_table

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
        sum=100,
        label=label
    )

    return label, quickpay.redirected_url

async def check_payment(uuid : str, user_id : str = None) -> bool:
    history = client.operation_history(
        label=uuid
    )
    # await change_operation_status(
    #                 uuid=uuid,
    #                 user_id=user_id or ""
    #             )
    # return True
    if await is_not_already_bought_operation(uuid=uuid):
        for operation in history.operations:
            if operation.status == "succeded":
                await change_operation_status(
                    uuid=uuid,
                    user_id=user_id or ""
                )
                return True
        
    return False


async def is_not_already_bought_operation(uuid : str) -> bool:
    buy = await buys_table.find_one(
        {"_id" : UUID(uuid)}
    )
    if buy:
        return False
    return True


async def change_operation_status(uuid : str, user_id : str = None):
    buy_schema : BuySchema = BuySchema(
                _id=UUID(uuid),
                buy_time=datetime.now(),
                user_id=user_id or "",
                token=""
            )
    
    await buys_table.insert_one(
        buy_schema.model_dump(
            by_alias=True
        )
    )


async def insert_token_in_buy_schema(schema_uuid : str, token : str) -> None:
    try:
        if await buys_table.find_one(
            {"_id" : UUID(schema_uuid)}
        ):
            await buys_table.update_one(
                {"_id" : UUID(schema_uuid)},
                {"$set" : {"token" : token}}
            )
    except Exception as e:
        raise Exception(e)
