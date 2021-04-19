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


# ===================================== FUNCIONES =====================================



# ======================================= RUTAS =======================================

# """"""""""""""""""""""""""""" Ruta principal """""""""""""""""""""""""""""
@app.route('/')
@app.route('/index')
def index() -> 'html':

    usuario = None
    clientes = None
    if 'usuario' in session:
        usuario = session['usuario']

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM clientes')
        clientes = cur.fetchall()
        
    return render_template('index.html',
                        page_title='Proyecto',
                        header_title='Página principal',
                        usuario=usuario,
                        clientes=clientes
    )


# """"""""""""""""""""""""""""" Ruta registro """""""""""""""""""""""""""""
@app.route('/registro', methods=['GET','POST'])
def registro() -> 'html':

    if request.method == 'POST':
        nombre_completo = request.form['nombre']
        username = request.form['user']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            print("Las password no coinciden")

        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO usuarios (nombre, user, password) VALUES (%s, %s, %s)',
                    (nombre_completo, username, password))
        mysql.connection.commit()

        flash('Se ha registrado correctamente')

        # Creamos una sesión para que el usuario no tenga que hacer login
        # cuando acaba de registrarse
        session['usuario'] = username

        # Redirigimos al index, que será diferente cuando hay una sesión activa
        return redirect(url_for('index'))

    else:
        return render_template('registro.html',
                                header_title='Registro de usuario',
                                page_title='Registro',
        )
    
# """"""""""""""""""""""""""""" Ruta logearse """""""""""""""""""""""""""""
@app.route('/login', methods=['GET', 'POST'])
def login() -> 'html':
    
    if request.method == 'POST':
        session['usuario'] = request.form['user']
        return redirect(url_for('index'))

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

        return render_template('registrar_cliente.html')
    else:
        return redirect(url_for('index'))

# """"""""""""""""""""""""""""" Ruta editar cliente """""""""""""""""""""""""""""
@app.route('/editar_cliente/<string:id>')
def editar_cliente(id):
    cur = mysql.connection.cursor()
    cur.execute(f'SELECT * FROM clientes WHERE id = {id}')
    data = cur.fetchall()

    print(data[0][1])

    return render_template('editar_cliente.html', cliente = data[0])


@app.route('/actualizar_cliente/<string:id>', methods=['POST'])
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

    flash('Los cambios se aplicaron correctamente.')

    return redirect(url_for('index'))

# """"""""""""""""""""""""""""" Ruta ingresar cliente """""""""""""""""""""""""""""
@app.route('/eliminar_cliente/<string:id>')
def eliminar_cliente(id):
    cur = mysql.connection.cursor()
    cur.execute(f'DELETE FROM clientes WHERE id = {id}')
    mysql.connection.commit()
    flash('El cliente ha sido eliminado.')
    return redirect(url_for('index'))

# ======================================= RUTAS =======================================

if __name__ == '__main__':
    app.run(debug=True, port=3000)