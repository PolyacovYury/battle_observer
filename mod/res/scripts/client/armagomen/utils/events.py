from Event import SafeEvent


class Events(object):

    def __init__(self):
        self.onArmorChanged = SafeEvent()
        self.onMarkerColorChanged = SafeEvent()
        self.onDispersionAngleChanged = SafeEvent()
        self.onDisconnected = SafeEvent()
        self.onConnected = SafeEvent()
        self.onLoginLoaded = SafeEvent()
        self.onHangarLoaded = SafeEvent()
        self.onBattlePageLoaded = SafeEvent()
        self.onHangarVehicleChanged = SafeEvent()
        self.updateVehicleStatus = SafeEvent()


g_events = Events()
