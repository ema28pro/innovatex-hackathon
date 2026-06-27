# Cuestionario de Diagnóstico de Protección de Datos Personales y Privacidad

Este documento contiene la estructura completa del diagnóstico de cumplimiento en protección de datos personales. Está diseñado de forma cuantitativa para evaluar el nivel de madurez de la organización a través de tres bloques clave, asignando un puntaje ponderado a cada respuesta para calcular un porcentaje de cumplimiento final.

---

## 📊 Estructura General del Diagnóstico

| Bloque | Descripción | Peso Máximo |
| :--- | :--- | :---: |
| **Bloque 1** | Política de datos personales | 40% |
| **Bloque 2** | Privacidad desde el diseño | 36% |
| **Bloque 3** | Gobernanza | 24% |
| **TOTAL** | **Evaluación Integral** | **100%** |

---

## ⚙️ Escala General de Valoración por Pregunta

Para cada pregunta (a excepción de las de control o validación), se aplicará la siguiente escala de madurez para determinar el porcentaje de puntos obtenidos sobre el peso asignado a la pregunta:

* **Nivel 0: No implementado (0%)** — No existe evidencia, procesos ni documentación al respecto.
* **Nivel 1: Inicial / En desarrollo (35%)** — Existen esfuerzos aislados, borradores o se encuentra en fase de diseño, pero no está operativo.
* **Nivel 2: Implementado Parcialmente (70%)** — El proceso existe y está operativo, pero le falta formalización, difusión, automatización o no cubre a toda la organización.
* **Nivel 3: Totalmente Implementado (100%)** — Proceso formalizado, documentado, difundido, en ejecución regular y con revisiones periódicas.

---

## 📂 Bloque 1: Política de Datos Personales (Peso Total: 40%)

Este bloque verifica la existencia, accesibilidad, calidad y el contenido mínimo legal de la política de tratamiento de datos personales.

### Pregunta 1: Pregunta Principal (Filtro)
**¿Cuenta con una política de tratamiento de datos personales?**
* **[ ] Sí** *(Permite evaluar las preguntas 2 a 5)*
* **[ ] No** *(Automáticamente las preguntas 2, 3, 4 y 5 obtienen un puntaje de 0%)*
* *Observación:* Esta pregunta opera como habilitadora. Si la respuesta es "No", el puntaje total de este bloque es 0%.

---

### Pregunta 2
**¿La política está documentada y publicada en un medio de fácil acceso?**
* **Peso de la pregunta:** 10% del total general.
* **Opciones de Respuesta y Valoración:**
    * [ ] **No (0%)**: No está documentada ni publicada. (0 puntos)
    * [ ] **Inicial (35%)**: Está documentada en borrador interno, pero no se ha publicado ni difundido. (3.5 puntos)
    * [ ] **Parcial (70%)**: Está aprobada y publicada, pero su acceso es difícil para el titular (ej. oculta en menús secundarios) o solo se encuentra en canales físicos restringidos. (7.0 puntos)
    * [ ] **Total (100%)**: Está formalmente aprobada, actualizada y publicada en la página web principal y canales de atención de manera visible y accesible de un solo clic. (10.0 puntos)

---

### Pregunta 3
**¿Define las finalidades del tratamiento de datos?**
* **Peso de la pregunta:** 10% del total general.
* **Opciones de Respuesta y Valoración:**
    * [ ] **No (0%)**: No se mencionan las finalidades para las cuales se recolectan los datos. (0 puntos)
    * [ ] **Inicial (35%)**: Se mencionan de forma genérica y ambigua (ej. "para fines comerciales y operativos") sin especificar el alcance real. (3.5 puntos)
    * [ ] **Parcial (70%)**: Se definen las finalidades de forma detallada para algunos tipos de titulares (ej. clientes), pero se omiten otros grupos (ej. empleados, proveedores). (7.0 puntos)
    * [ ] **Total (100%)**: Se definen de manera clara, explícita, específica y lícita las finalidades del tratamiento para cada categoría de titular de datos. (10.0 puntos)

