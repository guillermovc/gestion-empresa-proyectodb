import flask
from flask import render_template, request, redirect, url_for, flash, session

from database import mysql

pedidos = flask.Blueprint('pedidos', __name__)


def obtener_articulos_validos(lista_articulos):
    articulos = []
    for articulo in lista_articulos:
        if int(articulo[1]) > 0:
            articulos.append(articulo)
        
    return articulos


# """"""""""""""""""""""""""""" Ruta registrar pedido """""""""""""""""""""""""""""
@pedidos.route('/registrar_pedido', methods=['GET', 'POST'])
def registrar_pedido() -> 'html':
    if 'usuario' in session:

        cur = mysql.connection.cursor()

        if request.method == 'POST':

            print(f'El dict: {request.form}')
            request_list = list(request.form.items())   # Convertimos a lista el diccionario de request
            articulos_pedidos = obtener_articulos_validos(request_list[:-2]) # Solo articulos con cantidad != 0
            cliente_id = int(request.form['cliente'])   # Id del cliente
            fecha_entrega = request.form['fecha_entrega']   # Fecha de la entrega

            # Verificar que hayan suficientes articulos para satisfacer el pedido
            cur.execute('SELECT id, existencias FROM articulos') # Pedimos id y num. articulos existentes
            articulos_disp = cur.fetchall() 
            # print(f'Articulos disponibles: {articulos_disp}')
            for articulo in articulos_pedidos:
                for articulo_disp in articulos_disp:
                    id_articulo_pedido = int(articulo[0].split('_')[2])
                    cantidad_articulo_pedido = int(articulo[1])

                    id_articulo_disp = articulo_disp[0]
                    cantidad_articulo_disp = articulo_disp[1]

                    # Si coinciden los artículos, debemos verificar que existencias sea mayor
                    # o igual al numero de articulos que el usuario está pidiendo
                    if id_articulo_pedido == id_articulo_disp:
                        if cantidad_articulo_disp >= cantidad_articulo_pedido:
                            print('Hay articulos disponibles.')

                            # Calculamos la que será la nueva existencia del producto
                            nueva_existencia = cantidad_articulo_disp - cantidad_articulo_pedido

                            # Actualizar la tabla articulos para restar las existencias
                            cur.execute("""
                                    UPDATE articulos 
                                    SET existencias = %s 
                                    WHERE id = %s
                            """, (nueva_existencia, id_articulo_disp))
                            mysql.connection.commit()

                        else:
                            print('No hay articulos suficientes.')
                            # Informamos al usuario que su solicitud no pudo ser procesada
                            flash("""No hay articulos suficientes para completar su pedido.
                                    Verifique los campos e intentelo de nuevo.""")
                            return redirect(url_for('registrar_pedido'))


            total_cuenta = 0
            
            # Creamos un nuevo pedido, que en un inicio no tendrá total
            # pero lo necesitamos para ligar la tabla detalle pedidos
            cur.execute("""INSERT INTO pedidos 
                        (cliente_id, total, entrega) 
                        VALUES (%s, %s, %s) """,
                        (cliente_id, 0, fecha_entrega))
            mysql.connection.commit()

            # Recorremos cada artículo que el usuario pidió
            for articulo in articulos_pedidos:
                id_articulo = int(articulo[0].split('_')[-1])
                cantidad = int(articulo[1])

                # Necesitamos saber el precio del artículo que estamos comprando
                # para agregar a la cuenta la cantidad correcta
                cur.execute('SELECT precio FROM articulos WHERE id = %s', [id_articulo])
                precio = cur.fetchall()[0][0]
                print(f'Precio del articulo {id_articulo}: {precio}, cantidad:{cantidad}')

                acumulado = cantidad * precio

                # print(f'Se agrega a la cuenta: {acumulado}')
                
                # Obtenemos el último registro de la tabla pedidos
                cur.execute('SELECT MAX(id) FROM pedidos')
                ultimo_pedido_id = int(cur.fetchall()[0][0])
                # print(f'Id del ultimo pedido: {ultimo_pedido_id}')               

                # Insertamos un nuevo registro de detalle pedido, ligado al último pedido creado
                cur.execute("""INSERT INTO detalle_pedidos 
                            (pedido_id, articulo_id, cantidad, total) 
                            VALUES (%s, %s, %s, %s)""",
                            (ultimo_pedido_id, id_articulo, cantidad, acumulado))
                mysql.connection.commit()

                # Vamos acumulando el total de la cuenta
                total_cuenta += acumulado

            # Actualizamos el registro del pedido con el total correcto de la cuenta
            cur.execute("""
                        UPDATE pedidos
                        SET total = %s
                        WHERE id = %s
                        """, (total_cuenta, ultimo_pedido_id))
            mysql.connection.commit()

            # Agregamos el crédito que generó el pedido a la cuenta del usuario
            cur.execute("""SELECT saldo FROM clientes WHERE id=%s """,[cliente_id])
            saldo_cliente = cur.fetchall()[0][0]

            saldo_cliente += total_cuenta
            cur.execute("""
            UPDATE clientes 
            SET saldo = %s 
            WHERE id = %s""", (saldo_cliente, cliente_id))
            mysql.connection.commit()

            cur.close()

            flash('Se realizó el pedido con exito') # informamos que todo salió bien
            return redirect(url_for('index'))

        elif request.method == 'GET':
            # Obtenemos todos los articulos de la base
            cur.execute('SELECT * FROM articulos')
            articulos = cur.fetchall()

            cur.execute('SELECT * FROM clientes')
            clientes = cur.fetchall()

            cur.close()

            return render_template('registrar_pedido.html',
                                    articulos=articulos,
                                    clientes=clientes,
                                    usuario=session['nombre'])
    
    # No hay una sesión iniciada
    else:
        return redirect(url_for('index'))


