#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sys import exc_info
from decimal import Decimal
from gi.repository.Gtk import Builder
from gi.repository.Gtk import CellRendererText
from gi.repository.Gtk import CellRendererToggle
from gi.repository.Gtk import ListStore
from gi.repository.Gtk import TreeViewColumn
from mysql.connector import errors as MySqlErr
from clases import mensajes as Mens


##### Obtención de Archivos ############################################

def archivo(nombre):
    try:
        arch = Builder()
        arch.add_from_file("ventanas/" + nombre + ".glade")
        return arch
    except:
        return False


##### Configuración de Combos ##########################################

def combos_config(datos_conexion, objeto, tabla, cod):
    if tabla == "ajustemotivos":
        lista = ListStore(int, str, int)
    elif tabla == "impuestos":
        lista = ListStore(int, str, float)
    elif tabla == "monedas_s":
        lista = ListStore(int, str, int, str, str)
    elif tabla == "turnos":
        lista = ListStore(int, str, str, str)
    else:
        tipo = str if tabla in ("generos", "tipodocumentos", "unidadmedidas") else int
        lista = ListStore(tipo, str)
    objeto.set_model(lista)

    cell = CellRendererText()
    objeto.pack_start(cell, True)
    objeto.add_attribute(cell, 'text', 1)  # Mostrar segunda columna

    conexion = conectar(datos_conexion)
    cursor = consultar(conexion, "*", tabla, " ORDER BY " + cod)
    datos = cursor.fetchall()
    cant = cursor.rowcount
    conexion.close()

    lista.clear()
    for i in range(0, cant):
        listafila = [datos[i][0], datos[i][1]]
        if tabla in ("ajustemotivos", "impuestos"):
            listafila.append(datos[i][2])
        elif tabla == "monedas_s":
            listafila.extend([datos[i][2], datos[i][3], datos[i][4]])
        elif tabla == "turnos":
            listafila.extend([str(datos[i][2]), str(datos[i][3])])
        lista.append(listafila)


##### Conexión a Base de Datos #########################################

def conectar(datos_conexion):
    try:
        usuario = datos_conexion[0]
        contrasena = datos_conexion[1]

        from mysql.connector import MySQLConnection
        conexion = MySQLConnection(
            host="127.0.0.1", user=usuario, passwd=contrasena,
            db="distribuidora", charset="utf8")
        conexion.names = "utf8"
        return conexion
    except MySqlErr.ProgrammingError as e:
        print(("Conectar: Error de Programación:\n" + str(e) + "\n"))
        return False
    except:
        print("Error en Conectar: ", exc_info()[0])
        return False


##### Operaciones sobre Permisos #######################################

def concede_select(cursor, tabla, usuario):
    sql = "GRANT SELECT ON TABLE distribuidora." + tabla + " TO '" + usuario + "'"
    print(sql)
    cursor.execute(sql)


def revoca_select(cursor, tabla, usuario):
    sql = "REVOKE SELECT ON TABLE distribuidora." + tabla + " FROM '" + usuario + "'"
    print(sql)
    cursor.execute(sql)


def concede_rutina(cursor, tabla, usuario):
    sql = "GRANT EXECUTE ON PROCEDURE distribuidora." + tabla + " TO '" + usuario + "'"
    print(sql)
    cursor.execute(sql)


def revoca_rutina(cursor, tabla, usuario):
    sql = "REVOKE EXECUTE ON PROCEDURE distribuidora." + tabla + " FROM '" + usuario + "'"
    print(sql)
    cursor.execute(sql)


##### Operaciones sobre Registros ######################################

def consultar(conexion, campos, tabla, condicion=""):
    sql = "SELECT " + campos + " FROM " + tabla + condicion

    try:
        print(sql)
    except UnicodeEncodeError as e:
        print("Error de Unicode: " + str(e))

    cursor = conexion.cursor()
    cursor.execute(sql)
    return cursor