---

### Pregunta 4
**¿Incluye los derechos de los titulares?**
* **Peso de la pregunta:** 10% del total general.
* **Opciones de Respuesta y Valoración:**
    * [ ] **No (0%)**: No se mencionan los derechos de los usuarios/titulares en el documento. (0 puntos)
    * [ ] **Inicial (35%)**: Se hace una mención genérica a la ley de privacidad, pero no se listan explícitamente cuáles son los derechos. (3.5 puntos)
    * [ ] **Parcial (70%)**: Se listan los derechos básicos (Acceso, Rectificación), pero se omiten derechos modernos o locales específicos (ej. Cancelación, Oposición, Portabilidad, Supresión). (7.0 puntos)
    * [ ] **Total (100%)**: Se desglosan de forma taxativa y clara todos los derechos aplicables que le asisten al titular bajo la normatividad vigente. (10.0 puntos)

---

### Pregunta 5
**¿Menciona cómo ejercer los derechos de los titulares?**
* **Peso de la pregunta:** 10% del total general.
* **Opciones de Respuesta y Valoración:**
    * [ ] **No (0%)**: No establece canales ni procedimientos para que los usuarios radiquen consultas o reclamos. (0 puntos)
    * [ ] **Inicial (35%)**: Menciona que se pueden ejercer los derechos, pero no provee ningún canal de contacto (correo, teléfono o dirección). (3.5 puntos)
    * [ ] **Parcial (70%)**: Indica un canal de contacto (ej. un correo electrónico institucional genérico), pero no define el procedimiento interno, los requisitos del mensaje ni los tiempos de respuesta. (7.0 puntos)
    * [ ] **Total (100%)**: Define canales específicos y gratuitos (correo exclusivo, formularios), junto con un procedimiento claro, los requisitos de la solicitud y los tiempos de respuesta estipulados por ley. (10.0 puntos)

---

## 📂 Bloque 2: Privacidad desde el Diseño (Peso Total: 36%)

Evalúa si la empresa incorpora de forma proactiva y por defecto principios y técnicas de ingeniería de privacidad desde las etapas tempranas de sus proyectos y sistemas.

### Pregunta 6
**¿Incorpora evaluaciones de impacto (Privacy Impact Assessments - PIA)?**
* **Peso de la pregunta:** 12% del total general.
* **Opciones de Respuesta y Valoración:**
    * [ ] **No (0%)**: No se realizan evaluaciones de impacto bajo ningún escenario. (0 puntos)
    * [ ] **Inicial (35%)**: Se analizan los riesgos de privacidad de manera informal en reuniones, pero no hay metodologías ni registros documentados. (4.2 puntos)
    * [ ] **Parcial (70%)**: Se ejecutan metodologías de evaluación de impacto de manera reactiva, únicamente cuando ocurre un incidente o ante un requerimiento legal estricto. (8.4 puntos)
    * [ ] **Total (100%)**: Se cuenta con una política y plantilla formal de PIA que se aplica obligatoriamente a todo nuevo producto, servicio, software o tratamiento de datos de alto riesgo antes de su implementación. (12.0 puntos)

---

### Pregunta 7
**¿Aplica técnicas de minimización de datos?**
* **Peso de la pregunta:** 12% del total general.
* **Opciones de Respuesta y Valoración:**
    * [ ] **No (0%)**: Se recolectan y almacenan todos los datos posibles bajo la premisa de "por si se necesitan en el futuro". (0 puntos)
    * [ ] **Inicial (35%)**: Existe la directriz teórica de no pedir datos innecesarios, pero no se ha revisado si los formularios actuales la cumplen. (4.2 puntos)
    * [ ] **Parcial (70%)**: Se han depurado algunos formularios o bases de datos reduciendo campos innecesarios, pero no es una práctica estandarizada en el desarrollo técnico. (8.4 puntos)
    * [ ] **Total (100%)**: Cada base de datos, API y formulario de recolección pasa por un proceso de validación técnica donde se demuestra la estricta necesidad e idoneidad de cada dato solicitado respecto a la finalidad. (12.0 puntos)

