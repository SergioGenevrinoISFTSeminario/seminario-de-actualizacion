##  INTENTO 9 :
# RECONOCIMIENTO FACIAL 

from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_socketio import SocketIO, join_room, emit, disconnect
from cryptography.fernet import Fernet
import pymysql
import bcrypt
import os
import base64
from werkzeug.utils import secure_filename
from datetime import datetime
import cv2
import face_recognition
import requests
import numpy as np

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Cambia esta clave por una más segura
socketio = SocketIO(app)

# Generar una clave de cifrado (simétrica)
key = Fernet.generate_key().decode()  # Convertimos la clave a string
room_global = "sala_unica"  # Nombre de la sala compartida

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'botloginfinal',
    'port': 3306
}

# Conexión a la base de datos
def connect_db():
    """Establece la conexión con la base de datos."""
    return pymysql.connect(**db_config)


# Definir las carpetas para registro y login
UPLOAD_FOLDER = 'static/uploads'
REGISTER_FOLDER = os.path.join(UPLOAD_FOLDER, 'registro')
LOGIN_FOLDER = os.path.join(UPLOAD_FOLDER, 'login')

# Configurar las carpetas en la aplicación Flask
app.config['REGISTER_FOLDER'] = REGISTER_FOLDER
app.config['LOGIN_FOLDER'] = LOGIN_FOLDER

# Crear las carpetas si no existen
if not os.path.exists(REGISTER_FOLDER):
    os.makedirs(REGISTER_FOLDER)

if not os.path.exists(LOGIN_FOLDER):
    os.makedirs(LOGIN_FOLDER)


@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    

    # Conectar a la base de datos
    conn = connect_db()
    try:
        with conn.cursor() as cursor:
            # Buscar el usuario en la base de datos
            cursor.execute("SELECT * FROM usuarios WHERE usuario = %s", (username,))
            user = cursor.fetchone()

            if user:  # Si el usuario existe
                stored_password_hash = user[2]  # Suponiendo que la contraseña hasheada está en la columna 2 (índice 1)

                # Comparar la contraseña ingresada con la almacenada en la base de datos
                if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
                 
                 # ALMACENAR LA UBICACION DE LA FOTO DEL USUARIO     
                 session['image_path'] = user[4]  # Suponiendo que el image_path está en la columna 4
                 session['username'] = user[1]  # Guardar el nombre de usuario en la sesión
                 return redirect(url_for('recognition'))  # Redirige a la sala de chat tras el inicio de sesión
                else:
                    flash('Contraseña incorrecta', 'danger')
            else:
                flash('Usuario no encontrado', 'danger')

    except pymysql.MySQLError as e:
        flash('Error al verificar el usuario', 'danger')
        print(f"Error: {e}")
    finally:
        conn.close()

    return redirect(url_for('login'))  # Redirige al formulario de login si hay error

# Ruta para el registro de un nuevo usuario
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['usuario']
        password = request.form['password']
        email = request.form['email']
        photo_name = request.form['photoName']
        photo_data = request.form['photoData']

        if username and password and email and photo_name:
        # Decodificar la imagen desde base64
         photo_data = photo_data.split(',')[1]
         photo_bytes = base64.b64decode(photo_data)

        # Guardar la imagen en el servidor
        photo_filename = photo_name
        photo_path = os.path.join(app.config['REGISTER_FOLDER'], photo_filename)
        with open(photo_path, 'wb') as f:
            f.write(photo_bytes)


        if len(username) < 3 or len(password) < 6:
            flash('El nombre de usuario o la contraseña son demasiado cortos', 'danger')
            return redirect(url_for('register'))

        # Verificar si el usuario ya existe
        conn = connect_db()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM usuarios WHERE usuario = %s", (username,))
                existing_user = cursor.fetchone()
                if existing_user:
                    flash('El nombre de usuario ya existe', 'danger')
                    return redirect(url_for('register'))

                # Hashear la contraseña antes de almacenarla
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

                # Insertar el nuevo usuario en la base de datos
                cursor.execute("INSERT INTO usuarios (usuario, password, email, image_path) VALUES (%s, %s, %s, %s)", (username, password_hash, email, photo_name   ))
                conn.commit()
                flash('Usuario registrado exitosamente', 'success')

        except pymysql.MySQLError as e:
            flash('Error al registrar el usuario', 'danger')
            print(f"Error: {e}")
        finally:
            conn.close()

        return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/recognition')
def recognition():
    return render_template('reconocimientofacial.html')


