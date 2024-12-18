# MoexAlgo: Получение уникальных данных MOEX ALGOPACK 📈

### 🌐 [Сайт с полной документацией по продукту ALGOPACK](https://moexalgo.github.io/)

<br>

##### 🚀 MoexAlgo предоставляет данные и аналитику по рынку акций, фьючерсов и валют Московской Биржи (MOEX). 

##### 📊 Более 100 уникальных метрик!

##### С помощью ALGOPACK можно получать:
- ###### Исторические данные - для тестирования торговых стратегий, проверки гипотез и бэктестов
- ###### Онлайн данные - для алгоритмической торговли



<br>
[Changelog »](./CHANGELOG.md)
<br><br>

## MoexAlgo предоставляет наборы данных:

* ⏰📊 Real-time market data 
  1. 🕯️ `Candles` - свечи по тикеру за заданный период
  2. 📚 `OrderBook` - стакан котировок по тикеру

* 🚀🕯️ Super Candles
  1.  💹 `TradeStats` - метрики, рассчитанные на потоке сделок: цены, объемы, соотношения покупок и продаж
  2.  📊 `OrderStats` - метрики, рассчитанные на потоке заявок: кол-во и объемы выставленных/снятых заявок
  3.   📈 `OBStats` - метрики, рассчитанные на стакане котировок: кол-во уровней цен, спреды, ликвидность и дисбаланс покупок/продаж
* 🎯 `HI2` - Индекс рыночной концентрации 
* 💼 `FUTOI` - Открытые позиции по фьючерсным контрактам в разрезе физ. и юр. лиц 

Также, можно получить справочную информацию по инструментам, свечи и торговую статистику

<br>

## 🚀 Пример использования

<hr>

#### ⚡️ Быстрое знакомство с библиотекой MoexAlgo - [quick_start.ipynb](./samples/quick_start.ipynb)

#### ⬇️ Получение данных через API - [download_algopack_data.ipynb](./samples/download_algopack_data.ipynb)

#### 🔐 Пример авторизации - [auth.ipynb](./samples/auth.ipynb)

#### ⬇️ Получение данных c использованием APIКЕУ - [token.ipynb](./samples/token.ipynb)
<hr>

Для работы с библиотекой необходимо авторизоваться на https://passport.moex.com

```python
from moexalgo import session

username = "<email>"
password = "<password>"

session.authorize(username, password)

```

Чтобы получить доступ к полному набору данных, необходимо оформить бесплатную подписку на [странице](https://www.moex.com/ru/analyticalproducts?futoi) 

```python
from moexalgo import Ticker

# выбираем акции Сбера
sber = Ticker('SBER')

# получим дневные свечи с 2020 года
sber.candles(start='2020-01-01', end='2023-11-01').head()
```

<br>

<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>open</th>
      <th>close</th>
      <th>high</th>
      <th>low</th>
      <th>value</th>
      <th>volume</th>
      <th>begin</th>
      <th>end</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>255.99</td>
      <td>255.99</td>
      <td>258.19</td>
      <td>253.70</td>
      <td>9165475000</td>
      <td>35851840</td>
      <td>2020-01-03 09:00:00</td>
      <td>2020-01-03 18:59:59</td>
    </tr>
    <tr>
      <th>1</th>
      <td>254.75</td>
      <td>254.75</td>
      <td>254.84</td>
      <td>251.40</td>
      <td>5646010000</td>
      <td>22348300</td>
      <td>2020-01-06 09:00:00</td>
      <td>2020-01-06 18:59:59</td>
    </tr>
    <tr>
      <th>2</th>
      <td>253.57</td>
      <td>253.57</td>
      <td>259.15</td>
      <td>253.03</td>
      <td>10485880000</td>
      <td>40817240</td>
      <td>2020-01-08 09:00:00</td>
      <td>2020-01-08 18:59:59</td>
    </tr>
    <tr>
      <th>3</th>
      <td>259.40</td>
      <td>259.40</td>
      <td>261.76</td>
      <td>257.01</td>
      <td>9936032000</td>
      <td>38329020</td>
      <td>2020-01-09 09:00:00</td>
      <td>2020-01-09 18:59:59</td>
    </tr>
    <tr>
      <th>4</th>
      <td>257.86</td>
      <td>257.86</td>
      <td>259.25</td>
      <td>256.88</td>
      <td>4864405000</td>
      <td>18851390</td>
      <td>2020-01-10 09:00:00</td>
      <td>2020-01-10 18:59:59</td>
    </tr>
  </tbody>
</table>
</div>


<br>
Больше примеров смотрите в разделе samples

<br>

### 💻 Установка

Установка с помощью `pip`:

``` bash
pip install moexalgo[pandas]
```

### 🔍 Requirements

-   [Python](https://www.python.org) \>= 3.8+
-   [pandas](https://github.com/pydata/pandas)
-   [numpy](http://www.numpy.org) \>= 1.15.0


### 🤝 Комьюнити 

- Самые важные новости ALGOPACK [подписывайтесь](https://t.me/moex_algopack_news)
- Добавляйтесь в телеграмм-чат [ALGOPACK](https://t.me/moex_algopack)


### ❓ Вопросы?

Библиотека MoexAlgo будет дополняться. Если есть пожелания, идеи, замечания, пишите на <algopack@moex.com>

### 📜 Licence

Apache Software License
