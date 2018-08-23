#!/usr/bin/env python
from PySide2 import QtCore, QtGui
from functools import partial
import os

os.environ['SCENEGRAPH'] = os.path.join(os.path.dirname(os.path.realpath(__file__)))

import re
import pyside2uic
import xml.etree.ElementTree as xml
from io import StringIO

import json

import options
import core
import util

from ui import settings
from ui import models
from ui import attributes
from ui import graphics

log = core.log
SCENEGRAPH_UI = options.SCENEGRAPH_UI


def loadUiType(uiFile):
    """
    Pyside lacks the "loadUiType" command, so we have to convert the ui file to py code in-memory first
    and then execute it in a special frame to retrieve the form_class.
    """
    parsed = xml.parse(uiFile)
    widget_class = parsed.find('widget').get('class')
    form_class = parsed.find('class').text

    with open(uiFile, 'r') as f:
        o = StringIO()
        frame = {}

        pyside2uic.compileUi(f, o, indent=0)
        pyc = compile(o.getvalue(), '<string>', 'exec')
        try:
            exec(pyc)
        except ImportError as err:
            log.warning('loadUi: %s' % err)              

        #Fetch the base_class and form class based on their type in the xml from designer
        frame['Ui_%s'%form_class] = form_class
        base_class = eval('QtWidgets.%s'%widget_class)

    return form_class, base_class


#If you put the .ui file for this example elsewhere, just change this path.
form_class, base_class = loadUiType(SCENEGRAPH_UI)