# """"""""""""""""""""""""""""" Ruta ver detalles pedido """""""""""""""""""""""""""""
@pedidos.route('/detalles_pedido/<string:id>')
def detalles_pedido(id) -> 'html':
    if 'usuario' in session:
        cur = mysql.connection.cursor()
        
        # Consulta para obtener información general del pedido
        cur.execute("""SELECT * FROM pedidos WHERE id=%s""", [id])
        info_pedido = cur.fetchall()[0]

        # Informacion del cliente
        id_cliente = info_pedido[1]
        cur.execute("""SELECT * FROM clientes WHERE id=%s""",[id_cliente])
        info_cliente = cur.fetchall()[0]

        # Información de los artículos
        id_pedido = info_pedido[0]
        cur.execute("""SELECT articulos.id, articulos.fabrica_id, 
                    articulos.nombre, articulos.precio, detalle_pedidos.cantidad, 
                    articulos.descripcion 
                    FROM articulos 
                    INNER JOIN detalle_pedidos 
                    ON articulos.id=detalle_pedidos.articulo_id 
                    WHERE detalle_pedidos.pedido_id = %s""", [id_pedido])
        info_articulos = cur.fetchall()

        # print(f'Información del pedido: {info_pedido}')
        # print(f'Información del cliente: {info_cliente}')
        # print(f'IInformación de los articulos: {info_articulos}')

        # Cerramos la conexión 
        # cur.close()

        return render_template('detalles_pedido.html',
                                titulo = f'Detalles del pedido {id}',
                                pedido=info_pedido,
                                cliente=info_cliente,
                                articulos=info_articulos,
                                usuario=session['nombre'])

    return redirect(url_for('index'))


# """"""""""""""""""""""""""""" Ruta eliminar pedido """""""""""""""""""""""""""""
@pedidos.route('/eliminar_pedido/<id>')
def eliminar_pedido(id):

    if 'usuario' in session:
        cur = mysql.connection.cursor()

        # Devolver el credito al cliente 
        cur.execute(f'SELECT total, cliente_id FROM pedidos WHERE id ={id}')
        total_pedido, cliente_id = cur.fetchall()[0]
        
        cur.execute(f'SELECT saldo FROM clientes WHERE id = {cliente_id}')
        saldo_cliente = cur.fetchall()[0][0]
        saldo_cliente -= total_pedido
        
        cur.execute("""
            UPDATE clientes 
            SET saldo = %s 
            WHERE id = %s""", (saldo_cliente, cliente_id))
        mysql.connection.commit()

        # Devolver las existencias a los artículos
        # Información de los artículos
        cur.execute("""SELECT articulos.id, detalle_pedidos.cantidad FROM articulos 
                    INNER JOIN detalle_pedidos 
                    ON articulos.id=detalle_pedidos.articulo_id 
                    WHERE detalle_pedidos.pedido_id = %s""", [id])
        articulos_y_cant_pedida = cur.fetchall()

        for id_articulo, cant_pedida in articulos_y_cant_pedida:
            print(f'ID_ARTICULO: {id_articulo}, cant_pedida: {cant_pedida}')
            cur.execute("""
            UPDATE articulos 
            SET existencias = existencias + %s 
            WHERE id = %s;""", (cant_pedida, id_articulo))
            mysql.connection.commit()
        
        # Eliminar el pedido de la tabla
        cur.execute(f'DELETE FROM pedidos WHERE id = {id}')
        mysql.connection.commit()
        flash('El pedido ha sido eliminado.')
    return redirect(url_for('index'))