# -*- coding: utf-8 -*-
"""

Script Name: Cores.py
Author: Do Trinh/Jimmy - 3D artist.

Description:

"""
# -------------------------------------------------------------------------------------------------------------
""" Import """

# Python
import time, datetime
from damg                               import DAMGDICT, DAMG, DAMGLIST
from functools                          import partial

# PLM
from utils                              import str2bool, bool2str
from appData                            import layoutTypes
from cores.GlobalSetting import GlobalSetting

class InspectLayout(DAMG):

    key                     = 'InspectLayout'
    layoutTypes             = DAMGLIST()
    layoutKeys              = DAMGLIST()

    def __init__(self):
        super(InspectLayout, self).__init__(self)

        self.layoutTypes.appendList(layoutTypes)

    def doInspection(self, layout):
        self.layoutTypes.append(layout.Type)
        self.layoutKeys.append(layout.key)
        return layout

    def checkType(self, layout):
        if not self.haveType(layout):
            try:
                layout.show()
            except AttributeError:
                layoutType  = 'Object'
            else:
                layoutType  = 'UI'
            layout.__setattr__('Type', layoutType)

        return self.checkKey(layout)

    def checkKey(self, layout):
        if not self.haveKey(layout):
            key = layout.__class__.__name__
            layout.__setattr__('key', key)

        return layout

    def haveType(self, layout):
        try:
            layout.Type
        except AttributeError:
            return False
        else:
            return True

    def haveKey(self, layout):
        try:
            layout.key
        except KeyError:
            return False
        else:
            return True

