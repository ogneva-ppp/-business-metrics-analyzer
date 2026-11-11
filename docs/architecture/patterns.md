# Паттерны проектирования Business Metrics Analyzer

## 1. Введение

Business Metrics Analyzer — веб-приложение для
расчёта и визуализации ключевых показателей
эффективности (KPI) торговой компании.

Для организации программного кода используются
паттерны проектирования, позволяющие разделить
ответственность компонентов, упростить
тестирование, сопровождение и расширение системы.

В архитектуре приложения рассматриваются паттерны
Repository, Unit of Work, Service Layer, Factory,
Strategy, DTO, Adapter и Observer.

## 2. Выбор и обоснование паттернов

| Паттерн | Где применяется | Обоснование | Альтернативы |
|---|---|---|---|
| Repository | Слой доступа к данным о продажах | Отделяет бизнес-логику от работы с базой данных PostgreSQL, упрощает тестирование | Прямые SQL-запросы из сервисов |
| Unit of Work | Импорт данных о продажах | Обеспечивает атомарность транзакций: при ошибке изменения откатываются | Ручное управление транзакциями |
| Service Layer | Расчёт KPI и формирование отчётов | Объединяет бизнес-логику в отдельных сервисах, не перегружая API-контроллеры | Размещение бизнес-логики в контроллерах |
| Factory | Создание отчётов Excel и PDF | Позволяет создавать отчёты разных форматов через единый интерфейс | Условные операторы if/else |
| Strategy | Расчёт KPI: выручки, среднего чека, рентабельности | Позволяет использовать и расширять разные алгоритмы расчёта показателей | Жёстко заданные методы расчёта |
| DTO | Передача данных между FastAPI и клиентским интерфейсом | Обеспечивает понятную структуру данных и проверку формата запросов и ответов | Передача словарей или ORM-моделей напрямую |
| Adapter | Интеграция с 1С и сервисом email-уведомлений | Изолирует бизнес-логику от особенностей внешних систем | Прямые вызовы внешних API |
| Observer | Обновление дашборда после изменения данных | Позволяет уведомлять заинтересованные компоненты об изменениях | Периодический опрос сервера |


## 3. Примеры реализации паттернов на Python

### 3.1. Repository

Паттерн Repository используется для отделения
бизнес-логики приложения от операций доступа к
данным о продажах. Он позволяет получать и
сохранять данные через единый интерфейс.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Sale:
    id: int
    revenue: float
    cost: float


class SaleRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[Sale]:
        pass


class InMemorySaleRepository(SaleRepository):
    def __init__(self):
        self.sales = [
            Sale(1, 100000, 70000),
            Sale(2, 50000, 30000)
        ]

    def get_all(self) -> list[Sale]:
        return self.sales


repository = InMemorySaleRepository()
for sale in repository.get_all():
    print(f"Продажа {sale.id}: выручка {sale.revenue}")
```

В примере `SaleRepository` определяет интерфейс
доступа к данным, а `InMemorySaleRepository`
реализует хранение продаж в памяти. В реальном
приложении вместо него может использоваться
репозиторий на основе PostgreSQL и SQLAlchemy.

### 3.2. Unit of Work

Паттерн Unit of Work используется при импорте данных о продажах для управления транзакциями. Он обеспечивает согласованность данных: если операция завершилась успешно, изменения сохраняются, а при ошибке выполняется откат.

```python
class UnitOfWork:
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session = None

    def __enter__(self):
        self.session = self.session_factory()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if exc_type is None:
                self.session.commit()
            else:
                self.session.rollback()
        except Exception:
            self.session.rollback()
            raise
        finally:
            self.session.close()


# Пример использования с настроенной фабрикой сессий
# with UnitOfWork(session_factory) as uow:
#     uow.session.add(sale_record)
```

В данном примере UnitOfWork открывает сессию базы данных и управляет её жизненным циклом. При успешном выполнении операций вызывается commit(), а при возникновении ошибки — rollback(). После завершения работы сессия закрывается. Это позволяет избежать частичного сохранения данных при импорте продаж.

### 3.3. Strategy

Паттерн Strategy применяется для реализации различных алгоритмов расчёта KPI. Он позволяет добавлять новые показатели без изменения существующих алгоритмов.

```python
from abc import ABC, abstractmethod


class KpiStrategy(ABC):
    @abstractmethod
    def calculate(self, revenue: float, cost: float) -> float:
        pass


class ProfitStrategy(KpiStrategy):
    def calculate(self, revenue: float, cost: float) -> float:
        return revenue - cost


class ProfitabilityStrategy(KpiStrategy):
    def calculate(self, revenue: float, cost: float) -> float:
        if revenue == 0:
            return 0.0
        return (revenue - cost) / revenue * 100


class KpiCalculator:
    def __init__(self, strategy: KpiStrategy):
        self.strategy = strategy

    def calculate(self, revenue: float, cost: float) -> float:
        return self.strategy.calculate(revenue, cost)


calculator = KpiCalculator(ProfitStrategy())
print("Прибыль:", calculator.calculate(100000, 70000))

calculator = KpiCalculator(ProfitabilityStrategy())
print("Рентабельность:", calculator.calculate(100000, 70000), "%")
```

Результат выполнения:

```text
Прибыль: 30000
Рентабельность: 30.0 %
```

Класс `KpiStrategy` определяет общий интерфейс расчёта показателей. Классы `ProfitStrategy` и `ProfitabilityStrategy` реализуют разные алгоритмы. Класс `KpiCalculator` использует выбранную стратегию, позволяя изменять способ расчёта без изменения его собственного кода.

## 4. Вывод

Использование паттернов проектирования позволяет создать гибкую и поддерживаемую архитектуру Business Metrics Analyzer. Repository и Unit of Work упрощают работу с данными и транзакциями, а Strategy обеспечивает расширяемость алгоритмов расчёта KPI. Остальные выбранные паттерны помогают организовать бизнес-логику, формирование отчётов, передачу данных и интеграцию с внешними системами.
