# -*- coding: utf-8 -*-
"""

Script Name: 
Author: Do Trinh/Jimmy - 3D artist.

Description:


"""
# -------------------------------------------------------------------------------------------------------------

import re, json
from distutils.version import LooseVersion
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import qVersion


def setup_context_menu(graph):
    """
    Sets up the node graphs context menu with some basic menus and commands.
    .. code-block:: python
        :linenos:
        from NodeGraphQt import NodeGraph, setup_context_menu
        graph = NodeGraph()
        setup_context_menu(graph)
    Args:
        graph (NodeGraphQt.NodeGraph): node graph.
    """
    root_menu = graph.get_context_menu('graph')

    file_menu = root_menu.add_menu('&File')
    edit_menu = root_menu.add_menu('&Edit')

    # create "File" menu.
    file_menu.add_command('Open...', _open_session, QKeySequence.Open)
    file_menu.add_command('Save...', _save_session, QKeySequence.Save)
    file_menu.add_command('Save As...', _save_session_as, 'Ctrl+Shift+s')
    file_menu.add_command('Clear', _clear_session)

    file_menu.add_separator()

    file_menu.add_command('Zoom In', _zoom_in, '=')
    file_menu.add_command('Zoom Out', _zoom_out, '-')
    file_menu.add_command('Reset Zoom', _reset_zoom, 'h')

    # create "Edit" menu.
    undo_actn = graph.undo_stack().createUndoAction(graph.viewer(), '&Undo')
    if LooseVersion(qVersion()) >= LooseVersion('5.10'):
        undo_actn.setShortcutVisibleInContextMenu(True)
    undo_actn.setShortcuts(QKeySequence.Undo)
    edit_menu.qmenu.addAction(undo_actn)

    redo_actn = graph.undo_stack().createRedoAction(graph.viewer(), '&Redo')
    if LooseVersion(qVersion()) >= LooseVersion('5.10'):
        redo_actn.setShortcutVisibleInContextMenu(True)
    redo_actn.setShortcuts(QKeySequence.Redo)
    edit_menu.qmenu.addAction(redo_actn)

    edit_menu.add_separator()
    edit_menu.add_command('Clear Undo History', _clear_undo)
    edit_menu.add_separator()

    edit_menu.add_command('Copy', _copy_nodes, QKeySequence.Copy)
    edit_menu.add_command('Paste', _paste_nodes, QKeySequence.Paste)
    edit_menu.add_command('Delete', _delete_nodes, QKeySequence.Delete)

    edit_menu.add_separator()

    edit_menu.add_command('Select all', _select_all_nodes, 'Ctrl+A')
    edit_menu.add_command('Deselect all', _clear_node_selection, 'Ctrl+Shift+A')
    edit_menu.add_command('Enable/Disable', _disable_nodes, 'd')

    edit_menu.add_command('Duplicate', _duplicate_nodes, 'Alt+c')
    edit_menu.add_command('Center Selection', _fit_to_selection, 'f')

    edit_menu.add_separator()


def _copy_nodes(graph):
    graph.copy_nodes()


def _paste_nodes(graph):
    graph.paste_nodes()


def _delete_nodes(graph):
    graph.delete_nodes(graph.selected_nodes())


def _select_all_nodes(graph):
    graph.select_all()


def _clear_node_selection(graph):
    graph.clear_selection()


def _disable_nodes(graph):
    graph.disable_nodes(graph.selected_nodes())


def _duplicate_nodes(graph):
    graph.duplicate_nodes(graph.selected_nodes())


def _fit_to_selection(graph):
    graph.fit_to_selection()


def _zoom_in(graph):
    """
    Set the node graph to zoom in by 0.1
    Args:
        graph (NodeGraphQt.NodeGraph): node graph.
    """
    zoom = graph.get_zoom() + 0.1
    graph.set_zoom(zoom)


def _zoom_out(graph):
    """
    Set the node graph to zoom in by 0.1
    Args:
        graph (NodeGraphQt.NodeGraph): node graph.
    """
    zoom = graph.get_zoom() - 0.2
    graph.set_zoom(zoom)


def _reset_zoom(graph):
    graph.reset_zoom()


def _open_session(graph):
    """
    Prompts a file open dialog to load a session.
    Args:
        graph (NodeGraphQt.NodeGraph): node graph.
    """
    current = graph.current_session()
    viewer = graph.viewer()
    file_path = viewer.load_dialog(current)
    if file_path:
        graph.load_session(file_path)


def _save_session(graph):
    """
    Prompts a file save dialog to serialize a session if required.
    Args:
        graph (NodeGraphQt.NodeGraph): node graph.
    """
    current = graph.current_session()
    if current:
        graph.save_session(current)
        msg = 'Session layout saved:\n{}'.format(current)
        viewer = graph.viewer()
        viewer.message_dialog(msg, title='Session Saved')
    else:
        _save_session_as(graph)


def _save_session_as(graph):
    """
    Prompts a file save dialog to serialize a session.
    Args:
        graph (NodeGraphQt.NodeGraph): node graph.
    """
    current = graph.current_session()
    viewer = graph.viewer()
    file_path = viewer.save_dialog(current)
    if file_path:
        graph.save_session(file_path)


def _clear_session(graph):
    """
    Prompts a warning dialog to clear the node graph session.
    Args:
        graph (NodeGraphQt.NodeGraph): node graph.
    """
    viewer = graph.viewer()
    if viewer.question_dialog('Clear Current Session?', 'Clear Session'):
        graph.clear_session()


def _clear_undo(graph):
    """
    Prompts a warning dialog to clear undo.
    Args:
        graph (NodeGraphQt.NodeGraph): node graph.
    """
    viewer = graph.viewer()
    msg = 'Clear all undo history, Are you sure?'
    if viewer.question_dialog('Clear Undo History', msg):
        graph.undo_stack().clear()


def _loadConfig(filePath):
    with open(filePath, 'r') as myfile:
        fileString = myfile.read()
        cleanString = re.sub('//.*?\n|/\*.*?\*/', '', fileString, re.S)
        data = json.loads(cleanString)
    return data


def _saveData(filePath, data):
    f = open(filePath, "w")
    f.write(json.dumps(data,
                       sort_keys = True,
                       indent = 4,
                       ensure_ascii=False))
    f.close()
    print("Data successfully saved !")

def _loadData(filePath):
    with open(filePath) as json_file:
        j_data = json.load(json_file)
    json_file.close()
    print("Data successfully loaded !")
    return j_data

def _swapListIndices(inputList, oldIndex, newIndex):
    if oldIndex == -1:
        oldIndex = len(inputList)-1
    if newIndex == -1:
        newIndex = len(inputList)
    value = inputList[oldIndex]
    inputList.pop(oldIndex)
    inputList.insert(newIndex, value)


# -------------------------------------------------------------------------------------------------------------
# Created by Trinh Do on 5/6/2020 - 3:13 AM
# © 2017 - 2020 DAMGteam. All rights reserved