---

### Pregunta 8
**¿Configura sus sistemas para recopilar el mínimo de datos por defecto (Privacy by Default)?**
* **Peso de la pregunta:** 12% del total general.
* **Opciones de Respuesta y Valoración:**
    * [ ] **No (0%)**: Al registrarse o usar un sistema, las casillas de consentimiento masivo, cookies de rastreo y transferencia de datos vienen preactivadas (óptica *Opt-out* agresiva). (0 puntos)
    * [ ] **Inicial (35%)**: Las plataformas se configuran bajo criterios comerciales estándar y solo se modifican si el usuario lo solicita expresamente. (4.2 puntos)
    * [ ] **Parcial (70%)**: Se han configurado medidas por defecto en canales digitales principales (ej. la web pública), pero los sistemas internos o aplicaciones móviles siguen viniendo con configuraciones permisivas por defecto. (8.4 puntos)
    * [ ] **Total (100%)**: Todas las aplicaciones e infraestructuras están configuradas para que, de forma automática e inicial, solo se procesen los datos estrictamente necesarios para la actividad, requiriendo una acción positiva del usuario (*Opt-in*) para cualquier tratamiento adicional. (12.0 puntos)

---

## 📂 Bloque 3: Gobernanza (Peso Total: 24%)

Evalúa la estructura organizacional, la asignación de responsabilidades internas y la gestión proactiva de riesgos para garantizar la protección de los datos.

### Pregunta 9
**¿Cuenta con un sistema de administración de riesgos asociados al tratamiento de datos personales?**
* **Peso de la pregunta:** 16% del total general.
* **Opciones de Respuesta y Valoración:**
    * [ ] **No (0%)**: No se identifican, miden ni gestionan los riesgos de brechas de seguridad o pérdidas de privacidad de manera estructurada. (0 puntos)
    * [ ] **Inicial (35%)**: Los riesgos de privacidad están diluidos dentro de la matriz general de riesgos tecnológicos de la empresa, sin controles específicos para datos personales. (5.6 puntos)
    * [ ] **Parcial (70%)**: Se cuenta con una matriz de riesgos específica de protección de datos, pero no se actualiza periódicamente ni cuenta con planes de acción o responsables asignados para la mitigación. (11.2 puntos)
    * [ ] **Total (100%)**: Se tiene un Sistema de Gestión de Seguridad de la Información (SGSI) o modelo de administración de riesgos vivo, con revisiones semestrales o anuales, indicadores de exposición, planes de respuesta ante incidentes y controles técnicos/operativos auditados. (16.0 puntos)

---

### Pregunta 10
**¿Cuenta con un Oficial de Protección de Datos Personales (DPO / Data Protection Officer)?**
* **Peso de la pregunta:** 8% del total general.
* **Opciones de Respuesta y Valoración:**
    * [ ] **No (0%)**: No hay ninguna persona o área asignada para vigilar el cumplimiento de la privacidad. (0 puntos)
    * [ ] **Inicial (35%)**: Se asume de manera informal que el área Legal o de TI se encarga, pero ningún colaborador tiene la función asignada explícitamente dentro de su perfil laboral. (2.8 puntos)
    * [ ] **Parcial (70%)**: Se ha delegado la función a un comité interno o a un empleado como recarga de funciones, pero este no cuenta con autonomía, presupuesto ni tiempo suficiente dedicado a la tarea. (5.6 puntos)
    * [ ] **Total (100%)**: Existe un Oficial de Protección de Datos (interno o externo) designado explícitamente, con línea directa de reporte a la alta dirección, autonomía, recursos técnicos y capacidad para liderar el programa de cumplimiento. (8.0 puntos)

---

