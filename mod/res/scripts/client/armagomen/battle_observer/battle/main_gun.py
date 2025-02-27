from collections import defaultdict
from math import ceil

from armagomen.battle_observer.meta.battle.main_gun_meta import MainGunMeta
from armagomen.constants import MAIN_GUN, GLOBAL, POSTMORTEM
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from gui.battle_control.controllers.battle_field_ctrl import IBattleFieldListener


class MainGun(MainGunMeta, IBattleFieldListener):

    def __init__(self):
        super(MainGun, self).__init__()
        self.macros = defaultdict(lambda: GLOBAL.CONFIG_ERROR)
        self.damage = GLOBAL.ZERO
        self.gunScore = GLOBAL.ZERO
        self.enemiesHP = GLOBAL.ZERO
        self.gunIcons = None
        self.playerDead = False

    def onEnterBattlePage(self):
        super(MainGun, self).onEnterBattlePage()
        feedback = self.sessionProvider.shared.feedback
        if feedback:
            feedback.onPlayerFeedbackReceived += self.__onPlayerFeedbackReceived
        handler = avatar_getter.getInputHandler()
        if handler is not None:
            handler.onCameraChanged += self.onCameraChanged

    def onExitBattlePage(self):
        feedback = self.sessionProvider.shared.feedback
        if feedback:
            feedback.onPlayerFeedbackReceived -= self.__onPlayerFeedbackReceived
        handler = avatar_getter.getInputHandler()
        if handler is not None:
            handler.onCameraChanged += self.onCameraChanged
        super(MainGun, self).onExitBattlePage()

    def _populate(self):
        super(MainGun, self)._populate()
        self.macros.update(mainGunIcon=self.settings[MAIN_GUN.GUN_ICON],
                           mainGunColor=self.colors[MAIN_GUN.NAME][MAIN_GUN.COLOR],
                           mainGunDoneIcon=GLOBAL.EMPTY_LINE, mainGunFailureIcon=GLOBAL.EMPTY_LINE)
        self.gunIcons = {
            True: [self.settings[MAIN_GUN.DONE_ICON], self.settings[MAIN_GUN.FAILURE_ICON]],
            False: [GLOBAL.EMPTY_LINE, GLOBAL.EMPTY_LINE]
        }

    def updateTeamHealth(self, alliesHP, enemiesHP, totalAlliesHP, totalEnemiesHP):
        self.gunScore = max(MAIN_GUN.MIN_GUN_DAMAGE, int(ceil(totalEnemiesHP * MAIN_GUN.DAMAGE_RATE)))
        if not self.playerDead and self.enemiesHP != enemiesHP:
            self.enemiesHP = enemiesHP
            self.updateMainGun()

    def __onPlayerFeedbackReceived(self, events, *a, **kw):
        for event in events:
            if event.getType() == FEEDBACK_EVENT_ID.PLAYER_DAMAGED_HP_ENEMY:
                self.damage += int(event.getExtra().getDamage())
                self.updateMainGun()

    def updateMainGun(self):
        gunLeft = self.gunScore - self.damage
        achieved = gunLeft <= GLOBAL.ZERO
        self.macros[MAIN_GUN.INFO] = GLOBAL.EMPTY_LINE if achieved else gunLeft
        self.macros[MAIN_GUN.DONE_ICON] = self.gunIcons[achieved][GLOBAL.FIRST]
        self.macros[MAIN_GUN.FAILURE_ICON] = self.gunIcons[self.enemiesHP < gunLeft or self.playerDead][GLOBAL.LAST]
        self.as_mainGunTextS(self.settings[MAIN_GUN.TEMPLATE] % self.macros)

    def onCameraChanged(self, ctrlMode, vehicleID=None):
        if ctrlMode in POSTMORTEM.MODES:
            self.playerDead = True
            self.updateMainGun()
