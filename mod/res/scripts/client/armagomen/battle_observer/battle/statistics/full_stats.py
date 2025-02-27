from armagomen.battle_observer.meta.battle.stats_meta import StatsMeta
from armagomen.battle_observer.statistics.statistic_wtr import getStatisticString
from armagomen.constants import STATISTICS
from armagomen.utils.common import callback
from gui.shared import EVENT_BUS_SCOPE, events


class FullStats(StatsMeta):

    def py_getStatisticString(self, accountDBID, isEnemy, clanAbbrev):
        pattern = self.settings[STATISTICS.TAB_RIGHT] if isEnemy else self.settings[STATISTICS.TAB_LEFT]
        if pattern:
            result = getStatisticString(accountDBID, clanAbbrev)
            if result is not None:
                return pattern % result
        return None

    def _populate(self):
        super(FullStats, self)._populate()
        self.addListener(events.GameEvent.FULL_STATS, self.update, scope=EVENT_BUS_SCOPE.BATTLE)

    def _dispose(self):
        self.removeListener(events.GameEvent.FULL_STATS, self.update, scope=EVENT_BUS_SCOPE.BATTLE)

    def update(self, event):
        if event.ctx['isDown']:
            callback(0.1, self.as_updateInfoS)
