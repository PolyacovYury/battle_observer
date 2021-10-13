package net.armagomen.battleobserver.battle.components.playerspanels
{
	import flash.display.Sprite;
	import net.armagomen.battleobserver.utils.ProgressBar;
	import net.armagomen.battleobserver.utils.TextExt;
	
	public class ListItem extends Sprite
	{
		private var healthBar:ProgressBar = null;
		private var damage:TextExt        = null;
		private var isEnemy:Boolean       = false;
		private var animation:Boolean     = false;
		private var shadowSettings:Object = null;
		
		public function ListItem(enemy:Boolean, animation:Boolean, shadowSettings:Object)
		{
			super();
			this.name = "battleObserver";
			this.isEnemy = enemy;
			this.animation = animation;
			this.shadowSettings = shadowSettings;
			this.x = enemy ? -381 : 380;
		}
		
		public function updateDamage(text:String):void
		{
			this.damage.htmlText = text;
		}
		
		public function addDamage(params:Object):void
		{
			if (!this.damage)
			{
				var autoSize:String = params.align;
				if (this.isEnemy && autoSize != "center")
				{
					autoSize = params.align == "left" ? "right" : "left";
				}
				this.damage = new TextExt(this.isEnemy ? -params.x : params.x, params.y, null, autoSize, this.shadowSettings, this);
				this.damage.visible = false;
			}
		}
		
		public function addHealth(color:String, colors:Object, settings:Object, startVisible:Boolean):void
		{
			
			var barX:Number     = settings.players_bars_bar.x;
			var barWidth:Number = settings.players_bars_bar.width;
			var textX:Number    = settings.players_bars_text.x;
			var autoSize:String = settings.players_bars_text.align;
			if (this.isEnemy)
			{
				if (autoSize != "center")
				{
					autoSize = settings.players_bars_text.align == "left" ? "right" : "left";
				}
				barWidth = -barWidth;
				barX = -barX;
				textX = -textX;
			}
			this.healthBar = new ProgressBar(this.animation, barX, settings.players_bars_bar.y, barWidth, settings.players_bars_bar.height, colors.alpha, colors.bgAlpha, null, color, colors.bgColor, 0.6);
			if (settings.players_bars_bar.outline.enabled)
			{
				this.healthBar.setOutline(settings.players_bars_bar.outline.customColor, settings.players_bars_bar.outline.color, settings.players_bars_bar.outline.alpha);
			}
			this.healthBar.addTextField(textX, settings.players_bars_text.y, autoSize, null, shadowSettings);
			this.healthBar.setVisible(startVisible);
			this.addChild(this.healthBar);
		}
		
		public function updateHealth(scale:Number, text:String):void
		{
			if (this.healthBar){
				this.healthBar.setNewScale(scale);
				this.healthBar.setText(text);
			}
		}
		
		public function setHealthVisible(vis:Boolean):void
		{
			if (this.healthBar){
				this.healthBar.setVisible(vis);
			}
		}
		
		public function setDamageVisible(vis:Boolean):void
		{
			if (damage.visible != vis)
			{
				this.damage.visible = vis
			}
		}
		
		public function setColor(hpColor:String):void
		{
			this.healthBar.updateColor(hpColor);
		}
		
		public function setDeath():void
		{
			this.alpha = 0.6;
			this.updateHealth(0, "");
			this.setHealthVisible(false);
		}
	}
}