def procedimientos(conexion, tabla, valores, accion):
    sql = "CALL " + tabla + " (" + valores + ")"

    try:
        print(sql)
    except UnicodeEncodeError as e:
        print("Error de Unicode: " + str(e))

    try:
        cursor = conexion.cursor()
        cursor.execute(sql)
        cursor.close()
        return True

    except MySqlErr.ProgrammingError as e:
        print((accion + ": Error de Programación:\n" + str(e) + "\n"))
        Mens.no_tiene_permiso(accion)
        return False

    except MySqlErr.OperationalError as e:
        print((accion + ": Error Operacional:\n" + str(e) + "\n"))
        Mens.no_tiene_permiso(accion)
        return False

    except MySqlErr.IntegrityError as e:
        print((accion + ": Error de Integridad de Datos:\n" + str(e) + "\n"))
        return False

    except MySqlErr.InternalError as e:
        print((accion + ": Error Interno:\n" + str(e) + "\n"))
        '''if not conexion.isConnected():
            conexion.reconnect()
            procedimientos(conexion, tabla, valores, accion)'''
        return False

    except MySqlErr.Error as e:
        print("Error en Procedimientos: ", exc_info()[0])
        print((accion + ": Error de Conexion o Ejecucion:\n\t" + str(e) + "\n"))
        return False

    except MySqlErr.Warning as e:
        print((accion + ": Mensaje de Advertencia:\n" + str(e) + "\n"))
        return False


##### Llamadas a Operaciones sobre Registros ###########################

def nuevoid(datos_conexion, tabla, campoid):
    if type(datos_conexion) == list:
        conexion = conectar(datos_conexion)
    else:  # Para las transacciones
        conexion = datos_conexion

    cursor = consultar(conexion, "IFNULL(MAX(" + campoid + "), 0) + 1", tabla)
    datos = cursor.fetchall()
    ultimoid = str(datos[0][0])

    if type(datos_conexion) == list:
        conexion.close()  # Finaliza la conexión
    return ultimoid


def insertar(conexion, tabla, valores):
    tabla += "_i"
    estado = procedimientos(conexion, tabla, valores, "Insertar")
    return estado


def modificar(conexion, tabla, valores):
    tabla += "_u"
    estado = procedimientos(conexion, tabla, valores, "Modificar")
    return estado


def eliminar(conexion, tabla, valores):
    tabla += "_d"
    estado = procedimientos(conexion, tabla, valores, "Eliminar")
    if not estado:
        Mens.no_puede_borrar()
    return estado


def anular(conexion, tabla, valores):
    tabla += "_a"
    estado = procedimientos(conexion, tabla, valores, "Anular")
    return estado


##### Operaciones sobre Fechas #########################################

def compara_fechas(datos_conexion, fecha1, accion, fecha2):
    # Compara dos fechas usando al servidor
    sql = "SELECT IF(" + fecha1 + " " + accion + " " + fecha2 + ", 1, 0)"
    print(sql)

    conexion = conectar(datos_conexion)
    cursor = conexion.cursor()
    cursor.execute(sql)
    resultado = cursor.fetchall()[0][0]
    conexion.close()  # Finaliza la conexión

    respuesta = True if resultado == 1 else False
    return respuesta


def modifica_fecha(datos_conexion, fecha, cantidad, tipo):
    # Añade una cantidad de tiempo a una fecha usando al servidor
    sql = "SELECT DATE_ADD(" + fecha + ", INTERVAL " + cantidad + " " + tipo + ")"
    print(sql)

    conexion = conectar(datos_conexion)
    cursor = conexion.cursor()
    cursor.execute(sql)
    resultado = cursor.fetchall()[0][0]
    conexion.close()  # Finaliza la conexión

    return resultado


##### Operaciones sobre Valores ########################################

def redondear(datos_conexion, valor, decimales="2"):
    # Devuelve un número (float) con x cantidad de decimales
    conexion = conectar(datos_conexion)
    cursor = conexion.cursor()
    cursor.execute("SELECT ROUND(" + valor + ", " + decimales + ")")
    resultado = cursor.fetchall()[0][0]
    conexion.close()  # Finaliza la conexión
    return resultado


