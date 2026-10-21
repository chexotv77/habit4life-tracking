# Habit4Life — Microservicio de Habit Tracking

Laboratorio de **Arquitectura, SOLID y Patrones de diseño** — Ingeniería de
Software II (2016702), UNAL. Ruta A (desarrollo).

Dominio: app de seguimiento de hábitos **Habit4Life**.
Arquitectura macro: **microservicios**. Componente implementado: **Habit
Tracking**. Sub-arquitectura: **Hexagonal (puertos y adaptadores)**.

## Cómo ejecutar

Requiere Python 3.10+.

```bash
pip install -r requirements.txt    # solo pytest

python -m pytest -q                # corre las pruebas (18)
python demo.py                     # evidencia + escenarios de evolución (Fase 7)
```

## Estructura del proyecto (refleja la sub-arquitectura hexagonal)

```
src/habit_tracking/
├── domain/              # NÚCLEO — reglas de negocio, sin dependencias externas
│   ├── habit.py            Habit (contexto de State y Strategy; Subject de Observer)
│   ├── habit_state.py      State: Active / Paused / Archived
│   ├── goal_strategy.py    Strategy: Increase / Maintain / Reduce
│   ├── habit_factory.py    Factory Method: creadores por tipo
│   ├── habit_builder.py    Builder: armado fluido del hábito
│   ├── events.py           Observer: publicador, observer y eventos de dominio
│   └── errors.py           Excepciones de dominio
├── application/         # CASOS DE USO (Facade) + observadores
│   ├── habit_service.py    HabitTrackingService (Facade)
│   └── observers.py        NotificationObserver, WeeklySummaryObserver
├── ports/               # PUERTOS (interfaces que el núcleo define)
│   ├── habit_repository.py
│   └── notification_port.py
└── adapters/            # ADAPTADORES (implementan los puertos)
    ├── in_memory_habit_repository.py
    ├── repository_decorators.py       Decorator: Caching / Logging
    └── notifications/
        ├── providers.py               mocks de FCM / SMTP / SMS
        └── adapters.py                Adapter: Push / Email / SMS
tests/                   # 18 pruebas unitarias y de integración
docs/                    # Fase 1 (dominio) y Fase 2 (arquitectura macro)
demo.py                  # evidencia ejecutable + Fase 7
```

## Patrones aplicados → archivo y clase

| Familia | Patrón | Archivo | Clase(s) | Problema que resuelve |
|---|---|---|---|---|
| Creacional | **Factory Method** | `domain/habit_factory.py` | `HabitCreator`, `IncreaseHabitCreator`… | Elegir la estrategia correcta según el tipo de hábito, sin `if` dispersos |
| Creacional | **Builder** | `domain/habit_builder.py` | `HabitBuilder` | Armar un hábito con muchos datos opcionales de forma legible |
| Estructural | **Adapter** | `adapters/notifications/adapters.py` | `PushNotificationAdapter`, `EmailNotificationAdapter`, `SmsNotificationAdapter` | Integrar proveedores incompatibles tras un único `NotificationPort` |
| Estructural | **Decorator** | `adapters/repository_decorators.py` | `CachingHabitRepository`, `LoggingHabitRepository` | Añadir caché y auditoría al repositorio sin modificarlo |
| Comportamiento | **State** | `domain/habit_state.py` | `ActiveState`, `PausedState`, `ArchivedState` | Ciclo de vida del hábito sin `if estado == …` |
| Comportamiento | **Strategy** | `domain/goal_strategy.py` | `IncreaseGoalStrategy`, `MaintainGoalStrategy`, `ReduceGoalStrategy` | Regla de cumplimiento de meta intercambiable por tipo |
| Comportamiento | **Observer** | `domain/events.py` + `application/observers.py` | `HabitEventPublisher`, `NotificationObserver`, `WeeklySummaryObserver` | Avisar a varios reactores al cumplir meta/racha sin acoplarlos |
| (Extra) Estructural | **Facade** | `application/habit_service.py` | `HabitTrackingService` | API simple que oculta la coordinación entre repo, publicador y observadores |

> Son 7 patrones justificados por problemas reales del dominio (el mínimo pedido es 2+2+2).

## Evidencia de SOLID

| Principio | Evidencia |
|---|---|
| **S** — Responsabilidad única | Cada estrategia solo evalúa; cada adaptador solo traduce; `Habit` solo contiene reglas de negocio |
| **O** — Abierto/Cerrado | Agregar tipo de meta, canal o estado = agregar una clase. Demostrado en `test_goal_strategy.py` (nueva Strategy sin tocar el contexto) y en `demo.py` |
| **L** — Sustitución de Liskov | Cualquier `GoalEvaluationStrategy`, `HabitState` o decorador de repo es intercambiable sin romper al cliente |
| **I** — Segregación de interfaces | `NotificationPort` y `HabitObserver` tienen un solo método; `HabitRepository` es mínimo |
| **D** — Inversión de dependencias | `HabitTrackingService` depende de los puertos; los adaptadores concretos se inyectan por constructor |

### "Antes y después" (dos casos)
1. **Strategy vs. switch de tipo**: antes, `is_met` era un `if tipo == INCREASE … elif REDUCE …` que violaba O; ahora cada regla es una clase (`goal_strategy.py`).
2. **Adapter/Port vs. llamada directa**: antes, el servicio llamaba al SDK de FCM/SMTP directamente (violaba D); ahora depende de `NotificationPort` y los adaptadores traducen (`notifications/adapters.py`).

## Cobertura de los requisitos de la Ruta A
- [x] Componente implementado respetando la sub-arquitectura (estructura de paquetes = hexágono).
- [x] 6+ patrones en el código y referenciados (tabla de arriba).
- [x] Repos en memoria y mocks de servicios externos (resueltos con Adapter).
- [x] 18 pruebas, incluida una de Abierto/Cerrado (`test_goal_strategy.py::test_open_closed_…`).
- [x] README con ejecución, estructura y tabla patrón→archivo.