# Endpoint para procesar la imagen enviada por el formulario
@app.route('/verifyphoto', methods=['POST'])
def verify_user():
    # Obtener la imagen en base64 del formulario
    photo_data = request.form.get('photoData')
    photo_name = request.form.get('photoName')

    if not photo_data or not photo_name:
        flash('No se recibió ninguna imagen', 'danger')
        return redirect(url_for('index'))

    # Decodificar la imagen base64 y guardarla en un archivo
    try:
        # Eliminar la cabecera del data URL y decodificar la imagen
        img_data = base64.b64decode(photo_data.split(',')[1])
        
        # Definir la ruta para guardar la imagen
        save_path = os.path.join('static/uploads/login', photo_name)
        
        # Crear el directorio si no existe
        if not os.path.exists('static/uploads'):
            os.makedirs('static/uploads')
        
        # Guardar la imagen en el servidor
        with open(save_path, 'wb') as f:
            f.write(img_data)
        

        # RECUPERAR LA IMAGEN ALMACENADA DURANTE EL REGISTRO

        # Obtener la ruta de la imagen almacenada en la sesión
        session_image_path = session.get('image_path')
        if session_image_path:
            # Ruta completa de la imagen a comparar
            comparison_image_path = os.path.join('static/uploads/registro', session_image_path)


               # Imprimir los nombres de las imágenes
            print(f"Imagen subida: {photo_name}")
            print(f"Imagen de referencia: {session_image_path}")


            # Cargar ambas imágenes usando OpenCV
            uploaded_image = cv2.imread(save_path)
            registered_image = cv2.imread(comparison_image_path)

            # Preprocesamiento: Conversión a escala de grises y redimensionamiento
            uploaded_image_gray = cv2.cvtColor(uploaded_image, cv2.COLOR_BGR2GRAY)
            registered_image_gray = cv2.cvtColor(registered_image, cv2.COLOR_BGR2GRAY)

            uploaded_image_resized = cv2.resize(uploaded_image_gray, (registered_image_gray.shape[1], registered_image_gray.shape[0]))

            # Comparar histogramas
            hist_uploaded = cv2.calcHist([uploaded_image_resized], [0], None, [256], [0, 256])
            hist_registered = cv2.calcHist([registered_image_gray], [0], None, [256], [0, 256])
            cv2.normalize(hist_uploaded, hist_uploaded)
            cv2.normalize(hist_registered, hist_registered)

            # Comparar histogramas usando correlación
            comparison = cv2.compareHist(hist_uploaded, hist_registered, cv2.HISTCMP_CORREL)

            # Umbral para determinar si las imágenes son similares
            threshold = 0.9  # Ajusta este valor según sea necesario
            if comparison > threshold:
                flash('Las imágenes son iguales', 'success')
                return redirect(url_for('chat'))
  
            else:
                flash('Las imágenes no coinciden', 'danger')
                return redirect(url_for('index'))
        else:
            flash('No se encontró la imagen de referencia en la sesión', 'warning')
    
    except Exception as e:
        flash(f'Error al procesar la imagen: {str(e)}', 'danger')


    
  
  
@app.route('/chat')
def chat():
    if 'username' not in session:  # Verifica si el usuario está autenticado
        return redirect(url_for('login'))  # Si no, redirige al login
    username = session['username']
    return render_template('chat.html', username=username)

@app.route('/logout')
def logout():
    # Verifica si el usuario está autenticado
    if 'username' in session:
        session.pop('username', None)  # Elimina la sesión del usuario
        flash('Has cerrado sesión exitosamente.', 'success')
    else:
        flash('No estás autenticado.', 'danger')

    return redirect(url_for('index'))  # Redirige a la página de inicio de sesión


@socketio.on('connect')
def handle_connect():
    username = session.get('username')
    if username:  # Verifica si el usuario está autenticado
        join_room(room_global)  # Unir a todos los usuarios a la misma sala
        print(f"{username} se ha unido a la sala global")
        emit('clave', key, room=room_global)  # Enviamos la clave a todos los clientes conectados en la sala
        emit('mensaje', {'message': f"{username} se ha unido al chat."}, room=room_global)
    else:
        disconnect()  # Desconectar al usuario si no está autenticado


@socketio.on('message')
def handle_message(data):
    encrypted_message = data['encryptedMessage']
    username = session.get('username')
    print(f"Mensaje recibido cifrado de {username}: {encrypted_message}")
    # Enviar el mensaje cifrado y el nombre del usuario a todos en la sala, excepto al emisor
    emit('message', {'encryptedMessage': encrypted_message, 'username': username}, room=room_global, include_self=False)
    
@socketio.on('disconnect')
def handle_disconnect():
    username = session.get('username')
    if username:
        print(f"{username} ha salido de la sala")
        emit('mensaje', {'message': f"{username} ha salido del chat."}, room=room_global)

if __name__ == '__main__':
    socketio.run(app, host='localhost', port=5000)
