from math import degrees

from armagomen.battle_observer.core import settings, view_settings
from armagomen.constants import GLOBAL, MINIMAP
from armagomen.utils.common import overrideMethod
from constants import VISIBILITY
from gui.Scaleform.daapi.view.battle.shared.minimap import plugins
from gui.Scaleform.daapi.view.battle.shared.minimap.component import MinimapComponent
from gui.Scaleform.daapi.view.battle.shared.minimap.settings import CONTAINER_NAME


class PersonalEntriesPlugin(plugins.PersonalEntriesPlugin):

    def start(self):
        super(PersonalEntriesPlugin, self).start()
        if settings.minimap[MINIMAP.YAW] and self.__yawLimits is None:
            vInfo = self._arenaDP.getVehicleInfo()
            yawLimits = vInfo.vehicleType.turretYawLimits
            if yawLimits is not None:
                self.__yawLimits = (degrees(yawLimits[0]), degrees(yawLimits[1]))

    def _calcCircularVisionRadius(self):
        if settings.minimap[MINIMAP.VIEW_RADIUS]:
            vehAttrs = self.sessionProvider.shared.feedback.getVehicleAttrs()
            return vehAttrs.get('circularVisionRadius', VISIBILITY.MIN_RADIUS)
        return super(PersonalEntriesPlugin, self)._calcCircularVisionRadius()


class ArenaVehiclesPlugin(plugins.ArenaVehiclesPlugin):

    def __init__(self, *args, **kwargs):
        super(ArenaVehiclesPlugin, self).__init__(*args, **kwargs)
        self.__showDestroyEntries = settings.minimap[MINIMAP.DEATH_PERMANENT]
        self.__isDestroyImmediately = settings.minimap[MINIMAP.DEATH_PERMANENT]

    def _showVehicle(self, vehicleID, location):
        entry = self._entries[vehicleID]
        if entry.isAlive():
            super(ArenaVehiclesPlugin, self)._showVehicle(vehicleID, location)

    def _hideVehicle(self, entry):
        if entry.isAlive() and entry.isActive():
            super(ArenaVehiclesPlugin, self)._hideVehicle(entry)

    def __setDestroyed(self, vehicleID, entry):
        self.__clearAoIToFarCallback(vehicleID)
        if entry.setAlive(False) and not entry.wasSpotted():
            entryID = entry.getID()
            self._setInAoI(entry, True)
            self.__setActive(entry, True)
            self._move(entryID, CONTAINER_NAME.DEAD_VEHICLES)
            self._invoke(entryID, 'setDead', True)
            self._invoke(entryID, self._showNames)
        else:
            self.__setActive(entry, False)

    @property
    def _showNames(self):
        if self.__showDestroyEntries and settings.minimap[MINIMAP.SHOW_NAMES]:
            return 'showVehicleName'
        return 'hideVehicleName'


@overrideMethod(MinimapComponent, "_setupPlugins")
def _setupPlugins(base, plugin, arenaVisitor):
    _plugins = base(plugin, arenaVisitor)
    if settings.minimap[GLOBAL.ENABLED] and view_settings.notEpicBattle:
        if settings.minimap[MINIMAP.DEATH_PERMANENT]:
            _plugins['vehicles'] = ArenaVehiclesPlugin
        _plugins['personal'] = PersonalEntriesPlugin
    return _plugins
