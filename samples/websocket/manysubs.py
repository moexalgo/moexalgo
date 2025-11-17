"""
Пример для вебсокетов, как делать несколько подписок на одном соединении
"""

import asyncio

from moexalgo.beta import issplus


async def gen_subscription(client, destination, selector):
    subscription = await client.subscribe(destination, selector.format(ticker="MOEX"))
    # Отмена подписки через 45 сек
    asyncio.get_running_loop().call_later(45.0, lambda: asyncio.create_task(client.unsubscribe(subscription.id)))
    # Получение данных
    columns = []
    async for data in subscription:
        print(selector)
        if not columns:
            columns.extend(data["columns"])
            print("\t".join(columns))
        for rec in data["data"]:
            print("\t".join(map(str, [round(*cell) if isinstance(cell, list) else cell for cell in rec])))


async def main():
    url = "wss://iss.moex.com/infocx/v3/websocket"
    destination = "MXSE.orderbooks"
    selector = 'TICKER="MXSE.TQBR.{ticker}" and LANGUAGE="en"'
    tickers = ("MOEX", "GAZP")

    async with issplus.connect(url, issplus.Credentials("DEMO", "guest", "guest")) as client:
        tasks = [
            asyncio.create_task(gen_subscription(client, destination, selector.format(ticker=ticker)))
            for ticker in tickers
        ]

        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
