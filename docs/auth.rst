Авторизация и получение APIKEY
==============================

Для неавторизованных пользователей данные предоставляются в ограниченном наборе и задержкой по времени.
Чтобы получить доступ к полному набору данных, надо зарегистрироваться на `data.moex.com <https://data.moex.com>`_,
оформить подписку на `странице ALGOPACK <https://data.moex.com/products/algopack>`_ и получить APIKEY.

Оптимальный способ передать APIKEY в код используя переменную среды:

.. code:: python

    import os
    from moexalgo import session, Market
    session.TOKEN = os.environ['APIKEY']

    eq = Market('EQ')
    eq.tickers()