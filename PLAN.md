# Plan de Aplicación: Diagnóstico Ley 1581 de 2012

## Descripción

Plataforma web que diagnostica el estado actual de cumplimiento de la Ley 1581 de 2012 (Protección de Datos Personales) en organizaciones colombianas. Permite ejecutar un cuestionario estructurado asistido por IA, calcular un porcentaje de cumplimiento, generar recomendaciones automáticas y hacer seguimiento a un plan de acción.

---

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Frontend | React + Vite + Tailwind CSS + shadcn/ui |
| Backend | Python + FastAPI |
| DB | PostgreSQL |
| Auth | Supabase (email/password + JWT, OAuth2 Google) |
| IA | Capa agnóstica (OpenAI/Anthropic/Gemini intercambiables) |
| Reportes | `reportlab` (PDF) + `openpyxl` (Excel) |
| Deploy | Docker + docker-compose |

---

## Arquitectura General

```
┌─────────────────────────────────────────────────┐
│  Frontend (React + Vite)                        │
│  - Auth (Supabase email/password, Google)       │
│  - Onboarding (creación de empresa)             │
│  - Dashboard corporativo                        │
│  - Cuestionario interactivo con IA              │
│  - Reportes y plan de acción                    │
└──────────────┬──────────────────────────────────┘
               │ REST API + Supabase JWT
┌──────────────▼──────────────────────────────────┐
│  Backend (FastAPI)                              │
│  - Auth (verificación JWT Supabase)             │
│  - Multi-tenant middleware                      │
│  - Cuestionario engine                          │
│  - IA service (agnóstico)                       │
│  - Report generator                             │
│  - Action plan tracker                          │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│  PostgreSQL                                     │
│  - Users, Companies, Roles                      │
│  - Assessments, Answers, Scores                 │
│  - Action Plans, Recommendations                │
└─────────────────────────────────────────────────┘
```

---

## Modelo de Datos

```
users (shadow table — id = Supabase UUID)
├── id (UUID, FK a Supabase auth.users)
├── email, name
├── created_at, updated_at

companies (tenants)
├── id, name, nit, sector, size, contact_email
├── employee_count, db_count, data_types_processed
├── created_at

user_company_roles
├── user_id, company_id, role (admin/auditor/reader)
├── created_at

assessments (diagnósticos)
├── id, company_id, created_by, status (in_progress/completed)
├── overall_score, completed_at
├── created_at, updated_at

assessment_answers
├── id, assessment_id, section_id, question_id
├── answer (yes/no/partial/na), notes

sections (10 fijas + opcionales)
├── id, name, order, is_optional

questions
├── id, section_id, text, order
├── legal_reference, ai_explanation_prompt

scores
├── id, assessment_id, section_id
├── score, max_score, percentage

recommendations
├── id, assessment_id, section_id
├── ai_generated_text, priority (high/medium/low)

action_items
├── id, recommendation_id, assessment_id
├── status (pending/in_progress/completed)
├── assigned_to (user_id), notes

share_links
├── id, assessment_id, token, expires_at
├── created_by
```

---

## Módulos del Backend (FastAPI)

| Módulo | Responsabilidad |
|--------|----------------|
| `auth` | Verificación JWT Supabase, endpoints `/me` y `/verify` |
| `users` | Shadow table de usuarios (upsert on first action) |
| `companies` | CRUD empresas, onboarding, multi-tenant |
| `roles` | Asignación de roles por empresa (auto-admin al crear) |
| `assessments` | Crear, listar, completar diagnósticos |
| `questions` | Secciones y preguntas del cuestionario |
| `answers` | Guardado automático de respuestas |
| `scoring` | Cálculo de puntajes por sección y global |
| `ai_service` | Capa agnóstica: explicaciones + recomendaciones |
| `reports` | Generación PDF/Excel, links compartibles |
| `action_plans` | CRUD items de acción, seguimiento |

---

## Lógica de Scoring

##  Escala General de Valoración por Pregunta

