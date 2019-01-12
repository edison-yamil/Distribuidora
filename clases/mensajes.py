#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository.Gtk import MessageDialog
from gi.repository.Gtk import MessageType
from gi.repository.Gtk import ButtonsType
from gi.repository.Gtk import ResponseType


def mensaje(mensaje_principal, mensaje_secundario, tipodialogo):
    if tipodialogo == 0:
        # Tipo de Diálogo (Información). Opción de Botón (ACEPTAR)
        titulo = "¡Información!"
        tipodialogo = MessageType.INFO
        tipoboton = ButtonsType.OK

    elif tipodialogo == 1:
        # Tipo de Diálogo (Atención). Opción de Botones (ACEPTAR-CANCELAR)
        titulo = "¡Atención!"
        tipodialogo = MessageType.WARNING
        tipoboton = ButtonsType.OK_CANCEL

    elif tipodialogo == 2:
        # Tipo de Diálogo (Pregunta). Opción de Botones (SI-NO)
        titulo = "¡Atención!"
        tipodialogo = MessageType.QUESTION
        tipoboton = ButtonsType.YES_NO

    elif tipodialogo == 3:
        # Tipo de Diálogo (Error). Opción de Botón (CANCELAR)
        titulo = "¡Error!"
        tipodialogo = MessageType.ERROR
        tipoboton = ButtonsType.CANCEL

    dialogo = MessageDialog(None, 1, tipodialogo, tipoboton, mensaje_principal)  # Mensaje principal (letra grande)
    dialogo.format_secondary_text(mensaje_secundario)  # Mensaje secundario al usuario (letra pequeña)
    dialogo.set_position(1)  # Centrado del diálogo
    dialogo.set_title(titulo)  # Título de ventana

    # Tipos de Diálogos (MessageType): INFO, QUESTION, WARNING, ERROR
    # Tipos de Botones (ButtonsType): NONE, OK, CLOSE, CANCEL, YES_NO, OK_CANCEL
    # Respuesta (ResponseType): NO, YES

    resp = dialogo.run()  # Ejecutar el Diálogo
    dialogo.destroy()  # Luego de presionar algun botón, el Diálogo se destruye

    if resp in (ResponseType.YES, ResponseType.OK):  # Averiguamos si se presiono el Botón SI/OK
        resp = True  # Devuelve el valor True si se respondio con SI/OK
    else:
        resp = False  # Sino siempre devuelve False, incluyendo las opciones de ACEPTAR

    return resp


# Mensajes referentes a la Inserción, Modificación o Eliminación de un Registro

def no_tiene_permiso(accion):
    error_generico("No se ha podido " + accion + " el registro.",
    "No tiene permiso para realizar esta operación.\n" +
    "Hable con el Administrador del Sistema.")


def no_puede_guardar(accion, secun=None):
    secun = "Los Datos pueden no ser Correctos." if secun is None else secun
    error_generico("No se ha podido " + accion + " el registro.", secun)


def no_puede_borrar():
    error_generico("No se ha podido eliminar el registro",
    "Es posible que se este usando\nen otras instancias del Sistema.")


def no_puede_modificar_eliminar_anular(accion, secun):
    if accion == 1: accion = "Modificado"
    elif accion == 2: accion = "Eliminado"
    elif accion == 3: accion = "Anulado"
    error_generico("El registro seleccionado no puede ser " + accion + ".", secun)


# Mensajes referentes a Preguntas de Confirmación

def pregunta_borrar(informacion):
    resp = mensaje("¿Está seguro de que desea Borrar?", informacion, 2)
    return resp


def pregunta_anular(informacion):
    resp = mensaje("¿Está seguro de que desea Anular?", informacion, 2)
    return resp


# Otros Mensajes

def atencion_generico(princ, secun):
    mensaje(princ, secun, 1)


def error_generico(princ, secun):
    mensaje(princ, secun, 3)


def error_permiso_archivo(error=""):
    mensaje("Error de Permiso", "Puede ser que el nombre " +
        "elegido para el archivo a generar\nsea igual a uno que " +
        "en este momento se esté utilizando\n\n" + error, 3)


def informa_generico(princ, secun):
    mensaje(princ, secun, 0)


def operacion_correcta():
    mensaje("Operación Exitosa", "La operación ha sido realizada Satisfactoriamente.", 0)


def pregunta_generico(princ, secun):
    resp = mensaje(princ, secun, 2)
    return resp


# Mensajes de Ayuda a los Usuarios

def boton_guardar_cancelar(guardar, cancelar, titulo=None, bloquea=True):
    titulo = "actual" if titulo is None else "de " + titulo
    guardar.set_tooltip_text("Presione este botón para Guardar el registro " + titulo)
    cancelar.set_tooltip_text("Presione este botón para Cerrar esta ventana sin guardar cambios")
    if bloquea: guardar.set_sensitive(False)


def usar_boton(opcion):
    resp = "Use el botón de la derecha para ingresar\n" + opcion
    return resp
