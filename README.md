# Flask Auth Roles - Web

> **Aviso:** este proyecto es **codigo de ejemplo** con fines didacticos. Puede contener errores, simplificaciones o decisiones de diseno discutibles. Si se usa como base para un trabajo practico u otro entregable, **debe adaptarse a las buenas practicas y consignas especificas de la materia/catedra** (estilo de codigo, manejo de errores, validaciones, tests, estructura, seguridad, etc.).

## Motivacion

Este proyecto es el **frontend** de un **ejemplo integrador** que muestra como construir una pequena aplicacion full-stack (frontend + backend) en Flask, donde el frontend consume una API REST con **autenticacion JWT** y **control de acceso por roles** (`admin` / `usuario`).

Permite **registrar un usuario, iniciar sesion y acceder a paginas diferenciadas segun el rol**: cualquier usuario logueado ve su dashboard, y los administradores acceden ademas a un panel donde pueden listar y eliminar usuarios.

El objetivo es mostrar como un frontend renderizado del lado del servidor puede integrarse con una API stateless basada en JWT, **guardando el token en la sesion de Flask** (cookie firmada del lado servidor) en vez de exponerlo al navegador.

## Arquitectura

```
  Browser
     |
     |   (cookie de sesion de Flask con el JWT guardado server-side)
     v
  Flask Web (este proyecto, puerto 5001)
     |
     |  requests.get/post (HTTP) + header: Authorization: Bearer <jwt>
     v
  Flask API (flask-auth-roles-example-api, puerto 5000)
     |
     v
  MySQL
```

## Estructura del proyecto

```
flask-auth-roles-example-web/
├── app.py                              # Entry point Flask (puerto 5001)
├── requirements.txt                    # Dependencias Python
├── flask_auth_roles_example_web/
│   ├── constants.py                    # URL de la API backend y reglas de password
│   ├── utils.py                        # Helpers de sesion + decorador @requiere_login
│   ├── routes/
│   │   └── auth.py                     # Rutas: login, register, logout, dashboard, admin
│   └── services/
│       └── api.py                      # Cliente HTTP del backend (auth + usuarios)
├── templates/
│   ├── base.html                       # Template base (header, footer, flash, badges)
│   ├── login.html                      # Formulario de login
│   ├── register.html                   # Formulario de registro
│   ├── dashboard.html                  # Panel de cualquier usuario logueado
│   ├── admin.html                      # Panel exclusivo de administradores
│   └── 404.html                        # Pagina de error 404
└── static/
    └── css/
        └── styles.css                  # Estilos responsive
```

## Requisitos previos

- Python 3.10+
- La API (`flask-auth-roles-example-api`) corriendo en el puerto 5000
- Al menos un usuario admin creado en la API (ver el README del backend para el bootstrapping)

## Instalacion y ejecucion

El proyecto incluye scripts de setup que crean el entorno virtual, instalan las dependencias y levantan la aplicacion automaticamente.

Asegurate de que la API este corriendo primero, luego:

**Con virtualenv:**

```bash
# Windows
setup_virtualenv.bat

# Linux / macOS
chmod +x setup_virtualenv.sh
./setup_virtualenv.sh
```

**Con pipenv:**

```bash
# Windows
setup_pipenv.bat

# Linux / macOS
chmod +x setup_pipenv.sh
./setup_pipenv.sh
```

Una vez iniciada, la web estara disponible en `http://localhost:5001/`.

## Variables de entorno

| Variable     | Default                       | Descripcion                                                |
|--------------|-------------------------------|------------------------------------------------------------|
| `SECRET_KEY` | `change-me-please-frontend`   | Clave con la que Flask firma las cookies de sesion         |

En produccion definir siempre un `SECRET_KEY` propio y secreto.

## Paginas

| Ruta                                         | Metodo   | Acceso                | Descripcion                                  |
|----------------------------------------------|----------|-----------------------|----------------------------------------------|
| `/`                                          | GET      | -                     | Redirige al dashboard o al login segun sesion|
| `/login`                                     | GET/POST | Publico               | Formulario de login                          |
| `/register`                                  | GET/POST | Publico               | Formulario de registro (crea rol usuario)    |
| `/logout`                                    | POST     | Autenticado           | Cierra la sesion                             |
| `/dashboard`                                 | GET      | Autenticado           | Panel con los datos del usuario logueado     |
| `/admin`                                     | GET      | Solo `admin`          | Listado de usuarios                          |
| `/admin/usuarios/<id>/eliminar`              | POST     | Solo `admin`          | Elimina un usuario                           |

## Flujo principal

1. El usuario entra a `/` y, si no esta logueado, es redirigido a `/login`.
2. Ingresa email + password; el frontend hace `POST /login` a la API.
3. Si las credenciales son validas, la API devuelve `{token, usuario}`. El frontend guarda **ambos en la sesion de Flask** (`flask.session`).
4. A partir de ahi, cada request a la API se hace con el header `Authorization: Bearer <token>` tomado de la sesion.
5. Las vistas se protegen con el decorador `@requiere_login(rol=...)` definido en `flask_auth_roles_example_web/utils.py`:
   - Si no hay sesion, redirige a `/login` con un mensaje flash.
   - Si el rol no coincide con el requerido, redirige al dashboard con un mensaje flash.
6. Al hacer logout, se limpian las claves `token` y `usuario` de la sesion.

## Por que el JWT vive en `flask.session` y no en el browser

