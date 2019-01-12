#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from reportlab.platypus import Paragraph as Par
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Spacer
from reportlab.platypus import Table

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

from dialogos import dialogo_guardar
from fechas import fecha_hoy
from fechas import mysql_fecha_hora

from listado import cabecera_style
from listado import tabla_celda_centrado
from listado import tabla_celda_just_derecho
from listado import tabla_celda_total

from mensajes import operacion_correcta
from operaciones import cadenanumeros as cad
from operaciones import consultar


def informe_caja_mov_actual(conexion, estab, caja, numero):
    ubicacion_archivo = dialogo_guardar("Movimiento de Caja Actual")

    if ubicacion_archivo is not None:
        # Si no tiene la terminación .pdf se le agrega
        if ubicacion_archivo[-4:].lower() != ".pdf":
            ubicacion_archivo += ".pdf"

        print("Generar Informe de Movimiento de Caja Actual")
        story = []
        cabecera = cabecera_style()
        cel_monto = tabla_celda_just_derecho()
        cel_centro = tabla_celda_centrado()
        cel_total = tabla_celda_total()

        parrafo = Par("Apertura Nº " + numero, cabecera)
        story.append(parrafo)
        parrafo = Par("Establecimiento Nº " + cad(estab, 3), cabecera)
        story.append(parrafo)
        parrafo = Par("Caja Nº " + cad(caja, 3), cabecera)
        story.append(parrafo)
        story.append(Spacer(0, 20))

        # Obtener Datos de la Apertura de Caja

        parrafo = Par("<u>Resumen</u>", cabecera)
        story.append(parrafo)
        story.append(Spacer(0, 20))

        total = total_apertura = total_fact_cont = total_fact_cred = \
        total_nota_cred = total_nota_deb = total_recibo = cheque = tarjeta = 0.0

        # Obtener Monto inicial de la Apertura de esta Caja
        cursor = consultar(conexion, "MontoApertura",
        "cajaaperturas", " WHERE NroApertura = " + numero +
        " AND NroEstablecimiento = " + estab + " AND NroCaja = " + caja)
        total_apertura = cursor.fetchall()[0][0]
        total += total_apertura

        try:
            # Obtener Monto Total y Monto de Cheques y Tarjetas por Facturas Contado de esta Caja
            cursor = consultar(conexion, "IFNULL(SUM(TotalChequeTerceros), 0)," +
            " IFNULL(SUM(TotalTarjetas), 0), IFNULL(SUM(Total), 0)", "facturaventas_s",
            " WHERE NroApertura = " + numero + " AND idTipoFactura = 1" +
            " AND NroEstablecimiento = " + estab + " AND NroCaja = " + caja + " AND Anulado <> 1" +
            " GROUP BY NroApertura, NroEstablecimiento, NroCaja")
        except:
            pass
        else:
            if cursor.rowcount > 0:
                datos = cursor.fetchall()
                cheque += datos[0][0]
                tarjeta += datos[0][1]
                total_fact_cont = datos[0][2]
                total += total_fact_cont

        try:
            # Obtener Monto Total por Facturas Crédito de esta Caja
            cursor = consultar(conexion, "IFNULL(SUM(Total), 0)", "facturaventas_s",
            " WHERE NroApertura = " + numero + " AND idTipoFactura = 2" +
            " AND NroEstablecimiento = " + estab + " AND NroCaja = " + caja + " AND Anulado <> 1" +
            " GROUP BY NroApertura, NroEstablecimiento, NroCaja")
        except:
            pass
        else:
            if cursor.rowcount > 0:
                total_fact_cred = cursor.fetchall()[0][0]
                total += total_fact_cred

        try:
            # Obtener Monto Total de Notas de Crédito de esta Caja
            cursor = consultar(conexion, "IFNULL(SUM(Total), 0)",
            "notacreditoventas_s", " WHERE NroApertura = " + numero +
            " AND NroEstablecimiento = " + estab + " AND NroCaja = " + caja + " AND Anulado <> 1" +
            " GROUP BY NroApertura, NroEstablecimiento, NroCaja")
        except:
            pass
        else:
            if cursor.rowcount > 0:
                total_nota_cred = cursor.fetchall()[0][0]
                total += total_nota_cred

        try:
            # Obtener Monto Total de Notas de Débito de esta Caja
            cursor = consultar(conexion, "IFNULL(SUM(Total), 0)",
            "notadebitoventas_s", " WHERE NroApertura = " + numero +
            " AND NroEstablecimiento = " + estab + " AND NroCaja = " + caja + " AND Anulado <> 1" +
            " GROUP BY NroApertura, NroEstablecimiento, NroCaja")
        except:
            pass
        else:
            if cursor.rowcount > 0:
                total_nota_deb = cursor.fetchall()[0][0]
                total += total_nota_deb

        try:
            # Obtener Monto Total de Recibos de esta Caja
            cursor = consultar(conexion, "IFNULL(SUM(TotalChequeTerceros), 0), " +
            "IFNULL(SUM(TotalTarjetas), 0), IFNULL(SUM(Total), 0)", "recibos_s",
            " WHERE NroApertura = " + numero + " AND NroEstablecimiento = " + estab +
            " AND NroCaja = " + caja + " AND Anulado <> 1" +
            " GROUP BY NroApertura, NroEstablecimiento, NroCaja")
        except:
            pass
        else:
            if cursor.rowcount > 0:
                datos = cursor.fetchall()
                cheque += datos[0][0]
                tarjeta += datos[0][1]
                total_recibo = datos[0][2]
                total += total_recibo

        tabla = Table([
            [Par("<b>Apertura:</b>", cel_monto), Par(str(total_apertura), cel_monto)],
            [Par("<b>Facturas Contado:</b>", cel_monto), Par(str(total_fact_cont), cel_monto)],
            [Par("<b>Facturas Crédito:</b>", cel_monto), Par(str(total_fact_cred), cel_monto)],
            [Par("<b>Notas de Crédito:</b>", cel_monto), Par(str(total_nota_cred), cel_monto)],
            [Par("<b>Notas de Débito:</b>", cel_monto), Par(str(total_nota_deb), cel_monto)],
            [Par("<b>Recibos:</b>", cel_monto), Par(str(total_recibo), cel_monto)],
            [Par("<b>Total:</b>", cel_total), Par(str(total), cel_total)],
            [Par("<b>Cheques:</b>", cel_monto), Par(str(cheque), cel_monto)],
            [Par("<b>Tarjetas:</b>", cel_monto), Par(str(tarjeta), cel_monto)],
            [Par("<b>Total:</b>", cel_total), Par(str(cheque + tarjeta), cel_total)]
        ], [100, 100])
        tabla.setStyle([
            ('BACKGROUND', (0, -4), (-1, -4), colors.black),  # Color de Fondo del Total Documentos
            ('TEXTCOLOR', (0, -4), (-1, -4), colors.white),  # Color del Texto del Total Documentos
            ('BACKGROUND', (0, -1), (-1, -1), colors.black),  # Color de Fondo del Total Cheque y Tarjeta
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),  # Color del Texto del Total Cheque y Tarjeta
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),  # Alineación de la Primera Columna
            ('ALIGN', (1, 1), (-1, -1), 'LEFT'),  # Alineación de Otras Columnas
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alineación Vertical de la Tabla
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),  # Borde Exterior de la Tabla
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),  # Grilla Interior de la Tabla
            ('TOPPADDING', (0, 0), (-1, -1), 1),  # Espacio Arriba
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),  # Espacio Abajo
            ('LEFTPADDING', (0, 0), (-1, -1), 3),  # Espacio a la Izquierda
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),  # Espacio a la Derecha
        ])
        story.append(tabla)
        story.append(Spacer(0, 20))

        # Obtener Datos de las Facturas Contado

        lista_fact_cont = []
        parrafo = Par("<u>Facturas Contado</u>", cabecera)
        story.append(parrafo)
        story.append(Spacer(0, 20))

        try:
            cursor = consultar(conexion, "NroFactura, FechaHora, Total", "facturaventas_s",
            " WHERE NroApertura = " + numero + " AND idTipoFactura = 1" +
            " AND NroEstablecimiento = " + estab + " AND NroCaja = " + caja + " AND Anulado <> 1")
        except:
            pass
        else:
            cant = cursor.rowcount
            if cant > 0:
                datos = cursor.fetchall()
                for i in range(0, cant):
                    lista_fact_cont.append([
                    Par(cad(estab, 3) + "-" + cad(caja, 3) + "-" + cad(datos[i][0], 7), cel_centro),
                    Par(mysql_fecha_hora(datos[i][1]), cel_centro),
                    Par(str(datos[i][2]), cel_monto)])

        lista_fact_cont.append(["", Par("<b>Total:</b>", cel_total),
        Par(str(total_fact_cont), cel_total)])

        tabla = Table(lista_fact_cont, [100, 175, 100])
        tabla.setStyle([
            ('BACKGROUND', (0, -1), (-1, -1), colors.black),  # Color de Fondo del Total
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),  # Color del Texto del Total
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),  # Alineación de la Primera Columna
            ('ALIGN', (1, 1), (-1, -1), 'LEFT'),  # Alineación de Otras Columnas
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alineación Vertical de la Tabla
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),  # Borde Exterior de la Tabla
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),  # Grilla Interior de la Tabla
            ('TOPPADDING', (0, 0), (-1, -1), 1),  # Espacio Arriba
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),  # Espacio Abajo
            ('LEFTPADDING', (0, 0), (-1, -1), 3),  # Espacio a la Izquierda
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),  # Espacio a la Derecha
        ])
        story.append(tabla)
        story.append(Spacer(0, 20))

        # Obtener Datos de las Facturas Crédito

        lista_fact_cred = []
        parrafo = Par("<u>Facturas Crédito</u>", cabecera)
        story.append(parrafo)
        story.append(Spacer(0, 20))

        try:
            cursor = consultar(conexion, "NroFactura, FechaHora, Total", "facturaventas_s",
            " WHERE NroApertura = " + numero + " AND idTipoFactura = 2" +
            " AND NroEstablecimiento = " + estab + " AND NroCaja = " + caja + " AND Anulado <> 1")
        except:
            pass
        else:
            cant = cursor.rowcount
            if cant > 0:
                datos = cursor.fetchall()
                for i in range(0, cant):
                    lista_fact_cred.append([
                    Par(cad(estab, 3) + "-" + cad(caja, 3) + "-" + cad(datos[i][0], 7), cel_centro),
                    Par(mysql_fecha_hora(datos[i][1]), cel_centro),
                    Par(str(datos[i][2]), cel_monto)])

        lista_fact_cred.append(["", Par("<b>Total:</b>", cel_total),
        Par(str(total_fact_cred), cel_total)])

        tabla = Table(lista_fact_cred, [100, 175, 100])
        tabla.setStyle([
            ('BACKGROUND', (0, -1), (-1, -1), colors.black),  # Color de Fondo del Total
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),  # Color del Texto del Total
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),  # Alineación de la Primera Columna
            ('ALIGN', (1, 1), (-1, -1), 'LEFT'),  # Alineación de Otras Columnas
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alineación Vertical de la Tabla
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),  # Borde Exterior de la Tabla
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),  # Grilla Interior de la Tabla
            ('TOPPADDING', (0, 0), (-1, -1), 1),  # Espacio Arriba
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),  # Espacio Abajo
            ('LEFTPADDING', (0, 0), (-1, -1), 3),  # Espacio a la Izquierda
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),  # Espacio a la Derecha
        ])
        story.append(tabla)
        story.append(Spacer(0, 20))

        # Obtener Datos de las Notas de Crédito

        lista_nota_cred = []
        parrafo = Par("<u>Notas de Crédito</u>", cabecera)
        story.append(parrafo)
        story.append(Spacer(0, 20))

        try:
            cursor = consultar(conexion, "NroNotaCredito, FechaHora, Total",
            "notacreditoventas_s", " WHERE NroApertura = " + numero +
            " AND NroEstablecimiento = " + estab + " AND NroCaja = " + caja + " AND Anulado <> 1")
        except:
            pass
        else:
            cant = cursor.rowcount
            if cant > 0:
                datos = cursor.fetchall()
                for i in range(0, cant):
                    lista_nota_cred.append([
                    Par(cad(estab, 3) + "-" + cad(caja, 3) + "-" + cad(datos[i][0], 7), cel_centro),
                    Par(mysql_fecha_hora(datos[i][1]), cel_centro),
                    Par(str(datos[i][2]), cel_monto)])

        lista_nota_cred.append(["", Par("<b>Total:</b>", cel_total),
        Par(str(total_nota_cred), cel_total)])

        tabla = Table(lista_nota_cred, [100, 175, 100])
        tabla.setStyle([
            ('BACKGROUND', (0, -1), (-1, -1), colors.black),  # Color de Fondo del Total
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),  # Color del Texto del Total
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),  # Alineación de la Primera Columna
            ('ALIGN', (1, 1), (-1, -1), 'LEFT'),  # Alineación de Otras Columnas
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alineación Vertical de la Tabla
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),  # Borde Exterior de la Tabla
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),  # Grilla Interior de la Tabla
            ('TOPPADDING', (0, 0), (-1, -1), 1),  # Espacio Arriba
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),  # Espacio Abajo
            ('LEFTPADDING', (0, 0), (-1, -1), 3),  # Espacio a la Izquierda
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),  # Espacio a la Derecha
        ])
        story.append(tabla)
        story.append(Spacer(0, 20))

        # Obtener Datos de las Notas de Débito

        lista_nota_deb = []
        parrafo = Par("<u>Notas de Débito</u>", cabecera)
        story.append(parrafo)
        story.append(Spacer(0, 20))

        try:
            cursor = consultar(conexion, "NroNotaDebito, FechaHora, Total",
            "notadebitoventas_s", " WHERE NroApertura = " + numero +
            " AND NroEstablecimiento = " + estab + " AND NroCaja = " + caja + " AND Anulado <> 1")
        except:
            pass
        else:
            cant = cursor.rowcount
            if cant > 0:
                datos = cursor.fetchall()
                for i in range(0, cant):
                    lista_nota_deb.append([
                    Par(cad(estab, 3) + "-" + cad(caja, 3) + "-" + cad(datos[i][0], 7), cel_centro),
                    Par(mysql_fecha_hora(datos[i][1]), cel_centro),
                    Par(str(datos[i][2]), cel_monto)])

        lista_nota_deb.append(["", Par("<b>Total:</b>", cel_total),
        Par(str(total_nota_deb), cel_total)])

        tabla = Table(lista_nota_deb, [100, 175, 100])
        tabla.setStyle([
            ('BACKGROUND', (0, -1), (-1, -1), colors.black),  # Color de Fondo del Total
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),  # Color del Texto del Total
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),  # Alineación de la Primera Columna
            ('ALIGN', (1, 1), (-1, -1), 'LEFT'),  # Alineación de Otras Columnas
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alineación Vertical de la Tabla
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),  # Borde Exterior de la Tabla
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),  # Grilla Interior de la Tabla
            ('TOPPADDING', (0, 0), (-1, -1), 1),  # Espacio Arriba
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),  # Espacio Abajo
            ('LEFTPADDING', (0, 0), (-1, -1), 3),  # Espacio a la Izquierda
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),  # Espacio a la Derecha
        ])
        story.append(tabla)
        story.append(Spacer(0, 20))

        # Obtener Datos de los Recibos

        lista_recibo = []
        parrafo = Par("<u>Recibos</u>", cabecera)
        story.append(parrafo)
        story.append(Spacer(0, 20))

        try:
            cursor = consultar(conexion, "NroRecibo, FechaHora, Total",
            "recibos_s", " WHERE NroApertura = " + numero +
            " AND NroEstablecimiento = " + estab + " AND NroCaja = " + caja + " AND Anulado <> 1")
        except:
            pass
        else:
            cant = cursor.rowcount
            if cant > 0:
                datos = cursor.fetchall()
                for i in range(0, cant):
                    lista_recibo.append([Par(str(datos[i][0]), cel_centro),
                    Par(mysql_fecha_hora(datos[i][1]), cel_centro),
                    Par(str(datos[i][2]), cel_monto)])

        lista_recibo.append(["", Par("<b>Total:</b>", cel_total),
        Par(str(total_recibo), cel_total)])

        tabla = Table(lista_recibo, [100, 175, 100])
        tabla.setStyle([
            ('BACKGROUND', (0, -1), (-1, -1), colors.black),  # Color de Fondo del Total
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),  # Color del Texto del Total
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),  # Alineación de la Primera Columna
            ('ALIGN', (1, 1), (-1, -1), 'LEFT'),  # Alineación de Otras Columnas
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alineación Vertical de la Tabla
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),  # Borde Exterior de la Tabla
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),  # Grilla Interior de la Tabla
            ('TOPPADDING', (0, 0), (-1, -1), 1),  # Espacio Arriba
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),  # Espacio Abajo
            ('LEFTPADDING', (0, 0), (-1, -1), 3),  # Espacio a la Izquierda
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),  # Espacio a la Derecha
        ])
        story.append(tabla)
        story.append(Spacer(0, 20))

        # Datos del Documento
        doc = SimpleDocTemplate(
            ubicacion_archivo,
            pagesize=A4,  # Tamaño de Página
            leftMargin=3 * cm,  # Margen Izquierdo
            rightMargin=3 * cm,  # Margen Derecho
            topMargin=2.5 * cm,  # Margen Superior
            bottomMargin=2.5 * cm,  # Margen Inferior
            allowSplitting=1,
            title="Movimiento de Caja (" + fecha_hoy() + ")",
            author="Sistema Farmacia"
        )

        doc.build(story)
        operacion_correcta()
