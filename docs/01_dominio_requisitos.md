# Fase 1 — Dominio y problema

## Sector y problema
**Habit4Life** es una app móvil de seguimiento de hábitos ("Understand your
habits"). El problema: tomar buenas decisiones todo el día agota; el usuario
necesita un acompañante que le permita **registrar su progreso diario, ver sus
rachas y recibir retroalimentación** sin fricción, para sostener hábitos en el
tiempo.

## Actores
- **Usuario final**: crea hábitos, registra progreso, consulta detalle y resumen.
- **Proveedores de notificación** (sistemas externos): push (FCM), email (SMTP), SMS.
- **Servicio de Analítica/Resumen** (interno): consume eventos para el resumen semanal.

## Requisitos funcionales
1. Crear un hábito de tipo **aumentar**, **mantener** o **reducir**, con meta, unidad, frecuencia y motivo opcional.
2. Registrar progreso diario sobre un hábito.
3. Evaluar si un día cumplió la meta según el tipo de hábito.
4. Calcular la racha (días consecutivos cumplidos).
5. Notificar al usuario al cumplir la meta del día.
6. Notificar al alcanzar hitos de racha (7, 30, 100 días).
7. Gestionar el ciclo de vida del hábito: activar, pausar, reanudar, archivar.
8. Impedir registros en hábitos pausados o archivados.
9. Alimentar el resumen semanal (días cumplidos, mejor racha por hábito).

## Atributos de calidad
- **Mantenibilidad / extensibilidad**: agregar tipos de hábito, canales de
  notificación o estados debe ser aditivo (sin modificar el núcleo).
- **Testabilidad**: el dominio debe probarse sin BD ni red (repos en memoria, mocks).
- **Bajo acoplamiento**: el núcleo no depende de proveedores concretos.
- **Disponibilidad**: un canal de notificación caído no debe tumbar el registro del hábito.
