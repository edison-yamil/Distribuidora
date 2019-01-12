#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import popen

from clases.dialogos import dialogo_guardar
from clases.mensajes import error_generico

from reportlab.platypus import Paragraph
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Spacer
from reportlab.platypus import Table

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm


def listado(titulo, lista, tamanos, hoja):
    ubicacion_archivo = dialogo_guardar()

    if ubicacion_archivo is not None:
        # Si no tiene la terminación .pdf se le agrega
        if ubicacion_archivo[-4:].lower() != ".pdf":
            ubicacion_archivo += ".pdf"

        story = []
        cabecera = getSampleStyleSheet()['Heading1']
        cabecera.pageBreakBefore = 0
        cabecera.keepWithNext = 0

        parrafo = Paragraph("Registros de " + titulo, cabecera)
        story.append(parrafo)
        story.append(Spacer(0, 20))

        tabla = Table(lista, tamanos)
        tabla = tabla_style(tabla)

        if tabla.minWidth() <= (hoja[0] - 5 * cm):  # hoja (A4)
            story.append(tabla)
        else:
            story.append(tabla)
            print("Tabla de Tamanho mayor a permitido")

        '''
            for x in tamanos:
                pos = x
                newTable = [y[0:x] for y in tabla]

                tb = Table(newTable)
                tb.setStyle(tabla.getStyle())

                if tb.minWidth() <= (hoja[0] - 5*cm):
                    story.append(tb)
                    break
        '''

        doc = SimpleDocTemplate(
            ubicacion_archivo,
            #os.path.join(os.path.expanduser("~"), "Desktop", "listado.pdf"),
            pagesize=hoja,  # Tamaño de Página (landscape(A4) hoja horizontal)
            allowSplitting=1,
            title="Registros de " + titulo,
            author="Sistema Distribuidora"
        )

        try:  # Generar archiv
            doc.build(story)
            popen(ubicacion_archivo)
        except PermissionError as e:
            error_generico("Error de Permiso", "Puede ser que el nombre " +
                "elegido para el archivo a generar\nsea igual a uno que " +
                "en este momento se esté utilizando\n\n" + str(e))


def cabecera_style():
    style = getSampleStyleSheet()['Heading1']
    style.alignment = TA_CENTER
    style.textColor = colors.black
    style.pageBreakBefore = 0
    style.keepWithNext = 0
    return style


def parrafo_bodytext(tamano=12):
    style = getSampleStyleSheet()['BodyText']
    style.alignment = TA_JUSTIFY
    style.textColor = colors.black
    style.fontSize = tamano
    return style


def tabla_style(tabla):
    # Propiedades de la Tabla # (Columna, Fila) # (-1, hasta el final)
    tabla.setStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),  # Color de Fondo del Encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Color del Texto del Encabezado
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),  # Color del Texto de Tabla
        ('FONTSIZE', (0, 0), (-1, 0), 12),  # Tamaño de Fuente del Encabezado
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Alineación de la Columna Código
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alineación Vertical de la Tabla
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),  # Borde Exterior de la Tabla
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),  # Grilla Interior de la Tabla
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),  # Espacio Abajo del Encabezado
        ('BOTTOMPADDING', (0, 1), (-1, -1), 3),  # Espacio Abajo del Resto de Filas
        ('TOPPADDING', (0, 0), (-1, -1), 1),  # Espacio Arriba
        ('LEFTPADDING', (0, 0), (-1, -1), 3),  # Espacio a la Izquierda
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),  # Espacio a la Derecha
    ])
    return tabla


def tabla_celda_titulo(tamano=12):
    style = getSampleStyleSheet()["Normal"]
    style.alignment = TA_CENTER
    style.textColor = colors.white
    style.fontSize = tamano
    return style


def tabla_celda_total(tamano=10):
    style = getSampleStyleSheet()["Normal"]
    style.alignment = TA_RIGHT
    style.textColor = colors.white
    style.fontSize = tamano
    return style


def tabla_celda_centrado(tamano=10):
    style = getSampleStyleSheet()["Normal"]
    style.alignment = TA_CENTER
    style.textColor = colors.black
    style.fontSize = tamano
    return style


def tabla_celda_just_derecho(tamano=10):
    style = getSampleStyleSheet()["Normal"]
    style.alignment = TA_RIGHT
    style.textColor = colors.black
    style.fontSize = tamano
    return style


def tabla_celda_just_izquierdo(tamano=10):
    style = getSampleStyleSheet()["Normal"]
    style.alignment = TA_LEFT
    style.textColor = colors.black
    style.fontSize = tamano
    return style