Para cada pregunta (a excepción de las de control o validación), se aplicará la siguiente escala de madurez para determinar el porcentaje de puntos obtenidos sobre el peso asignado a la pregunta:

* **Nivel 0: No implementado (0%)** — No existe evidencia, procesos ni documentación al respecto.
* **Nivel 1: Inicial / En desarrollo (35%)** — Existen esfuerzos aislados, borradores o se encuentra en fase de diseño, pero no está operativo.
* **Nivel 2: Implementado Parcialmente (70%)** — El proceso existe y está operativo, pero le falta formalización, difusión, automatización o no cubre a toda la organización.
* **Nivel 3: Totalmente Implementado (100%)** — Proceso formalizado, documentado, difundido, en ejecución regular y con revisiones periódicas.

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


##  Matriz de Interpretación del Resultado

Dependiendo del **Porcentaje Final** obtenido, la organización se clasifica en uno de los siguientes rangos de madurez en cumplimiento de privacidad:

*  **De 0% a 39% — Nivel Crítico (Riesgo Alto):** La organización carece de una estructura mínima de protección de datos. Existe un alto riesgo de sanciones legales, multas y brechas de seguridad catastróficas. Se requiere intervención inmediata de la alta dirección.
*  **De 40% a 69% — Nivel Básico (Cumplimiento Reactivo):** Se cuenta con políticas elementales escritas, pero la operación diaria no aplica los principios de privacidad de forma sistemática. La protección se ejecuta de manera reactiva ante incidentes.
*  **De 70% a 89% — Nivel Avanzado (Cumplimiento Proactivo):** Existe una gobernanza clara y las políticas están integradas en la mayoría de los procesos tecnológicos y organizacionales. Se gestionan los riesgos de manera estructurada con margen menor de optimización.
*  **De 90% a 100% — Nivel Optimizado (Liderazgo en Privacidad):** La cultura de protección de datos personales está completamente embebida en el ADN de la organización. Las prácticas de minimización, privacidad por defecto y auditorías recurrentes garantizan resiliencia y ventaja competitiva.

---

## Integración IA (Capa Agnóstica)

```python
# ai_service.py - interfaz unificada
class AIService(Protocol):
    async def explain_question(question, company_context) -> str
    async def suggest_answer(question, company_context, prior_answers) -> str
    async def generate_recommendations(assessment_results) -> list[Recommendation]
    async def generate_action_plan(recommendations) -> list[ActionItem]
```

### Funcionalidades IA

- **En tiempo real**: Al hacer clic en "Explicar" en cada pregunta, llama a `explain_question`. Al hacer clic en "Sugerir", llama a `suggest_answer` basada en contexto previo.
- **Al finalizar**: `generate_recommendations` + `generate_action_plan` con todas las respuestas del diagnóstico.

---

## Páginas del Frontend

| Ruta | Descripción |
|------|-------------|
| `/login` | Pantalla de login con email/password (Supabase) |
| `/register` | Registro de usuario con email/password |
| `/onboarding` | Creación obligatoria de empresa (nombre, NIT, sector, tamaño) |
| `/dashboard` | Vista general: último diagnóstico, score, tendencias |
| `/company/profile` | Datos de la empresa |
| `/company/switch` | Cambiar de empresa (multi-tenant) |
| `/assessment/new` | Iniciar nuevo diagnóstico |
| `/assessment/:id` | Cuestionario interactivo (guardado auto) |
| `/assessment/:id/results` | Resultados: score global + por sección + gráficos |
| `/assessment/:id/recommendations` | Recomendaciones IA + plan de acción |
| `/assessment/:id/action-plan` | Checklist de seguimiento |
| `/assessment/:id/export` | Exportar PDF/Excel/link |
| `/admin/users` | Gestión de usuarios de la empresa |
| `/history` | Histórico de diagnósticos |

### Flujo de Onboarding

Después del registro o login, si el usuario no tiene empresas asociadas, es redirigido automáticamente a `/onboarding` donde debe crear su primera empresa. El usuario creador es asignado automáticamente como **admin**.

