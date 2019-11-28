# -*- coding: utf-8 -*-
"""

Script Name: ActionManager.py
Author: Do Trinh/Jimmy - 3D artist.

Description:

"""
# -------------------------------------------------------------------------------------------------------------
from __future__ import absolute_import, unicode_literals

import os
from functools import partial

from bin                        import DAMGDICT, DAMGLIST
from toolkits.Widgets           import Action
from utils                      import data_handler, is_action, is_string
from appData                    import (mainConfig, SHOWLAYOUT_KEY, START_FILE_KEY, EXECUTING_KEY, OPEN_BROWSER_KEY,
                                        CONFIG_DEV, CONFIG_TOOLS, CONFIG_OFFICE, CONFIG_TDS, CONFIG_ART, CONFIG_TEX,
                                        CONFIG_POST, CONFIG_VFX, CONFIG_EXTRA, CONFIG_SYSTRAY, RESTORE_KEY, SHOWMIN_KEY,
                                        SHOWMAX_KEY, EDIT_KEY, STYLESHEET_KEY)

class ActionManager(DAMGDICT):

    key                         = 'ActionManager'
    _name                       = 'ActionManager'

    appInfo                     = data_handler(filePath=mainConfig)

    actionKeys                  = DAMGLIST()
    showLayoutKeys              = DAMGLIST()
    showRestoreKeys             = DAMGLIST()
    showMaximizeKeys            = DAMGLIST()
    showMinimizeKeys            = DAMGLIST()
    startFileKeys               = DAMGLIST()
    openBrowserKeys             = DAMGLIST()
    executingKeys               = DAMGLIST()

    orgActions                  = ['Organisation']
    teamActions                 = ['Team']
    prjActions                  = ['Project']
    taskActions                 = ['Task']
    stylesheetActions           = STYLESHEET_KEY

    appActions                  = ['SettingUI', 'Configuration', 'Preferences', 'Exit']
    goActions                   = ['ConfigFolder', 'IconFolder', 'SettingFolder', 'AppFolder']
    officeActions               = ['TextEditor', 'NoteReminder'] + CONFIG_OFFICE
    toolsActions                = CONFIG_TOOLS + ['CleanPyc', 'ReConfig', 'Debug']
    devActions                  = CONFIG_DEV
    libActions                  = ['Alpha', 'HDRI', 'Texture']
    helpActions                 = ['PLM wiki', 'About', 'CodeOfConduct', 'Contributing', 'Credit', 'Reference', 'Version', 'Feedback', 'ContactUs', ]

    editActions                 = EDIT_KEY

    tdActions                   = CONFIG_TDS
    artActions                  = CONFIG_ART
    texActions                  = CONFIG_TEX
    postActions                 = CONFIG_POST
    vfxActions                  = CONFIG_VFX
    extraActions                = CONFIG_EXTRA
    sysTrayActions              = CONFIG_SYSTRAY

    def __init__(self, parent=None):
        super(ActionManager, self).__init__(self)

        self.parent = parent
        self.showLayoutKeys.appendList(SHOWLAYOUT_KEY)
        self.startFileKeys.appendList(START_FILE_KEY)
        self.executingKeys.appendList(EXECUTING_KEY)
        self.openBrowserKeys.appendList(OPEN_BROWSER_KEY)
        self.showRestoreKeys.appendList(RESTORE_KEY)
        self.showMaximizeKeys.appendList(SHOWMAX_KEY)
        self.showMinimizeKeys.appendList(SHOWMIN_KEY)

        self.actionKeys = self.showLayoutKeys + self.startFileKeys + self.executingKeys + self.officeActions + \
                          self.showRestoreKeys + self.showMaximizeKeys + self.showMinimizeKeys

    def actionConfigError(self, key):
        return print('ActionKeyConfigError: This key is not registered: {0}'.format(key))

    def actionRegisterError(self, key):
        return print('ActionRegisterError: This action is already registered: {0}'.format(key))

    def editMenuActions(self, parent):
        return self.createActions(self.editActions, parent)

    def extraToolActions(self, parent):
        return self.createActions(self.extraActions, parent)

    def tdToolBarActions(self, parent):
        return self.createActions(self.tdActions, parent)

    def artToolBarActions(self, parent):
        return self.createActions(self.artActions, parent)

    def texToolBarActions(self, parent):
        return self.createActions(self.texActions, parent)

    def postToolBarActions(self, parent):
        return self.createActions(self.postActions, parent)

    def vfxToolBarActions(self, parent):
        return self.createActions(self.vfxActions, parent)

    def sysTrayMenuActions(self, parent):
        return self.createActions(self.sysTrayActions, parent)

    def appMenuActions(self, parent):
        return self.createActions(self.appActions, parent)

    def orgMenuActions(self, parent):
        return self.createActions(self.orgActions, parent)

    def teamMenuActions(self, parent):
        return self.createActions(self.teamActions, parent)

    def stylesheetMenuActions(self, parent):
        return self.createActions(self.stylesheetActions, parent)

    def projectMenuActions(self, parent):
        return self.createActions(self.prjActions, parent)

    def taskMenuActions(self, parent):
        return self.createActions(self.taskActions, parent)

    def goMenuActions(self, parent):
        return self.createActions(self.goActions, parent)

    def officeMenuActions(self, parent):
        return self.createActions(self.officeActions, parent)

    def toolsMenuActions(self, parent):
        return self.createActions(self.toolsActions, parent)

    def devMenuActions(self, parent):
        return self.createActions(self.devActions, parent)

    def libMenuActions(self, parent):
        return self.createActions(self.libActions, parent)

    def helpMenuActions(self, parent):
        return self.createActions(self.helpActions, parent)

    def createActions(self, keys, parent):
        actions = []
        for key in keys:
            if key in self.appInfo.keys():
                if is_string(key):
                    action = self.createAction(key, parent)
                    actions.append(action)
                elif is_action(key):
                    action = key
                    action.setParent(parent)
                    self.register(action)
                    actions.append(action)
                else:
                    print("DataTypeError: Could not add action: {0}".format(key))

        return actions

    def createAction(self, key, parent):
        if key in self.showLayoutKeys:
            # print('{0} is set to {1} action'.format(key, 'showlayout'))
            return self.showLayoutAction(key, parent)
        elif key in self.startFileKeys:
            # print('{0} is set to {1} action'.format(key, 'startfile'))
            return self.startFileAction(key, parent)
        elif key in self.executingKeys:
            # print('{0} is set to {1} action'.format(key, 'executing'))
            return self.executingAction(key, parent)
        elif key in self.openBrowserKeys:
            # print('{0} is set to {1} action'.format(key, 'openBrowser'))
            return self.openBrowserAction(key, parent)
        elif key in self.showMinimizeKeys:
            # print('{0} is set to {1} action'.format(key, 'showminimized'))
            return self.showMinAction(key, parent)
        elif key in self.showMaximizeKeys:
            # print('{0} is set to {1} action'.format(key, 'showmaximized'))
            return self.showMaxAction(key, parent)
        elif key in self.showRestoreKeys:
            # print('{0} is set to {1} action'.format(key, 'showrestore'))
            return self.showRestoreAction(key, parent)
        else:
            return self.actionConfigError(key)

    def showLayoutAction(self, key, parent):
        if key in self.appInfo.keys():
            action = Action({'icon': self.appInfo[key][1],
                             'txt': '&{0}'.format(key),
                             'stt': self.appInfo[key][0],
                             'trg': partial(parent.signals.emit, 'showLayout', key, 'show'), }, parent)
            action.key = '{0}_{1}_Action'.format(parent.key, key)
            action._name = action.key
            if action.key in self.actionKeys:
                return self[action.key]
            else:
                action._name = '{0} Action'.format(key)
                action.Type = 'DAMGShowLayoutAction'
                self.register(action)
                return action
        else:
            return self.actionConfigError(key)

    def showRestoreAction(self, key, parent):
        if key in self.appInfo.keys():
            action = Action({'icon': self.appInfo[key][1],
                             'txt': '&{0}'.format(key),
                             'stt': self.appInfo[key][0],
                             'trg': partial(parent.signals.emit, 'showLayout', self.appInfo[key][2], 'showRestore'), }, parent)
            action.key = '{0}_{1}_Action'.format(parent.key, key)
            action._name = action.key
            if action.key in self.actionKeys:
                return self[action.key]
            else:
                action._name = '{0} Action'.format(key)
                action.Type = 'DAMGShowNormalAction'
                self.register(action)
                return action
        else:
            return self.actionConfigError(key)

    def showMaxAction(self, key, parent):
        if key in self.appInfo.keys():
            action = Action({'icon': self.appInfo[key][1],
                             'txt': '&{0}'.format(key),
                             'stt': self.appInfo[key][0],
                             'trg': partial(parent.signals.emit, 'showLayout', self.appInfo[key][2], 'showMax'), }, parent)
            action.key = '{0}_{1}_Action'.format(parent.key, key)
            action._name = action.key
            if action.key in self.actionKeys:
                return self[action.key]
            else:
                action._name = '{0} Action'.format(key)
                action.Type = 'DAMGShowMaximizeAction'
                self.register(action)
                return action
        else:
            return self.actionConfigError(key)

    def showMinAction(self, key, parent):
        if key in self.appInfo.keys():
            action = Action({'icon': self.appInfo[key][1],
                             'txt': '&{0}'.format(key),
                             'stt': self.appInfo[key][0],
                             'trg': partial(parent.signals.emit, 'showLayout', self.appInfo[key][2], 'showMin'), }, parent)
            action.key = '{0}_{1}_Action'.format(parent.key, key)
            action._name = action.key
            if action.key in self.actionKeys:
                return self[action.key]
            else:
                action._name = '{0} Action'.format(key)
                action.Type = 'DAMGShowMinimizeAction'
                self.register(action)
                return action
        else:
            return self.actionConfigError(key)

    def startFileAction(self, key, parent):
        if key in self.appInfo.keys():
            # print('create start file action: {} {}'.format(key, self.appInfo[key][2]))
            action = Action({'icon': self.appInfo[key][1],
                             'txt': '&{0}'.format(key),
                             'stt': self.appInfo[key][0],
                             'trg': partial(os.startfile, self.appInfo[key][2])}, parent)
            action.key = '{0}_{1}_Action'.format(parent.key, key)
            action._name = action.key
            if action.key in self.actionKeys:
                return self[action.key]
            else:
                action._name = '{0} Action'.format(key)
                action.Type = 'DAMGStartFileAction'
                self.register(action)
                return action
        else:
            return self.actionConfigError(key)

    def executingAction(self, key, parent):
        if key in self.appInfo.keys():
            action = Action({'icon': self.appInfo[key][1],
                             'txt': '&{0}'.format(key),
                             'stt': self.appInfo[key][0],
                             'trg': partial(parent.signals.emit, 'executing', self.appInfo[key][2]), }, parent)
            action.key = '{0}_{1}_Action'.format(parent.key, key)
            action._name = '{0} Action'.format(key)
            if action.key in self.actionKeys:
                return self[action.key]
            else:
                action.Type = 'DAMGExecutingAction'
                self.register(action)
                return action
        else:
            return self.actionConfigError(key)

    def openBrowserAction(self, key, parent):
        if key in self.appInfo.keys():
            action = Action({'icon': self.appInfo[key][1],
                             'txt': '&{0}'.format(key),
                             'stt': self.appInfo[key][0],
                             'trg': partial(parent.signals.emit, 'openBrowser', self.appInfo[key][2]), }, parent)
            action.key = '{0}_{1}_Action'.format(parent.key, key)
            action._name = action.key
            if action.key in self.actionKeys:
                return self[action.key]
            else:
                action._name = '{0} Action'.format(key)
                action.Type = 'DAMGOpenBrowserAction'
                self.register(action)
                return action
        else:
            return self.actionConfigError(key)

    def register(self, action):
        # print('register action: {}'.format(action))
        if not action.key in self.actionKeys:
            self.actionKeys.append(action.key)
            self[action.key] = action
        else:
            return self.actionRegisterError(action.key)

    def actions(self):
        return self.values()

# -------------------------------------------------------------------------------------------------------------
# Created by panda on 3/11/2019 - 5:26 PM
# © 2017 - 2018 DAMGteam. All rights reserved