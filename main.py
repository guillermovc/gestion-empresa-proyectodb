from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import bcrypt

app = Flask(__name__)

# ===================================== DATABASE =====================================
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'proyecto_db'
mysql = MySQL(app)

# ===================================== ENCRIPTADO =====================================
semilla = bcrypt.gensalt()  # Generamos la semilla de encriptado

# ===================================== SESION =====================================
app.secret_key = 'llave_secreta'

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
# ===================================== FUNCIONES =====================================



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
    if 'usuario' in session:
        usuario = session['usuario']
        nombre = session['nombre']
        print(session)

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

    return render_template('index.html',
                        page_title='Proyecto',
                        header_title='Página principal',
                        usuario=nombre,
                        clientes=clientes,
                        articulos=articulos,
                        fabricas=fabricas
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
    session.pop('usuario', None)
    return redirect(url_for('index'))

# """"""""""""""""""""""""""""" Ruta ingresar cliente """""""""""""""""""""""""""""
@app.route('/registrar_cliente', methods=['GET', 'POST'])
def registrar_cliente() -> 'html':
    if 'usuario' in session:
        if request.method == 'POST':
            
            nombre_completo = request.form['nombre']
            direccion = request.form['direccion']
            saldo = float(request.form['saldo'])
            descuento = float(request.form['descuento'])
            saldo_limite = 300000.0

            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO clientes (nombre_completo, direccion, saldo, limite_saldo, descuento) VALUES (%s, %s, %s, %s, %s)',
                        (nombre_completo, direccion, saldo, saldo_limite, descuento))
            mysql.connection.commit()

            flash('Cliente registrado correctamente')

        usuario = session["usuario"]

        return render_template('registrar_cliente.html',
                                usuario=usuario,)
    else:
        return redirect(url_for('index'))

# """"""""""""""""""""""""""""" Ruta registrar articulo """""""""""""""""""""""""""""
@app.route('/registrar_articulo', methods=['GET', 'POST'])
def registrar_articulo() -> 'html':
    if 'usuario' in session:
        fabricas = None
        if request.method == 'POST':
            
            nombre = request.form['nombre']
            precio = float(request.form['precio'])
            existencias = float(request.form['existencias'])
            descripcion = request.form['descripcion']
            ID_fabrica = request.form['fabrica']
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO articulos (nombre, precio, existencias, descripcion, fabrica_id) VALUES (%s, %s, %s, %s)',
                        (nombre, precio, existencias, descripcion, ID_fabrica))
            mysql.connection.commit()
            flash('Articulo registrado correctamente')
            return render_template('registrar_articulo.html')
        else:
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM fabricas')
            fabricas = cur.fetchall()
            return render_template('registrar_articulo.html', fabricas=fabricas)
    else:
        return redirect(url_for('index'))

# """"""""""""""""""""""""""""" Ruta editar articulo """""""""""""""""""""""""""""
@app.route('/editar_articulo/<string:id>')
def editar_articulo(id):

    cur = mysql.connection.cursor()
    cur.execute(f'SELECT * FROM articulos WHERE id = {id}')
    data = cur.fetchall()
    cur.execute(f'SELECT * FROM fabricas')
    fabricas = cur.fetchall()
    return render_template('editar_articulo.html', articulo = data[0], fabricas=fabricas)

    if 'usuario' in session:
        cur = mysql.connection.cursor()
        cur.execute(f'SELECT * FROM articulos WHERE id = {id}')
        data = cur.fetchall()

        return render_template('editar_articulo.html', articulo = data[0])
    
    else:
        return redirect(url_for('index'))


@app.route('/actualizar_articulo/<id>', methods=['POST'])
def actualizar_articulo(id):
    nombre = request.form['nombre']
    precio = float(request.form['precio'])
    existencias = float(request.form['existencias'])
    descripcion = request.form['descripcion']
    ID_fabrica = request.form['fabrica']
    cur = mysql.connection.cursor()
    cur.execute("""
    UPDATE articulos 
    SET nombre = %s,
        precio = %s,
        existencias = %s,
        descripcion = %s,
        fabrica_id = %s
    WHERE id = %s
    """, (nombre, precio, existencias, descripcion, ID_fabrica, id))
    mysql.connection.commit()
    flash('Los cambios se aplicaron correctamente.')

    return redirect(url_for('index'))

# """"""""""""""""""""""""""""" Ruta eliminar articulo """""""""""""""""""""""""""""
@app.route('/eliminar_articulo/<string:id>')
def eliminar_articulo(id):
    cur = mysql.connection.cursor()
    cur.execute(f'DELETE FROM articulos WHERE id = {id}')
    mysql.connection.commit()
    flash('El cliente ha sido eliminado.')
    return redirect(url_for('index'))

