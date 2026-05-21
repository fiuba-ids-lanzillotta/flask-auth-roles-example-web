import logging
import requests

from ..constants import API_BASE_URL, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------

def _headers_auth(token: str) -> dict:
    return {'Authorization': f'Bearer {token}'} if token else {}


def _respuesta_error(response) -> dict:
    """Devuelve el JSON de error de la API si esta disponible."""
    try:
        return response.json()
    except Exception:
        return {'errors': [{'description': f'Error del servidor: HTTP {response.status_code}'}]}


def _error_conexion() -> dict:
    return {'errors': [{'description': 'No se pudo conectar con el servidor. Verificá que la API esté corriendo.'}]}


# ---------------------------------------------------------------
# Auth
# ---------------------------------------------------------------

def registrar(email: str, nombre: str, password: str) -> dict:
    """
    POST /register. Retorna:
      - {'ok': True, 'usuario': {...}} si fue exitoso
      - {'ok': False, 'error_response': {...}} si la API devolvio error
    """
    try:
        response = requests.post(
            f'{API_BASE_URL}/register',
            json={'email': email, 'nombre': nombre, 'password': password},
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code == 201:
            return {'ok': True, 'usuario': response.json()}

        return {'ok': False, 'error_response': _respuesta_error(response)}

    except requests.exceptions.ConnectionError:
        logger.error(f"No se pudo conectar con la API en {API_BASE_URL}")

        return {'ok': False, 'error_response': _error_conexion()}

    except Exception as e:
        logger.error(f"Error inesperado al registrar usuario: {e}")

        return {'ok': False, 'error_response': {'errors': [{'description': f'Error inesperado: {e}'}]}}


def login(email: str, password: str) -> dict:
    """
    POST /login. Retorna:
      - {'ok': True, 'token': ..., 'usuario': {...}}
      - {'ok': False, 'error_response': {...}}
    """
    try:
        response = requests.post(
            f'{API_BASE_URL}/login',
            json={'email': email, 'password': password},
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code == 200:
            data = response.json()

            return {'ok': True, 'token': data['token'], 'usuario': data['usuario']}

        return {'ok': False, 'error_response': _respuesta_error(response)}

    except requests.exceptions.ConnectionError:
        logger.error(f"No se pudo conectar con la API en {API_BASE_URL}")

        return {'ok': False, 'error_response': _error_conexion()}

    except Exception as e:
        logger.error(f"Error inesperado al hacer login: {e}")

        return {'ok': False, 'error_response': {'errors': [{'description': f'Error inesperado: {e}'}]}}


# ---------------------------------------------------------------
# Usuarios
# ---------------------------------------------------------------

def obtener_me(token: str) -> dict:
    """GET /me. Retorna el usuario o un dict vacio si fallo."""
    try:
        response = requests.get(
            f'{API_BASE_URL}/me',
            headers=_headers_auth(token),
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code == 200:
            return response.json()

    except Exception as e:
        logger.error(f"Error al obtener /me: {e}")

    return {}


def listar_usuarios(token: str) -> list[dict]:
    """GET /usuarios. Solo admin. Retorna lista (vacia si fallo o sin contenido)."""
    try:
        response = requests.get(
            f'{API_BASE_URL}/usuarios',
            headers=_headers_auth(token),
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code == 200:
            return response.json()

        if response.status_code == 204:
            return []

    except Exception as e:
        logger.error(f"Error al listar usuarios: {e}")

    return []


def eliminar_usuario(token: str, usuario_id: int) -> dict:
    """DELETE /usuarios/<id>. Retorna {'ok': True} o {'ok': False, 'error_response': ...}."""
    try:
        response = requests.delete(
            f'{API_BASE_URL}/usuarios/{usuario_id}',
            headers=_headers_auth(token),
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code == 204:
            return {'ok': True}

        return {'ok': False, 'error_response': _respuesta_error(response)}

    except requests.exceptions.ConnectionError:
        return {'ok': False, 'error_response': _error_conexion()}

    except Exception as e:
        logger.error(f"Error al eliminar usuario {usuario_id}: {e}")

        return {'ok': False, 'error_response': {'errors': [{'description': f'Error inesperado: {e}'}]}}
