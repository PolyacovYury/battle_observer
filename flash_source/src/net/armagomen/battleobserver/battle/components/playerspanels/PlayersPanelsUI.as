package net.armagomen.battleobserver.battle.components.playerspanels
{
	import flash.events.Event;
	import net.wg.data.constants.generated.PLAYERS_PANEL_STATE;
	import net.armagomen.battleobserver.battle.base.ObserverBattleDisplayable;
	import net.armagomen.battleobserver.battle.components.playerspanels.ListItem;
	import net.wg.gui.battle.components.stats.playersPanel.SpottedIndicator;
	
	public class PlayersPanelsUI extends ObserverBattleDisplayable
	{
		private var playersPanel:* = null;
		private var storage:Object = new Object();
		public var onAddedToStorage:Function;
		public var clear:Function;
		
		public function PlayersPanelsUI(panels:*)
		{
			this.playersPanel = panels;
			super();
		}
		
		public function as_clearStorage():void
		{
			this.clear();
			for each (var item:ListItem in this.storage)
			{
				if (item && item.parent)
				{
					item.removeChildren();
					item.parent.removeChild(item);
				}
			}
			App.utils.data.cleanupDynamicObject(this.storage);
		}
		
		override protected function onPopulate():void
		{
			super.onPopulate();
			this.playersPanel.addEventListener(Event.CHANGE, this.onChange);
		}
		
		override public function setCompVisible(param0:Boolean):void
		{
			super.setCompVisible(param0);
			if (param0)
			{
				var oldMode:int = int(this.playersPanel.state);
				this.playersPanel.as_setPanelMode(PLAYERS_PANEL_STATE.HIDDEN);
				this.playersPanel.as_setPanelMode(PLAYERS_PANEL_STATE.FULL);
				this.playersPanel.as_setPanelMode(oldMode);
				this.playersPanel.parent.updateDamageLogPosition();
			}
		}
		
		override protected function onBeforeDispose():void
		{
			super.onBeforeDispose();
			this.as_clearStorage();
			this.playersPanel.removeEventListener(Event.CHANGE, this.onChange);
			this.playersPanel = null;
		}
		
		private function onChange(eve:Event):void
		{
			this.as_clearStorage();
		}
		
		public function as_AddVehIdToList(vehicleID:int, enemy:Boolean):void
		{
			if (this.storage[vehicleID])
			{
				return;
			}
			var listitem:* = this.getWGListitem(vehicleID, enemy);
			if (listitem && !this.storage[vehicleID])
			{
				this.storage[vehicleID] = new ListItem(enemy, getShadowSettings());
				this.onAddedToStorage(vehicleID, enemy);
				listitem.addChild(this.storage[vehicleID]);
			}
		}
		
		public function as_updateHealthBar(vehicleID:int, scale:Number, text:String):void
		{
			if (this.storage.hasOwnProperty(vehicleID))
			{
				this.storage[vehicleID].updateHealth(scale, text);
			}
		}
		
		public function as_setHealthBarsVisible(vis:Boolean):void
		{
			for each (var item:ListItem in storage)
			{
				item.setHealthVisible(vis);
			}
		}
		
		public function as_addHealthBar(vehicleID:int, color:String, colors:Object, settings:Object, team:String, startVisible:Boolean):void
		{
			if (this.storage.hasOwnProperty(vehicleID))
			{
				this.storage[vehicleID].addHealth(color, colors, settings, startVisible);
			}
		}
		
		public function as_addDamage(vehicleID:int, params:Object):void
		{
			if (this.storage.hasOwnProperty(vehicleID))
			{
				this.storage[vehicleID].addDamage(params);
			}
		}
		
		public function as_updateDamage(vehicleID:int, text:String):void
		{
			if (this.storage.hasOwnProperty(vehicleID))
			{
				this.storage[vehicleID].updateDamage(text);
			}
		}
		
		public function as_setVehicleDead(vehicleID:int):void
		{
			if (this.storage.hasOwnProperty(vehicleID))
			{
				this.storage[vehicleID].setDeath();
			}
		}
		
		public function as_setSpottedPosition(vehicleID:int):void
		{
			var listitem:* = this.getWGListitem(vehicleID, true);
			if (listitem)
			{
				var spottedIndicator:SpottedIndicator = listitem.spottedIndicator;
				spottedIndicator.scaleX = spottedIndicator.scaleY = 1.5;
				spottedIndicator.y = -6;
				spottedIndicator.x = -335;
			}
		}
		
		public function as_colorBlindBars(hpColor:String):void
		{
			if (this.storage)
			{
				for each (var item:ListItem in this.storage)
				{
					if (item.isEnemy)
					{
						item.setColor(hpColor);
					}
				}
			}
		}
		
		public function as_setPlayersDamageVisible(vis:Boolean):void
		{
			if (this.storage)
			{
				for each (var item:ListItem in this.storage)
				{
					item.setDamageVisible(vis);
				}
			}
		}
		
		private function getWGListitem(vehicleID:int, enemy:Boolean):*
		{
			if (playersPanel)
			{
				var list:*   = enemy ? playersPanel.listRight : playersPanel.listLeft;
				var holder:* = list.getHolderByVehicleID(vehicleID);
				if (holder)
				{
					return holder.getListItem();
				}
			}
			return null;
		}
	}
}