class SceneGraphUI(form_class, base_class):
    def __init__(self, parent=None, **kwargs):
        super(SceneGraphUI, self).__init__(parent)
        from icn import icons

        self.setupUi(self)        
        self.setDockNestingEnabled(True)
        #self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.icons                = icons.ICONS
        self.fonts                = dict()  
        self.view                 = None                                    # GraphicsView
        self.pmanager             = None                                    # Plugin manager UI
        self.attr_manager         = None                                    # Attribute manager dialog  
        self.graph_attrs          = None

        # font prefs
        self.font_family_ui       = None
        self.font_family_mono     = None
        self.font_family_nodes    = None
        self.font_size_ui         = None
        self.font_size_mono       = None

        # stylesheet
        self.stylesheet_name      = None
        self.palette_style        = None
        self.font_style           = None  

        # preferences
        self.debug                = kwargs.get('debug', False)
        self.use_gl               = kwargs.get('use_gl', False)
        self.use_stylesheet       = kwargs.get('use_stylesheet', True)
        self.stylesheet           = None                                    # stylesheet manager
        self.ignore_scene_prefs   = False

        self._show_private        = False
        self._valid_plugins       = []  

        self.edge_type            = kwargs.get('edge_type', 'bezier')
        self.viewport_mode        = kwargs.get('viewport_mode', 'smart')
        self.render_fx            = kwargs.get('render_fx', True)
        self.antialiasing         = 2
        self.environment          = kwargs.get('env', 'standalone')

        # setup default user path
        self._work_path           = kwargs.get('start', options.SCENEGRAPH_USER_WORK_PATH)
        self.status_timer         = QtCore.QTimer()
        self.autosave_inc         = 30000 
        self.autosave_timer       = QtCore.QTimer()

        # stash temp selections here
        self._selected_nodes      = []

        # undo stack
        self.undo_stack           = QtGui.QUndoStack(self)

        # preferences
        self.settings_file        = os.path.join(options.SCENEGRAPH_PREFS_PATH, 'SceneGraph.ini')
        self.qsettings            = settings.Settings(self.settings_file, QtCore.QSettings.IniFormat, parent=self)

        self.qsettings.setFallbacksEnabled(False)

        # icon
        self.setWindowIcon(QtGui.QIcon(os.path.join(options.SCENEGRAPH_ICON_PATH, 'graph_icon.png')))

        # item views/models
        self.tableView = models.TableView(self.sceneWidgetContents)
        self.sceneScrollAreaLayout.addWidget(self.tableView)
        self.tableModel = models.GraphTableModel(headers=['Node Type', 'Node'])
        self.tableView.setModel(self.tableModel)
        self.tableSelectionModel = self.tableView.selectionModel()

        # nodes list model
        self.nodesModel = models.NodesListModel()
        self.nodeStatsList.setModel(self.nodesModel)
        self.nodeListSelModel = self.nodeStatsList.selectionModel()

        # edges list 
        self.edgesModel = models.EdgesListModel()
        self.edgeStatsList.setModel(self.edgesModel)
        self.edgeListSelModel = self.edgeStatsList.selectionModel()

        # setup
        self.initializeWorkPath(self._work_path)

        # read settings first, so that user prefs will override defaults
        self.readSettings(**kwargs)

        self.initializeStylesheet()        
        self.initializeUI()           
        self.connectSignals()       

        self.resetStatus()

    #- Attributes ----
    @property
    def handler(self):
        """
        Return the current SceneEventHandler.

         .. todo::: probably should take this out, useful for debugging mostly.

        :returns: SceneEventHandler instance.
        :rtype: SceneEventHandler
        """
        return self.view.scene().handler

    def eventFilter(self, obj, event):
        """
        Install an event filter to filter key presses away from the parent.
        """        
        if event.type() == QtCore.QEvent.KeyPress:
            #if event.key() == QtCore.Qt.Key_Delete:
            if self.hasFocus():
                return True
            return False
        else:
            return super(SceneGraphUI, self).eventFilter(obj, event)

    def initializeWorkPath(self, path=None):
        """
        Setup the user work directory.

        :param str path: user work path.
        """
        if not path:
            path = options.SCENEGRAPH_USER_WORK_PATH
        if os.path.exists(path):
            os.chdir(path)
            return path
        else:
            if os.makedirs(path):
                os.chdir(path)
                return path
        return

    def initializeUI(self):
        """
        Set up the main UI
        """
        # build the graph
        self.initializeGraphicsView()
        self.initializePreferencesPane()
        
        self.initializeRecentFilesMenu()
        self.buildWindowTitle()
        self.resetStatus()

        # Qt application style menu
        self.app_style_label.setHidden(True)
        self.app_style_menu.setHidden(True)

        # setup undo/redo
        undo_action = self.view.scene().undo_stack.createUndoAction(self, "&Undo")
        undo_action.setShortcuts(QtGui.QKeySequence.Undo)
        
        redo_action = self.view.scene().undo_stack.createRedoAction(self, "&Redo")
        redo_action.setShortcuts(QtGui.QKeySequence.Redo)

        self.menu_edit.addAction(undo_action)
        self.menu_edit.addAction(redo_action)

        # validators for console widget
        self.scene_posx.setValidator(QtGui.QDoubleValidator(-5000, 10000, 2, self.scene_posx))
        self.scene_posy.setValidator(QtGui.QDoubleValidator(-5000, 10000, 2, self.scene_posy))
        self.view_posx.setValidator(QtGui.QDoubleValidator(-5000, 10000, 2, self.view_posx))
        self.view_posy.setValidator(QtGui.QDoubleValidator(-5000, 10000, 2, self.view_posy))

        self.autosave_time_edit.setValidator(QtGui.QDoubleValidator(0, 1000, 2, self.autosave_time_edit))
        self.consoleTextEdit.textChanged.connect(self.outputTextChangedAction)
        self.toggleDebug()

    def initializeStylesheet(self, paths=[], style='default', **kwargs):
        """
        Setup the stylehsheet.
        """
        overrides = dict(
            font_family_ui = kwargs.get('font_family_ui', self.font_family_ui),
            font_family_mono = kwargs.get('font_family_mono', self.font_family_mono),
            font_size_ui = kwargs.get('font_size_ui', self.font_size_ui),
            font_size_mono = kwargs.get('font_size_mono', self.font_size_mono),
            stylesheet_name = kwargs.get('stylesheet_name', self.stylesheet_name),
            palette_style = kwargs.get('palette_style', self.palette_style),
            font_style = kwargs.get('font_style', self.font_style)
            )

        self.stylesheet.run(paths=paths) 
        style_data = self.stylesheet.style_data(style=style, **overrides)

        if self.use_stylesheet:
            self.setStyleSheet(style_data)
            attr_editor = self.getAttributeEditorWidget()
            if attr_editor:
                attr_editor.setStyleSheet(style_data)

    def initializeGraphicsView(self, filter=False):
        """
        Initialize the graphics view/scen and graph objects.
        """
        # initialize the Graph
        self.graph = core.Graph()
        self.network = self.graph.network        

        # add our custom GraphicsView object (gview is defined in the ui file)
        self.view = graphics.GraphicsView(self.gview, ui=self, use_gl=self.use_gl, edge_type=self.edge_type)
        self.gviewLayout.addWidget(self.view) 

        self.view.setSceneRect(-5000, -5000, 10000, 10000)
        self.view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.network.graph['environment'] = self.environment

        # disable plugins
        if self._valid_plugins:
            for plugin in self.graph.plug_mgr.node_types():
                if plugin not in self._valid_plugins:
                    log.info('disabling plugin "%s"' % plugin)
                    self.graph.plug_mgr.node_types().get(plugin).update(enabled=False)
        
    def connectSignals(self):
        """
        Setup signals & slots.
        """
        # timers
        self.status_timer.timeout.connect(self.resetStatus)
        self.autosave_timer.timeout.connect(self.autoSaveAction)
        
        self.view.tabPressed.connect(partial(self.createTabMenu, self.view))
        self.view.statusEvent.connect(self.updateConsole)

        # Scene handler
        self.view.selectionChanged.connect(self.nodesSelectedAction)

        # file & ui menu
        self.menu_file.aboutToShow.connect(self.initializeFileMenu)
        self.menu_graph.aboutToShow.connect(self.initializeGraphMenu)
        self.menu_window.aboutToShow.connect(self.initializeWindowMenu)
        self.menu_debug.aboutToShow.connect(self.initializeDebugMenu) 
        self.menu_nodes.aboutToShow.connect(self.initializeNodesMenu)

        self.action_new_graph.triggered.connect(self.resetGraph)
        self.action_read_graph.triggered.connect(self.readGraph)
        self.action_save_graph.triggered.connect(self.saveCurrentGraph) 
        self.action_save_graph_as.triggered.connect(self.saveGraphAs)               
        self.action_revert.triggered.connect(self.revertGraph)
        self.action_show_all.triggered.connect(self.togglePrivate)
        
        self.action_reset_scale.triggered.connect(self.resetScale)
        self.action_restore_default_layout.triggered.connect(self.restoreDefaultSettings)
        self.action_exit.triggered.connect(self.close)
        self.action_save_layout.triggered.connect(self.saveLayoutAction)
        self.action_plugins.triggered.connect(self.pluginManagerAction)

        # debug menu
        self.action_reset_dots.triggered.connect(self.resetDotsAction)
        self.action_evaluate.triggered.connect(self.evaluateScene)
        self.action_plugin_output.triggered.connect(self.evaluatePlugins)
        self.action_update_nodes.triggered.connect(self.graphAttributesAction)
        self.action_style_output.triggered.connect(self.stylesheetOutputAction)

        # preferences
        self.ignore_scene_prefs_check.toggled.connect(self.toggleIgnore)
        self.action_debug_mode.triggered.connect(self.toggleDebug)
        self.edge_type_menu.currentIndexChanged.connect(self.edgeTypeChangedAction)
        self.viewport_mode_menu.currentIndexChanged.connect(self.toggleViewMode)
        self.check_use_gl.toggled.connect(self.toggleOpenGLMode)
        self.logging_level_menu.currentIndexChanged.connect(self.toggleLoggingLevel)
        self.check_render_fx.toggled.connect(self.toggleEffectsRendering)
        self.autosave_time_edit.editingFinished.connect(self.setAutosaveDelay)
        self.app_style_menu.currentIndexChanged.connect(self.applicationStyleChanged)

        self.ui_font_menu.currentIndexChanged.connect(self.stylesheetChangedAction)
        self.mono_font_menu.currentIndexChanged.connect(self.stylesheetChangedAction)
        self.node_font_menu.currentIndexChanged.connect(self.stylesheetChangedAction)
        
        # styles
        self.stylesheet_menu.currentIndexChanged.connect(self.stylesheetChangedAction)
        self.palette_style_menu.currentIndexChanged.connect(self.stylesheetChangedAction)
        self.font_style_menu.currentIndexChanged.connect(self.stylesheetChangedAction)
        
        self.ui_fontsize_spinbox.valueChanged.connect(self.stylesheetChangedAction)
        self.mono_fontsize_spinbox.valueChanged.connect(self.stylesheetChangedAction)
        self.button_reset_fonts.clicked.connect(self.resetFontsAction)

        
        # output tab buttons
        self.tabWidget.currentChanged.connect(self.updateOutput)
        self.tabWidget.currentChanged.connect(self.updateMetadata)
        self.button_refresh.clicked.connect(self.updateOutput)
        self.button_clear.clicked.connect(self.outputTextBrowser.clear)
        self.consoleTabWidget.currentChanged.connect(self.updateStats)

        # table view
        self.tableSelectionModel.selectionChanged.connect(self.tableSelectionChangedAction)
        self.nodeListSelModel.selectionChanged.connect(self.nodesModelChangedAction)
        self.edgeListSelModel.selectionChanged.connect(self.edgesModelChangedAction)

        # undo tab
        self.undo_stack.cleanChanged.connect(self.buildWindowTitle)
        self.button_undo_clean.clicked.connect(self.clearUndoStack)
        self.button_console_clear.clicked.connect(self.consoleTextEdit.clear)

        # status tips
        self.action_new_graph.setStatusTip("Clear the graph")
        self.action_read_graph.setStatusTip("Open a scene")
        self.action_save_graph.setStatusTip("Save current graph")
        self.action_save_graph_as.setStatusTip("Save current graph as")
        self.action_revert.setStatusTip("Revert graph to last saved version")
        self.action_show_all.setStatusTip("Show hidden node attributes")

        #self.statusBar().messageChanged.connect(self.status_timer.start(4000))

    def initializeFileMenu(self):
        """
        Setup the file menu before it is drawn.
        """
        current_scene = self.graph.getScene()
        if not current_scene:
            #self.action_save_graph.setEnabled(False)
            self.action_revert.setEnabled(False)

        # create the recent files menu
        self.initializeRecentFilesMenu()

    def initializeGraphMenu(self):
        """
        Setup the graph menu before it is drawn.
        """
        edge_type = 'bezier'
        if self.view.scene().edge_type == 'bezier':
            edge_type = 'polygon'
        self.action_edge_type.setText('%s lines' % edge_type.title())

        db_label = 'Debug on'
        debug = os.getenv('SCENEGRAPH_DEBUG', False)

        if debug in ['true', '1']:
            debug = True

        if debug in ['false', '0']:
            debug = False

        if debug:
            db_label = 'Debug off'

        show_msg = 'Show all attrbutes'
        if self._show_private:
            show_msg = 'Hide private attrbutes'

        self.action_debug_mode.setText(db_label)
        self.action_show_all.setText(show_msg)

    def initializeWindowMenu(self):
        """
        Set up the Window menu.
        """
        restore_menu = self.menu_restore_layout
        delete_menu = self.menu_delete_layout

        restore_menu.clear()
        delete_menu.clear()
        
        layout_names = self.qsettings.get_layouts()

        for layout in layout_names:
            restore_action = restore_menu.addAction(layout)
            restore_action.triggered.connect(partial(self.qsettings.restoreLayout, layout))

            if layout != 'default':
                delete_action = delete_menu.addAction(layout)
                delete_action.triggered.connect(partial(self.qsettings.deleteLayout, layout))

    def initializeDebugMenu(self):
        """
        Set up the debug menu.
        """
        has_dots = False
        for node in self.view.scene().get_nodes():
            if node.node_class == 'dot':
                has_dots = True

        self.action_reset_dots.setEnabled(has_dots)

    def initializeNodesMenu(self):
        """
        Set up the nodes menu.
        """
        current_pos = QtGui.QCursor().pos()
        color = False
        attribute = False
        scene = self.view.scene()
        nodes = scene.selectedNodes()

        if nodes:
            color = True
            attribute = True

        self.createNodesMenu(self.menu_nodes, pos=current_pos, color=color, attribute=attribute)

    def initializeRecentFilesMenu(self):
        """
        Build a menu of recently opened scenes.
        """
        recent_files = self.qsettings.getRecentFiles()
        self.menu_recent_files.clear()
        self.menu_recent_files.setEnabled(False)
        if recent_files:
            i = 0
            # Recent files menu
            for filename in reversed(recent_files):
                if filename:
                    if i < self.qsettings._max_files:
                        file_action = QtGui.QAction(filename, self.menu_recent_files)
                        file_action.triggered.connect(partial(self.readGraph, filename))
                        self.menu_recent_files.addAction(file_action)
                        i+=1
            self.menu_recent_files.setEnabled(True)

    def initializePreferencesPane(self, **kwargs):
        """
        Setup the preferences area.
        """
        ignore_scene_prefs = kwargs.pop('ignore_scene_prefs', self.ignore_scene_prefs)
        render_fx = kwargs.pop('render_fx', self.render_fx)
        viewport_mode = kwargs.pop('viewport_mode', self.viewport_mode)
        font_family_ui = kwargs.pop('font_family_ui', self.font_family_ui)
        autosave_inc = kwargs.pop('autosave_inc', self.autosave_inc)
        antialiasing = kwargs.pop('antialiasing', self.antialiasing)
        font_size_mono = kwargs.pop('font_size_mono', self.font_size_mono)
        stylesheet_name = kwargs.pop('stylesheet_name', self.stylesheet_name)
        palette_style = kwargs.pop('palette_style', self.palette_style)
        font_style = kwargs.pop('font_style', self.font_style)
        font_size_ui = kwargs.pop('font_size_ui', self.font_size_ui)
        edge_type = kwargs.pop('edge_type', self.edge_type)
        font_family_nodes = kwargs.pop('font_family_nodes', self.font_family_nodes)
        use_gl = kwargs.pop('use_gl', self.use_gl)
        font_family_mono = kwargs.pop('font_family_mono', self.font_family_mono)

        self.ignore_scene_prefs_check.blockSignals(True)
        self.edge_type_menu.blockSignals(True)
        self.edge_type_menu.blockSignals(True)
        self.viewport_mode_menu.blockSignals(True)
        self.check_use_gl.blockSignals(True)
        self.logging_level_menu.blockSignals(True)
        self.check_render_fx.blockSignals(True)
        self.app_style_menu.blockSignals(True)
        self.ui_font_menu.blockSignals(True)
        self.mono_font_menu.blockSignals(True)
        self.node_font_menu.blockSignals(True)
        self.ui_fontsize_spinbox.blockSignals(True)
        self.mono_fontsize_spinbox.blockSignals(True)
        self.stylesheet_menu.blockSignals(True)
        self.palette_style_menu.blockSignals(True)
        self.font_style_menu.blockSignals(True)
        

        # global preferences
        self.ignore_scene_prefs_check.setChecked(ignore_scene_prefs)

        self.edge_type_menu.clear()
        self.viewport_mode_menu.clear()
        self.logging_level_menu.clear()

        # edge type menu
        self.edge_type_menu.addItems(options.EDGE_TYPES)
        self.edge_type_menu.setCurrentIndex(self.edge_type_menu.findText(edge_type))

        # render FX
        self.check_render_fx.setChecked(render_fx)

        # build the viewport menu
        for item in options.VIEWPORT_MODES.items():
            label, mode = item[0], item[1]
            self.viewport_mode_menu.addItem(label, str(mode))
        self.viewport_mode_menu.setCurrentIndex(self.viewport_mode_menu.findText(viewport_mode))

        # OpenGL check
        GL_MODE = use_gl
        if GL_MODE is None:
            GL_MODE = False

        self.check_use_gl.setChecked(GL_MODE)

        # logging level
        log_level_str = [x[0] for x in options.LOGGING_LEVELS.items() if x[1] == log.level][0]

        # add current log levels to the menu
        for item in options.LOGGING_LEVELS.items():
            label, mode = item[0], item[1]
            self.logging_level_menu.addItem(label.lower(), mode)            
        self.logging_level_menu.setCurrentIndex(self.logging_level_menu.findText(log_level_str.lower()))
    
        # undo viewer
        self.undoView = QtGui.QUndoView(self.tab_undo)
        self.undoTabLayout.insertWidget(0,self.undoView)
        self.undoView.setStack(self.undo_stack)
        self.undoView.setCleanIcon(self.icons.get("arrow_curve_180_left"))

        # autosave prefs
        self.autosave_time_edit.setText(str(autosave_inc/1000))

        # application style
        app = QtGui.QApplication.instance()
        current_style = app.style().metaObject().className()
        current_style = current_style.split(':')[0]
        app_styles = [current_style]
        app_styles.extend(QtGui.QStyleFactory.keys())
        app_styles = list(set(app_styles))

        self.app_style_menu.clear()
        self.app_style_menu.addItems(app_styles)
        self.app_style_menu.setCurrentIndex(self.app_style_menu.findText(current_style))

        # font/stylesheet preferences
        self.ui_font_menu.clear()
        self.mono_font_menu.clear()
        self.stylesheet_menu.clear()
        self.palette_style_menu.clear()
        self.font_style_menu.clear()        


        
        # font menus
        self.ui_font_menu.addItems(self.stylesheet.buildUIFontList())
        self.mono_font_menu.addItems(self.stylesheet.buildMonospaceFontList())
        self.node_font_menu.addItems(self.stylesheet.buildNodesFontList())
        self.stylesheet_menu.addItems(self.stylesheet.qss_names)
        self.palette_style_menu.addItems(self.stylesheet.palette_styles)
        self.font_style_menu.addItems(self.stylesheet.font_styles)        


        self.ui_font_menu.setCurrentIndex(self.ui_font_menu.findText(font_family_ui))
        self.mono_font_menu.setCurrentIndex(self.mono_font_menu.findText(font_family_mono))
        self.node_font_menu.setCurrentIndex(self.node_font_menu.findText(font_family_nodes))       
        self.stylesheet_menu.setCurrentIndex(self.stylesheet_menu.findText(stylesheet_name))
        self.palette_style_menu.setCurrentIndex(self.palette_style_menu.findText(palette_style))
        self.font_style_menu.setCurrentIndex(self.font_style_menu.findText(font_style))        

        ui_font_size = float(re.sub('pt$', '', font_size_ui))
        mono_font_size = float(re.sub('pt$', '', font_size_mono))

        self.ui_fontsize_spinbox.setValue(ui_font_size)
        self.mono_fontsize_spinbox.setValue(mono_font_size)

        self.ignore_scene_prefs_check.blockSignals(False)
        self.edge_type_menu.blockSignals(False)
        self.viewport_mode_menu.blockSignals(False)
        self.check_use_gl.blockSignals(False)
        self.logging_level_menu.blockSignals(False)
        self.check_render_fx.blockSignals(False)
        self.app_style_menu.blockSignals(False)
        self.ui_font_menu.blockSignals(False)
        self.mono_font_menu.blockSignals(False)
        self.node_font_menu.blockSignals(False)
        self.ui_fontsize_spinbox.blockSignals(False)
        self.mono_fontsize_spinbox.blockSignals(False)
        self.stylesheet_menu.blockSignals(False)
        self.palette_style_menu.blockSignals(False)
        self.font_style_menu.blockSignals(False)        

    def buildWindowTitle(self):
        """
        Build the window title
        """
        title_str = 'Scene Graph'
        if self.environment not in ['standalone']:
            title_str = 'Scene Graph - %s' % self.environment.title()
        if self.graph.getScene():
            title_str = '%s: %s' % (title_str, self.graph.getScene())

        # add an asterisk if the current stack is dirty (scene is changed)
        if not self.undo_stack.isClean():
            title_str = '%s*' % title_str
            #self.autosave_timer.start(self.autosave_inc)
        self.setWindowTitle(title_str)

    def sizeHint(self):
        return QtCore.QSize(800, 675)

    #- Status & Messaging ------
    
    def updateStatus(self, msg, level='info'):
        """
        Send output to logger/statusbar
        """
        if level == 'info':
            self.statusBar().showMessage(self._getInfoStatus(msg))
            log.info(msg)

        if level == 'error':
            self.statusBar().showMessage(self._getErrorStatus(msg))
            log.error(msg)

        if level == 'warning':
            self.statusBar().showMessage(self._getWarningStatus(msg))
            log.warning(msg)

        self.status_timer.start(4000)

    def resetStatus(self):
        """
        Reset the status bar message.
        """
        self.statusBar().showMessage('[SceneGraph]: ready')

    def _getInfoStatus(self, msg):
        return '[SceneGraph]: INFO: %s' % msg

    def _getErrorStatus(self, val):
        return '[SceneGraph]: ERROR: %s' % msg

    def _getWarningStatus(self, val):
        return '[SceneGraph]: WARNING: %s' % msg

    #- Saving & Loading ------
    
    def saveGraphAs(self, filename=None):
        """
        Save the current graph to a json file. Pass the filename argument to override.

        :param str filename: file path to save.
        """
        import os
        if not filename:
            filename = os.path.join(os.getenv('HOME'), 'my_graph.json')
            if self.graph.getScene():
                filename = self.graph.getScene()

            scenefile, filters = QtGui.QFileDialog.getSaveFileName(self, "Save graph file", 
                                                                filename, 
                                                                "JSON files (*.json)")
            basename, fext = os.path.splitext(scenefile)
            if not fext:
                scenefile = '%s.json' % basename

        self.undo_stack.setClean()
        filename = str(os.path.normpath(scenefile))
        self.updateStatus('saving current graph "%s"' % scenefile)

        self.graph.write(scenefile)
        #self.action_save_graph.setEnabled(True)
        self.action_revert.setEnabled(True)

        # remove autosave files
        autosave_file = '%s~' % scenefile
        if os.path.exists(autosave_file):
            os.remove(autosave_file)

        self.qsettings.addRecentFile(scenefile)
        self.initializeRecentFilesMenu()
        self.buildWindowTitle()

    def saveCurrentGraph(self):
        """
        Save the current graph file.

         .. todo::: 
            - combine this with saveGraphAs
        """
        if not self.graph.getScene():
            filename = self.saveDialog()
            if filename:
                self.graph.setScene(filename)
            else:
                return

        self.undo_stack.setClean()
        filename = self.graph.getScene()
        self.updateStatus('saving current graph "%s"' % filename)
        self.graph.write(filename)
        self.buildWindowTitle()

        self.qsettings.addRecentFile(filename)
        self.initializeRecentFilesMenu()

        # remove autosave files
        autosave_file = '%s~' % filename
        if os.path.exists(autosave_file):
            os.remove(autosave_file)

        return self.graph.getScene()      

    def autoSaveAction(self):
        """
        Save a temp file when the graph changes. Set to auto-fire when the autosave timer
        timeouts.
        """
        if self.undo_stack.isClean():
            self.autosave_timer.start(self.autosave_inc)
            return

        if self.graph.getScene():
            autosave = '%s~' % self.graph.getScene()
        else:
            # use the graph's autosave path
            autosave = self.graph.autosave_path
       
        self.graph.write(autosave, auto=True)
        self.updateStatus('autosaving "%s"...' % autosave)
        #self.undo_stack.setClean()
        return autosave

    def readGraph(self, filename=None):
        """
        Read the current graph from a json file.

        :param str filename: scene file to read.
        """
        if filename is None:
            filename = self.openDialog("Open graph file", path=self._work_path)
            if not filename:
                return

        if not os.path.exists(filename):
            log.error('filename %s does not exist' % filename)
            return

        # stash a string for recent files menu
        recent_file = filename

        # check for autosave file
        filename = self.autoSaveCheck(filename)

        self.resetGraph()
        self.updateStatus('reading graph "%s"' % filename)
        self.graph.read(filename)
        #self.action_save_graph.setEnabled(True)

        self.qsettings.addRecentFile(recent_file)
        log.debug('adding recent file: "%s"' % filename)

        self.buildWindowTitle()
        self.view.scene().clearSelection()
        self.undo_stack.setClean()
        self.autosave_timer.start(self.autosave_inc)
        self.clearUndoStack()

    def autoSaveCheck(self, filename):
        """
        Queries the user to choose to use a newer autosave version
        of the given filename. If the user chooses the autosave file, 
        the autosave is copied over the current filename and removed.
        
        :param str filename: file to check for autosave.

        :returns: file to read.
        :rtype: str
        """
        autosave_file = '%s~' % filename
        if os.path.exists(autosave_file):
            if util.is_newer(autosave_file, filename):
                use_autosave = self.promptDialog("Autosave exists", "Newer file exists: %s, use that?" % autosave_file)

                if use_autosave:
                    try:
                        import shutil
                        shutil.copy(autosave_file, filename)
                    except:
                        pass
            # remove the autosave file.
            os.remove(autosave_file)
        return filename

    def revertGraph(self):
        """
        Revert the current graph file.
        """
        filename=self.graph.getScene()
        if filename:
            self.resetGraph()
            self.readGraph(filename)
            log.info('reverting graph: %s' % filename)
            self.clearUndoStack()

    def resetGraph(self):
        """
        Clear the current graph.
        """
        self.view.scene().initialize()
        self.graph.reset()
        #self.action_save_graph.setEnabled(False)
        self.buildWindowTitle()
        self.updateOutput()
        self.clearUndoStack()

    def resetScale(self):
        self.view.resetMatrix()      

    def clearUndoStack(self):
        """
        Reset the undo stack.
        """
        self.undo_stack.clear()

    def toggleViewMode(self):
        """
        Update the GraphicsView update mode for performance.
        """
        mode = self.viewport_mode_menu.currentText()        
        qmode = self.viewport_mode_menu.itemData(self.viewport_mode_menu.currentIndex())
        self.view.viewport_mode = eval(qmode)
        self.view.scene().update()
        self.viewport_mode = mode

    def toggleOpenGLMode(self, val):
        """
        Toggle OpenGL mode and swap out viewports.
        """
        self.use_gl = val

        widget = self.view.viewport()
        widget.deleteLater()

        if self.use_gl:
            from PySide import QtOpenGL            
            self.view.setViewport(QtOpenGL.QGLWidget(QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers)))
            log.info('initializing OpenGL renderer.')
        else:
            self.view.setViewport(QtGui.QWidget())

        self.initializeStylesheet()
        self.view.scene().update()

    def toggleEffectsRendering(self, val):
        """
        Toggle rendering of node effects.

         .. todo::: this probably belongs in GraphicsView/Scene.
        """
        self.render_fx = val
        log.info('toggling effects %s' % ('on' if val else 'off'))
        for node in self.view.scene().scenenodes.values():
            if hasattr(node, '_render_effects'):
                node._render_effects = self.render_fx 
                node.update()
        self.view.scene().update()

    def toggleLoggingLevel(self):
        """
        Toggle the logging level.
        """
        log.level = self.logging_level_menu.itemData(self.logging_level_menu.currentIndex())
        print('# DEBUG: toggling log level: ', log.level)

    def toggleIgnore(self):
        self.ignore_scene_prefs = self.ignore_scene_prefs_check.isChecked()

    def toggleDebug(self):
        """
        Set the debug environment variable and set widget
        debug values to match.
        """
        debug = os.getenv('SCENEGRAPH_DEBUG', False)

        if debug in ['true', '1']:
            debug = False

        if debug in ['false', '0']:
            debug = True

        nodes = self.view.scene().get_nodes()
        edge_widgets = self.view.scene().get_edges()

        if nodes:
            for widget in nodes:
                widget.setDebug(debug)

        if edge_widgets:
            for ewidget in edge_widgets:
                ewidget._debug = debug

        self.debug = debug
        self.view.scene().update()
        self.view.scene().update()
        os.environ['SCENEGRAPH_DEBUG'] = '1' if debug else '0' 

    def toggleEdgeTypes(self, edge_type):
        """
        Toggle the edge types.

        :params str edge_type:  edge type (bezier or polygon)
        """           
        if edge_type != self.edge_type:
            self.edge_type = edge_type

            for edge in self.view.scene().get_edges():
                edge.edge_type = self.edge_type
            self.view.scene().update()

            menu_text = self.edge_type_menu.currentText()
            if menu_text != edge_type:
                self.edge_type_menu.blockSignals(True)
                self.edge_type_menu.setCurrentIndex(self.edge_type_menu.findText(edge_type))
                self.edge_type_menu.blockSignals(False)

    def togglePrivate(self):
        """
        **Debug
        """
        self._show_private = not self._show_private

        ae = self.getAttributeEditorWidget()
        if ae:
            ae.setNodes(self.view.scene().selectedDagNodes(), clear=True)

    def setAutosaveDelay(self):
        """
        Update the autosave increment time.

        Time is in seconds, so mult X 1000
        """
        astime = int(self.autosave_time_edit.text())
        log.info('updating autosave delay to: %d seconds.' % astime)
        self.autosave_timer.stop()
        self.autosave_inc = astime * 1000
        self.autosave_timer.start(self.autosave_inc)

    #- Actions ----
    
    def edgeTypeChangedAction(self):
        """
        Runs when the current edge type menu is changed.
        """
        edge_type = self.edge_type_menu.currentText()
        self.toggleEdgeTypes(edge_type)

    def applicationStyleChanged(self, index):
        """
        Sets the current application style.
        """
        style_name = self.app_style_menu.currentText()
        app = QtGui.QApplication.instance()
        log.debug('setting application style: "%s"' % str(style_name))
        app.setStyle(style_name)
        self.initializeStylesheet()

    def stylesheetChangedAction(self, index):
        """
        Runs when the user updates a font/stylesheet pref.
        """
        self.font_family_ui = str(self.ui_font_menu.currentText())
        self.font_family_mono = str(self.mono_font_menu.currentText())
        self.font_family_nodes = str(self.node_font_menu.currentText())
        
        ui_fontsize = self.ui_fontsize_spinbox.value()
        mono_fontsize = self.mono_fontsize_spinbox.value()

        ui_fontsize = '%.2fpt' % ui_fontsize
        mono_fontsize = '%.2fpt' % mono_fontsize

        self.font_size_ui = ui_fontsize
        self.font_size_mono = mono_fontsize

        stylesheet_name = self.stylesheet_menu.currentText()
        palette_style = self.palette_style_menu.currentText()
        font_style = self.font_style_menu.currentText()

        self.stylesheet_name = stylesheet_name
        self.palette_style = palette_style
        self.font_style = font_style

        overrides = dict(
            font_family_ui = self.font_family_ui,
            font_family_mono = self.font_family_mono,
            font_size_ui = self.font_size_ui,
            font_size_mono = self.font_size_mono,
            stylesheet_name = stylesheet_name,
            palette_style = palette_style,
            font_style = font_style
            )

        self.initializeStylesheet(**overrides)

        # update scene node fonts
        self.handler.scene.updateNodes(_font=self.font_family_nodes)

    def resetFontsAction(self, platform=None, style='default'):
        """
        Reset fonts to their defaults.
        """
        if platform is None:
            platform = options.PLATFORM

        defaults = self.stylesheet.font_defaults(platform=platform, style=style)
        
        self.font_family_ui = defaults.get("font_family_ui")
        self.font_family_mono = defaults.get("font_family_mono")
        self.font_size_ui = defaults.get("font_size_ui")
        self.font_size_mono = defaults.get("font_size_mono")

        overrides = dict(
            font_family_ui = self.font_family_ui,
            font_family_mono = self.font_family_mono,
            font_size_ui = self.font_size_ui,
            font_size_mono = self.font_size_mono,
            )

        self.initializeStylesheet(**overrides)

        self.ui_font_menu.blockSignals(True)
        self.mono_font_menu.blockSignals(True)
        self.ui_fontsize_spinbox.blockSignals(True)
        self.mono_fontsize_spinbox.blockSignals(True)

        self.ui_font_menu.setCurrentIndex(self.ui_font_menu.findText(self.font_family_ui))
        self.mono_font_menu.setCurrentIndex(self.mono_font_menu.findText(self.font_family_mono))
        
        ui_font_size = float(re.sub('pt$', '', self.font_size_ui))
        mono_font_size = float(re.sub('pt$', '', self.font_size_mono))

        self.ui_fontsize_spinbox.setValue(ui_font_size)
        self.mono_fontsize_spinbox.setValue(mono_font_size)
        self.ui_font_menu.blockSignals(False)
        self.mono_font_menu.blockSignals(False)
        self.ui_fontsize_spinbox.blockSignals(False)
        self.mono_fontsize_spinbox.blockSignals(False)

    def resetDotsAction(self):
        """
        * Debug
        """
        dot_nodes = []
        for node in self.view.scene().get_nodes():
            if node.node_class == 'dot':
                dot_nodes.append(node)

                for conn_name in node.connections:
                    conn_widget = node.connections.get(conn_name)
                    conn_widget.setRotation(0)
                    conn_widget.setTransformOriginPoint(conn_widget.mapFromParent(QtCore.QPointF(0,0)))

    def nodesSelectedAction(self):
        """
        Action that runs whenever a node is selected in the UI
        """
        from SceneGraph import ui
        # get a list of selected node widgets
        selected_nodes = self.view.scene().selectedNodes(nodes_only=True)

        # clear the list view
        self.tableModel.clear()
        self.tableView.reset()
        self.tableView.setHidden(True)

        if selected_nodes:
            node = selected_nodes[0]

            node_selection_changed = False

            for n in selected_nodes:
                # edges: 65538, nodes: 65537

                if n not in self._selected_nodes:
                    node_selection_changed = True

            if node_selection_changed:
                self._selected_nodes = selected_nodes
                dagnodes = [x.dagnode for x in selected_nodes]
                self.updateAttributeEditor(dagnodes)

                # populate the graph widget with downstream nodes
                UUID = node.dagnode.id
                if UUID:
                    ds_ids = self.graph.downstream(node.dagnode.name)
                    dagnodes = []
                    for nid in ds_ids:
                        dnodes = self.graph.get_node(nid)
                        if dnodes:
                            dagnodes.append(dnodes[0])

                    dagnodes = [x for x in reversed(dagnodes)]
                    self.tableModel.addNodes(dagnodes)
                    self.tableView.setHidden(False)
                    self.tableView.resizeRowToContents(0)
                    self.tableView.resizeRowToContents(1)

                self.updateMetadata()

        else:
            self._selected_nodes = []
            self.removeAttributeEditorWidget()

    def getAttributeEditorWidget(self):
        """
        Returns the AttributeEditor widget (if it exists).

        returns:
            (QWidget) - AttributeEditor instance.
        """
        return self.attrEditorWidget.findChild(QtGui.QWidget, 'AttributeEditor')

    def removeAttributeEditorWidget(self):
        """
        Remove a widget from the detailGroup box.
        """
        for i in reversed(range(self.attributeScrollAreaLayout.count())):
            widget = self.attributeScrollAreaLayout.takeAt(i).widget()
            if widget is not None:
                widget.deleteLater()

    def updateAttributeEditor(self, dagnodes, **attrs):
        """
        Update the attribute editor with a selected node.

        params:
            dagnodes (list) - list of dag node objects.
        """
        if type(dagnodes) not in [list, tuple]:
            dagnodes = [dagnodes,]

        attr_widget = self.getAttributeEditorWidget()
                
        if not attr_widget:
            attr_widget = attributes.AttributeEditor(self.attrEditorWidget, handler=self.view.scene().handler, ui=self)
            self.attributeScrollAreaLayout.addWidget(attr_widget)
        attr_widget.setNodes(dagnodes)

    def tableSelectionChangedAction(self):
        """
        Update the attribute editor when a node is selected in the dependencies list.
        """
        if self.tableSelectionModel.selectedRows():
            idx = self.tableSelectionModel.selectedRows()[0]
            dagnode = self.tableModel.nodes[idx.row()]
            self.updateAttributeEditor(dagnode)

            # can't do this, else model updates
            #self.view.scene().clearSelection()
            #node = self.view.scene().getNode(dagnode.name)
            #node.setSelected(True)

    def nodesModelChangedAction(self):
        """
        Runs when the widget in the nodes listView changes.
        """
        self.view.scene().clearSelection()
        if self.nodeListSelModel.selectedRows():
            idx = self.nodeListSelModel.selectedRows()[0]
            node = self.nodesModel.nodes[idx.row()]
            node.setSelected(True)
            self.updateAttributeEditor(node.dagnode)

    def edgesModelChangedAction(self):
        """
        Runs when the widget in the edges listView changes.
        """
        self.view.scene().clearSelection()
        if self.edgeListSelModel.selectedRows():
            idx = self.edgeListSelModel.selectedRows()[0]

            edge = self.edgesModel.edges[idx.row()]
            edge.setSelected(True)

    def nodeAddedAction(self, node):
        """
        Action whenever a node is added to the graph.

        .. todo::
            - deprecated?
        """
        self.updateOutput()

    def nodesChangedAction(self, dagnodes):
        """
        Runs whenever nodes are changed in the UI.

        params:
            nodes (list) - list of Node widgets.
        """
        attr_widget = self.getAttributeEditorWidget()

        # update the AttributeEditor
        if attr_widget:
            attr_widget.updateChildEditors()

    # TODO: disabling this, causing lag
    def sceneChangedAction(self, event):
        pass
    
    def createCreateMenuActions(self):
        pass

    def outputTextChangedAction(self):
        current_text = self.outputTextBrowser.toPlainText()
        valid = False
        try:
            json_data = json.loads(current_text, indent=5)
            valid=True
        except:
            pass

        if valid:
            print('text is valid!')
        #self.outputTextBrowser.clear()   

    #- Events ----
    def closeEvent(self, event):
        """
        Write window prefs when UI is closed
        """
        self.writeSettings()

        save_action = False
        if not self.undo_stack.isClean():            
            save_action = self.promptDialog("Scene Modified", "Scene has been modified, save?")

            if save_action:
                filename = self.graph.getScene()
                if not filename:
                    filename = self.saveDialog()

                if filename:
                    self.graph.write(filename)

        QtGui.QApplication.instance().removeEventFilter(self)
        return super(SceneGraphUI, self).closeEvent(event)

    #- Menus -----
    def createNodesMenu(self, parent, pos, add=True, color=True, attribute=True):
        """
        Build a context menu at the current pointer pos.

        :param QtGui.QWidget parent: parent ui (window, GraphicsView, etc.)
        :param QtCore.QPointF pos: position to build the menu.

        :param bool add: build the **add node** sub-menu.
        :param bool color: build the **node color** sub-menu.
        :param bool attribute: build the **node attribute** sub-menu.
        """
        parent.clear()
        qcurs = QtGui.QCursor()

        menu_add_node   = QtGui.QMenu('Add node:   ', parent)
        menu_node_color = QtGui.QMenu('Node color: ', parent)
        menu_node_attributes = QtGui.QMenu('Attributes: ', parent)

        # build the add node menu
        if add:
            for node in self.graph.node_types():
                node_action = menu_add_node.addAction(node)
                # add the node at the scene pos
                node_action.triggered.connect(partial(self.graph.add_node, node_type=node, pos=[pos.x(), pos.y()]))

        # build the color menu
        if color:
            for color_name in options.SCENEGRAPH_COLORS:
                color_val = options.SCENEGRAPH_COLORS.get(color_name)
                color = QtGui.QColor(*color_val)
                pixmap = QtGui.QPixmap(24, 24)
                pixmap.fill(color)

                icon = QtGui.QIcon(pixmap)
                color_action = menu_node_color.addAction(icon, color_name)
                color_action.setIconVisibleInMenu(True)
                color_action.triggered.connect(partial(self.view.scene().colorChangedAction, color=color_val))

        if attribute:
            for action_name in ['add', 'remove']:
                attr_action = menu_node_attributes.addAction('{0} attribute...'.format(action_name))
                attr_action.triggered.connect(partial(self.attributeManagerAction, action=action_name))

        # add the add node menu
        if add:
            parent.addMenu(menu_add_node)

        # if a node is selected, add the color menu.
        if color:
            parent.addMenu(menu_node_color)

        if attribute:
            parent.addMenu(menu_node_attributes)

        # parent isn't getting stylesheet
        parent.setStyleSheet(self.styleSheet())

    def createTabMenu(self, parent):
        """
        Build a context menu at the current pointer pos.

        :param  QtGui.QWidget parent: parent widget.
        """
        tab_menu = QtGui.QMenu(parent)
        tab_menu.clear()
        add_menu = QtGui.QMenu('Add node:')

        style_data = self.styleSheet()

        # apply the stylesheet
        add_menu.setStyleSheet(style_data)
        tab_menu.setStyleSheet(style_data)

        tab_menu.addMenu(add_menu)
        
        qcurs = QtGui.QCursor()
        view_pos =  self.view.current_cursor_pos
        scene_pos = self.view.mapToScene(view_pos)

        for node in self.graph.node_types():
            node_action = QtGui.QAction(node, parent)
            add_menu.addAction(node_action)
            # add the node at the scene pos
            node_action.triggered.connect(partial(self.graph.add_node, node_type=node, pos=(scene_pos.x(), scene_pos.y())))

        tab_menu.exec_(qcurs.pos())

    def spinAction(self):
        self.status_timer.timeout.connect(self.rotateView)
        self.status_timer.start(90)

    def rotateView(self):
        self.view.rotate(4)

    #- Settings -----
    def readSettings(self, **kwargs):
        """
        Read user settings from preferences. Any arguments passed in kwargs are ignored,
        as the have been passed to the UI.
        """
        self.qsettings.beginGroup("MainWindow")
        self.restoreGeometry(self.qsettings.value("geometry"))
        self.restoreState(self.qsettings.value("windowState"))
        if self.qsettings.group():
            self.qsettings.endGroup()
        self.qsettings.beginGroup("Preferences")

        # viewport mode (ie smart, full, minimal) (global?)
        if 'ignore_scene_prefs' not in kwargs:
            ignore_scene_prefs = self.qsettings.value("ignore_scene_prefs")
            self.ignore_scene_prefs = False
            if ignore_scene_prefs is not None:
                self.ignore_scene_prefs = bool(int(ignore_scene_prefs))


        # viewport mode (ie smart, full, minimal) (global?)
        if 'viewport_mode' not in kwargs:
            viewport_mode = self.qsettings.value("viewport_mode")
            if viewport_mode is not None:
                self.viewport_mode = viewport_mode

        # render fx (scene?)
        if not 'render_fx' in kwargs:
            render_fx = self.qsettings.value("render_fx")
            self.render_fx = False
            if render_fx is not None:
                self.render_fx = bool(int(render_fx))

        # edge type (scene)
        if not 'edge_type' in kwargs:
            edge_type = self.qsettings.value("edge_type")
            if edge_type is not None:
                self.edge_type = edge_type

        # OpenGL mode (global)
        if not 'use_gl' in kwargs:
            use_gl = self.qsettings.value("use_gl")
            self.use_gl = False
            if use_gl is not None:
                self.use_gl = bool(int(use_gl))

        #logging level (global)
        logging_level = self.qsettings.value("logging_level")
        if logging_level is None:
            logging_level = options.SCENEGRAPH_PREFERENCES.get('logging_level').get('default')

        #autosave delay (global)
        autosave_inc = self.qsettings.value("autosave_inc")
        if autosave_inc is None:
            autosave_inc = options.SCENEGRAPH_PREFERENCES.get('autosave_inc').get('default')

        # update valid plugin types
        plugins = self.qsettings.value("plugins")
        if plugins:
            if type(plugins) in [str, unicode]:
                plugins = [plugins,]
            for plugin in plugins:
                if plugin not in self._valid_plugins:
                    self._valid_plugins.append(plugin)

        # font/stylesheet preferences
        for attr in ['font_family_ui', 'font_family_mono', 'font_family_nodes', 'font_size_ui', 'font_size_mono', 'stylesheet_name', 'palette_style', 'font_style']:
            if attr not in kwargs:
                value = self.qsettings.value(attr)
                if value is None:
                    default = self.qsettings.getDefaultValue(attr, 'Preferences')
                    if default is not None:
                        value = default

                if value is not None:
                    setattr(self, attr, value)

        self.qsettings.endGroup()
        # set globals prefs
        self.autosave_inc = int(autosave_inc)
        log.level = int(logging_level)

        # read the dock settings
        for w in self.findChildren(QtGui.QDockWidget):
            dock_name = w.objectName()
            self.qsettings.beginGroup(dock_name)
            if "geometry" in self.qsettings.childKeys():
                w.restoreGeometry(self.qsettings.value("geometry"))
            self.qsettings.endGroup()

    def writeSettings(self):
        """
        Write Qt settings to file
        """
        self.qsettings.beginGroup('MainWindow')
        width = self.width()
        height = self.height()
        self.qsettings.setValue("geometry", self.saveGeometry())
        self.qsettings.setValue("windowState", self.saveState())
        self.qsettings.endGroup()
        # general preferences
        self.qsettings.beginGroup('Preferences')

        for attr in options.SCENEGRAPH_PREFERENCES:
            if attr == 'logging_level':
                value = log.level

            else:
                if not hasattr(self, attr):
                    log.debug('SceneGraphUI has no attribute "%s", skipping...' % attr)
                    continue
                value = getattr(self, attr)

                if type(value) is bool:
                    value = int(value)

            self.qsettings.setValue(attr, value)

        # font/stylesheet preferences
        for fattr in ['font_family_ui', 'font_family_mono', 'font_family_nodes', 'font_size_ui', 'font_size_mono', 'stylesheet_name']:
            if not hasattr(self, fattr):
                continue
            self.qsettings.setValue(fattr, getattr(self, fattr))

        self.qsettings.setValue('plugins', self.graph.plug_mgr.valid_plugins)

        self.qsettings.endGroup()
        # write the dock settings
        for w in self.findChildren(QtGui.QDockWidget):
            dock_name = w.objectName()
            no_default = False

            # this is the first launch
            if dock_name not in self.qsettings.childGroups():
                no_default = True

            self.qsettings.beginGroup(dock_name)
            # save defaults
            if no_default:
                self.qsettings.setValue("geometry/default", w.saveGeometry())
            self.qsettings.setValue("geometry", w.saveGeometry())
            self.qsettings.endGroup()

    def restoreDefaultSettings(self):
        """
        Attempts to restore docks and window to factory fresh state.
        """
        pos = self.pos()
        # read the mainwindow defaults
        main_geo_key = 'MainWindow/geometry/default'
        main_state_key = 'MainWindow/windowState/default'
        
        self.restoreGeometry(self.qsettings.value(main_geo_key))
        self.restoreState(self.qsettings.value(main_state_key))
        
        for w in self.findChildren(QtGui.QDockWidget):
            dock_name = w.objectName()

            defaults_key = '%s/geometry/default' % dock_name
            if defaults_key in self.qsettings.allKeys():
                w.restoreGeometry(self.qsettings.value(defaults_key))
        self.move(pos)

    def getCurrentLayouts(self):
        window_keys = self.qsettings.window_keys()

    def saveLayoutAction(self):
        """
        Prompts the user to save a named layout.
        """
        layout_name = self.inputDialog('Save current layout', 'Layout Name:')
        if not layout_name:
            return 

        layout_name = util.clean_name(layout_name)
        self.qsettings.saveLayout(layout_name)

    def pluginManagerAction(self):
        """
        Launches the PluginManager.
        """
        try:
            self.pmanager.close()
        except:
            from SceneGraph.ui import PluginManager
            reload(PluginManager)
            self.pmanager = PluginManager.PluginManager(self)
            self.pmanager.show()

    def attributeManagerAction(self, action):
        """
        Launches the Attribute Manager.
        """
        try:
            self.attr_manager.close()
        except:
            from SceneGraph.ui import AttributeManager
            reload(AttributeManager)
            self.attr_manager = AttributeManager.AttributeManager(self)
            self.attr_manager.show()

    def graphAttributesAction(self):
        """
        Launches the Graph Attributes dialog.
        """
        try:
            self.graph_attrs.close()
        except:
            from SceneGraph.ui import GraphAttributes
            reload(GraphAttributes)
            self.graph_attrs = GraphAttributes.GraphAttributes(self)
            self.graph_attrs.show()

    def updateOutput(self):
        """
        Update the output text edit.
        """
        # store the current position in the text box
        bar = self.outputTextBrowser.verticalScrollBar()
        posy = bar.value()

        self.outputTextBrowser.clear()        

        # update graph attributes
        self.graph.updateGraphAttributes()
        graph_data = self.graph.snapshot()
        html_data = self.formatOutputHtml(graph_data, highlight=['name'])
        self.outputTextBrowser.setHtml(html_data)

        self.outputTextBrowser.scrollContentsBy(0, posy)
        #self.outputTextBrowser.setReadOnly(True)

    def updateMetadata(self):
        """
        Update the metadata text edit.
        """        
        bar = self.metdataBrowser.verticalScrollBar()
        posy = bar.value()

        self.metdataBrowser.clear()        

        # update graph attributes
        nodes = self.view.scene().selectedNodes()
        if not nodes:
            return

        if len(nodes) > 1:
            return

        node = nodes[0]
        if not hasattr(node, 'dagnode'):
            return
        metadata = node.dagnode.metadata.data   # was node.dagnode.metadata.data
        html_data = self.formatOutputHtml(metadata)
        self.metdataBrowser.setHtml(html_data)

        self.metdataBrowser.scrollContentsBy(0, posy)
        #self.outputTextBrowser.setReadOnly(True)

    def formatOutputHtml(self, data, highlight=[]):
        """
        Fast and dirty html formatting.

        :param str data: data string.
        :param list highlight: list of words to highlight.

        :returns: formatted html data.
        :rtype: str
        """
        import simplejson as json
        html_result = ""
        rawdata = json.dumps(data, indent=5)
        for line in rawdata.split('\n'):
            if line:
                ind = "&nbsp;"*line.count(" ")
                fline = "<br>%s%s</br>" % (ind, line)
                for hname in highlight:
                    if '"%s":' % hname in line:
                        fline = '<br><b><font color="#628fab">%s%s</font></b></br>' % (ind, line)
                html_result += fline
        return html_result

    def updateConsole(self, status):
        """
        Update the console data.

        :param dict status: data from GraphicsView mouseMoveEvent
        """        
        self.sceneRectLineEdit.clear()
        self.viewRectLineEdit.clear()
        self.zoomLevelLineEdit.clear()

        if status.get('view_cursor'):
            vx, vy = status.get('view_cursor', (0.0,0.0))
            self.view_posx.clear()
            self.view_posy.clear()
            self.view_posx.setText('%.2f' % vx)
            self.view_posy.setText('%.2f' % vy)

        if status.get('scene_cursor'):
            sx, sy = status.get('scene_cursor', (0.0,0.0))
            self.scene_posx.clear()
            self.scene_posy.clear()
            self.scene_posx.setText('%.2f' % sx)
            self.scene_posy.setText('%.2f' % sy)

        scene_str = '%s, %s' % (status.get('scene_size')[0], status.get('scene_size')[1])
        self.sceneRectLineEdit.setText(scene_str)

        view_str = '%s, %s' % (status.get('view_size')[0], status.get('view_size')[1])
        self.viewRectLineEdit.setText(view_str)

        zoom_str = '%.3f' % status.get('zoom_level')[0]
        self.zoomLevelLineEdit.setText(zoom_str)

    def updateStats(self):
        """
        Update the console stats lists.
        """
        self.nodesModel.clear()
        self.edgesModel.clear()

        nodes = self.view.scene().get_nodes()
        edges = self.view.scene().get_edges()

        self.nodesModel.addNodes(nodes)
        self.edgesModel.addEdges(edges)

    def evaluateScene(self):
        """
        Evaluate the current scene.
        """
        self.view.scene().evaluate()

    def evaluatePlugins(self):
        """
        Evaluate currently loaded plugins.
        """
        self.graph.plugins

    def stylesheetOutputAction(self):
        """
        Debug method. 
        """
        pass

    #- Dialogs -----
    def promptDialog(self, label, msg):
        """
        Simple Qt prompt dialog.
        """
        result = QtGui.QMessageBox.question(self, label, msg, QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
        if (result == QtGui.QMessageBox.Yes):
            return True
        return False

    def saveDialog(self, force=True):
        """
        Simple Qt file dialog.

        :param bool force: force file extension.

        :returns: save file name.
        :rtype: str
        """
        filename, filters = QtGui.QFileDialog.getSaveFileName(self, caption='Save Current Scene', directory=os.getcwd(), filter="json files (*.json)")
        if not filename:
            return
        bn, fext = os.path.splitext(filename)
        if not fext and force:
            filename = '%s.json' % bn
        return filename

    def openDialog(self, msg, path=None):
        """
        Opens a file input dialog. Arguments are message (dialog title) and
        label (input widget title) ie:

            "Open file", "file"

        :param str msg: message string to pass to the dialog title.
        :param str path: start path.
        """
        if path is None:
            path = self._work_path

        filename, ok = QtGui.QFileDialog.getOpenFileName(self, msg, path, "JSON files (*.json)")
        if filename == "":
            return
        return filename

    def inputDialog(self, msg, label, clean=True):
        """
        Prompts the user for an input. Arguments are message (dialog title) and
        label (input widget title) ie:

            "Save current file", "file name"

        :param str msg: message string to pass to the dialog title.
        :param str label: message string to pass to the input widget.
        :param bool clean: clean resulting string of illegal characters.
        """
        text, ok = QtGui.QInputDialog.getText(self, msg, label)
        if text:
            if clean:
                text = util.clean_name(text)
            return text
        return

