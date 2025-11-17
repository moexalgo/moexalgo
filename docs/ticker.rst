Получение данных по тикеру
==========================

Методы для получения данных по инструменту делятся на три группы:


- Основные:
    * `.info` - Информация об инструменте;
    * `.trades` - Сделки за последний день;
    * `.candles` - Свечи с различными периодами.
    * `.orderbook` - Текущий стакан лучших цен;
- Данные ALGOPACK:
    * `.tradestats` - Метрики **TradeStat** по инструменту;
    * `.orderstats` - Метрики **OrderStat** по инструменту;
    * `.obstats` - Метрики **ObStat** по инструменту;
    * `.alerts` - Метрики **MegaAlert** по инструменту;
    * `.hi2` - Метрики **Hi2** по инструменту.
- Данные FUTOI:
    * `.futoi` - Метрики **FUTOI** по инструменту.

.. note::

   Настоятельно рекомендуется использовать хелпер `moexalgo.Ticker` для объекта
   методы которого будут использованы для доступа к данным по инструменту. Параметром
   этого метода является символьный код инструмента. Таблицы распределения доступных
   методов аналогична той что представлена в :doc:`market`.

.. code:: python

   import moexalgo
   sber = moexalgo.Ticker('SBER')
   sber.candles(start='2025-01-01', end='2025-01-31', period='1h')

.. code:: python

   import moexalgo
   moex = moexalgo.Ticker('MOEX')
   moex.orderstats(start='2025-01-01', end='2025-01-31')

API
---

.. autoclass:: moexalgo.engines.stock::Ticker
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: moexalgo.engines.currency::Ticker
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: moexalgo.engines.futures::Ticker
   :members:
   :inherited-members:
   :undoc-members:
