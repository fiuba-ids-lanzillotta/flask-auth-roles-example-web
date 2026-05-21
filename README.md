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
