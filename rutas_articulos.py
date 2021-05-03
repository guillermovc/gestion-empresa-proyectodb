import flask
from flask import render_template, request, redirect, url_for, flash, session

from database import mysql

articulos = flask.Blueprint('articulos', __name__)

# """"""""""""""""""""""""""""" Ruta registrar articulo """""""""""""""""""""""""""""
@articulos.route('/registrar_articulo', methods=['GET', 'POST'])
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
            cur.execute('INSERT INTO articulos (nombre, precio, existencias, descripcion, fabrica_id) VALUES (%s, %s, %s, %s, %s)',
                        (nombre, precio, existencias, descripcion, ID_fabrica))
            mysql.connection.commit()
            flash('Articulo registrado correctamente')
            return render_template('registrar_articulo.html')
        else:
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM fabricas')
            fabricas = cur.fetchall()
            return render_template('registrar_articulo.html', 
            fabricas=fabricas, usuario=session['usuario'])
    else:
        return redirect(url_for('index'))


# """"""""""""""""""""""""""""" Ruta editar articulo """""""""""""""""""""""""""""
@articulos.route('/editar_articulo/<string:id>')
def editar_articulo(id):

    if 'usuario' in session:
        cur = mysql.connection.cursor()
        cur.execute(f'SELECT * FROM articulos WHERE id = {id}')
        data = cur.fetchall()
        cur.execute(f'SELECT * FROM fabricas')
        fabricas = cur.fetchall()
        return render_template('editar_articulo.html', 
        articulo = data[0], fabricas=fabricas,usuario=session['usuario'])
    
    else:
        return redirect(url_for('index'))


# """"""""""""""""""""""""""""" Ruta actualizar articulo """""""""""""""""""""""""""""
@articulos.route('/actualizar_articulo/<id>', methods=['POST'])
def actualizar_articulo(id):
    if 'usuario' in session:
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
@articulos.route('/eliminar_articulo/<string:id>')
def eliminar_articulo(id):
    if 'usuario' in session:
        cur = mysql.connection.cursor()
        cur.execute(f'DELETE FROM articulos WHERE id = {id}')
        mysql.connection.commit()
        flash('El cliente ha sido eliminado.')
    return redirect(url_for('index'))