**Campos del formulario de onboarding:**
- Nombre de la empresa (requerido)
- NIT (requerido, texto libre)
- Sector (Tecnología, Salud, Finanzas, Comercio, Manufactura, Educación, Gobierno, Otro)
- Tamaño (Micro 1-10, Pequeña 11-50, Mediana 51-200, Grande 200+)

**Lógica de redirección (ProtectedRoute):**
- Auth cargando → spinner
- No autenticado → `/login`
- Autenticado sin empresas → `/onboarding`
- Autenticado con empresas → renderizar contenido

---

## Componentes Clave del Cuestionario

- **Barra de progreso** por sección y global
- **Botón "Explicar"** en cada pregunta → tooltip/modal con explicación IA del contexto legal
- **Botón "Sugerir"** → IA sugiere respuesta basada en contexto previo de la empresa
- **Guardado automático** en cada cambio (debounce 500ms)
- **Navegación libre** entre secciones

---

## Cuestionario de Diagnóstico de Cumplimiento – Ley 1581 de 2012

## Estructura General del Diagnóstico

| Bloque | Descripción | Peso Máximo |
| :--- | :--- | :---: |
| **Bloque 1** | Política de datos personales | 40% |
| **Bloque 2** | Privacidad desde el diseño | 36% |
| **Bloque 3** | Gobernanza | 24% |
| **TOTAL** | **Evaluación Integral** | **100%** |

## Bloque 1: Política de Datos Personales (Peso Total: 40%)

Este bloque verifica la existencia, accesibilidad, calidad y el contenido mínimo legal de la política de tratamiento de datos personales.

### Pregunta 1: Pregunta Principal (Filtro)
**¿Cuenta con una política de tratamiento de datos personales?**
* **[ ] Sí** *(Permite evaluar las preguntas 2 a 5)*
* **[ ] No** *(Automáticamente las preguntas 2, 3, 4 y 5 obtienen un puntaje de 0%)*
* *Observación:* Esta pregunta opera como habilitadora. Si la respuesta es "No", el puntaje total de este bloque es 0%.

### Pregunta 2
**¿La política está documentada y publicada en un medio de fácil acceso?**
* **Peso de la pregunta:** 10% del total general.
* **Opciones de Respuesta y Valoración:**
    * [ ] **No (0%)**: No está documentada ni publicada. (0 puntos)
    * [ ] **Inicial (35%)**: Está documentada en borrador interno, pero no se ha publicado ni difundido. (3.5 puntos)
    * [ ] **Parcial (70%)**: Está aprobada y publicada, pero su acceso es difícil para el titular (ej. oculta en menús secundarios) o solo se encuentra en canales físicos restringidos. (7.0 puntos)
    * [ ] **Total (100%)**: Está formalmente aprobada, actualizada y publicada en la página web principal y canales de atención de manera visible y accesible de un solo clic. (10.0 puntos)

### Pregunta 3
**¿Define las finalidades del tratamiento de datos?**
* **Peso de la pregunta:** 10% del total general.
* **Opciones de Respuesta y Valoración:**
    * [ ] **No (0%)**: No se mencionan las finalidades para las cuales se recolectan los datos. (0 puntos)
    * [ ] **Inicial (35%)**: Se mencionan de forma genérica y ambigua (ej. "para fines comerciales y operativos") sin especificar el alcance real. (3.5 puntos)
    * [ ] **Parcial (70%)**: Se definen las finalidades de forma detallada para algunos tipos de titulares (ej. clientes), pero se omiten otros grupos (ej. empleados, proveedores). (7.0 puntos)
    * [ ] **Total (100%)**: Se definen de manera clara, explícita, específica y lícita las finalidades del tratamiento para cada categoría de titular de datos. (10.0 puntos)

