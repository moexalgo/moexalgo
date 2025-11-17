Получение данных по рынкам
==========================

Методы для получения данных по рынку делятся на три группы:

- Основные:
    * `.tickers` - Информация о всех инструментах рынка;
    * `.marketdata` - Статистическая информация о всех инструментах рынка;
    * `.trades` - Последние сделки по всем инструментам рынка;
    * `.candles` - Две последние минутные свечи по всем инструментам рынка.
- Данные ALGOPACK:
    * `.tradestats` - Метрики **TradeStat** по всем инструментам рынка за день;
    * `.orderstats` - Метрики **OrderStat** по всем инструментам рынка за день;
    * `.obstats` - Метрики **ObStat** по всем инструментам рынка за день;
    * `.alerts` - Метрики **MegaAlert** по всем инструментам рынка за день;
    * `.hi2` - Метрики **Hi2** по всем инструментам рынка за день.
- Данные FUTOI:
    * `.futoi` - Метрики **FUTOI** по всем инструментам рынка за день.


.. note::

   Настоятельно рекомендуется использовать хелпер `moexalgo.Market` для объекта
   методы которого будут использованы для доступа к данным. Параметром этого метода
   является алиасы имени рынка (регистр не важен). Смотрите ниже примеры, алиасы, и
   таблицы доступных методов.

.. code:: python

   import moexalgo
   idx = moexalgo.Market('index')
   idx.trades()

.. code:: python

   import moexalgo
   eq = moexalgo.Market('EQ')
   eq.orderstats(date='2025-01-07')


======== ========= ================== =========================
Рынок    Раздел    Алиасы             Доступные методы
======== ========= ================== =========================
Фондовый Акции     shares, stocks, eq Основные, ALGOPACK
     -   Индексы   index              Основные
     -   Бонды     bonds              Основные
Валютный           selt, currency, fx Основные, ALGOPACK
Срочный  Фьючерсы  futures, forts, fo Основные, ALGOPACK, FUTOI
     -   Опционы   options            Основные
======== ========= ================== =========================

API
---

.. autoclass:: moexalgo.engines.stock::Market
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: moexalgo.engines.currency::Market
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: moexalgo.engines.futures::Market
   :members:
   :inherited-members:
   :undoc-members:
