import flask
from flask import render_template, request, redirect, url_for, flash, session

from database import mysql

clientes = flask.Blueprint('clientes', __name__)


# """"""""""""""""""""""""""""" Ruta ingresar cliente """""""""""""""""""""""""""""
@clientes.route('/registrar_cliente', methods=['GET', 'POST'])
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


# """"""""""""""""""""""""""""" Ruta editar cliente """""""""""""""""""""""""""""
@clientes.route('/editar_cliente/<id>')
def editar_cliente(id) -> 'html':
    cur = mysql.connection.cursor()
    cur.execute(f'SELECT * FROM clientes WHERE id = {id}')
    data = cur.fetchall()

    return render_template('editar_cliente.html', cliente = data[0])


# """"""""""""""""""""""""""""" Ruta actualizar cliente """""""""""""""""""""""""""""
@clientes.route('/actualizar_cliente/<id>', methods=['POST'])
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
@clientes.route('/eliminar_cliente/<string:id>')
def eliminar_cliente(id):
    cur = mysql.connection.cursor()
    cur.execute(f'DELETE FROM clientes WHERE id = {id}')
    mysql.connection.commit()
    flash('El cliente ha sido eliminado.')
    return redirect(url_for('index'))