# innovatex-hackathon

Plataforma web para diagnosticar el nivel de cumplimiento de la Ley 1581 de 2012 sobre protección de datos personales en organizaciones colombianas. La solución combina cuestionario guiado, cálculo automático de puntaje, recomendaciones asistidas por IA y seguimiento de un plan de acción.

## Qué resuelve

- Evalúa el estado de cumplimiento de privacidad de una empresa.
- Calcula un porcentaje de madurez por bloques y por pregunta.
- Genera recomendaciones y acciones de mejora.
- Permite un flujo de uso más claro para equipos legales, TI y auditoría.

## Estructura

- frontend/: interfaz web construida en React.
- backend/: API y lógica de negocio en FastAPI.

## Tecnologías

### Frontend

- React 18
- Vite
- TypeScript
- Tailwind CSS
- Zustand
- React Router
- Supabase JS
- Axios

### Backend

- Python 3.12+
- FastAPI
- Uvicorn
- SQLAlchemy
- Alembic
- Pydantic Settings
- PyJWT
- ReportLab
- OpenPyXL

### Infraestructura

- Supabase como base de datos PostgreSQL administrada
- Docker y docker-compose
- Nginx para servir la aplicación en despliegue

## Arquitectura general

El frontend consume la API del backend para autenticar usuarios, cargar empresas, ejecutar diagnósticos y obtener resultados.

- El frontend administra la experiencia de usuario y el estado visual.
- El backend expone endpoints REST para compañías, cuestionarios, reportes y scoring.
- La base de datos persiste empresas, diagnósticos, respuestas, recomendaciones y planes de acción en Supabase.
- La capa de IA se integra como un servicio desacoplado para poder cambiar de proveedor sin reescribir el negocio.

## Autenticación

La plataforma usa Supabase Auth para el acceso de usuarios.

- Inicio de sesión con correo y contraseña.
- Inicio de sesión con OAuth de Google.
- La sesión se utiliza para consumir la API y asociar al usuario con sus empresas y diagnósticos.

## Requisitos

- Node.js y npm.
- Python 3.12 o superior.
- uv instalado para manejar el entorno del backend.
- PostgreSQL disponible para la API.

## Cómo ejecutar el backend

Los comandos se ejecutan dentro de la carpeta backend.

```powershell
cd backend
uv sync
.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Si usas CMD en Windows, puedes activar el entorno con:

```cmd
.venv\Scripts\activate.bat
```

## Backend: qué incluye

- `app/main.py`: arranque de la aplicación FastAPI.
- `app/config.py`: configuración y variables de entorno.
- `app/database.py`: conexión a PostgreSQL.
- `app/models/`: modelos de datos.
- `app/schemas/`: contratos de entrada y salida.
- `app/routers/`: rutas de la API.
- `app/services/`: lógica de negocio.
- `app/reports/`: exportación a PDF y Excel.

## Cómo ejecutar el frontend

Los comandos se ejecutan dentro de la carpeta frontend.

```bash
cd frontend
npm install
npm run dev
```

## Frontend: qué incluye

- `src/main.tsx`: punto de entrada de React.
- `src/App.tsx`: composición general de la aplicación.
- `src/pages/`: pantallas del flujo de usuario.
- `src/components/`: componentes reutilizables.
- `src/api/`: cliente HTTP para consumir el backend.
- `src/stores/`: estado global con Zustand.
- `src/lib/`: utilidades y helpers.

## Notas

- El backend expone la API en http://127.0.0.1:8000.
- El frontend levanta el servidor de desarrollo con Vite.
- Cada parte del proyecto se ejecuta desde su carpeta correspondiente.
- Si necesitas editar variables de entorno o configuración, revisa los archivos de cada carpeta antes de iniciar los servicios.

## Flujo esperado

1. Iniciar el backend desde backend.
2. Iniciar el frontend desde frontend.
3. Abrir la aplicación web y autenticarte.
4. Crear o seleccionar una empresa.
5. Ejecutar el diagnóstico y revisar resultados, reportes y plan de acción.