### Pregunta 4
**¿Incluye los derechos de los titulares?**
* **Peso de la pregunta:** 10% del total general.
* **Opciones de Respuesta y Valoración:**
    * [ ] **No (0%)**: No se mencionan los derechos de los usuarios/titulares en el documento. (0 puntos)
    * [ ] **Inicial (35%)**: Se hace una mención genérica a la ley de privacidad, pero no se listan explícitamente cuáles son los derechos. (3.5 puntos)
    * [ ] **Parcial (70%)**: Se listan los derechos básicos (Acceso, Rectificación), pero se omiten derechos modernos o locales específicos (ej. Cancelación, Oposición, Portabilidad, Supresión). (7.0 puntos)
    * [ ] **Total (100%)**: Se desglosan de forma taxativa y clara todos los derechos aplicables que le asisten al titular bajo la normatividad vigente. (10.0 puntos)

### Pregunta 5
**¿Menciona cómo ejercer los derechos de los titulares?**
* **Peso de la pregunta:** 10% del total general.
* **Opciones de Respuesta y Valoración:**
    * [ ] **No (0%)**: No establece canales ni procedimientos para que los usuarios radiquen consultas o reclamos. (0 puntos)
    * [ ] **Inicial (35%)**: Menciona que se pueden ejercer los derechos, pero no provee ningún canal de contacto (correo, teléfono o dirección). (3.5 puntos)
    * [ ] **Parcial (70%)**: Indica un canal de contacto (ej. un correo electrónico institucional genérico), pero no define el procedimiento interno, los requisitos del mensaje ni los tiempos de respuesta. (7.0 puntos)
    * [ ] **Total (100%)**: Define canales específicos y gratuitos (correo exclusivo, formularios), junto con un procedimiento claro, los requisitos de la solicitud y los tiempos de respuesta estipulados por ley. (10.0 puntos)

## Bloque 2: Privacidad desde el Diseño (Peso Total: 36%)

Evalúa si la empresa incorpora de forma proactiva y por defecto principios y técnicas de ingeniería de privacidad desde las etapas tempranas de sus proyectos y sistemas.

### Pregunta 6
**¿Incorpora evaluaciones de impacto (Privacy Impact Assessments - PIA)?**
* **Peso de la pregunta:** 12% del total general.
* **Opciones de Respuesta y Valoración:**
    * [ ] **No (0%)**: No se realizan evaluaciones de impacto bajo ningún escenario. (0 puntos)
    * [ ] **Inicial (35%)**: Se analizan los riesgos de privacidad de manera informal en reuniones, pero no hay metodologías ni registros documentados. (4.2 puntos)
    * [ ] **Parcial (70%)**: Se ejecutan metodologías de evaluación de impacto de manera reactiva, únicamente cuando ocurre un incidente o ante un requerimiento legal estricto. (8.4 puntos)
    * [ ] **Total (100%)**: Se cuenta con una política y plantilla formal de PIA que se aplica obligatoriamente a todo nuevo producto, servicio, software o tratamiento de datos de alto riesgo antes de su implementación. (12.0 puntos)

### Pregunta 7
**¿Aplica técnicas de minimización de datos?**
* **Peso de la pregunta:** 12% del total general.
* **Opciones de Respuesta y Valoración:**
    * [ ] **No (0%)**: Se recolectan y almacenan todos los datos posibles bajo la premisa de "por si se necesitan en el futuro". (0 puntos)
    * [ ] **Inicial (35%)**: Existe la directriz teórica de no pedir datos innecesarios, pero no se ha revisado si los formularios actuales la cumplen. (4.2 puntos)
    * [ ] **Parcial (70%)**: Se han depurado algunos formularios o bases de datos reduciendo campos innecesarios, pero no es una práctica estandarizada en el desarrollo técnico. (8.4 puntos)
    * [ ] **Total (100%)**: Cada base de datos, API y formulario de recolección pasa por un proceso de validación técnica donde se demuestra la estricta necesidad e idoneidad de cada dato solicitado respecto a la finalidad. (12.0 puntos)

