# /// script
# dependencies = [
#   "moexalgo[issplus]",
# ]
# ///
import asyncio
import os

from moexalgo.beta import issplus


async def out_lasttrades(user, password):
    selector = 'TICKER="MXSE.TQBR.{ticker}" and LANGUAGE="en"'
    url = "wss://iss.moex.com/infocx/v3/websocket"
    async with issplus.connect(url, issplus.Credentials("passport", user, password)) as client:
        # подписка на последние сделки, MOEX
        destination = "MXSE.lasttrades"
        subscription = await client.subscribe(destination, selector.format(ticker="MOEX"))
        # Отмена подписки через 45 сек
        asyncio.get_running_loop().call_later(45.0, lambda: asyncio.create_task(client.unsubscribe(subscription.id)))
        # Получение данных
        columns = []
        async for data in subscription:
            if not columns:
                columns.extend(data["columns"])
                print("\t".join(columns))
            for rec in data["data"]:
                print("\t".join(map(str, [round(*cell) if isinstance(cell, list) else cell for cell in rec])))


if __name__ == "__main__":
    asyncio.run(
        out_lasttrades(
            os.environ.get("USER", "<Your account>"),
            os.environ.get("PASSWORD", "<Your password"),
        )
    )
