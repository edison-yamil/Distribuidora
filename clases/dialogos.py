#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os.path import expanduser
from gi.repository.Gtk import FileFilter
from gi.repository.Gtk import FileChooserDialog
from gi.repository.Gtk import FileChooserAction
from gi.repository.Gtk import ResponseType
from gi.repository.Gtk import STOCK_SAVE, STOCK_CANCEL


def dialogo_guardar(nombre="listado"):
    vent = FileChooserDialog(title="Guardar como...", action=FileChooserAction.SAVE,
    buttons=(STOCK_SAVE, ResponseType.OK, STOCK_CANCEL, ResponseType.CANCEL))
    vent.set_default_response(ResponseType.OK)
    vent.set_current_folder(expanduser("~"))
    vent.set_current_name(nombre + ".pdf")

    vent.set_position(1)
    vent.set_default_size(600, 400)
    vent.set_modal(True)

    filtro = FileFilter()
    filtro.set_name("PDF")
    filtro.add_pattern("*.pdf")
    vent.add_filter(filtro)

    filtro = FileFilter()
    filtro.set_name("Todos los Archivos")
    filtro.add_pattern("*")
    vent.add_filter(filtro)

    resp = vent.run()
    seleccion = None

    if resp == ResponseType.OK:
        seleccion = vent.get_filename()

    vent.destroy()
    return seleccion
