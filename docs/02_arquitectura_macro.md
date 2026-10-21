# Fase 2 — Arquitectura macro

## Decisión: microservicios
Habit4Life se plantea como **microservicios** detrás de un API Gateway y con un
broker de eventos:

```
          ┌───────────────┐
Móvil ──► │  API Gateway  │
          └──────┬────────┘
     ┌───────────┼─────────────┬───────────────┐
     ▼           ▼             ▼               ▼
 ┌────────┐ ┌──────────┐ ┌───────────┐  ┌───────────────┐
 │ Auth   │ │ Habit    │ │ Analytics │  │ Notifications │
 │ Service│ │ Tracking │ │ /Summary  │  │  Service      │
 └────────┘ └────┬─────┘ └─────┬─────┘  └──────┬────────┘
                 │  eventos    │                │
                 └────────►  Broker  ◄──────────┘
                 (GoalMet / StreakMilestone)
```

El componente diseñado e implementado en este laboratorio es el
**microservicio de Habit Tracking** (el más rico del dominio: en él viven el
ciclo de vida del hábito, las reglas de meta, el cálculo de racha y la
publicación de eventos).

## Justificación frente al monolito
| Atributo de calidad | Microservicios | Monolito (descartado) |
|---|---|---|
| Mantenibilidad | Cada servicio evoluciona y se despliega aparte | Un cambio recompila/redeploya todo |
| Disponibilidad | Si Notifications cae, Habit Tracking sigue registrando | Un fallo puede tumbar toda la app |
| Escalabilidad | Se escala solo el servicio con carga (p. ej. Tracking) | Se escala todo el bloque |
| Costo inicial | Mayor (red, orquestación) | Menor |

Para un equipo pequeño el monolito es más barato de arrancar, pero la
independencia de despliegue y el aislamiento de fallos de notificación pesan
más en este dominio (donde el registro diario no puede depender de que el
proveedor de push esté arriba). Por eso se elige microservicios; el patrón
Observer + los puertos ya dejan el código listo para comunicarse vía broker.

## Sub-arquitectura del componente: Hexagonal
El microservicio de Habit Tracking usa **puertos y adaptadores**:
- **Núcleo** (`domain/`): Habit, estados, estrategias, eventos. Sin dependencias externas.
- **Aplicación** (`application/`): casos de uso (Facade) y observadores.
- **Puertos** (`ports/`): `HabitRepository`, `NotificationPort`.
- **Adaptadores** (`adapters/`): repo en memoria + decoradores, adaptadores de notificación.
