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
| Auth | Supabase (email/password + JWT) |
| IA | Capa agnóstica (OpenAI/Anthropic/Gemini intercambiables) |
| Reportes | `reportlab` (PDF) + `openpyxl` (Excel) |
| Deploy | Docker + docker-compose |

---

## Arquitectura General

```
┌─────────────────────────────────────────────────┐
│  Frontend (React + Vite)                        │
│  - Auth (Supabase email/password)               │
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

- Cada pregunta: `Sí = 1`, `Parcial = 0.5`, `No = 0`
- Puntaje por sección = suma respuestas / total preguntas sección
- Puntaje global = promedio ponderado de secciones (peso igual)
- Porcentaje de cumplimiento = puntaje global × 100
- Matriz de madurez:
  - 0-20% = No existe
  - 21-40% = Inicial
  - 41-60% = Parcialmente implementado
  - 61-80% = Implementado
  - 81-100% = Optimizado

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

### 1. Gobierno y Responsabilidad

1. ¿La empresa ha identificado si actúa como Responsable del Tratamiento, Encargado del Tratamiento o ambos? `[Sí] [No] [Parcial]`
2. ¿Existe un responsable interno para la gestión de protección de datos personales? `[Sí] [No] [Parcial]`
3. ¿Se han definido roles y responsabilidades documentadas sobre tratamiento de datos? `[Sí] [No] [Parcial]`
4. ¿La alta dirección conoce y aprueba las políticas de protección de datos? `[Sí] [No] [Parcial]`

### 2. Inventario y Bases de Datos

1. ¿La empresa tiene inventariadas todas las bases de datos que contienen datos personales? `[Sí] [No] [Parcial]`
2. ¿Se clasifican los datos según su tipo (personales, sensibles, menores de edad)? `[Sí] [No] [Parcial]`
3. ¿Se documenta la finalidad de cada base de datos? `[Sí] [No] [Parcial]`
4. ¿Se identifican los terceros que reciben o procesan datos personales? `[Sí] [No] [Parcial]`

### 3. Autorización y Consentimiento

1. ¿La empresa obtiene autorización previa, expresa e informada para el tratamiento de datos? `[Sí] [No] [Parcial]`
2. ¿Conserva evidencia verificable de las autorizaciones otorgadas? `[Sí] [No] [Parcial]`
3. ¿Los formularios informan claramente la finalidad del tratamiento? `[Sí] [No] [Parcial]`
4. ¿Se informa al titular sobre sus derechos antes de recolectar datos? `[Sí] [No] [Parcial]`

### 4. Política de Tratamiento

1. ¿Existe una política de tratamiento de datos personales vigente? `[Sí] [No] [Parcial]`
2. ¿La política es pública y fácilmente accesible? `[Sí] [No] [Parcial]`
3. ¿Describe finalidades, derechos de titulares y canales de atención? `[Sí] [No] [Parcial]`
4. ¿Se revisa y actualiza periódicamente? `[Sí] [No] [Parcial]`

### 5. Derechos de los Titulares

1. ¿Existe un procedimiento para consultas de titulares? `[Sí] [No] [Parcial]`
2. ¿Las consultas se atienden dentro de los plazos legales? `[Sí] [No] [Parcial]`
3. ¿Existe un procedimiento para reclamos, rectificaciones y supresiones? `[Sí] [No] [Parcial]`
4. ¿Se conservan evidencias de la atención de solicitudes? `[Sí] [No] [Parcial]`

### 6. Seguridad de la Información

1. ¿Se aplican controles de acceso a la información personal? `[Sí] [No] [Parcial]`
2. ¿Existen medidas para prevenir pérdida, alteración o acceso no autorizado? `[Sí] [No] [Parcial]`
3. ¿Se realizan copias de seguridad de información crítica? `[Sí] [No] [Parcial]`
4. ¿Se registran y gestionan incidentes de seguridad? `[Sí] [No] [Parcial]`
5. ¿Existe un procedimiento para reportar incidentes relevantes a la SIC? `[Sí] [No] [Parcial]`

### 7. Datos Sensibles y Menores

1. ¿La empresa trata datos sensibles? `[Sí] [No] [Parcial]`
2. Si la respuesta es sí, ¿cuenta con autorización explícita? `[Sí] [No] [Parcial]`
3. ¿Se informa el carácter facultativo de suministrar datos sensibles? `[Sí] [No] [Parcial]`
4. ¿Se tratan datos de niños, niñas o adolescentes? `[Sí] [No] [Parcial]`
5. ¿Existen controles especiales para proteger dichos datos? `[Sí] [No] [Parcial]`

### 8. Terceros y Transferencias

1. ¿Existen contratos con encargados que procesan datos por cuenta de la empresa? `[Sí] [No] [Parcial]`
2. ¿Los contratos incluyen obligaciones de confidencialidad y seguridad? `[Sí] [No] [Parcial]`
3. ¿Se transfieren datos fuera de Colombia? `[Sí] [No] [Parcial]`
4. ¿Se verifican los requisitos legales para transferencias internacionales? `[Sí] [No] [Parcial]`

### 9. Capacitación y Cultura

1. ¿Los empleados reciben capacitación en protección de datos? `[Sí] [No] [Parcial]`
2. ¿La capacitación se realiza periódicamente? `[Sí] [No] [Parcial]`
3. ¿Los nuevos colaboradores reciben inducción sobre privacidad? `[Sí] [No] [Parcial]`

### 10. Cumplimiento y Evidencia

1. ¿La empresa realiza auditorías o autoevaluaciones de cumplimiento? `[Sí] [No] [Parcial]`
2. ¿Se conservan registros de autorizaciones, consultas y reclamos? `[Sí] [No] [Parcial]`
3. ¿Se cuenta con indicadores de cumplimiento? `[Sí] [No] [Parcial]`
4. ¿Existe un plan de mejora para hallazgos detectados? `[Sí] [No] [Parcial]`

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
