from functools import wraps
from flask import session, redirect, url_for, flash


def usuario_actual() -> dict:
    """Retorna el usuario logueado guardado en la sesion, o {} si no hay."""
    return session.get('usuario') or {}


def token_actual() -> str:
    """Retorna el JWT guardado en la sesion, o cadena vacia si no hay."""
    return session.get('token') or ''


def guardar_sesion(token: str, usuario: dict) -> None:
    """Persiste token y usuario en la sesion de Flask."""
    session['token']   = token
    session['usuario'] = usuario


def limpiar_sesion() -> None:
    """Borra todos los datos de autenticacion de la sesion."""
    session.pop('token', None)
    session.pop('usuario', None)


def extraer_mensajes_error(api_response: dict) -> list[str]:
    """Obtiene una lista de descripciones de error desde una respuesta de la API."""
    errores = (api_response or {}).get('errors', [])

    return [e.get('description') or e.get('message') or 'Error desconocido' for e in errores]


def requiere_login(rol: str = None):
    """
    Decorador para vistas: exige que haya un usuario en sesion y, opcionalmente,
    un rol especifico. Si falla, redirige a /login con un mensaje flash.
    """
    def decorador(funcion):
        @wraps(funcion)
        def wrapper(*args, **kwargs):
            usuario = usuario_actual()

            if not usuario or not token_actual():
                flash('Iniciá sesión para continuar.', 'error')

                return redirect(url_for('auth.login'))

            if rol is not None and usuario.get('rol') != rol:
                flash(f"No tenés permisos para acceder a esta sección (requiere rol '{rol}').", 'error')

                return redirect(url_for('auth.dashboard'))

            return funcion(*args, **kwargs)

        return wrapper

    return decorador