### Pregunta 8
**¿Configura sus sistemas para recopilar el mínimo de datos por defecto (Privacy by Default)?**
* **Peso de la pregunta:** 12% del total general.
* **Opciones de Respuesta y Valoración:**
    * [ ] **No (0%)**: Al registrarse o usar un sistema, las casillas de consentimiento masivo, cookies de rastreo y transferencia de datos vienen preactivadas (óptica *Opt-out* agresiva). (0 puntos)
    * [ ] **Inicial (35%)**: Las plataformas se configuran bajo criterios comerciales estándar y solo se modifican si el usuario lo solicita expresamente. (4.2 puntos)
    * [ ] **Parcial (70%)**: Se han configurado medidas por defecto en canales digitales principales (ej. la web pública), pero los sistemas internos o aplicaciones móviles siguen viniendo con configuraciones permisivas por defecto. (8.4 puntos)
    * [ ] **Total (100%)**: Todas las aplicaciones e infraestructuras están configuradas para que, de forma automática e inicial, solo se procesen los datos estrictamente necesarios para la actividad, requiriendo una acción positiva del usuario (*Opt-in*) para cualquier tratamiento adicional. (12.0 puntos)

##  Bloque 3: Gobernanza (Peso Total: 24%)

Evalúa la estructura organizacional, la asignación de responsabilidades internas y la gestión proactiva de riesgos para garantizar la protección de los datos.

### Pregunta 9
**¿Cuenta con un sistema de administración de riesgos asociados al tratamiento de datos personales?**
* **Peso de la pregunta:** 16% del total general.
* **Opciones de Respuesta y Valoración:**
    * [ ] **No (0%)**: No se identifican, miden ni gestionan los riesgos de brechas de seguridad o pérdidas de privacidad de manera estructurada. (0 puntos)
    * [ ] **Inicial (35%)**: Los riesgos de privacidad están diluidos dentro de la matriz general de riesgos tecnológicos de la empresa, sin controles específicos para datos personales. (5.6 puntos)
    * [ ] **Parcial (70%)**: Se cuenta con una matriz de riesgos específica de protección de datos, pero no se actualiza periódicamente ni cuenta con planes de acción o responsables asignados para la mitigación. (11.2 puntos)
    * [ ] **Total (100%)**: Se tiene un Sistema de Gestión de Seguridad de la Información (SGSI) o modelo de administración de riesgos vivo, con revisiones semestrales o anuales, indicadores de exposición, planes de respuesta ante incidentes y controles técnicos/operativos auditados. (16.0 puntos)

### Pregunta 10
**¿Cuenta con un Oficial de Protección de Datos Personales (DPO / Data Protection Officer)?**
* **Peso de la pregunta:** 8% del total general.
* **Opciones de Respuesta y Valoración:**
    * [ ] **No (0%)**: No hay ninguna persona o área asignada para vigilar el cumplimiento de la privacidad. (0 puntos)
    * [ ] **Inicial (35%)**: Se asume de manera informal que el área Legal o de TI se encarga, pero ningún colaborador tiene la función asignada explícitamente dentro de su perfil laboral. (2.8 puntos)
    * [ ] **Parcial (70%)**: Se ha delegado la función a un comité interno o a un empleado como recarga de funciones, pero este no cuenta con autonomía, presupuesto ni tiempo suficiente dedicado a la tarea. (5.6 puntos)
    * [ ] **Total (100%)**: Existe un Oficial de Protección de Datos (interno o externo) designado explícitamente, con línea directa de reporte a la alta dirección, autonomía, recursos técnicos y capacidad para liderar el programa de cumplimiento. (8.0 puntos)

### Pregunta 11: Pregunta Complementaria (Validación)
**¿Está designado formalmente el Oficial de Protección de Datos?**
* **Peso de la pregunta:** 0% *(No altera numéricamente el porcentaje final)*.
* **Opciones de Respuesta:**
    * [ ] **Sí**: Existe un acta de junta directiva, resolución, contrato o designación firmada y notificada internamente (y ante la autoridad reguladora si aplica legalmente).
    * [ ] **No**: Fue una designación verbal o circunstancial, sin soporte documental que valide su cargo ante una auditoría exterior.
