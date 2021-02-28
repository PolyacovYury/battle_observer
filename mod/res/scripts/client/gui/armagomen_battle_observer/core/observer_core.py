import os
from shutil import rmtree

from gui.shared.personality import ServicesLocator
from skeletons.gui.app_loader import GuiGlobalSpaceID
from .bo_constants import FILE_NAME, MOD_VERSION, MASSAGES, GLOBAL, CACHE_DIRS, MAIN, MOD_NAME
from .utils.common import logInfo, logError, getPreferencesFilePath, getCurrentModPath


class ObserverCore(object):
    __slots__ = ("modsDir", "gameVersion", "workingDir", "fileName", "isFileValid", "mod_version",
                 "config", "cache", "configLoader", "moduleLoader")

    def __init__(self, config, cache, configLoader, moduleLoader):
        self.config, self.cache = config, cache
        self.configLoader, self.moduleLoader = configLoader, moduleLoader
        self.modsDir, self.gameVersion = getCurrentModPath()
        self.workingDir = os.path.join(self.modsDir, self.gameVersion)
        self.fileName = FILE_NAME.format(MOD_VERSION)
        self.isFileValid = self.isModValidFileName()
        self.mod_version = 'v{0} - {1}'.format(MOD_VERSION, self.gameVersion)

    def clearClientCache(self, category=None):
        path = os.path.normpath(unicode(getPreferencesFilePath(), 'utf-8', errors='ignore'))
        path = os.path.split(path)[GLOBAL.FIRST]
        if category is None:
            for dirName in CACHE_DIRS:
                self.removeDirs(os.path.join(path, dirName), dirName)
        else:
            self.removeDirs(os.path.join(path, category), category)

    @staticmethod
    def removeDirs(normpath, dirName):
        if os.path.exists(normpath):
            rmtree(normpath, ignore_errors=True, onerror=None)
            logInfo('CLEANING CACHE: {0}'.format(dirName))

    def onExit(self):
        if self.isFileValid:
            if self.config.main[MAIN.AUTO_CLEAR_CACHE]:
                self.clearClientCache()
            if self.cache.errorKeysSet and GLOBAL.DEBUG_MODE:
                for key in sorted(self.cache.errorKeysSet):
                    logError(key)
            logInfo('MOD {}: {}'.format(MASSAGES.FINISH, self.mod_version))

    def isModValidFileName(self):
        return self.fileName in os.listdir(self.workingDir)

    def start(self):
        if self.isFileValid:
            logInfo('MOD {}: {}'.format(MASSAGES.START, self.mod_version))
            self.configLoader.start()
            self.moduleLoader.start()
        else:
            from .utils.common import logWarning
            from gui.Scaleform.daapi.view import dialogs
            from gui import DialogsInterface
            from .update.dialog_button import DialogButtons
            locked = MASSAGES.LOCKED_BY_FILE_NAME.format(self.fileName)
            logWarning(locked)

            def loadBlocked(spaceID):
                if spaceID in (GuiGlobalSpaceID.LOGIN, GuiGlobalSpaceID.LOBBY):
                    title = '{} is locked'.format(MOD_NAME)
                    btn = DialogButtons('Close')
                    DialogsInterface.showDialog(dialogs.SimpleDialogMeta(title, locked, btn), lambda proceed: None)
                    ServicesLocator.appLoader.onGUISpaceEntered -= loadBlocked

            ServicesLocator.appLoader.onGUISpaceEntered += loadBlocked
