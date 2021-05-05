# Hecho por: Guillermo Velazquez

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin
import bcrypt

from database import mysql

# Importamos nuestros Blueprints
from rutas_articulos import articulos
from rutas_clientes import clientes
from rutas_fabricas import fabricas
from rutas_pedidos import pedidos

app = Flask(__name__)

# ===================================== DATABASE =====================================
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'proyecto_db'
mysql.init_app(app)

# Registramos nuestros Blueprints
app.register_blueprint(articulos)
app.register_blueprint(clientes)
app.register_blueprint(fabricas)
app.register_blueprint(pedidos)

# ===================================== SESION =====================================
app.config['SECRET_KEY'] = 'thisissecret'

# ==================================== CLASE =========================================

# ===================================== ENCRIPTADO =====================================
semilla = bcrypt.gensalt()  # Generamos la semilla de encriptado

# ===================================== FUNCIONES =====================================
def encriptar(cadena, semilla) -> str:
    cadena = cadena.encode('utf-8') # Convierte en bytes
    encriptada = bcrypt.hashpw(cadena, semilla)
    return encriptada

def comparar_contraseñas(password, confirm_password):
    if password != confirm_password:
        print("Las password no coinciden")
        flash("Las contraseñas no coinciden. Intentelo de nuevo.")
        return redirect(url_for('registro'))

def verificar_password_login(password_ingresada, password_base):
    password_encriptado_encode = password_base.encode('utf-8')
    password_encode = password_ingresada.encode('utf-8')
    return bcrypt.checkpw(password_encode, password_encriptado_encode)


# ================================= FIN FUNCIONES =====================================


# ======================================= RUTAS =======================================

# """"""""""""""""""""""""""""" Ruta principal """""""""""""""""""""""""""""
@app.route('/')
@app.route('/index')
def index() -> 'html':

    usuario = None
    clientes = None
    articulos = None
    fabricas = None
    nombre = None
    pedidos = None
    if 'usuario' in session:
        usuario = session['usuario']
        nombre = session['nombre']

        cur = mysql.connection.cursor()

        # Consulta para obtener información de los clientes
        cur.execute('SELECT * FROM clientes')
        clientes = cur.fetchall()

        # Consulta para obtener información de los artículos  
        cur.execute('SELECT * FROM articulos')
        articulos = cur.fetchall()

        # Consulta para obtener información de las fábricas
        cur.execute('SELECT * FROM fabricas')
        fabricas = cur.fetchall()

        # Consulta para obtener información de los pedidos
        cur.execute("""SELECT pedidos.id, clientes.nombre_completo, clientes.direccion, 
                        pedidos.total, pedidos.fecha, pedidos.entrega 
                        FROM pedidos 
                        INNER JOIN clientes ON pedidos.cliente_id=clientes.id""")
        pedidos = cur.fetchall()

        cur.close()

    return render_template('index.html',
                        page_title='Proyecto',
                        header_title='Página principal',
                        usuario=nombre,
                        clientes=clientes,
                        articulos=articulos,
                        fabricas=fabricas,
                        pedidos=pedidos
    )


# """"""""""""""""""""""""""""" Ruta registro """""""""""""""""""""""""""""
@app.route('/registro', methods=['GET','POST'])
def registro() -> 'html':

    if request.method == 'POST':

        nombre_completo = request.form['nombre']
        username = request.form['user']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        comparar_contraseñas(password, confirm_password)

        password_encriptada = encriptar(password, semilla)        

        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO usuarios (nombre, user, password) VALUES (%s, %s, %s)',
                    (nombre_completo, username, password_encriptada))
        mysql.connection.commit()

        flash('Se ha registrado correctamente')

        # Creamos una sesión para que el usuario no tenga que hacer login
        # cuando acaba de registrarse
        session['usuario'] = username
        session['nombre'] = nombre_completo

        # Redirigimos al index, que será diferente cuando hay una sesión activa
        return redirect(url_for('index'))

    else:
        if 'usuario' in session:
            return redirect(url_for('index'))

        return render_template('registro.html',
                                header_title='Registro de usuario',
                                page_title='Registro',
        )
    
# """"""""""""""""""""""""""""" Ruta logearse """""""""""""""""""""""""""""
@app.route('/login', methods=['GET', 'POST'])
def login() -> 'html':
    
    # Verificar si es que ya existe una sesion activa
    if 'usuario' in session:
        return redirect(url_for('index'))

    # Verificar si se ha enviado un formulario
    if request.method == 'POST':
        username = request.form['user']
        password_ingresada = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuarios WHERE user = %s', [username])

        # Verificar que el usuario exista
        data = cur.fetchall()

        if len(data) != 0:
            usuario = data[0]
            password_base = usuario[3]
            nombre = usuario[1]

            # Verificar que las contraseñas coincidan
            if verificar_password_login(password_ingresada, password_base):
                session['usuario'] = username
                session['nombre'] = nombre
                return redirect(url_for('index'))
            else:
                flash('La contraseña es incorrecta.')
                return render_template('login.html')

        else:
            flash('El usuario no existe')
            return render_template('login.html')
    else:
        return render_template('login.html',
                                header_title='Ingreso de usuario',
                                page_title='Ingreso'                   
        )

# """"""""""""""""""""""""""""" Ruta cerrar sesion """""""""""""""""""""""""""""
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=3000)