* *Observación:* Esta pregunta sirve como mecanismo de control para auditar la robustez legal de la respuesta dada en la Pregunta 10.

---

## Seguridad (OWASP)

- JWT Supabase con expiración corta + refresh token automático
- Verificación JWT en backend (ES256 vía JWKS o HS256 fallback)
- HTTPS obligatorio
- Rate limiting en API
- Sanitización de inputs
- CORS configurado por dominio
- Datos de diferentes tenants aislados por middleware
- Variables de entorno para secrets

---

## Roles de Usuario

| Rol | Permisos |
|-----|----------|
| **Admin** | Gestiona empresa, usuarios, crea diagnósticos, ve reportes, gestiona plan de acción |
| **Auditor** | Responde cuestionario, ve reportes, gestiona plan de acción |
| **Lector** | Solo visualiza reportes y estado del plan de acción |

---

## Reportes y Exportación

- **PDF**: Reporte formal con gráficos de radar por sección, score global, recomendaciones priorizadas
- **Excel**: Datos detallados por pregunta, sección, puntajes, para análisis interno
- **Link compartible**: URL con token de expiración para compartir resultados con terceros

---

## Plan de Acción (Checklist)

- Cada recomendación se convierte en un item de acción
- Estados: `Pendiente` → `En progreso` → `Completada`
- Sin fechas límite (MVP)
- Asignación de responsable por item
- Notas/observaciones por item

---

## Estructura de Archivos

```
reto_hackaton/
├── docker-compose.yml
├── .env.example
├── PLAN.md
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── index.html
│   ├── public/
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── index.css            # Tailwind + custom component classes
│       ├── api/                 # Cliente API (axios)
│       │   ├── client.ts        # Axios instance + interceptors
│       │   └── companies.ts     # API de empresas
│       ├── components/          # Componentes reutilizables
│       │   ├── ui/              # shadcn/ui components
│       │   ├── ProtectedRoute.tsx  # Auth guard + onboarding redirect
│       │   ├── layout/          # Header, Sidebar, Layout
│       │   ├── assessment/      # QuestionCard, SectionNav, ProgressBar
│       │   ├── dashboard/       # ScoreCard, RadarChart, TrendChart
│       │   └── action-plan/     # ActionItem, ChecklistView
│       ├── hooks/               # Custom hooks
│       ├── pages/               # Páginas/rutas
│       │   ├── LoginPage.tsx
│       │   ├── RegisterPage.tsx
│       │   ├── OnboardingPage.tsx  # Creación de empresa (forzada)
│       │   ├── DashboardPage.tsx
│       │   ├── CompanyProfilePage.tsx
│       │   ├── AssessmentPage.tsx
│       │   ├── ResultsPage.tsx
│       │   ├── RecommendationsPage.tsx
│       │   ├── ActionPlanPage.tsx
│       │   ├── ExportPage.tsx
│       │   ├── AdminUsersPage.tsx
│       │   └── HistoryPage.tsx
│       ├── stores/              # Estado global (zustand)
│       │   ├── authStore.ts     # Sesión Supabase
│       │   └── companyStore.ts  # Empresas del usuario + empresa seleccionada
│       ├── types/               # Tipos TypeScript
│       │   └── company.ts       # Company, CompanyCreate, CompanyListItem
│       └── lib/                 # Utilidades
│           └── supabase.ts      # Cliente Supabase JS
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml           # Dependencias (uv)
│   ├── uv.lock
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Settings (pydantic-settings)
│   │   ├── database.py          # SQLAlchemy engine + session
│   │   ├── dependencies.py      # Verificación JWT Supabase (ES256/HS256)
│   │   ├── models/              # Modelos SQLAlchemy
│   │   │   ├── user.py          # Shadow table (id=Supabase UUID)
│   │   │   ├── company.py       # Company + UserCompanyRole
│   │   │   ├── assessment.py
│   │   │   ├── question.py
│   │   │   ├── recommendation.py
│   │   │   └── action_item.py
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── company.py       # CompanyCreate, CompanyRead, CompanyListItem
│   │   │   ├── assessment.py
│   │   │   ├── question.py
│   │   │   └── report.py
│   │   ├── routers/             # Endpoints
│   │   │   ├── auth.py          # GET /me, GET /verify
│   │   │   ├── companies.py     # GET /, POST /, GET /{id}
│   │   │   ├── assessments.py
│   │   │   ├── questions.py
│   │   │   ├── reports.py
│   │   │   └── action_plans.py
│   │   ├── services/            # Lógica de negocio
│   │   │   ├── company_service.py  # Upsert user + create company + assign admin
│   │   │   ├── assessment_service.py
│   │   │   ├── scoring_service.py
│   │   │   └── report_service.py
│   │   ├── ai/                  # Servicio IA agnóstico
│   │   │   ├── base.py          # Protocol/Interface
│   │   │   ├── openai_provider.py
│   │   │   ├── anthropic_provider.py
│   │   │   └── gemini_provider.py
│   │   ├── reports/             # Generadores PDF/Excel
│   │   │   ├── pdf_generator.py
│   │   │   └── excel_generator.py
│   │   └── middleware/          # Multi-tenant, auth
│   │       └── tenant_middleware.py
│   └── alembic/                 # Migraciones DB
│       ├── alembic.ini
│       ├── env.py
│       └── versions/
└── nginx/
    └── nginx.conf
```

