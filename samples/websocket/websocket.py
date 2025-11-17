"""
Пример использования интерфейса ISS+ основанного на технологии websocket.
Для запуска этого примера необходимо установить библиотеку MOEXAlgo c дополнительными
зависимостями `pip install moexalgo[issplus]`.
Установятся модули для работы с websocket+STOMP.
"""
import asyncio

from moexalgo.beta import issplus


async def sample_websocket(url):
    async with issplus.connect(url, issplus.Credentials('DEMO', 'guest', 'guest')) as client:
        print('\n\n\n== META Info ===')
        print(client.structure)

        # режим "Вопрос/Ответ"
        print('\n\n\n== Request: SEARCH.ticker, pattern="SBER"  ===')
        result = await client.request(R'SEARCH.ticker', 'pattern="SBER"')
        print(result)

        # режим "Подписка"
        subs = await client.subscribe('MXSE.securities', 'TICKER="MXSE.TQBR.GAZP" and LANGUAGE="en"')
        print(f'\n\n\n== Subscribe ({subs.id}): MXSE.securities, TICKER="MXSE.TQBR.GAZP" and LANGUAGE="en"  ===')

        # Отмена подписки через 45 сек
        asyncio.get_running_loop().call_later(45.0, lambda: asyncio.create_task(client.unsubscribe(subs.id)))
        # Отключение клиента через 50 сек
        asyncio.get_running_loop().call_later(50.0, lambda: asyncio.create_task(client.close()))

        # вывод данных по подписке
        async for data in subs:
            print(data)
        print(f'\n\n\n== UnSubscribe ({subs.id}): MXSE.securities, TICKER="MXSE.TQBR.GAZP" and LANGUAGE="en"  ===')

        await client  # Ожидание пока клиент активен
        print(f'\n\n\n== End')


if __name__ == '__main__':
    asyncio.run(sample_websocket('wss://iss.moex.com/infocx/v3/websocket'))
