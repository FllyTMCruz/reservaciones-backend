# Sistema de Reservaciones - Backend (API RESTful)

Núcleo lógico y de alto rendimiento del Sistema de Reservaciones. Procesa las operaciones CRUD, valida datos estrictamente y maneja la concurrencia de múltiples usuarios[cite: 2]. La arquitectura está preparada para contenedorización con Docker[cite: 2].

## 🚀 Características
* **Gestión de Citas (CRUD):** Lógica principal y manejo de espacios de tiempo, a cargo de Dev2[cite: 1].
* **Validación Estricta:** Modelado de datos (fechas, IDs, textos) mediante Pydantic antes de la inserción en base de datos[cite: 2].
* **Seguridad y Persistencia:** Autenticación por tokens JWT y persistencia en Supabase (PostgreSQL) gestionados por Dev3[cite: 1, 2].

## 🛠️ Stack Tecnológico
* **Framework:** FastAPI[cite: 2].
* **Lenguaje:** Python[cite: 2].
* **Base de Datos & Auth:** Supabase (PostgreSQL + JWT Auth)[cite: 2].
* **Infraestructura:** Docker y DigitalOcean (Droplet o App Platform)[cite: 2].

## ⚙️ Desarrollo Local
1. Clonar el repositorio.
2. Crear un entorno virtual e instalar las dependencias con `pip install -r requirements.txt`.
3. Configurar variables de entorno para la conexión con Supabase.
4. Ejecutar el servidor con `uvicorn app.main:app --reload`.

## 📁 Estructura del proyecto

```text
reservaciones-backend/
├── app/
│   ├── routers/            # Controladores y endpoints por recurso
│   ├── models/             # Esquemas y validaciones de Pydantic
│   ├── auth/               # Verificación y validación de tokens JWT
│   ├── db/                 # Conexión y adaptadores de base de datos
│   └── main.py             # Entrada de la aplicación y configuración de CORS
├── requirements.txt        # Dependencias de Python
└── Dockerfile              # Configuración para ejecutar con Docker
```

### `app/main.py`

Es el punto de entrada de la aplicación FastAPI. Aquí se crea la instancia
principal, se configura CORS y se registran los routers de la API.

### `app/routers/`

Contiene los endpoints organizados por recurso, por ejemplo espacios, reservas
y usuarios.

### `app/models/`

Contiene los modelos de Pydantic, utilizados para validar los datos que recibe
y devuelve la API.

### `app/auth/`

Contiene la lógica relacionada con autenticación y autorización, incluyendo la
validación de tokens JWT.

### `app/db/`

Contiene la configuración de conexión con Supabase/PostgreSQL y los adaptadores
para consultar y modificar datos.

### `requirements.txt`

Lista las dependencias necesarias para instalar y ejecutar el proyecto.

### `Dockerfile`

Define cómo construir la imagen Docker del backend y cómo iniciar el servidor.

## 🩺 Endpoint de salud

La ruta `GET /health` permite verificar que la API está funcionando
correctamente.

Respuesta:

```json
{
  "status": "ok"
}
```

La documentación interactiva de la API está disponible en
`http://127.0.0.1:8000/docs` cuando el servidor está ejecutándose.
