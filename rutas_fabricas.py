# Hecho por: Juan Hernandez

import flask
from flask import render_template, request, redirect, url_for, flash, session

from database import mysql

fabricas = flask.Blueprint('fabricas', __name__)

# """"""""""""""""""""""""""""" Ruta registrar fábrica """""""""""""""""""""""""""""
@fabricas.route('/registrar_fabrica', methods=['GET', 'POST'])
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

        return render_template('registrar_fabrica.html',
        usuario=session['nombre'])

    else:
        return redirect(url_for('index'))


# """"""""""""""""""""""""""""" Ruta editar fábrica """""""""""""""""""""""""""""
@fabricas.route('/editar_fabrica/<string:id>')
def editar_fabrica(id) -> 'html':
    if 'usuario' in session:
        cur = mysql.connection.cursor()
        cur.execute(f'SELECT * FROM fabricas WHERE id = {id}')
        data = cur.fetchall()

        return render_template('editar_fabrica.html', 
        fabrica = data[0], usuario=session['nombre'])
    else:
        return redirect(url_for('index'))


# """"""""""""""""""""""""""""" Ruta actualizar fabrica """""""""""""""""""""""""""""
@fabricas.route('/actualizar_fabrica/<id>', methods=['POST'])
def actualizar_fabrica(id):
    if 'usuario' in session:
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


# """"""""""""""""""""""""""""" Ruta eliminar cliente """""""""""""""""""""""""""""
@fabricas.route('/eliminar_fabrica/<string:id>')
def eliminar_fabrica(id):
    if 'usuario' in session:
        cur = mysql.connection.cursor()
        cur.execute(f'DELETE FROM fabricas WHERE id = {id}')
        mysql.connection.commit()
        flash('La fábrica ha sido eliminado.')
    return redirect(url_for('index'))