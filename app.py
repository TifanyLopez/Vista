from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from pprint import pprint
from werkzeug.security import generate_password_hash
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)
app.secret_key = 'appsecretkey'

# Database configuration
db_config = {
    'host': 'bnkjqfasakrmkj3plnxy-mysql.services.clever-cloud.com',
    'port': 3306,
    'user': 'up315axc2il16igk',
    'password': 'GV2iKi0QPHqJnK6opHxs',
    'database': 'bnkjqfasakrmkj3plnxy'
}

def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# LOGIN
@app.route('/accesologin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuario WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            if pbkdf2_sha256.verify(password, user['password']):
                session['logueado'] = True
                session['id'] = user['id']
                session['id_rol'] = user['id_rol']
                if user['id_rol'] == 1:
                    return render_template('admin.html')
                else:
                    return render_template('usuario.html')
        
        return render_template('login.html', error='Usuario o contraseña incorrectos')

    return render_template('login.html')

# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/listarUsuario', methods=['GET', 'POST'])
def listarUsuario():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuario (nombre, email, password, id_rol) VALUES (%s, %s, %s, '2')",
            (nombre, email, password)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('listarUsuario'))

    # GET: mostrar lista de usuarios
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, email, password FROM usuario ORDER BY id ASC")
    listarUsuarios = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('listarUsuario.html', usuarios=listarUsuarios)

@app.route('/eliminar/<int:id>', methods=['DELETE'])
def eliminar(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuario WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True, 'message': 'Usuario eliminado correctamente'})

@app.route('/updateUsuario', methods=['POST']) # actualizar and guardar, agregar
def updateUsuario():
    try:
        id = request.form['id']
        nombre = request.form['nombre'] 
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuario SET nombre = %s, email = %s, password = %s WHERE id = %s",
            (nombre, email, password, id)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Usuario actualizado correctamente'})

    except Exception as e:
        print("Error al actualizar:", e)

        return jsonify({'success': False, 'message': 'Error interno al actualizar'})

#/////////////////////////////////guardar
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        tipo = request.form.get('contraseña')

        if not nombre or not email or not tipo:
            flash("Todos los campos son obligatorios")
            return redirect(url_for('registro'))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO personas (nombre, email, contraseña) VALUES (%s, %s, %s)",
            (nombre, email, tipo)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('registro'))

    # Mostrar lista de registros
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_personas, nombre, email, contraseña FROM personas ORDER BY id_personas ASC")
    listarUsuarios = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('registro.html', usuarios=listarUsuarios)

# CREAR USUARIO - Procesa el formulario
@app.route('/crearusuario', methods=['POST'])
def crearusuario():
    nombre = request.form['nombre']
    email = request.form['email']
    password = request.form['password']
    
    # Encriptar la contraseña antes de guardar
    hash_password = pbkdf2_sha256.hash(password)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO usuario (nombre, email, password, id_rol) VALUES (%s, %s, %s, '2')",
        (nombre, email, hash_password)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('login'))

# PÁGINAS DE INFORMACIÓN
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')


# RUTA ADMIN – panel con números
@app.route('/admin')
def admin():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Contar usuarios
    cursor.execute("SELECT COUNT(*) AS total FROM usuario")
    total_usuario = cursor.fetchone()['total']

    # Contar personas registradas
    cursor.execute("SELECT COUNT(*) AS total FROM datos")
    total_datos = cursor.fetchone()['total']

    # Contar aves / adoptantes
    cursor.execute("SELECT COUNT(*) AS total FROM vista")
    total_vista = cursor.fetchone()['total']

    cursor.close()
    conn.close()

    return render_template('admin.html',
                           total_usuarios=total_usuario,
                           total_personas=total_vista,
                           total_vista=total_datos)

@app.route('/listarusuario')
def listaregistro():
    return render_template('listaregistro.html')

# Lista  formulario-------o
@app.route('/listar_agregados')
def listar_agregados():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vista")
    datos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('listar_agregados.html', datos=datos)

# Listar informacion con tabla (solo lista)
@app.route('/listar_informacion')
def listar_informacion():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vista")
    datos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('listar_informacion.html', datos=datos)

# Agregar 
@app.route('/agregar_datos', methods=['POST'])
def agregar_datos():
    nombre = request.form['nombre']
    correo = request.form['correo']
    descripcion = request.form['descripcion']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO vista (nombre, correo, descripcion) VALUES (%s, %s, %s)",
        (nombre, correo, descripcion)
    )
    conn.commit()
    cursor.close()
    conn.close()
    flash("agregado correctamente", "success")
    return redirect(url_for('listar_agregados'))

# Editar
@app.route('/editar_datos', methods=['POST'])
def editar_datos():
    id = request.form['id']
    nombre = request.form['nombre']
    correo = request.form['correo']
    descripcion = request.form['descripcion']
    fecha = request.form['fecha']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE datos
        SET nombre=%s, correo=%s, descripcion=%s
        WHERE id=%s
    """, (nombre, correo, descripcion, id))
    conn.commit()
    cursor.close()
    conn.close()
    flash("actualizado correctamente", "success")
    return redirect(url_for('listar_informacion'))

# Eliminar
@app.route('/eliminar_datos/<int:id>')
def eliminar_datos(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM datos WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Eliminado correctamente", "success")
    return redirect(url_for('listar_informacion'))
    
if __name__ == '__main__':
    app.run(debug=True, port=8000)