# Manual de Usuario

## ¿Qué es Credio?

Credio es un asistente conversacional que evalúa el riesgo crediticio de una solicitud de crédito. El usuario conversa con él en español, de forma natural, y el asistente va recolectando los datos necesarios; cuando ya tiene todo, muestra un resumen para que se confirme, y solo entonces solicita una predicción a un modelo de Machine Learning ya entrenado. El asistente **nunca inventa el resultado**: la evaluación de riesgo siempre la calcula ese modelo, no el chat.

## Cómo acceder

Con el sistema en ejecución (ver `docs/DOCUMENTACION_TECNICA.md` si es necesario iniciarlo), abrir en el navegador:

```
http://localhost:7860
```

Se mostrará una interfaz de chat titulada **Credio**.

## Datos que se solicitarán

A lo largo de la conversación, el asistente necesita estos datos. Pueden entregarse todos de una vez en un solo mensaje, o de a poco, ya que el asistente preguntará por lo que falte.

| #   | Dato                                              | Formato / ejemplo                          |
| --- | ------------------------------------------------- | ------------------------------------------ |
| 1   | Ingreso anual bruto                               | Un número, en dólares (ej. 38000)          |
| 2   | Salario neto mensual                              | Un número, en dólares (ej. 3100)           |
| 3   | Antigüedad del historial crediticio               | Meses (ej. 78)                             |
| 4   | Total en cuotas mensuales fijas que ya paga       | Un número, en dólares (ej. 65.7)           |
| 5   | Tasa de interés                                   | Un número o porcentaje (ej. 13.5%)         |
| 6   | Número de préstamos activos                       | Un entero (ej. 3)                          |
| 7   | Días de atraso desde la fecha de vencimiento      | Un entero (ej. 18; 0 si nunca hubo atraso) |
| 8   | Número de consultas de crédito realizadas         | Un entero (ej. 5)                          |
| 9   | Mezcla de crédito                                 | Buena, Estándar o Mala                     |
| 10  | Deuda pendiente total                             | Un número, en dólares (ej. 1200)           |
| 11  | Porcentaje del crédito disponible que está usando | Un porcentaje (ej. 32.5%)                  |
| 12  | Si paga el monto mínimo de sus deudas             | Sí o No                                    |
| 13  | Saldo promedio que le queda al final del mes      | Un número, en dólares (ej. 340)            |
| 14  | Patrón de gasto                                   | Bajo o Alto                                |
| 15  | Patrón de pago                                    | Pequeño, Medio o Grande                    |

No es necesario usar estas palabras exactas: el asistente entiende variaciones naturales ("gano 45 mil al año", "sí pago siempre a tiempo", "uso como el 30% de mi límite", etc.) y también convierte a dólares si el monto se indica en otra moneda.

## Ejemplo de cómo se ve una conversación típica

**Usuario:**

> Gano 45000 dólares al año y mi salario neto mensual es de 3200. Mi historial crediticio tiene 60 meses de antigüedad. Pago 400 al mes en cuotas fijas. Mi tasa de interés es del 18%. Tengo 2 préstamos activos. Llevo 10 días de atraso en mis pagos. Me han hecho 4 consultas de crédito. Mi mezcla de crédito es estándar. Debo 1200 dólares en total. Estoy usando el 55% de mi crédito disponible. Sí pago el monto mínimo siempre. Mi saldo promedio a fin de mes es de 250 dólares. Gasto poco normalmente, y mis pagos suelen ser de valor mediano.

**Credio** (si falta algo, lo solicita; si ya tiene los 15 datos, muestra un resumen):

> Ya se recopilaron todos los datos necesarios. Este es el resumen:
>
> - Ingreso anual bruto: 45000.0
> - Salario neto mensual: 3200.0
> - ... (los 15 datos)
>
> ¿Son correctos estos datos? (sí/no)

**Usuario:**

> Sí, todo correcto

**Credio**:

> Se completó la evaluación de su solicitud. Su perfil crediticio es considerado bajo riesgo, por lo que se aprueba su solicitud con condiciones estándar. Es importante seguir siendo responsable con sus finanzas...

## Confirmación de Datos

Antes de predecir, Credio siempre muestra el resumen completo de los 15 datos y pregunta si son correctos. Esto es intencional: le da al usuario la oportunidad de corregir cualquier dato mal interpretado para evitar calcular un resultado con información equivocada.

- Si la respuesta es algo como **"sí", "correcto", "así es"**, entonces se ejecuta la predicción.
- Si la respuesta es algo como **"no", "en realidad es...", "eso está mal"**, entonces el asistente pide que se indique qué corregir. Al indicar el dato correcto (ej. "mi salario en realidad es 4000"), el asistente vuelve a mostrar el resumen actualizado para confirmar de nuevo.
- Si la respuesta no es un sí/no claro, entonces el asistente vuelve a preguntar.

## Qué significa el resultado

El modelo clasifica el riesgo en tres niveles, cada uno con una acción asociada:

| Nivel de riesgo | Qué significa                                                 |
| --------------- | ------------------------------------------------------------- |
|    **Bajo**     | Se aprueba la solicitud con condiciones estándar.             |
|    **Medio**    | Se solicita documentación adicional y se evalúa nuevamente.   |
|    **Alto**     | Se rechaza la solicitud y se recomienda educación financiera. |

El texto exacto que se muestra lo redacta el asistente en el momento, pero siempre respeta esa política de fondo según el nivel que haya devuelto el modelo.

## Empezar de nuevo

Una vez completada una evaluación (se confirma y el modelo entrega un resultado), la conversación se reinicia automáticamente, es decir, se puede empezar a describir una nueva solicitud desde cero en el mismo chat.