# """"""""""""""""""""""""""""" Ruta editar cliente """""""""""""""""""""""""""""
@app.route('/editar_cliente/<string:id>')
def editar_cliente(id) -> 'html':
    cur = mysql.connection.cursor()
    cur.execute(f'SELECT * FROM clientes WHERE id = {id}')
    data = cur.fetchall()

    return render_template('editar_cliente.html', cliente = data[0])

 
# """"""""""""""""""""""""""""" Ruta actualizar cliente """""""""""""""""""""""""""""
@app.route('/actualizar_cliente/<id>', methods=['POST'])
def actualizar_cliente(id):
    nombre = request.form['nombre']
    direccion = request.form['direccion']
    saldo = float(request.form['saldo'])
    descuento = float(request.form['descuento'])
    saldo_limite = float(request.form['saldo_limite'])

    cur = mysql.connection.cursor()
    cur.execute("""
    UPDATE clientes 
    SET nombre_completo = %s,
        direccion = %s,
        saldo = %s,
        limite_saldo = %s,
        descuento = %s
    WHERE id = %s
    """, (nombre, direccion, saldo, saldo_limite, descuento, id))
    mysql.connection.commit()
    flash('Los cambios se aplicaron correctamente.')
    return redirect(url_for('index'))

# """"""""""""""""""""""""""""" Ruta eliminar cliente """""""""""""""""""""""""""""
@app.route('/eliminar_cliente/<string:id>')
def eliminar_cliente(id):
    cur = mysql.connection.cursor()
    cur.execute(f'DELETE FROM clientes WHERE id = {id}')
    mysql.connection.commit()
    flash('El cliente ha sido eliminado.')
    return redirect(url_for('index'))

# """"""""""""""""""""""""""""" Ruta registrar fábrica """""""""""""""""""""""""""""
@app.route('/registrar_fabrica', methods=['GET', 'POST'])
def registrar_fabrica() -> 'html':
    if 'usuario' in session:
        if request.method == 'POST':            
            nombre      = request.form['nombre']
            telefono    = request.form['telefono']
            direccion   = request.form['direccion']
            ciudad      = request.form['ciudad']
            alternativa = int(request.form['es_alternativa'])

            cur = mysql.connection.cursor()
            cur.execute("""
            INSERT INTO fabricas
            (nombre, telefono, direccion, ciudad, alternativa)
            VALUES (%s, %s, %s, %s, %s)
            """, (nombre, telefono, direccion, ciudad, alternativa))
            mysql.connection.commit()

            flash('Fábrica registrada correctamente.')

        return render_template('registrar_fabrica.html')

    else:
        return redirect(url_for('index'))

# """"""""""""""""""""""""""""" Ruta editar fábrica """""""""""""""""""""""""""""
@app.route('/editar_fabrica/<string:id>')
def editar_fabrica(id) -> 'html':
    cur = mysql.connection.cursor()
    cur.execute(f'SELECT * FROM fabricas WHERE id = {id}')
    data = cur.fetchall()

    return render_template('editar_fabrica.html', fabrica = data[0])

# """"""""""""""""""""""""""""" Ruta actualizar fabrica """""""""""""""""""""""""""""
@app.route('/actualizar_fabrica/<id>', methods=['POST'])
def actualizar_fabrica(id):
    nombre = request.form['nombre']
    telefono = request.form['telefono']
    direccion = request.form['direccion']
    ciudad = request.form['ciudad']
    es_alternativa = int(request.form['es_alternativa'])

    cur = mysql.connection.cursor()
    cur.execute("""
    UPDATE fabricas 
    SET nombre = %s,
        telefono = %s,
        direccion = %s,
        ciudad = %s,
        alternativa = %s
    WHERE id = %s
    """, (nombre, telefono, direccion, ciudad, es_alternativa, id))
    mysql.connection.commit()
    flash('Los cambios se aplicaron correctamente.')
    return redirect(url_for('index'))

# """"""""""""""""""""""""""""" Ruta registrar pedido """""""""""""""""""""""""""""
@app.route('/registrar_pedido', methods=['GET', 'POST'])
def registrar_pedido() -> 'html':
    if 'usuario' in session:

        if request.method == 'POST':
            print(f'El request:{request.form}')
            print(f'Longitud del dict: {len(request.form)}')
            print(f'El dict hecho lista: {list(request.form)}')

            # El último elemento del diccionario es el nombre del usuario
            # Así que todos los anteriores serán los artículos que eligió
            llaves_articulos = list(request.form)[:-1]
            print(f'Las llaves son: {llaves_articulos}')
            for llave in llaves_articulos:
                print(f'Llamando al diccionario request: {request.form[llave]}')

        elif request.method == 'GET':
            # Obtenemos todos los articulos de la base
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM articulos')
            articulos = cur.fetchall()
            cur.close()

            return render_template('registrar_pedido.html', articulos=articulos)
    
        
    else:
        return redirect(url_for('index'))

# ======================================= RUTAS =======================================

if __name__ == '__main__':
    app.run(debug=True, port=3000)