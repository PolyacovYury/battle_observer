from collections import defaultdict

from armagomen.battle_observer.core import keysParser
from armagomen.battle_observer.meta.battle.damage_logs_meta import DamageLogsMeta
from armagomen.constants import DAMAGE_LOG, GLOBAL, VEHICLE_TYPES
from armagomen.utils.common import callback, logWarning, percentToRGB
from constants import ATTACK_REASONS, SHELL_TYPES_LIST
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID


class DamageLog(DamageLogsMeta):

    def __init__(self):
        super(DamageLog, self).__init__()
        self.input_log = {}
        self.damage_log = {}
        self.top_log = None
        self.vehicle_colors = defaultdict(lambda: self.vehicle_types[VEHICLE_TYPES.CLASS_COLORS][VEHICLE_TYPES.UNKNOWN],
                                          **self.vehicle_types[VEHICLE_TYPES.CLASS_COLORS])
        self.vehicle_icons = defaultdict(lambda: self.vehicle_types[VEHICLE_TYPES.CLASS_ICON][VEHICLE_TYPES.UNKNOWN],
                                         **self.vehicle_types[VEHICLE_TYPES.CLASS_ICON])

    def _populate(self):
        super(DamageLog, self)._populate()
        self.top_log = defaultdict(int, **self.settings.log_total[DAMAGE_LOG.ICONS])
        self.as_startUpdateS({DAMAGE_LOG.D_LOG: self.settings.log_damage_extended[GLOBAL.SETTINGS],
                              DAMAGE_LOG.IN_LOG: self.settings.log_input_extended[GLOBAL.SETTINGS],
                              DAMAGE_LOG.MAIN_LOG: self.settings.log_total[GLOBAL.SETTINGS]},
                             {DAMAGE_LOG.D_LOG: self.settings.log_damage_extended[GLOBAL.ENABLED],
                              DAMAGE_LOG.IN_LOG: self.settings.log_input_extended[GLOBAL.ENABLED],
                              DAMAGE_LOG.MAIN_LOG: self.settings.log_total[GLOBAL.ENABLED]})

    def _dispose(self):
        DAMAGE_LOG.AVG_DAMAGE_DATA = 0.0
        super(DamageLog, self)._dispose()

    def isLogEnabled(self, eventType):
        if eventType == FEEDBACK_EVENT_ID.PLAYER_DAMAGED_HP_ENEMY:
            return self.settings.log_damage_extended[GLOBAL.ENABLED]
        elif eventType == FEEDBACK_EVENT_ID.ENEMY_DAMAGED_HP_PLAYER:
            return self.settings.log_input_extended[GLOBAL.ENABLED]
        logWarning(DAMAGE_LOG.WARNING_MESSAGE)
        return False

    def getLogDictAndSettings(self, eventType):
        if eventType == FEEDBACK_EVENT_ID.PLAYER_DAMAGED_HP_ENEMY:
            return self.damage_log, self.settings.log_damage_extended
        elif eventType == FEEDBACK_EVENT_ID.ENEMY_DAMAGED_HP_PLAYER:
            return self.input_log, self.settings.log_input_extended
        logWarning(DAMAGE_LOG.WARNING_MESSAGE)
        raise ValueError("eventType %s NOT FOUND" % eventType)

    def onEnterBattlePage(self):
        super(DamageLog, self).onEnterBattlePage()
        if self._player is not None and self._player.vehicle is not None:
            self.input_log.update(kills=set(), shots=list())
            self.damage_log.update(kills=set(), shots=list())
            extended_log = self.settings.log_damage_extended[GLOBAL.ENABLED] or self.settings.log_input_extended[
                GLOBAL.ENABLED]
            if extended_log:
                keysParser.onKeyPressed += self.keyEvent
                arena = self._arenaVisitor.getArenaSubscription()
                if arena is not None:
                    arena.onVehicleAdded += self.onVehicleAddUpdate
                    arena.onVehicleUpdated += self.onVehicleAddUpdate
                    arena.onVehicleKilled += self.onVehicleKilled
                keysParser.registerComponent(DAMAGE_LOG.HOT_KEY, self.settings.log_global[DAMAGE_LOG.HOT_KEY])
            if self.settings.log_total[GLOBAL.ENABLED] or extended_log:
                feedback = self.sessionProvider.shared.feedback
                if feedback:
                    feedback.onPlayerFeedbackReceived += self.__onPlayerFeedbackReceived
            if not self._arenaDP.getVehicleInfo().isSPG():
                self.top_log.update(stun=GLOBAL.EMPTY_LINE, stunIcon=GLOBAL.EMPTY_LINE)
            self.updateAvgDamage()
            self.updateTopLog()

    def onExitBattlePage(self):
        if self._player is not None:
            extended_log = self.settings.log_damage_extended[GLOBAL.ENABLED] or self.settings.log_input_extended[
                GLOBAL.ENABLED]
            if extended_log:
                keysParser.onKeyPressed -= self.keyEvent
                arena = self._arenaVisitor.getArenaSubscription()
                if arena is not None:
                    arena.onVehicleAdded -= self.onVehicleAddUpdate
                    arena.onVehicleUpdated -= self.onVehicleAddUpdate
                    arena.onVehicleKilled -= self.onVehicleKilled
            if self.settings.log_total[GLOBAL.ENABLED] or extended_log:
                feedback = self.sessionProvider.shared.feedback
                if feedback:
                    feedback.onPlayerFeedbackReceived -= self.__onPlayerFeedbackReceived
            self.input_log.clear()
            self.damage_log.clear()
            self.top_log.clear()
        super(DamageLog, self).onExitBattlePage()

    def updateAvgDamage(self):
        """sets the average damage to the selected tank"""
        if self._player is not None and not DAMAGE_LOG.AVG_DAMAGE_DATA:
            max_health = self._player.vehicle.typeDescriptor.maxHealth
            DAMAGE_LOG.AVG_DAMAGE_DATA = max(DAMAGE_LOG.RANDOM_MIN_AVG, float(max_health))
        self.top_log[DAMAGE_LOG.AVG_DAMAGE] = int(DAMAGE_LOG.AVG_DAMAGE_DATA)

    def keyEvent(self, key, isKeyDown):
        """hot key event"""
        if key == DAMAGE_LOG.HOT_KEY:
            if self.settings.log_damage_extended[GLOBAL.ENABLED]:
                self.updateExtendedLog(self.damage_log, self.settings.log_damage_extended, altMode=isKeyDown)
            if self.settings.log_input_extended[GLOBAL.ENABLED]:
                self.updateExtendedLog(self.input_log, self.settings.log_input_extended, altMode=isKeyDown)

    def __onPlayerFeedbackReceived(self, events, *args, **kwargs):
        """wg Feedback event parser"""
        for event in events:
            e_type = event.getType()
            extra = event.getExtra()
            data = 0
            if e_type == FEEDBACK_EVENT_ID.PLAYER_SPOTTED_ENEMY:
                data += event.getCount()
            elif e_type in DAMAGE_LOG.TOP_LOG_ASSIST or e_type in DAMAGE_LOG.EXTENDED_DAMAGE:
                data += int(extra.getDamage())
            elif e_type == FEEDBACK_EVENT_ID.DESTRUCTIBLE_DAMAGED:
                data += int(extra)
            if e_type in DAMAGE_LOG.TOP_MACROS_NAME:
                if e_type == FEEDBACK_EVENT_ID.PLAYER_ASSIST_TO_STUN_ENEMY and not self.top_log[DAMAGE_LOG.STUN_ICON]:
                    self.top_log[DAMAGE_LOG.STUN_ICON] = self.settings.log_total[DAMAGE_LOG.ICONS][DAMAGE_LOG.STUN_ICON]
                    self.top_log[DAMAGE_LOG.ASSIST_STUN] = GLOBAL.ZERO
                self.top_log[DAMAGE_LOG.TOP_MACROS_NAME[e_type]] += data
                self.updateTopLog()
            if e_type in DAMAGE_LOG.EXTENDED_DAMAGE and self.isLogEnabled(e_type):
                log_dict, settings = self.getLogDictAndSettings(e_type)
                self.addToExtendedLog(log_dict, settings, event.getTargetID(),
                                      extra.getAttackReasonID(), data, extra.getShellType(), extra.isShellGold())

    def updateTopLog(self):
        """update global sums in log"""
        if self.settings.log_total[GLOBAL.ENABLED]:
            value = self.top_log[DAMAGE_LOG.PLAYER_DAMAGE] / DAMAGE_LOG.AVG_DAMAGE_DATA
            self.top_log[DAMAGE_LOG.DAMAGE_AVG_COLOR] = percentToRGB(value, **self.settings.log_total[
                GLOBAL.AVG_COLOR])
            self.as_updateDamageS(self.settings.log_total[DAMAGE_LOG.TEMPLATE_MAIN_DMG] % self.top_log)

    def onVehicleAddUpdate(self, vehicleID, *args, **kwargs):
        """update log item in GM-mode"""
        vehicleInfoVO = self._arenaDP.getVehicleInfo(vehicleID)
        if vehicleInfoVO:
            vehicleType = vehicleInfoVO.vehicleType
            if vehicleType and vehicleType.maxHealth and vehicleType.classTag:
                log_dict, settings = self.getLogDictAndSettings(FEEDBACK_EVENT_ID.ENEMY_DAMAGED_HP_PLAYER)
                vehicle = log_dict.get(vehicleID, {})
                if vehicle and vehicle.get(DAMAGE_LOG.VEHICLE_CLASS) is None:
                    vehicle[DAMAGE_LOG.VEHICLE_CLASS] = vehicleType.classTag
                    vehicle[DAMAGE_LOG.TANK_NAMES] = {vehicleType.shortName}
                    vehicle[DAMAGE_LOG.TANK_NAME] = vehicleType.shortName
                    vehicle[DAMAGE_LOG.ICON_NAME] = vehicleType.iconName
                    vehicle[DAMAGE_LOG.TANK_LEVEL] = vehicleType.level
                    vehicle[DAMAGE_LOG.CLASS_ICON] = self.vehicle_icons[vehicleType.classTag]
                    vehicle[DAMAGE_LOG.CLASS_COLOR] = self.vehicle_colors[vehicleType.classTag]
                    self.updateExtendedLog(log_dict, settings)

    def onVehicleKilled(self, targetID, attackerID, *args, **kwargs):
        if self._player is not None:
            if self._player.playerVehicleID in (targetID, attackerID):
                if self._player.playerVehicleID == targetID:
                    eventID = FEEDBACK_EVENT_ID.ENEMY_DAMAGED_HP_PLAYER
                    target = attackerID
                else:
                    eventID = FEEDBACK_EVENT_ID.PLAYER_DAMAGED_HP_ENEMY
                    target = targetID
                log_dict, settings = self.getLogDictAndSettings(eventID)
                log_dict[DAMAGE_LOG.KILLS].add(target)
                self.updateExtendedLog(log_dict, settings)

    def checkShell(self, attack_reason_id, gold, is_dlog, shell_type):
        if is_dlog and attack_reason_id == GLOBAL.ZERO:
            if self._player is not None:
                shell = self._player.getVehicleDescriptor().shot.shell
                shell_type = shell.kind
                shell_icon_name = shell.iconName
                gold = shell_icon_name in DAMAGE_LOG.PREMIUM_SHELLS
            else:
                shell_type = DAMAGE_LOG.UNDEFINED
                shell_icon_name = DAMAGE_LOG.UNDEFINED
        elif shell_type in DAMAGE_LOG.PREMIUM_SHELLS or shell_type in SHELL_TYPES_LIST:
            shell_icon_name = shell_type + DAMAGE_LOG.PREMIUM if gold else shell_type
        else:
            shell_type = DAMAGE_LOG.UNDEFINED
            shell_icon_name = DAMAGE_LOG.UNDEFINED
        return gold, shell_icon_name, shell_type

    def addToExtendedLog(self, log_dict, settings, vehicle_id, attack_reason_id, damage, shell_type, gold):
        """add or update log item"""
        is_dlog = log_dict is self.damage_log
        if vehicle_id not in log_dict[DAMAGE_LOG.SHOTS]:
            log_dict[DAMAGE_LOG.SHOTS].append(vehicle_id)
        gold, shell_icon_name, shell_type = self.checkShell(attack_reason_id, gold, is_dlog, shell_type)
        vehicle = log_dict.setdefault(vehicle_id, defaultdict(lambda: GLOBAL.CONFIG_ERROR))
        info = self._arenaDP.getVehicleInfo(vehicle_id)
        if vehicle:
            vehicle[DAMAGE_LOG.DAMAGE_LIST].append(damage)
            vehicle[DAMAGE_LOG.TANK_NAMES].add(info.vehicleType.shortName)
        else:
            vehicle[DAMAGE_LOG.INDEX] = len(log_dict[DAMAGE_LOG.SHOTS])
            vehicle[DAMAGE_LOG.DAMAGE_LIST] = [damage]
            vehicle[DAMAGE_LOG.VEHICLE_CLASS] = info.vehicleType.classTag
            vehicle[DAMAGE_LOG.TANK_NAMES] = {info.vehicleType.shortName}
            vehicle[DAMAGE_LOG.ICON_NAME] = info.vehicleType.iconName
            vehicle[DAMAGE_LOG.USER_NAME] = info.player.name
            vehicle[DAMAGE_LOG.TANK_LEVEL] = info.vehicleType.level
            vehicle[DAMAGE_LOG.KILLED_ICON] = GLOBAL.EMPTY_LINE
            vehicle[DAMAGE_LOG.CLASS_ICON] = self.vehicle_icons[info.vehicleType.classTag]
            vehicle[DAMAGE_LOG.CLASS_COLOR] = self.vehicle_colors[info.vehicleType.classTag]
            vehicle_id = self._player.playerVehicleID if not is_dlog else vehicle_id
            vehicle[DAMAGE_LOG.MAX_HEALTH] = self._arenaDP.getVehicleInfo(vehicle_id).vehicleType.maxHealth
        vehicle[DAMAGE_LOG.SHOTS] = len(vehicle[DAMAGE_LOG.DAMAGE_LIST])
        vehicle[DAMAGE_LOG.TOTAL_DAMAGE] = sum(vehicle[DAMAGE_LOG.DAMAGE_LIST])
        vehicle[DAMAGE_LOG.ALL_DAMAGES] = DAMAGE_LOG.COMMA.join(str(x) for x in vehicle[DAMAGE_LOG.DAMAGE_LIST])
        vehicle[DAMAGE_LOG.LAST_DAMAGE] = vehicle[DAMAGE_LOG.DAMAGE_LIST][GLOBAL.LAST]
        vehicle[DAMAGE_LOG.ATTACK_REASON] = self.settings.log_global[DAMAGE_LOG.ATTACK_REASON][
            ATTACK_REASONS[attack_reason_id]]
        vehicle[DAMAGE_LOG.SHELL_TYPE] = settings[DAMAGE_LOG.SHELL_TYPES][shell_type]
        vehicle[DAMAGE_LOG.SHELL_ICON] = settings[DAMAGE_LOG.SHELL_ICONS][shell_icon_name]
        vehicle[DAMAGE_LOG.SHELL_COLOR] = settings[DAMAGE_LOG.SHELL_COLOR][DAMAGE_LOG.SHELL[gold]]
        vehicle[DAMAGE_LOG.TANK_NAME] = DAMAGE_LOG.LIST_SEPARATOR.join(sorted(vehicle[DAMAGE_LOG.TANK_NAMES]))
        percent = float(vehicle[DAMAGE_LOG.TOTAL_DAMAGE]) / vehicle[DAMAGE_LOG.MAX_HEALTH]
        vehicle[DAMAGE_LOG.PERCENT_AVG_COLOR] = percentToRGB(percent, **settings[GLOBAL.AVG_COLOR])
        callback(0.1, lambda: self.updateExtendedLog(log_dict, settings))

    def updateExtendedLog(self, log_dict, settings, altMode=False):
        """
        Final log processing and flash output,
        also works when the alt mode is activated by hot key.
        """
        if log_dict:
            log_name = DAMAGE_LOG.D_LOG if log_dict is self.damage_log else DAMAGE_LOG.IN_LOG
            template = GLOBAL.EMPTY_LINE.join(settings[DAMAGE_LOG.LOG_MODE[int(altMode)]])
            log = log_dict[DAMAGE_LOG.SHOTS]
            if len(log) > DAMAGE_LOG.LOG_MAX_LEN:
                log = log[-DAMAGE_LOG.LOG_MAX_LEN:]
            data = reversed(log) if settings[DAMAGE_LOG.REVERSE] else log
            for vehicleID in log:
                if vehicleID in log_dict[DAMAGE_LOG.KILLS] and not log_dict[vehicleID][DAMAGE_LOG.KILLED_ICON]:
                    log_dict[vehicleID][DAMAGE_LOG.KILLED_ICON] = settings[DAMAGE_LOG.KILLED_ICON]
            self.as_updateLogS(log_name, DAMAGE_LOG.NEW_LINE.join(template % log_dict[key] for key in data))