Una opcion tradicional para SPAs es guardar el JWT en `localStorage` o en una cookie accesible desde JavaScript. En este ejemplo se opto por **mantener el token completamente del lado del servidor**, dentro de la sesion de Flask:

- El navegador solo ve la **cookie de sesion firmada** de Flask (`session`), nunca el JWT en si.
- El frontend (Flask) es quien lee el token de la sesion y lo envia a la API como `Authorization: Bearer ...`.
- Esto evita exponer el JWT al JavaScript del cliente y, en consecuencia, **reduce la superficie de ataque** ante XSS.

Es una decision coherente con el patron del proyecto (renderizado del lado del servidor, mismo estilo que `student-grades-example-web`). En una arquitectura cliente-servidor pura (SPA + API), esta separacion no aplicaria y la decision de donde guardar el token tendria otros trade-offs.

## Manejo de errores

El frontend define un **error handler 404** centralizado en `app.py` que renderiza `templates/404.html`.

Los errores que devuelve la API se muestran como **mensajes flash** en la pagina actual (con la clase `flash--error`). Las respuestas de exito tambien usan flash messages (`flash--success`).

Las redirecciones disparadas por `@requiere_login` informan al usuario el motivo (sesion faltante o rol insuficiente).

## Glosario de terminos

- **API REST**: estilo de arquitectura para servicios web que expone recursos via HTTP (GET, POST, PUT, DELETE) usando, en general, JSON como formato de intercambio.
- **Endpoint**: ruta concreta de la API (por ejemplo `POST /login`) que responde a un metodo HTTP y realiza una accion sobre un recurso.
- **Bearer token**: esquema de autenticacion HTTP donde el JWT viaja en el header `Authorization: Bearer <token>`.
- **Flask**: micro framework web de Python. En este ejemplo se usa tanto en el frontend (este proyecto) como en la API backend.
- **Frontend**: aplicacion que renderiza las paginas HTML del lado del servidor y consume la API. En este proyecto corre en el puerto 5001.
- **Backend / API**: servicio HTTP REST (`flask-auth-roles-example-api`) que expone los endpoints de autenticacion y usuarios. Corre en el puerto 5000.
- **Autenticacion**: proceso de verificar **quien** es el usuario (login con email y password).
- **Autorizacion**: proceso de verificar **que** puede hacer el usuario autenticado (por ejemplo, si su rol es `admin`).
- **Rol**: etiqueta asociada al usuario que define sus permisos. En este proyecto: `admin` y `usuario`.
- **JWT (JSON Web Token)**: token firmado que contiene informacion del usuario (`sub`, `rol`, `exp`). La API lo emite en el login y el cliente lo envia en cada request protegida.
- **Stateless**: la API **no** guarda sesiones en memoria ni en base; cada request se autentica de cero validando el JWT.
- **Bootstrapping**: pasos iniciales para dejar el sistema usable (en este caso, crear el primer usuario `admin`), ya que el registro publico solo crea usuarios con rol `usuario`.
- **Sesion de Flask (`flask.session`)**: diccionario asociado a una cookie firmada por el servidor. Aca se guarda el JWT y los datos del usuario logueado del lado del servidor.
- **Cookie de sesion firmada**: cookie que Flask envia al navegador firmada con `SECRET_KEY`; el navegador no puede modificarla sin invalidar la firma.
- **`SECRET_KEY`**: clave secreta con la que Flask firma las cookies de sesion. Debe ser unica y privada en produccion.
- **SSR (Server-Side Rendering)**: renderizado del HTML en el servidor (con Jinja2) antes de enviarlo al navegador. Es el enfoque usado en este frontend.
- **SPA (Single Page Application)**: alternativa al SSR donde el frontend corre como JavaScript en el navegador y consume la API directamente. **No** es lo que hace este proyecto.
- **Jinja2**: motor de templates que usa Flask para generar HTML dinamico (los archivos `.html` en `templates/`).
- **Template base (`base.html`)**: plantilla con la estructura comun (header, footer, flash) de la que heredan las demas paginas.
- **Flash message**: mensaje temporal de una sola lectura que Flask muestra al usuario tras una accion (exito o error).
- **Decorador `@requiere_login`**: decorador propio (`flask_auth_roles_example_web/utils.py`) que protege vistas: exige sesion activa y, opcionalmente, un rol especifico.
- **XSS (Cross-Site Scripting)**: ataque que inyecta JavaScript malicioso en el navegador. Guardar el JWT server-side reduce el riesgo de que sea robado por XSS.
- **`requests`**: libreria de Python que el frontend usa para hacer llamadas HTTP a la API.
- **Entorno virtual**: directorio aislado con la version de Python y las dependencias del proyecto, para no mezclarlas con las del sistema.
- **virtualenv / `venv`**: herramienta estandar de Python para crear entornos virtuales. Las dependencias se declaran en `requirements.txt` y se instalan con `pip install -r requirements.txt`. En este proyecto lo levantan los scripts `setup_virtualenv.sh` / `setup_virtualenv.bat`.
- **pipenv**: herramienta alternativa que combina la gestion del entorno virtual con la de dependencias en un solo flujo. Usa `Pipfile` (declaracion) y `Pipfile.lock` (versiones exactas resueltas) en vez de `requirements.txt`. En este proyecto lo levantan los scripts `setup_pipenv.sh` / `setup_pipenv.bat`.
- **`pip`**: gestor de paquetes de Python. Instala librerias desde PyPI dentro del entorno activo.
