﻿package net.armagomen.battleobserver.utils
{
	
	import flash.display.*;
	import flash.text.*;
	import net.armagomen.battleobserver.utils.tween.Tween;
	
	/**
	 * ...
	 * @author Armagomen
	 */
	public class ProgressBar extends Sprite
	{
		private var bar:Shape            = new Shape();
		private var background:Shape     = new Shape();
		private var outline:Shape        = new Shape();
		private var uiText:TextExt       = null;
		private var animation:Tween      = null;
		private var barColor:uint        = 0;
		private var customColor:Boolean  = false;
		private var animationTime:Number = 1.0;
		
		public function ProgressBar(x:Number, y:Number, width:Number, height:Number, alpha:Number, bgAlpha:Number, filters:Array, color:String, bgColor:String = "#000000", time:Number = 1.0)
		{
			super();
			if (bgColor == null)
			{
				bgColor = "#000000";
			}
			this.animationTime = time;
			this.x = x;
			this.y = y;
			this.barColor = Utils.colorConvert(color);
			this.background.graphics.beginFill(Utils.colorConvert(bgColor), Math.max(0.1, bgAlpha));
			this.background.graphics.drawRect(0, 0, width, height);
			this.background.graphics.endFill();
			this.addChild(this.background);
			this.bar.graphics.beginFill(this.barColor, Math.max(0.1, alpha));
			this.bar.graphics.drawRect(0, 0, width, height);
			this.bar.graphics.endFill();
			if (filters != null)
			{
				this.bar.filters = filters;
			}
			this.addChild(this.bar);
			this.animation = new Tween(this.bar, "scaleX", this.bar.scaleX, 1.0, this.animationTime, true);
		}
		
		public function setNewScale(newScale:Number):void
		{
			if (this.bar.scaleX != newScale)
			{
				var scale:Number = Math.max(0, newScale);
				this.animation.continueTo(scale, this.visible ? this.animationTime : 0.01);
			}
		}
		
		public function setText(text:String):void
		{
			this.uiText.htmlText = text;
		}
		
		public function addTextField(x:Number, y:Number, align:String, format:TextFormat, shdowSettings:Object):void
		{
			this.uiText = new TextExt(x, y, format, align, shdowSettings, this);
		}
		
		public function setOutline(customColor:Boolean = false, color:String = "#000000", alpha:Number = 1.0, width:Number = 0, height:Number = 0):void
		{
			this.customColor = customColor;
			this.outline.graphics.lineStyle(1, customColor ? Utils.colorConvert(color) : this.barColor, Math.max(0.2, alpha), true, LineScaleMode.NONE);
			this.outline.graphics.drawRect(0, 0, width, height);
			this.addChild(this.outline);
		}
		
		public function setVisible(vis:Boolean):void
		{
			var active:Boolean = vis && this.bar.scaleX > 0;
			if (this.visible != active)
			{
				this.visible = active;
			}
		}
		
		public function updateColor(hpColor:String):void
		{
			Utils.updateColor(this.bar, hpColor);
			if (!this.customColor)
			{
				Utils.updateColor(this.outline, hpColor);
			}
		}
		
		public function remove():void
		{
			this.removeChildren();
			this.bar = null;
			this.background = null;
			this.outline = null;
			this.uiText = null;
			this.animation.stop();
			this.animation = null;
		}
	}
}