def cadenanumeros(num, cant):
    # Devuelve un string con una cantidad de ceros antes de un número
    resp = ""
    for i in range(len(str(num)), cant):
        resp += "0"
    resp += str(num)
    return resp


def comprobar_numero(tipo, objeto, campo, barraestado, igual_cero=True):
    try:
        valor = tipo(objeto.get_text())
    except:
        objeto.grab_focus()
        ex = " (##.#)" if tipo == float else ""
        barraestado.push(0, "Por favor cargue solamente números para " + campo + ex + ".")
        return False
    else:
        if valor >= 0:
            if valor > 0 or igual_cero:
                barraestado.push(0, "")
                return True
            else:
                objeto.grab_focus()
                barraestado.push(0, "El " + campo + " debe ser mayor a CERO.")
                return False
        else:
            objeto.grab_focus()
            barraestado.push(0, "El " + campo + " debe ser un Número Positivo.")
            return False


def comprobar_unique(datos_conexion, tabla, campo, valor, objeto, guardar, barraestado, mensaje):
    if type(datos_conexion) == list:
        conexion = conectar(datos_conexion)
    else:  # Para las transacciones
        conexion = datos_conexion

    cursor = consultar(conexion, campo, tabla, " WHERE " + campo + " = " + valor)
    print(cursor.fetchall())  # Necesario para que la siguiente linea funcione
    cantidad_encontrada = cursor.rowcount

    if type(datos_conexion) == list:
        conexion.close()  # Finaliza la conexión

    if cantidad_encontrada > 0:
        # Si se han encontrado coincidencias es un error de duplicación de datos
        try:
            guardar.set_sensitive(False)  # Es un solo botón
        except:
            guardar(False)  # Son más dos o más botones (en una función)

        objeto.grab_focus()
        barraestado.push(0, mensaje)
        return False
    else:
        barraestado.push(0, "")
        return True


def obtener_nombre(nombre, otronombre, apellido, otroapellido):
    # Nombres
    texto = nombre
    if otronombre is not None:
        texto += " " + otronombre
    # Apellidos
    texto += " " + apellido
    if otroapellido is not None:
        texto += " " + otroapellido
    # Nombre y Apellido
    return texto


def obtener_salario_minimo(datos_conexion):
    conexion = conectar(datos_conexion)
    cursor = conexion.cursor()

    cursor.execute("SELECT MAX(S.FechaVigencia) FROM salariosminimos S")
    fecha = str(cursor.fetchall()[0][0])

    cursor.execute("SELECT S.idSalarioMinimo, S.Monto, S.FechaVigencia " +
        "FROM salariosminimos S WHERE (IF((S.FechaVigencia = '" + fecha + "'), 1, 0) = 1)")
    datos = cursor.fetchall()

    if cursor.rowcount > 0:
        salario = Decimal(datos[0][1])
    else:
        salario = Decimal(0.0)

    return salario


##### Campos de Texto, Botones, Combos o SpinButton ####################

def objetos_set_sensitive(lista, estado):
    for objeto in lista:
        objeto.set_sensitive(estado)


##### Tablas o Grillas #################################################

def celdas(alineacion):
    celda = CellRendererText()
    celda.set_property('xalign', alineacion)  # Alineación del Contenido
    # 0.0 = izquierda, 0.5 = centrada, 1.0 = derecha
    return celda


def columnas(titulo, celda, texto, resize, anchominimo=None, anchomaximo=None):
    col = TreeViewColumn(titulo, celda, text=texto)
    col.set_resizable(resize)  # Columna puede cambiar de tamaño
    col.set_alignment(0.5)  # Alineación del Título
    if anchominimo is not None:
        col.set_property('min-width', anchominimo)
    if anchomaximo is not None:
        col.set_property('max-width', anchomaximo)
    return col


def columna_active(titulo, act):
    col = TreeViewColumn(titulo, CellRendererToggle(), active=act)
    col.set_resizable(False)  # Columna no puede cambiar de tamaño
    col.set_alignment(0.5)    # Alineación del Título (centrado)
    col.set_property('min-width', 90)  # Ancho Mínimo de Columna
    return col
