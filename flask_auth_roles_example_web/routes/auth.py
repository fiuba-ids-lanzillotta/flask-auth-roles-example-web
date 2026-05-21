from flask import Blueprint, render_template, request, redirect, url_for, flash

from ..constants import PASSWORD_MIN_LEN, PASSWORD_MAX_LEN, ROL_ADMIN
from ..services import api
from ..utils import (
    guardar_sesion,
    limpiar_sesion,
    usuario_actual,
    token_actual,
    extraer_mensajes_error,
    requiere_login,
)

auth_bp = Blueprint('auth', __name__)


# ---------------------------------------------------------------
# Pagina raiz
# ---------------------------------------------------------------

@auth_bp.route('/')
def home():
    """Si hay sesion abre el dashboard, si no manda al login."""
    if usuario_actual():
        return redirect(url_for('auth.dashboard'))

    return redirect(url_for('auth.login'))


# ---------------------------------------------------------------
# Login
# ---------------------------------------------------------------

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if usuario_actual():
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        errores = []

        if not email:
            errores.append('El email es obligatorio.')

        if not password:
            errores.append('El password es obligatorio.')

        if errores:
            for e in errores:
                flash(e, 'error')

            return redirect(url_for('auth.login'))

        resultado = api.login(email, password)

        if resultado.get('ok'):
            guardar_sesion(resultado['token'], resultado['usuario'])
            flash(f"¡Bienvenido, {resultado['usuario']['nombre']}!", 'success')

            return redirect(url_for('auth.dashboard'))

        for mensaje in extraer_mensajes_error(resultado.get('error_response')):
            flash(mensaje, 'error')

        return redirect(url_for('auth.login'))

    return render_template('login.html')


# ---------------------------------------------------------------
# Registro
# ---------------------------------------------------------------

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if usuario_actual():
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        nombre   = request.form.get('nombre', '').strip()
        password = request.form.get('password', '')

        errores = []

        if not email:
            errores.append('El email es obligatorio.')

        if not nombre:
            errores.append('El nombre es obligatorio.')

        if len(password) < PASSWORD_MIN_LEN or len(password) > PASSWORD_MAX_LEN:
            errores.append(f'El password debe tener entre {PASSWORD_MIN_LEN} y {PASSWORD_MAX_LEN} caracteres.')

        if errores:
            for e in errores:
                flash(e, 'error')

            return redirect(url_for('auth.register'))

        resultado = api.registrar(email, nombre, password)

        if resultado.get('ok'):
            flash('Usuario creado con éxito. Ya podés iniciar sesión.', 'success')

            return redirect(url_for('auth.login'))

        for mensaje in extraer_mensajes_error(resultado.get('error_response')):
            flash(mensaje, 'error')

        return redirect(url_for('auth.register'))

    return render_template('register.html',
                          password_min=PASSWORD_MIN_LEN,
                          password_max=PASSWORD_MAX_LEN)


# ---------------------------------------------------------------
# Logout
# ---------------------------------------------------------------

@auth_bp.route('/logout', methods=['POST'])
def logout():
    limpiar_sesion()
    flash('Cerraste sesión.', 'success')

    return redirect(url_for('auth.login'))


# ---------------------------------------------------------------
# Dashboard (cualquier usuario autenticado)
# ---------------------------------------------------------------

@auth_bp.route('/dashboard')
@requiere_login()
def dashboard():
    return render_template('dashboard.html', usuario=usuario_actual())


# ---------------------------------------------------------------
# Panel de admin
# ---------------------------------------------------------------

@auth_bp.route('/admin')
@requiere_login(rol=ROL_ADMIN)
def admin():
    usuarios = api.listar_usuarios(token_actual())

    return render_template('admin.html', usuario=usuario_actual(), usuarios=usuarios)


@auth_bp.route('/admin/usuarios/<usuario_id>/eliminar', methods=['POST'])
@requiere_login(rol=ROL_ADMIN)
def eliminar_usuario(usuario_id):
    yo = usuario_actual()

    if str(yo.get('id')) == str(usuario_id):
        flash('No podés eliminar tu propio usuario.', 'error')

        return redirect(url_for('auth.admin'))

    resultado = api.eliminar_usuario(token_actual(), usuario_id)

    if resultado.get('ok'):
        flash('Usuario eliminado.', 'success')
    else:
        for mensaje in extraer_mensajes_error(resultado.get('error_response')):
            flash(mensaje, 'error')

    return redirect(url_for('auth.admin'))
