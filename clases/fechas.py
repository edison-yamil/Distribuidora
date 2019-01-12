#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import date
from clases.operaciones import archivo
from clases.operaciones import cadenanumeros


def calendario():
    arch = archivo("calendario")
    obj = arch.get_object

    obj("ventana").set_title("Calendario: Seleccione una Fecha")
    obj("ventana").set_default_size(350, 300)
    obj("ventana").set_position(1)
    obj("ventana").set_modal(True)

    resp = obj("ventana").run()
    seleccion = False

    if resp == 1:
        year, month, day = obj("calendar").get_date()

        fechaletra = cadenanumeros(day, 2) + " de " + \
            mesesletras(month + 1) + " de " + str(year)
        fechamysql = str(year) + "-" + \
            cadenanumeros(month + 1, 2) + "-" + cadenanumeros(day, 2)

        seleccion = [fechaletra, fechamysql]

    obj("ventana").destroy()
    return seleccion


def mesesletras(mes):
    if mes == 1:
        resp = "Enero"
    elif mes == 2:
        resp = "Febrero"
    elif mes == 3:
        resp = "Marzo"
    elif mes == 4:
        resp = "Abril"
    elif mes == 5:
        resp = "Mayo"
    elif mes == 6:
        resp = "Junio"
    elif mes == 7:
        resp = "Julio"
    elif mes == 8:
        resp = "Agosto"
    elif mes == 9:
        resp = "Septiembre"
    elif mes == 10:
        resp = "Octubre"
    elif mes == 11:
        resp = "Noviembre"
    elif mes == 12:
        resp = "Diciembre"
    return resp


def mysql_fecha(cadena):
    # Pasa de 'AA-MM-DD' a 'DD de MM de AA'
    anio = cadena.strftime("%Y")
    mes = mesesletras(int(cadena.strftime("%m")))
    dia = cadena.strftime("%d")
    fecha = dia + " de " + mes + " de " + anio
    return fecha


def mysql_fecha_hora(cadena):
    # Pasa de 'AA-MM-DD HH:MM:SS' a 'DD de MM de AA HH:MM:SS'
    anio = cadena.strftime("%Y")
    mes = mesesletras(int(cadena.strftime("%m")))
    dia = cadena.strftime("%d")
    hora = cadena.strftime("%H:%M:%S")
    fecha_hora = dia + " de " + mes + " de " + anio + " " + hora
    return fecha_hora


def cadena_fecha(cadena):
    # Pasa de 'AA-MM-DD' a 'DD de MM de AA'
    anio = cadena[:4]
    mes = mesesletras(int(cadena[5:7]))
    dia = cadena[8:]
    fecha = dia + " de " + mes + " de " + anio
    return fecha


def cantidad_dias(ini, fin):  # Formato AAAA-MM-DD
    dias = date(int(fin[:4]), int(fin[5:7]), int(fin[8:])) - \
        date(int(ini[:4]), int(ini[5:7]), int(ini[8:]))
    dias = dias.days + 1
    return dias


def mes_mas_uno(mes, anho):
    mes = cadenanumeros(int(mes) + 1, 2)
    if int(mes) > 12:
        mes, anho = "01", str(int(anho) + 1)
    return mes, anho


def fecha_hoy():
    hoy = mysql_fecha(date.today())
    return hoy


def dia_hoy():
    hoy = date.today()
    # Lunes(0) ... Domingo(6)
    cod = date.weekday(hoy) + 2

    if cod > 7:
        cod -= 7
    return cod


def dia_hoy_letras():
    cod = dia_hoy()

    if cod == 1:
        dia = "Domingo"
    elif cod == 2:
        dia = "Lunes"
    elif cod == 3:
        dia = "Martes"
    elif cod == 4:
        dia = "Miércoles"
    elif cod == 5:
        dia = "Jueves"
    elif cod == 6:
        dia = "Viernes"
    elif cod == 7:
        dia = "Sábado"
    return dia


def antiguedad(fecha):
    entrada = date(int(fecha[:4]), int(fecha[5:7]), int(fecha[8:]))
    hoy = date.today()

    # Años de Antigüedad
    ano = hoy.year - entrada.year
    if date(hoy.year - ano, hoy.month, hoy.day) < entrada:
        ano -= 1

    # Meses de Antigüedad
    hoy = date(hoy.year - ano, hoy.month, hoy.day)
    if hoy.year != entrada.year:
        mes = hoy.month + (12 - entrada.month)
    else:
        mes = hoy.month - entrada.month

    if hoy.day < entrada.day:
        mes -= 1

    # Antigüedad en Letras: anos, meses
    v_ano = "año" if ano == 1 else "años"
    v_mes = "mes" if mes == 1 else "meses"
    antig = str(ano) + " " + v_ano + ", " + str(mes) + " " + v_mes

    return ano, antig


def preavisos(antig):  # Días de Preaviso
    if antig < 1:
        preaviso = 30
    elif antig < 5:
        preaviso = 45
    elif antig < 10:
        preaviso = 60
    else:
        preaviso = 90

    return preaviso


def vacaciones(antig):  # Días de Vacaciones
    if antig < 5:
        vacacion = 12
    elif antig < 10:
        vacacion = 18
    else:
        vacacion = 30

    return vacacion