---

## Orden de Implementación

| Fase | Tareas |
|------|--------|
| **1. Setup + Auth** | Docker, docker-compose, DB, Supabase auth (frontend login/register), JWT verification (backend) |
| **2. Modelos + Onboarding** | Users (shadow table), Companies, UserCompanyRole, Alembic migration, API CRUD empresas, onboarding forzado (frontend) |
| **3. Cuestionario** | Secciones, preguntas, respuestas, guardado automático |
| **4. Scoring** | Cálculo de puntajes por sección, global, porcentaje, matriz de madurez |
| **5. IA** | Integración agnóstica: explicaciones en tiempo real + recomendaciones finales |
| **6. Reportes** | Generación PDF, Excel, links compartibles con token |
| **7. Plan de acción** | CRUD items de acción, checklist con estados, asignación |
| **8. Dashboard** | Gráficos (radar, barras, tendencia), histórico, UI completa |
| **9. Seguridad + Polish** | OWASP checks, responsive, manejo de errores, validaciones |

---

## Requerimientos Funcionales

1. **Registro e inicio de sesión** mediante Supabase (email/password)
2. **Onboarding obligatorio**: creación de empresa (nombre, NIT, sector, tamaño) tras registro o login sin empresas
3. **Captura de información básica de la empresa** (nombre, NIT, sector, tamaño, contacto, cantidad empleados, bases de datos, tipos de datos)
4. **Ejecución de cuestionario estructurado** con 10 secciones fijas + secciones opcionales
5. **Asistencia por IA** para explicar preguntas y sugerir respuestas en tiempo real
6. **Generación de recomendaciones automáticas** por IA al completar el diagnóstico
7. **Cálculo de resultado porcentual** de cumplimiento con matriz de madurez
8. **Diagnóstico visual claro** con gráficos de radar por sección y score global
9. **Estrategias para cerrar brechas** mediante plan de acción con checklist
10. **Seguimiento del plan de acción** con estados y asignación de responsables
11. **Exportación de reportes** en PDF, Excel y link compartible
12. **Multi-empresa** con roles (Admin, Auditor, Lector) — un usuario puede registrar múltiples empresas
13. **Guardado automático** del progreso del cuestionario
14. **Histórico de diagnósticos** por empresa

## Requerimientos No Funcionales

1. **Fácil de usar** y amigable (UX intuitiva)
2. **Segura** (OWASP, Supabase JWT, HTTPS, aislamiento de tenants)
3. **Escalable** (multiempresa, arquitectura modular)
4. **Basada en buenas prácticas** (OWASP, privacidad por diseño)
5. **Portable** (Docker, desplegable en cualquier cloud)