class LayoutManager(DAMGDICT):

    key                                 = 'LayoutManager'

    _buildAll                           = False

    noShowHideAttrs                     = DAMGLIST()
    unHidableLayouts                    = DAMGLIST()
    unShowableLayouts                   = DAMGLIST()
    awaitingSlots                       = DAMGLIST()
    layout_names                        = DAMGLIST()
    layout_ids                          = DAMGLIST()
    layout_datetimes                    = DAMGLIST()

    ignoreIDs = ['MainMenuSection', 'MainMenuBar', 'MainToolBarSection', 'MainToolBar',
                 'Notification', 'TopTab', 'BotTab', 'Footer', 'TopTab2', 'TopTab1',
                 'TopTab3', 'MainStatusBar', 'ConnectStatus', 'GridLayout']

    def __init__(self, setting, actionManager, buttonManager, parent=None):
        super(LayoutManager, self).__init__()

        self.parent = parent
        self.settings = setting
        self.inspect = InspectLayout()
        self.actionManager = actionManager
        self.buttonManager = buttonManager
        self.globalSetting = None

    def layouts(self):
        return self.values()

    def buildLayouts(self):
        self.mains                      = self.mainLayouts()
        self.funcs                      = self.functionLayouts()

        self.infos                      = self.infoLayouts()
        self.setts                      = self.settingLayouts()
        self.tools                      = self.toolLayouts()
        self.prjs                       = self.projectLayouts()

        cbs = [
            self.preferences.layout.tbTDCB,
            self.preferences.layout.tbCompCB,
            self.preferences.layout.tbArtCB,
            self.preferences.layout.tbTexCB,
            self.preferences.layout.tbPostCB,

            self.preferences.layout.mainToolBarCB,

            self.preferences.layout.statusBarCB,

            self.preferences.layout.connectStatuCB,

            self.preferences.layout.notifiCB,
        ]
    
        sections = [
            self.mainUI.mainToolBar.tdToolBar,
            self.mainUI.mainToolBar.compToolBar,
            self.mainUI.mainToolBar.artToolBar,
            self.mainUI.mainToolBar.textureToolBar,
            self.mainUI.mainToolBar.postToolBar,

            self.mainUI.mainToolBarSec,

            self.mainUI.statusBar,

            self.mainUI.connectStatusSec,

            self.mainUI.notifiSec,
        ]
    
        for i in range(len(sections)):
            key = self.preferences.layout.keys[i]
            grp = self.mainUI.key

            if self.settings.initValue(grp, key) is None:
                if i == 3 or i == 4:
                    val = False
                else:
                    val = True
            else:
                val = str2bool(self.settings.initValue(key))
    
            cbs[i].setChecked(val)
            sections[i].setVisible(val)
            cbs[i].stateChanged.connect(sections[i].setVisible)
            cbs[i].stateChanged.connect(partial(self.mainUI.signals.setSetting.emit, key, bool2str(val), grp))

        for layout in self.layouts():
            try:
                layout.isHidden()
            except AttributeError:
                self.noShowHideAttrs.append(layout)

        layouts = []
        for listLayout in [self.mains, self.funcs, self.infos, self.setts, self.tools, self.prjs]:
            layouts = layouts + list(listLayout)
        self._buildAll = True

        self.globalSetting = GlobalSetting(layouts)

        return layouts

    def functionLayouts(self):
        from ui.Funcs.SignIn import SignIn
        from ui.Funcs.SignUp import SignUp
        from ui.Funcs.ForgotPassword import ForgotPassword

        self.signin     = SignIn()
        self.forgotPW   = ForgotPassword()
        self.signup     = SignUp()

        for layout in [self.signin, self.signup, self.forgotPW]:
            self.regisLayout(layout)

        return self.signin, self.signup, self.forgotPW

    def mainLayouts(self):
        from ui.PipelineManager import PipelineManager
        from ui.SysTray import SysTray

        self.mainUI     = PipelineManager(self.settings, self.actionManager, self.buttonManager)
        self.sysTray    = SysTray(self.actionManager)
        self.setLayoutUnHidable(self.sysTray)

        layouts = [self.mainUI, self.sysTray]

        for layout in layouts:
            self.regisLayout(layout)

        for layout in self.mainUI.mainUI_layouts:
            self.regisLayout(layout)

        for layout in self.mainUI.topTabUI.tabLst:
            key = layout.key
            if not key in self.keys():
                self[key] = layout

        return layouts

    def infoLayouts(self):
        from ui.Info.InfoWidget import InfoWidget

        self.about                          = InfoWidget(key='About')
        self.codeConduct                    = InfoWidget(key='CodeOfConduct')
        self.contributing                   = InfoWidget(key='Contributing')
        self.credit                         = InfoWidget(key="Credit")
        self.licence                        = InfoWidget(key='Licence')
        self.reference                      = InfoWidget(key='Reference')
        self.version                        = InfoWidget(key='Version')

        layouts = [self.about, self.codeConduct, self.contributing, self.credit, self.licence,
                    self. reference, self.version]

        for layout in layouts:
            self.regisLayout(layout)

        return layouts

    def settingLayouts(self):
        from ui.Settings.SettingUI import SettingUI
        from ui.Settings.UserSetting import UserSetting

        self.settingUI                      = SettingUI(self.settings, self)
        self.userSetting                    = UserSetting()

        layouts = [self.settingUI, self.userSetting]

        for layout in layouts:
            self.regisLayout(layout)

        return layouts

    def toolLayouts(self):
        from ui.Tools import (Screenshot, NoteReminder, ImageViewer, FindFiles, EnglishDictionary,
                              Calendar, Calculator)
        from ui.Tools.NodeGraph import NodeGraph
        from ui.Tools.TextEditor import TextEditor
        from ui.Menus.config import Configuration, Preferences

        self.calculator     = Calculator.Calculator()
        self.calendar       = Calendar.Calendar()
        self.configuration  = Configuration.Configuration()
        self.engDict        = EnglishDictionary.EnglishDictionary()
        self.findFile       = FindFiles.FindFiles()
        self.imageViewer    = ImageViewer.ImageViewer()
        self.nodeGraph      = NodeGraph.NodeGraph()
        self.noteReminder   = NoteReminder.NoteReminder()
        self.preferences    = Preferences.Preferences()
        self.screenShot     = Screenshot.Screenshot()
        self.textEditor     = TextEditor.TextEditor()

        layouts     = [self.calculator, self.calendar, self.configuration, self.engDict, self.findFile,
                       self.imageViewer, self.nodeGraph, self.noteReminder, self.preferences, self.screenShot,
                       self.textEditor]

        for layout in layouts:
            self.regisLayout(layout)

        return layouts

    def projectLayouts(self):
        from ui.Projects.NewProject import NewProject

        self.newProject     = NewProject()

        for layout in [self.newProject, ]:
            self.regisLayout(layout)

        layouts = [self.newProject]
        return layouts

    def regisLayout(self, layout):

        ui = self.inspect.doInspection(layout)
        key = ui.key
        if self.isLayout(ui):
            if self.isAwaitingSlot(ui):
                self.awaitingSlots.remove(key)
                self.doRegister(ui)
            else:
                if not self.isRegistered(ui):
                    self.doRegister(ui)
                else:
                    # print("Already registered: {0}".format(key))
                    return False

    def isAwaitingSlot(self, layout):
        key = layout.key
        if key in self.awaitingSlots:
            return True
        else:
            return False

    def doRegister(self, layout):
        key = layout.key

        self.layout_names.append(layout.name)
        self.layout_ids.append(id(layout))
        self.layout_datetimes.append(str(datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S|%d.%m.%Y')))

        # print("Registing layout: {0} : {1}".format(layout.key, layout))
        self[key] = layout
        return True

    def deRegister(self, layout):
        key = layout.key
        index = self.layout_names.index(layout.name)

        if self.isRegistered(layout):
            self.awaitingSlots.append(key)
            try:
                del self[key]
            except KeyError:
                self.pop(key, None)
            self.layout_names.remove(self.layout_names[index])
            self.layout_ids.remove(self.layout_ids[index])
            self.layout_datetimes.remove(self.layout_datetimes[index])
            return True
        else:
            return False

    def isRegistered(self, layout):
        key = layout.key
        if key in self.keys():
            return True
        else:
            return False

    def isLayout(self, layout):
        if layout.Type in self.inspect.layoutTypes:
            return True
        else:
            return False

    def signOutEvent(self):
        self.showOnlyLayout(self.signin)

    def newAcountEvent(self):
        self.showOnlyLayout(self.signup)

    def switchAccountEvent(self):
        self.showOnlyLayout(self.signin)

    def signUpEvent(self):
        self.showOnlyLayout(self.signup)

    def showOnlyLayout(self, layout):
        layouts = [l for l in self.layouts() if not l is layout and not l in self.unHidableLayouts]
        if self.isHidable(layout):
            self.show(layout)

        for l in layouts:
            self.hide(l)

    def hideOnlyLayout(self, layout):
        layouts = [l for l in self.layouts() if not l is layout and not l in self.unHidableLayouts]
        if self.isHidable(layout):
            self.hide(layout)

        for l in layouts:
            self.show(l)

    def setLayoutUnHidable(self, layout):
        if not layout in self.unHidableLayouts:
            layout.show()
            layout.setVisible(True)
            return self.unHidableLayouts.append(layout)

    def setLayoutUnShowable(self, layout):
        if not layout in self.unShowableLayouts:
            self.hide(layout)
            return self.unShowableLayouts.append(layout)

    def setLayoutHidable(self, layout):
        if layout in self.unHidableLayouts:
            self.show(layout)
            return self.unHidableLayouts.remove(layout)

    def isHidable(self, layout):
        if not layout in self.noShowHideAttrs:
            if not layout in self.unHidableLayouts:
                try:
                    layout.isHidden()
                except AttributeError:
                    return False
                else:
                    return True
            elif layout in self.unShowableLayouts:
                return False
            else:
                return False
        else:
            return False

    def hide(self, layout):
        if not layout.key in self.ignoreIDs:
            layout.hide()
            return layout.setValue('state', 'hide')

    def show(self, layout):
        if not layout.key in self.ignoreIDs:
            layout.show()
            return layout.setValue('state', 'show')

    def showNormal(self, layout):
        if not layout.key in self.ignoreIDs:
            layout.showNormal()
            return layout.setValue('state', 'showNormal')

    def showMinnimize(self, layout):
        if not layout.key in self.ignoreIDs:
            layout.showMinimize()
            return layout.setValue('state', 'showMinimize')

    def showMaximized(self, layout):
        if not layout.key in self.ignoreIDs:
            layout.showMaximized()
            return layout.setValue('state', 'showMaximized')

    def showAllLayout(self):
        for layout in self.layouts():
            self.show(layout)

    @property
    def buildAll(self):
        return self._buildAll

    @buildAll.setter
    def buildAll(self, val):
        self._buildAll = val

# -------------------------------------------------------------------------------------------------------------
# Created by panda on 6/07/2018 - 11:31 AM
# © 2017 - 2018 DAMGteam. All rights reserved