### Pregunta 11: Pregunta Complementaria (Validación)
**¿Está designado formalmente el Oficial de Protección de Datos?**
* **Peso de la pregunta:** 0% *(No altera numéricamente el porcentaje final)*.
* **Opciones de Respuesta:**
    * [ ] **Sí**: Existe un acta de junta directiva, resolución, contrato o designación firmada y notificada internamente (y ante la autoridad reguladora si aplica legalmente).
    * [ ] **No**: Fue una designación verbal o circunstancial, sin soporte documental que valide su cargo ante una auditoría exterior.
* *Observación:* Esta pregunta sirve como mecanismo de control para auditar la robustez legal de la respuesta dada en la Pregunta 10.

---

## 📈 Sistema de Calificación y Porcentaje Final

Para obtener el puntaje global de cumplimiento, sume los puntos obtenidos en cada una de las 9 preguntas evaluables (P2 a P10).

### Fórmula de Cálculo:

$$\text{Porcentaje Final de Cumplimiento} = \sum_{i=2}^{10} \text{Puntaje Obtenido en P}_i$$

O expresado de forma detallada:

$$\text{Porcentaje Final} = P_2 + P_3 + P_4 + P_5 + P_6 + P_7 + P_8 + P_9 + P_{10}$$

### Tabla de Conversión para el Cálculo Automático/Manual

| Pregunta | Peso Máx. | Si marcas 'No (0%)' | Si marcas 'Inicial (35%)' | Si marcas 'Parcial (70%)' | Si marcas 'Total (100%)' | Tu Puntaje |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **P2** (Publicación) | 10% | 0.0% | 3.5% | 7.0% | 10.0% | |
| **P3** (Finalidades) | 10% | 0.0% | 3.5% | 7.0% | 10.0% | |
| **P4** (Derechos) | 10% | 0.0% | 3.5% | 7.0% | 10.0% | |
| **P5** (Canales) | 10% | 0.0% | 3.5% | 7.0% | 10.0% | |
| **P6** (Impacto-PIA) | 12% | 0.0% | 4.2% | 8.4% | 12.0% | |
| **P7** (Minimización) | 12% | 0.0% | 4.2% | 8.4% | 12.0% | |
| **P8** (Defecto) | 12% | 0.0% | 4.2% | 8.4% | 12.0% | |
| **P9** (Riesgos) | 16% | 0.0% | 5.6% | 11.2% | 16.0% | |
| **P10** (Oficial DPO) | 8% | 0.0% | 2.8% | 5.6% | 8.0% | |
| **P11** (Formalización)| 0% | *Validación*| *Validación* | *Validación* | *Validación* | *N/A* |
| **TOTAL** | **100%**| | | | **Puntaje Sumado:** | **____ %** |

---

## 🚦 Matriz de Interpretación del Resultado

Dependiendo del **Porcentaje Final** obtenido, la organización se clasifica en uno de los siguientes rangos de madurez en cumplimiento de privacidad:

* 🔴 **De 0% a 39% — Nivel Crítico (Riesgo Alto):** La organización carece de una estructura mínima de protección de datos. Existe un alto riesgo de sanciones legales, multas y brechas de seguridad catastróficas. Se requiere intervención inmediata de la alta dirección.
* 🟡 **De 40% a 69% — Nivel Básico (Cumplimiento Reactivo):** Se cuenta con políticas elementales escritas, pero la operación diaria no aplica los principios de privacidad de forma sistemática. La protección se ejecuta de manera reactiva ante incidentes.
* 🟢 **De 70% a 89% — Nivel Avanzado (Cumplimiento Proactivo):** Existe una gobernanza clara y las políticas están integradas en la mayoría de los procesos tecnológicos y organizacionales. Se gestionan los riesgos de manera estructurada con margen menor de optimización.
* 🔵 **De 90% a 100% — Nivel Optimizado (Liderazgo en Privacidad):** La cultura de protección de datos personales está completamente embebida en el ADN de la organización. Las prácticas de minimización, privacidad por defecto y auditorías recurrentes garantizan resiliencia y ventaja competitiva.
