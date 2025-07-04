# Stream Icons

These are legacy for some old stream elements projects which streamers may be using. Unlikely but I keep it here just in case.

## Usage

To use a simple wheel spin app in an overlay which can be modified and activated in chat, use the following code in the appropriate place for the overlay item.

Source: <https://github.com/pjonp/pjTestBot/tree/master/modules/.SE_Overlays/chatterWheel>

### Html

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/2.0.2/TweenMax.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/tinycolor/1.4.1/tinycolor.min.js"></script>
<div id="container">
  <canvas id="canvas" width="{{wheelSize}}" height="{{wheelSize}}"></canvas>
  <div id="video-center-piece">
    <video src='{{foregroundVideo}}' autoplay loop />
  </div>
  <div id="frame">
    <div id="spin"></div>
  </div>
  <div id="image-center-piece">
    <image src='{{foregroundImage}}' />
  </div>
</div>
```

### CSS

```css
@import url('https://fonts.googleapis.com/css2?family={{fontNameFD}}&display=swap');
* {
margin: 0;
padding: 0;
}
#container {
  font-family: {{fontNameFD}}, sans-serif;
  opacity: 0;
  position: absolute;
  left: {wheelStartingPositionX}px;
  top: {wheelStartingPositionY}px;
}
#canvas{
 position: relative;
 left: 0px;
 top: 0px;
}
#video-center-piece video{
  position: absolute;
  width: {foregroundVideoSizeFD}%;
}
#image-center-piece img{
  position: absolute;
  width: {foregroundImageSizeFD}%;
  border-radius: {foregroundImageRadiusFD}%;
}
.show {
    animation: fadein 1s forwards;
}
.hide {
    animation: fadeout 1s forwards;
}
@keyframes fadein {
    from {opacity: 0;left: 2000px}
    to {opacity: 1;left: {wheelStartingPositionX}px}
}
@keyframes fadeout {
    from {opacity: 1;left: {wheelStartingPositionX}px}
    to {opacity: 0;left: 2000px}
}

#frame {
    position: absolute;
    mask-position: top left;
      -webkit-mask-position: top left;
      mask-repeat: no-repeat;
      -webkit-mask-repeat: no-repeat;
      mask-size: contain;
      -webkit-mask-size: contain;
}
#spin {
    height: 100%;
    width: 100%;
  background: linear-gradient(90deg, {{firstColor}} 0%, {{secondColor}} 50%);
    animation:spin {{frameDuration}}s linear infinite;
}
@keyframes spin { 100% { -webkit-transform: rotate(360deg); transform:rotate(360deg); }}
```

### JavaScript

```js
/*
NOTE: There are (2) json files for field settings: simple and advanced
      If you are reading this to edit the code; please review the options available with the advanced field settings:
      https://github.com/pjonp/pjTestBot/tree/master/modules/.SE_Overlays/chatterWheel
*/

//Prize Wheel Settings
let wheelBot = 'nexxxbot', //Lowercase name if wanting to use a bot to call commands
  soundEffectVolume = 0.5,
  tickSoundVolume = 0.5, //tick sound volume
  clearDoubleUpAfterSpins = true, //remove the bonus jackpot after spin
  hideWheelAfterSpin = true, //hide the wheel when done spinning; default: true
  doubleUpSeconds = 30 * 60, //seconds or minutes*60
  doubleUpCommand = '!doublegolds', //This command will adjust the size of all segements with the following name:
  doubleUpTarget = 'GOLD', //Which **COLOR** segments are targeted with the command
  doubleUpSizeAdder = 0.5, //size **add on** for the !doubleup command; 1 is default size; so a segment with deaulf size: 0.5 + an adder of 0.5 will grow from 1/2 the normal size to match the other segments
  prizeAddonCommand = 'THIS COMMAND NOT USED !addon', //command to add a prize to the wheel; !addon VIP ROLE
  prizeAddonCommand2 = 'THIS COMMAND NOT USED !addon2', //should start the same as `prizeAddonCommand`, alternate response; same as !addon; e.g. !addon2 1000
  prizeAddonSeconds = 60 * 60, //seconds or minutes*60
  prizeAddonRes = '!s {winner} SubWheel just hit {prize} !', //!addon VIP ROLE -> "pjonp just won VIP ROLE for a month!"
  prizeAddonRes2 = '!s {winner} just hit {prize} 2!', //!addon2 1000 -> "pjonp just won 1000 point!"
  prizeAddonsClearOnCommand = false,
  addonFontSize = 15,
  addonFontFamily = 'Verdana'
  defaultWheelAngle = -5;

/* EXAMPLE PRIZE LIST OBJECT
  {
     text: 'Example' //What is shown on the Wheel
     fillStyle: 'red', //Color of the segment; if empty it is randomized
     fontFamily: 'webdings', //Font style of this segment; if empty use the default in the settings
     fontSize: 20, //Font size of this segment; if empty use the default in the settings
     res: '{winner} wins the Example!', //chat response for this segment. Overrides the default respose if not a Number,
     size: 2, //size factor compared to a default segement. DO NOT OVERRIDE ALL SIZES. 0.5 = half the size of others, 2 = double the size
   };
*/

//THIS IS A STATIC WHEEL EXAMPLE WITH 1 PRIZE SET
//SET TO COMMAND ONLY IN THE OPTIONS

let defaultPrizeList = [
  {
    text: "Fake - Rhino",
    fillStyle: 'red',
    res: '!p Fake - Rhino'
  },
  {
    text: "Menthol - Obsidian",
    fillStyle: 'yellow',
    res: '!p Menthol - Obsidian'
  },

  {
    text: "Menthol - Ultra",
    fillStyle: 'white',
    res: '!p Menthol - Ultra'
  },
  {
    text: "Nose Bleach",
    fillStyle: 'skyblue',
    res: '!p Nose Bleach',
  size: 0.05
  },
  {
    text: "Beast - Strong",
    fillStyle: 'white',
    res: '!p Beast - Strong'
  },
  {
    text: "Beast - Stronger",
    fillStyle: 'green',
    res: '!p Beast - Stronger'
  },
  {
    text: "Beast - Strongest",
    fillStyle: 'white',
    res: '!p Beast - Strongest'
  },
  {
    text: "Pumpkin Spiked Lobotomy",
    fillStyle: 'blue',
    res: '!p Pumpkin Spiked Lobotomy',
  size: 0.10
  },
  {
    text: "Saiyan Salts!",
    fillStyle: 'green',
    res: '!p Saiyan Salts!'
  },
  {
    text: "Saiyan Salts GT",
    fillStyle: 'black',
    res: '!p Saiyan Salts GT',
  size: 0.10
  },
  {
    text: "Basic",
    fillStyle: 'GOLD',
    res: '!p Basic',
  size: 0.10
  },
  {
    text: "Ultra",
    fillStyle: 'black',
    res: '!p Ultra',
  },
  {
    text: "No Frills",
    fillStyle: 'GOLD',
    res: '!p No Frills',
  },
  {
    text: "Irish Carbomb",
    fillStyle: 'black',
    res: '!p Irish Carbomb',
  size: 0.10
  },
];

let prizeLists = [
    [...defaultPrizeList]
  ],
  prizeListThresholds = [0], //0
  wheelGlow = ['black'], //inner glow of the wheel; default wheel: white
  wheelGlowAmount = 0.45, //default wheel 0.5
  //DO NOT EDIT BELOW
  prizeWheelSegements = [],
  prizeAddons = [],
  doubleUp = false,
  doubleUpTimer,
  randomSpins,
  randomTime,
  foregroundImages = [];

const randomInt = (min, max) => Math.floor((Math.random() * (max - min) + min));
let theWheel, channelName, fieldData, cooldown, spins, wheelSize, textSize, wheelSpinning = false,
  goalTrigger = 0,
  gameQueue = [],
  jebaitedAPIToken, sayToChat = true,
  chatResponse, spinCommand, gameOverDelay, tipMultipler, chatResponseDelay,
  soundEffect, pointerAngle, playSound, wheelAngle = defaultWheelAngle,
  videoOffsetX, videoOffsetY, imageOffsetX, imageOffsetY,
  textFontFamily, wheelShowCommand, wheelHideCommand, wheelClearCommand,
  wheelOnScreen = false,
  tickSound = new Audio('https://raw.githubusercontent.com/zarocknz/javascript-winwheel/master/examples/wheel_of_fortune/tick.mp3');

tickSound.volume = tickSoundVolume;

window.addEventListener('onEventReceived', function(obj) {
  //Test Button
  if (obj.detail.event.listener === 'widget-button' && obj.detail.event.field === 'testButton') {
    theWheel = buildWheel();
    $("#container").removeClass("hide").addClass("show");
    wheelOnScreen = true;
    return;
  };
  const skippable = ["bot:counter", "event:test", "event:skip"]; //Array of events coming to widget that are not queued so they can come even queue is on hold
  if (skippable.indexOf(obj.detail.listener) !== -1) return;

  //Broadcaster Commands
  if (obj.detail.listener === "message") {
    let data = obj.detail.event.data;
    if (data.userId === data.tags['room-id'] || data.nick === wheelBot) { //Broadcaster && LOWERCASE name
      if (data.text.startsWith(spinCommand)) {
        let msg = data.text.split(' '),
          user = typeof msg[1] === 'string' ? msg[1].replace('@', '') : 'free_spin',
          amount = parseInt(msg[2]) >= 0 ? parseInt(msg[2]) : prizeListThresholds[0],
          wheelTypeIndex = prizeListThresholds.indexOf(prizeListThresholds.reduce((prev, curr) => amount >= curr ? curr : prev));
        startSpin({
          user: user,
          type: wheelTypeIndex,
          amount: amount
        });
      } else if (data.text === wheelShowCommand) {
        $("#container").removeClass("hide").addClass("show");
        wheelOnScreen = true;
        buildWheel();
      } else if (data.text === wheelHideCommand) {
        $("#container").removeClass("show").addClass("hide");
        wheelOnScreen = false;
      } else if (data.text === wheelClearCommand) {
        if (wheelSpinning) return;
        if (doubleUp) {
          clearTimeout(doubleUpTimer);
          doubleUp = false;
          prizeLists.forEach(i => i.forEach(j => j.fillStyle === doubleUpTarget ? j.size -= doubleUpSizeAdder : null));
        };
        if (prizeAddonsClearOnCommand) {
          prizeAddons = [];
        };
        buildWheel();
      } else if (data.text.startsWith(doubleUpCommand)) {
        if (doubleUp) return;
        doubleUp = true;
        prizeLists.forEach(i => i.forEach(j => j.fillStyle === doubleUpTarget ? !j.size ? j.size = 1 + doubleUpSizeAdder : j.size += doubleUpSizeAdder : null));
        doubleUpTimer = setTimeout(() => {
          doubleUp = false
          prizeLists.forEach(i => i.forEach(j => j.fillStyle === doubleUpTarget ? j.size -= doubleUpSizeAdder : null));
          buildWheel();
        }, doubleUpSeconds * 1000);
        buildWheel();
      } else if (data.text.startsWith(prizeAddonCommand)) {
        let msg = data.text.replace(prizeAddonCommand, '').trim(),
          res = prizeAddonRes.replace('{prize}', msg);
        if (data.text.startsWith(prizeAddonCommand2)) {
          msg = data.text.replace(prizeAddonCommand2, '').trim();
          res = prizeAddonRes2.replace('{prize}', msg);
        };
        let prizeAddon = {
          text: msg,
          fillStyle: '',
          res: res,
          fontSize: addonFontSize,
          fontFamily: addonFontFamily
        };
        prizeAddons.push(prizeAddon);
        setTimeout(() => {
          let addonIndex = prizeAddons.findIndex(i => i.text === msg);
          if (addonIndex !== -1) prizeAddons.splice(addonIndex, 1);
          buildWheel();
        }, prizeAddonSeconds * 1000);
        buildWheel();
      };
    };
    //Look for tips & cheers
  } else if (obj.detail.listener === 'tip-latest' || obj.detail.listener === 'cheer-latest') {
    let tipAmount = obj.detail.event.amount
    if (fieldData.listener === 'chatCommandOnly') {
      return;
    } else if (fieldData.listener === 'tipsAndCheers') { //Not Used
      if (obj.detail.listener === 'cheer-latest') tipAmount *= 0.01;
    } else if (obj.detail.listener !== fieldData.listener) {
      return;
    };
    if (tipAmount < goalTrigger) return;
    let wheelTypeIndex = prizeListThresholds.indexOf(prizeListThresholds.reduce((prev, curr) => tipAmount >= curr ? curr : prev));
    startSpin({
      user: obj.detail.event.name,
      type: wheelTypeIndex,
      amount: tipAmount
    });
  } else return;
});

window.addEventListener('onWidgetLoad', function(obj) {
  channelName = obj["detail"]["channel"]["username"];
  fieldData = obj.detail.fieldData;
  //Get all the field data
  jebaitedAPIToken = fieldData.jebaitedAPITokenFD;
  sayToChat = fieldData.sayToChatFD === 'yes';
  chatResponse = fieldData.chatResponseFD;
  spinCommand = fieldData.spinCommandFD || '!spin';
  wheelShowCommand = fieldData.wheelShowCommandFD || '!showwheel';
  wheelHideCommand = fieldData.wheelHideCommandFD || '!hidewheel';
  wheelClearCommand = fieldData.wheelClearCommandFD || '!clearwheel';

  chatResponseDelay = fieldData.chatResponseDelayFD || 5;

  gameOverDelay = fieldData.gameOverDelayFD || 5;
  textFontFamily = fieldData.fontNameFD;
  videoOffsetX = fieldData.videoOffsetXFD || 1;
  videoOffsetY = fieldData.videoOffsetYFD || 5;
  imageOffsetX = fieldData.imageOffsetXFD || 0;
  imageOffsetY = fieldData.imageOffsetYFD || 0;

  pointerAngle = fieldData.pointerAngleFD || 270;
  //  tipMultipler = fieldData.tipMultiplerFD || 100; //not used
  playSound = fieldData.playSoundFD === 'yes';
  soundEffect = new Audio(fieldData.soundEffectFD || '');

  soundEffect.volume = soundEffectVolume;

  cooldown = fieldData.duration || 20;
  spins = fieldData.spins || 15;
  wheelSize = fieldData.wheelSize || 900;
  textSize = fieldData.textSize;
  goalTrigger = fieldData.minAmountFD || 5;

  prizeListThresholds = prizeListThresholds.map(i => goalTrigger + i);

  if (!jebaitedAPIToken || jebaitedAPIToken === 'need: botMsg') sayToChat = false; //Prevent API call with no token;
  if (!soundEffect) playSound = false; //Prevent audio call with no source;

  theWheel = buildWheel();

  if (fieldData.showWheelOnLoadFD === 'yes') {
    $("#container").css('opacity', '1').addClass("show");
    wheelOnScreen = true;
  };
  if (!fieldData.defaultForegroundImage) fieldData.defaultForegroundImage = fieldData.foregroundImage
  foregroundImages = [fieldData.defaultForegroundImage, fieldData.prizeList1ForegroundImage, fieldData.prizeList2ForegroundImage, fieldData.prizeList3ForegroundImage];
  $("#image-center-piece img").attr('src', foregroundImages[0]);

  let updateCanvas = () => { //Set video/image position
    let canvas = $("#canvas");
    if (!fieldData.foregroundVideo || fieldData.foregroundVideo === 'none') {
      $("#video-center-piece").html('');
    } else {
      $("#video-center-piece video").css('left', `${(canvas.width() - $("#video-center-piece video").width())/2 + videoOffsetX}px`);
      $("#video-center-piece video").css('top', `${(canvas.height() - $("#video-center-piece video").height())/2 + videoOffsetY}px`);
    };
    if (!fieldData.defaultForegroundImage || fieldData.defaultForegroundImage === 'none') {
      $("#image-center-piece").html('');
    } else {
      $("#image-center-piece img").css('left', `${(canvas.width() - $("#image-center-piece img").width())/2 + imageOffsetX}px`);
      $("#image-center-piece img").css('top', `${(canvas.height() - $("#image-center-piece img").height())/2 + imageOffsetY}px`);
    };
  };

  $(() => updateCanvas()); //DOM ready
  setTimeout(() => updateCanvas(), 10000); //force update after loaded for 10 seconds

  //"Animated gradient webcam frame" by Kagrayz
  if (fieldData.mask && fieldData.mask !== 'none') {
    buildGradient(obj.detail.fieldData);
  } else {
    $("#frame").html('');
  };
});

const buildWheel = (prizeListNumber) => {
  if(wheelSpinning) return;
  prizeListNumber = typeof prizeListNumber === 'number' ? prizeListNumber : 0;
  prizeWheelSegements = [...prizeLists[prizeListNumber]],
    addonIndexMultiple = Math.floor((prizeWheelSegements.length + prizeAddons.length) / prizeAddons.length),
    addonIndexCounter = 1;
  if (prizeAddons.length > 0) {
    for (let i = 0; i < prizeAddons.length; i++) {
      prizeWheelSegements.splice(addonIndexMultiple * addonIndexCounter, 0, prizeAddons[i])
      addonIndexCounter++
    };
  };

  if (prizeWheelSegements.length < 0) return;
  let canvas = document.getElementById('canvas'),
    ctx = canvas.getContext('2d'),
    canvasCenter = canvas.height / 2,
    defaultSegSize = prizeWheelSegements.reduce((total, num) => total + (!num.size ? 1 : num.size), 0);

  prizeSegments = prizeWheelSegements.map(i => {
    let radGradient = ctx.createRadialGradient(canvasCenter, canvasCenter, 0, canvasCenter, canvasCenter, wheelSize),
      hexColor = i.fillStyle ? i.fillStyle : i.fillStyle = tinycolor.random().toHexString();
    radGradient.addColorStop(0, wheelGlow[prizeListNumber]);
    radGradient.addColorStop(wheelGlowAmount, i.fillStyle);
    let segementOBJ = {
      text: i.text, //.slice(0,18), //can't shorten names if removing winners
      fillStyle: radGradient,
      textFontFamily: i.fontFamily || textFontFamily,
      textFontSize: i.fontSize || textSize,
      textFillStyle: tinycolor.mostReadable(i.fillStyle, [i.fillStyle], {
        includeFallbackColors: true
      }).toHexString() // white or black
    };
    if (i.size > 0) segementOBJ.size = 360 / defaultSegSize * i.size;
    return segementOBJ;
  })
  //STATIC WHEEL ADDITION
  randomSpins = randomInt((spins - 3), (spins + 4)),
    randomTime = randomInt((cooldown - 3), (cooldown + 4));
  //END STATIC WHEEL ADDITION
  return new Winwheel({
    'outerRadius': wheelSize / 2, // Set outer radius so wheel fits inside the background.
    'textFontSize': textSize, // Set default font size for the segments.
    'textDirection': 'reversed',
    'textAlignment': 'outer', // Align text to outside of wheel.
    'textMargin': 20,
    'numSegments': prizeSegments.length, // Specify number of segments.
    'segments': prizeSegments, // Define segments including colour and text.
    'pointerAngle': pointerAngle,
     rotationAngle: wheelAngle,
    'animation': // Specify the animation to use.
    {
      'type': 'spinToStop',
      'duration': randomTime, //STATIC WHEEL CHANGE
      'spins': randomSpins, //STATIC WHEEL CHANGE
      'easing': 'Power4.easeOut'
    }
  });
};

const startSpin = async (spinObj) => {
  if (wheelSpinning) {
    console.log('SPINNING')
    gameQueue.push(spinObj);
    return;
  } else {
    let wheelType = spinObj.type || 0;
    theWheel = buildWheel(wheelType);
    wheelSpinning = true;
    $('#center-text').html(spinObj.user);
    $("#image-center-piece img").attr('src', foregroundImages[wheelType]);
    $("#container").removeClass("hide").addClass("show");
    theWheel.rotationAngle = wheelAngle;
    theWheel.stopAnimation(false);
    if (playSound) theWheel.animation.callbackSound = playSoundEffect;
    if (!wheelOnScreen) await (async () => new Promise(resolve => setTimeout(resolve, 1200)))();
    wheelOnScreen = true;
    theWheel.startAnimation();
    backgroundSound();
    setTimeout(() => endSpin(spinObj), randomTime * 1000 + 100);
  };
};

const endSpin = (spinObj) => {
  tickSound.pause();
  tickSound.currentTime = 0;
  //get winner and make wheel pretty
  try {
    let winningSegmentNumber = theWheel.getIndicatedSegmentNumber(),
      canvas = document.getElementById('canvas'),
      ctx = canvas.getContext('2d'),
      canvasCenter = canvas.height / 2,
      radGradient = ctx.createRadialGradient(canvasCenter, canvasCenter, 0, canvasCenter, canvasCenter, wheelSize); // x0,y0,r0,x1,y1,r1

    wheelPrize = theWheel.getIndicatedSegment().text;
    radGradient.addColorStop(0, "white");
    radGradient.addColorStop(0.5, "gray");
    for (let i = 1; i < theWheel.segments.length; i++) {
      if (i !== winningSegmentNumber) {
        theWheel.segments[i].fillStyle = radGradient;
        theWheel.segments[i].textFillStyle = 'black';
      };
    }
    theWheel.draw();
  } catch {
    wheelPrize = 'Nothing'
  };

  let segmentIndex = prizeWheelSegements.findIndex(i => i.text === wheelPrize),
    prizeRes = prizeWheelSegements[segmentIndex].res || wheelPrize,
    amountpoints = spinObj.amount * prizeRes,
    chatMessage = isNaN(amountpoints) ? prizeRes.replace('{winner}', spinObj.user).replace('{user}', spinObj.user).replace('{prize}', prizeRes).replace('{amount}', spinObj.amount) : chatResponse.replace('{winner}', spinObj.user).replace('{user}', spinObj.user).replace('{prize}', prizeRes).replace('{amount}', spinObj.amount).replace('{amountpoints}', amountpoints);
  //delay chat response
  setTimeout(() => {
    sayMessage(chatMessage);
  }, chatResponseDelay * 1000);
  //check if done
  setTimeout(() => {
    soundEffect.pause();
    soundEffect.currentTime = 0;
    wheelSpinning = false;
    $('#center-text').html('');
    $("#image-center-piece img").attr('src', foregroundImages[0]);
    if (doubleUp && clearDoubleUpAfterSpins) {
      clearTimeout(doubleUpTimer);
      doubleUp = false;
      prizeLists.forEach(i => i.forEach(j => j.fillStyle === doubleUpTarget ? j.size -= doubleUpSizeAdder : null));
    };
    //check if an addon
    let addonIndex = prizeAddons.findIndex(i => i.text === wheelPrize);
    if (addonIndex !== -1) prizeAddons.splice(addonIndex, 1);

    if (gameQueue.length === 0) {
      console.log('Games Over');
      if (hideWheelAfterSpin) {
        $("#container").removeClass("show").addClass("hide");
        wheelOnScreen = false;
        wheelAngle = defaultWheelAngle;
      };
    } else {
      wheelAngle = parseInt(theWheel.rotationAngle % 360);
      startSpin(gameQueue.shift());
    };
  }, gameOverDelay * 1000);
};

const sayMessage = (message) => {
  console.log(message);
  if (!sayToChat) return;
  if (jebaitedAPIToken.length !== 24) {
    console.log('API Token is not correct')
    return;
  };
  message = encodeURIComponent(message);
  fetch(`https://api.jebaited.net/botMsg/${jebaitedAPIToken}/${message}`)
    .catch(error => {
      console.error(`Error sending message to chat`)
    });
};

const playSoundEffect = () => {
  //  soundEffect.pause();
  tickSound.currentTime = 0;
  tickSound.play();
};

const backgroundSound = () => {
  soundEffect.currentTime = 0;
  soundEffect.play();
};

const buildGradient = (fieldData) => { //"Animated gradient webcam frame" by Kagrayz
  if (fieldData.mask) {
    let maskUrl = fieldData.mask + (fieldData.cacheMask ? '' : '?_nocache=' + new Date().getTime());
    $('#frame')
      .css('width', `${wheelSize+fieldData.gradientOverrideFD}px`)
      .css('height', `${wheelSize+fieldData.gradientOverrideFD}px`)
      .css('left', `${-1*fieldData.gradientOverrideFD/2}px`)
      .css('top', `${-1*fieldData.gradientOverrideFD/2}px`)
      .css('mask-image', 'url(' + maskUrl + ')')
      .css('-webkit-mask-image', 'url(' + maskUrl + ')');
  };
};


    /*
    winWheel.js 2.8.0
    The MIT License (MIT)
    Copyright (c) 2012-2019 Douglas McKechie
    */
    function Winwheel(a,c){defaultOptions={canvasId:"canvas",centerX:null,centerY:null,outerRadius:null,innerRadius:0,numSegments:1,drawMode:"code",rotationAngle:0,textFontFamily:"Arial",textFontSize:20,textFontWeight:"bold",textOrientation:"horizontal",textAlignment:"center",textDirection:"normal",textMargin:null,textFillStyle:"black",textStrokeStyle:null,textLineWidth:1,fillStyle:"silver",strokeStyle:"black",lineWidth:1,clearTheCanvas:!0,imageOverlay:!1,drawText:!0,pointerAngle:0,wheelImage:null,imageDirection:"N",
    responsive:!1,scaleFactor:1};for(var b in defaultOptions)this[b]=null!=a&&"undefined"!==typeof a[b]?a[b]:defaultOptions[b];if(null!=a)for(var d in a)"undefined"===typeof this[d]&&(this[d]=a[d]);this.canvasId?(this.canvas=document.getElementById(this.canvasId))?(null==this.centerX&&(this.centerX=this.canvas.width/2),null==this.centerY&&(this.centerY=this.canvas.height/2),null==this.outerRadius&&(this.outerRadius=this.canvas.width<this.canvas.height?this.canvas.width/2-this.lineWidth:this.canvas.height/
    2-this.lineWidth),this.ctx=this.canvas.getContext("2d")):this.ctx=this.canvas=null:this.ctx=this.canvas=null;this.segments=Array(null);for(b=1;b<=this.numSegments;b++)this.segments[b]=null!=a&&a.segments&&"undefined"!==typeof a.segments[b-1]?new Segment(a.segments[b-1]):new Segment;this.updateSegmentSizes();null===this.textMargin&&(this.textMargin=this.textFontSize/1.7);this.animation=null!=a&&a.animation&&"undefined"!==typeof a.animation?new Animation(a.animation):new Animation;null!=a&&a.pins&&
    "undefined"!==typeof a.pins&&(this.pins=new Pin(a.pins));"image"==this.drawMode||"segmentImage"==this.drawMode?("undefined"===typeof a.fillStyle&&(this.fillStyle=null),"undefined"===typeof a.strokeStyle&&(this.strokeStyle="red"),"undefined"===typeof a.drawText&&(this.drawText=!1),"undefined"===typeof a.lineWidth&&(this.lineWidth=1),"undefined"===typeof c&&(c=!1)):"undefined"===typeof c&&(c=!0);this.pointerGuide=null!=a&&a.pointerGuide&&"undefined"!==typeof a.pointerGuide?new PointerGuide(a.pointerGuide):
    new PointerGuide;this.responsive&&(winwheelToDrawDuringAnimation=this,this._originalCanvasWidth=this.canvas.width,this._originalCanvasHeight=this.canvas.height,this._responsiveScaleHeight=this.canvas.dataset.responsivescaleheight,this._responsiveMinWidth=this.canvas.dataset.responsiveminwidth,this._responsiveMinHeight=this.canvas.dataset.responsiveminheight,this._responsiveMargin=this.canvas.dataset.responsivemargin,window.addEventListener("load",winwheelResize),window.addEventListener("resize",winwheelResize));
    if(1==c)this.draw(this.clearTheCanvas);else if("segmentImage"==this.drawMode)for(winwheelToDrawDuringAnimation=this,winhweelAlreadyDrawn=!1,b=1;b<=this.numSegments;b++)null!==this.segments[b].image&&(this.segments[b].imgData=new Image,this.segments[b].imgData.onload=winwheelLoadedImage,this.segments[b].imgData.src=this.segments[b].image)}
    Winwheel.prototype.updateSegmentSizes=function(){if(this.segments){for(var a=0,c=0,b=1;b<=this.numSegments;b++)null!==this.segments[b].size&&(a+=this.segments[b].size,c++);b=360-a;a=0;0<b&&(a=b/(this.numSegments-c));c=0;for(b=1;b<=this.numSegments;b++)this.segments[b].startAngle=c,c=this.segments[b].size?c+this.segments[b].size:c+a,this.segments[b].endAngle=c}};Winwheel.prototype.clearCanvas=function(){this.ctx&&this.ctx.clearRect(0,0,this.canvas.width,this.canvas.height)};
    Winwheel.prototype.draw=function(a){this.ctx&&("undefined"!==typeof a?1==a&&this.clearCanvas():this.clearCanvas(),"image"==this.drawMode?(this.drawWheelImage(),1==this.drawText&&this.drawSegmentText(),1==this.imageOverlay&&this.drawSegments()):"segmentImage"==this.drawMode?(this.drawSegmentImages(),1==this.drawText&&this.drawSegmentText(),1==this.imageOverlay&&this.drawSegments()):(this.drawSegments(),1==this.drawText&&this.drawSegmentText()),"undefined"!==typeof this.pins&&1==this.pins.visible&&
    this.drawPins(),1==this.pointerGuide.display&&this.drawPointerGuide())};
    Winwheel.prototype.drawPins=function(){if(this.pins&&this.pins.number){var a=this.centerX*this.scaleFactor,c=this.centerY*this.scaleFactor,b=this.outerRadius*this.scaleFactor,d=this.pins.outerRadius,e=this.pins.margin;this.pins.responsive&&(d=this.pins.outerRadius*this.scaleFactor,e=this.pins.margin*this.scaleFactor);for(var t=360/this.pins.number,h=1;h<=this.pins.number;h++)this.ctx.save(),this.ctx.strokeStyle=this.pins.strokeStyle,this.ctx.lineWidth=this.pins.lineWidth,this.ctx.fillStyle=this.pins.fillStyle,
    this.ctx.translate(a,c),this.ctx.rotate(this.degToRad(h*t+this.rotationAngle)),this.ctx.translate(-a,-c),this.ctx.beginPath(),this.ctx.arc(a,c-b+d+e,d,0,2*Math.PI),this.pins.fillStyle&&this.ctx.fill(),this.pins.strokeStyle&&this.ctx.stroke(),this.ctx.restore()}};
    Winwheel.prototype.drawPointerGuide=function(){if(this.ctx){var a=this.centerX*this.scaleFactor,c=this.centerY*this.scaleFactor,b=this.outerRadius*this.scaleFactor;this.ctx.save();this.ctx.translate(a,c);this.ctx.rotate(this.degToRad(this.pointerAngle));this.ctx.translate(-a,-c);this.ctx.strokeStyle=this.pointerGuide.strokeStyle;this.ctx.lineWidth=this.pointerGuide.lineWidth;this.ctx.beginPath();this.ctx.moveTo(a,c);this.ctx.lineTo(a,-(b/4));this.ctx.stroke();this.ctx.restore()}};
    Winwheel.prototype.drawWheelImage=function(){if(null!=this.wheelImage){var a=this.centerX*this.scaleFactor,c=this.centerY*this.scaleFactor,b=this.wheelImage.width*this.scaleFactor,d=this.wheelImage.height*this.scaleFactor,e=a-b/2,t=c-d/2;this.ctx.save();this.ctx.translate(a,c);this.ctx.rotate(this.degToRad(this.rotationAngle));this.ctx.translate(-a,-c);this.ctx.drawImage(this.wheelImage,e,t,b,d);this.ctx.restore()}};
    Winwheel.prototype.drawSegmentImages=function(){if(this.ctx){var a=this.centerX*this.scaleFactor,c=this.centerY*this.scaleFactor;if(this.segments)for(var b=1;b<=this.numSegments;b++){var d=this.segments[b];if(d.imgData.height){var e=d.imgData.width*this.scaleFactor,t=d.imgData.height*this.scaleFactor;var h=null!==d.imageDirection?d.imageDirection:this.imageDirection;if("S"==h){h=a-e/2;var n=c;var r=d.startAngle+180+(d.endAngle-d.startAngle)/2}else"E"==h?(h=a,n=c-t/2,r=d.startAngle+270+(d.endAngle-
    d.startAngle)/2):"W"==h?(h=a-e,n=c-t/2,r=d.startAngle+90+(d.endAngle-d.startAngle)/2):(h=a-e/2,n=c-t,r=d.startAngle+(d.endAngle-d.startAngle)/2);this.ctx.save();this.ctx.translate(a,c);this.ctx.rotate(this.degToRad(this.rotationAngle+r));this.ctx.translate(-a,-c);this.ctx.drawImage(d.imgData,h,n,e,t);this.ctx.restore()}else console.log("Segment "+b+" imgData is not loaded")}}};
    Winwheel.prototype.drawSegments=function(){if(this.ctx&&this.segments)for(var a=this.centerX*this.scaleFactor,c=this.centerY*this.scaleFactor,b=this.innerRadius*this.scaleFactor,d=this.outerRadius*this.scaleFactor,e=1;e<=this.numSegments;e++){var t=this.segments[e];var h=null!==t.fillStyle?t.fillStyle:this.fillStyle;this.ctx.fillStyle=h;var n=null!==t.lineWidth?t.lineWidth:this.lineWidth;this.ctx.lineWidth=n;var r=null!==t.strokeStyle?t.strokeStyle:this.strokeStyle;if((this.ctx.strokeStyle=r)||h){this.ctx.beginPath();
    if(this.innerRadius){var f=Math.cos(this.degToRad(t.startAngle+this.rotationAngle-90))*(b-n/2);n=Math.sin(this.degToRad(t.startAngle+this.rotationAngle-90))*(b-n/2);this.ctx.moveTo(a+f,c+n)}else this.ctx.moveTo(a,c);this.ctx.arc(a,c,d,this.degToRad(t.startAngle+this.rotationAngle-90),this.degToRad(t.endAngle+this.rotationAngle-90),!1);this.innerRadius?this.ctx.arc(a,c,b,this.degToRad(t.endAngle+this.rotationAngle-90),this.degToRad(t.startAngle+this.rotationAngle-90),!0):this.ctx.lineTo(a,c);h&&this.ctx.fill();
    r&&this.ctx.stroke()}}};
    Winwheel.prototype.drawSegmentText=function(){if(this.ctx)for(var a,c,b,d,e,t,h,n,r,f,l=this.centerX*this.scaleFactor,p=this.centerY*this.scaleFactor,w=this.outerRadius*this.scaleFactor,v=this.innerRadius*this.scaleFactor,y=1;y<=this.numSegments;y++){this.ctx.save();var g=this.segments[y];if(g.text){a=null!==g.textFontFamily?g.textFontFamily:this.textFontFamily;c=null!==g.textFontSize?g.textFontSize:this.textFontSize;b=null!==g.textFontWeight?g.textFontWeight:this.textFontWeight;d=null!==g.textOrientation?
    g.textOrientation:this.textOrientation;e=null!==g.textAlignment?g.textAlignment:this.textAlignment;t=null!==g.textDirection?g.textDirection:this.textDirection;h=null!==g.textMargin?g.textMargin:this.textMargin;n=null!==g.textFillStyle?g.textFillStyle:this.textFillStyle;r=null!==g.textStrokeStyle?g.textStrokeStyle:this.textStrokeStyle;f=null!==g.textLineWidth?g.textLineWidth:this.textLineWidth;c*=this.scaleFactor;h*=this.scaleFactor;var m="";null!=b&&(m+=b+" ");null!=c&&(m+=c+"px ");null!=a&&(m+=a);
    this.ctx.font=m;this.ctx.fillStyle=n;this.ctx.strokeStyle=r;this.ctx.lineWidth=f;a=g.text.split("\n");b=-(a.length/2*c)+c/2;"curved"!=d||"inner"!=e&&"outer"!=e||(b=0);for(f=0;f<a.length;f++){if("reversed"==t)if("horizontal"==d)this.ctx.textAlign="inner"==e?"right":"outer"==e?"left":"center",this.ctx.textBaseline="middle",m=this.degToRad(g.endAngle-(g.endAngle-g.startAngle)/2+this.rotationAngle-90-180),this.ctx.save(),this.ctx.translate(l,p),this.ctx.rotate(m),this.ctx.translate(-l,-p),"inner"==e?
    (n&&this.ctx.fillText(a[f],l-v-h,p+b),r&&this.ctx.strokeText(a[f],l-v-h,p+b)):"outer"==e?(n&&this.ctx.fillText(a[f],l-w+h,p+b),r&&this.ctx.strokeText(a[f],l-w+h,p+b)):(n&&this.ctx.fillText(a[f],l-v-(w-v)/2-h,p+b),r&&this.ctx.strokeText(a[f],l-v-(w-v)/2-h,p+b)),this.ctx.restore();else if("vertical"==d){this.ctx.textAlign="center";this.ctx.textBaseline="inner"==e?"top":"outer"==e?"bottom":"middle";m=g.endAngle-(g.endAngle-g.startAngle)/2-180;m+=this.rotationAngle;this.ctx.save();this.ctx.translate(l,
    p);this.ctx.rotate(this.degToRad(m));this.ctx.translate(-l,-p);var k=0;"outer"==e?k=p+w-h:"inner"==e&&(k=p+v+h);m=c-c/9;if("outer"==e)for(var q=a[f].length-1;0<=q;q--){var u=a[f].charAt(q);n&&this.ctx.fillText(u,l+b,k);r&&this.ctx.strokeText(u,l+b,k);k-=m}else if("inner"==e)for(q=0;q<a[f].length;q++)u=a[f].charAt(q),n&&this.ctx.fillText(u,l+b,k),r&&this.ctx.strokeText(u,l+b,k),k+=m;else if("center"==e)for(k=0,1<a[f].length&&(k=m*(a[f].length-1)/2),k=p+v+(w-v)/2+k+h,q=a[f].length-1;0<=q;q--)u=a[f].charAt(q),
    n&&this.ctx.fillText(u,l+b,k),r&&this.ctx.strokeText(u,l+b,k),k-=m;this.ctx.restore()}else{if("curved"==d)for(m=0,"inner"==e?(m=v+h,this.ctx.textBaseline="top"):"outer"==e?(m=w-h,this.ctx.textBaseline="bottom",m-=c*(a.length-1)):"center"==e&&(m=v+h+(w-v)/2,this.ctx.textBaseline="middle"),k=0,1<a[f].length?(this.ctx.textAlign="left",k=c/10*4,k*=100/m,q=g.startAngle+((g.endAngle-g.startAngle)/2-k*a[f].length/2)):(q=g.startAngle+(g.endAngle-g.startAngle)/2,this.ctx.textAlign="center"),q+=this.rotationAngle,
    q-=180,u=a[f].length;0<=u;u--){this.ctx.save();var x=a[f].charAt(u);this.ctx.translate(l,p);this.ctx.rotate(this.degToRad(q));this.ctx.translate(-l,-p);r&&this.ctx.strokeText(x,l,p+m+b);n&&this.ctx.fillText(x,l,p+m+b);q+=k;this.ctx.restore()}}else if("horizontal"==d)this.ctx.textAlign="inner"==e?"left":"outer"==e?"right":"center",this.ctx.textBaseline="middle",m=this.degToRad(g.endAngle-(g.endAngle-g.startAngle)/2+this.rotationAngle-90),this.ctx.save(),this.ctx.translate(l,p),this.ctx.rotate(m),this.ctx.translate(-l,
    -p),"inner"==e?(n&&this.ctx.fillText(a[f],l+v+h,p+b),r&&this.ctx.strokeText(a[f],l+v+h,p+b)):"outer"==e?(n&&this.ctx.fillText(a[f],l+w-h,p+b),r&&this.ctx.strokeText(a[f],l+w-h,p+b)):(n&&this.ctx.fillText(a[f],l+v+(w-v)/2+h,p+b),r&&this.ctx.strokeText(a[f],l+v+(w-v)/2+h,p+b)),this.ctx.restore();else if("vertical"==d){this.ctx.textAlign="center";this.ctx.textBaseline="inner"==e?"bottom":"outer"==e?"top":"middle";m=g.endAngle-(g.endAngle-g.startAngle)/2;m+=this.rotationAngle;this.ctx.save();this.ctx.translate(l,
    p);this.ctx.rotate(this.degToRad(m));this.ctx.translate(-l,-p);k=0;"outer"==e?k=p-w+h:"inner"==e&&(k=p-v-h);m=c-c/9;if("outer"==e)for(q=0;q<a[f].length;q++)u=a[f].charAt(q),n&&this.ctx.fillText(u,l+b,k),r&&this.ctx.strokeText(u,l+b,k),k+=m;else if("inner"==e)for(q=a[f].length-1;0<=q;q--)u=a[f].charAt(q),n&&this.ctx.fillText(u,l+b,k),r&&this.ctx.strokeText(u,l+b,k),k-=m;else if("center"==e)for(k=0,1<a[f].length&&(k=m*(a[f].length-1)/2),k=p-v-(w-v)/2-k-h,q=0;q<a[f].length;q++)u=a[f].charAt(q),n&&this.ctx.fillText(u,
    l+b,k),r&&this.ctx.strokeText(u,l+b,k),k+=m;this.ctx.restore()}else if("curved"==d)for(m=0,"inner"==e?(m=v+h,this.ctx.textBaseline="bottom",m+=c*(a.length-1)):"outer"==e?(m=w-h,this.ctx.textBaseline="top"):"center"==e&&(m=v+h+(w-v)/2,this.ctx.textBaseline="middle"),k=0,1<a[f].length?(this.ctx.textAlign="left",k=c/10*4,k*=100/m,q=g.startAngle+((g.endAngle-g.startAngle)/2-k*a[f].length/2)):(q=g.startAngle+(g.endAngle-g.startAngle)/2,this.ctx.textAlign="center"),q+=this.rotationAngle,u=0;u<a[f].length;u++)this.ctx.save(),
    x=a[f].charAt(u),this.ctx.translate(l,p),this.ctx.rotate(this.degToRad(q)),this.ctx.translate(-l,-p),r&&this.ctx.strokeText(x,l,p-m+b),n&&this.ctx.fillText(x,l,p-m+b),q+=k,this.ctx.restore();b+=c}}this.ctx.restore()}};Winwheel.prototype.degToRad=function(a){return.017453292519943295*a};Winwheel.prototype.setCenter=function(a,c){this.centerX=a;this.centerY=c};
    Winwheel.prototype.addSegment=function(a,c){var b=new Segment(a);this.numSegments++;if("undefined"!==typeof c){for(var d=this.numSegments;d>c;d--)this.segments[d]=this.segments[d-1];this.segments[c]=b;b=c}else this.segments[this.numSegments]=b,b=this.numSegments;this.updateSegmentSizes();return this.segments[b]};
    Winwheel.prototype.setCanvasId=function(a){if(a){if(this.canvasId=a,this.canvas=document.getElementById(this.canvasId))this.ctx=this.canvas.getContext("2d")}else this.canvas=this.ctx=this.canvasId=null};Winwheel.prototype.deleteSegment=function(a){if(1<this.numSegments){if("undefined"!==typeof a)for(;a<this.numSegments;a++)this.segments[a]=this.segments[a+1];this.segments[this.numSegments]=void 0;this.numSegments--;this.updateSegmentSizes()}};
    Winwheel.prototype.windowToCanvas=function(a,c){var b=this.canvas.getBoundingClientRect();return{x:Math.floor(a-this.canvas.width/b.width*b.left),y:Math.floor(c-this.canvas.height/b.height*b.top)}};Winwheel.prototype.getSegmentAt=function(a,c){var b=null,d=this.getSegmentNumberAt(a,c);null!==d&&(b=this.segments[d]);return b};
    Winwheel.prototype.getSegmentNumberAt=function(a,c){var b=this.windowToCanvas(a,c);var d=this.centerX*this.scaleFactor;var e=this.centerY*this.scaleFactor;var t=this.outerRadius*this.scaleFactor,h=this.innerRadius*this.scaleFactor;if(b.x>d){var n=b.x-d;d="R"}else n=d-b.x,d="L";if(b.y>e){var r=b.y-e;e="B"}else r=e-b.y,e="T";var f=180*Math.atan(r/n)/Math.PI;b=0;n=Math.sqrt(r*r+n*n);"T"==e&&"R"==d?b=Math.round(90-f):"B"==e&&"R"==d?b=Math.round(f+90):"B"==e&&"L"==d?b=Math.round(90-f+180):"T"==e&&"L"==
    d&&(b=Math.round(f+270));0!=this.rotationAngle&&(d=this.getRotationPosition(),b-=d,0>b&&(b=360-Math.abs(b)));d=null;for(e=1;e<=this.numSegments;e++)if(b>=this.segments[e].startAngle&&b<=this.segments[e].endAngle&&n>=h&&n<=t){d=e;break}return d};Winwheel.prototype.getIndicatedSegment=function(){var a=this.getIndicatedSegmentNumber();return this.segments[a]};
    Winwheel.prototype.getIndicatedSegmentNumber=function(){var a=0,c=this.getRotationPosition();c=Math.floor(this.pointerAngle-c);0>c&&(c=360-Math.abs(c));for(var b=1;b<this.segments.length;b++)if(c>=this.segments[b].startAngle&&c<=this.segments[b].endAngle){a=b;break}return a};
    Winwheel.prototype.getCurrentPinNumber=function(){var a=0;if(this.pins){var c=this.getRotationPosition();c=Math.floor(this.pointerAngle-c);0>c&&(c=360-Math.abs(c));for(var b=360/this.pins.number,d=0,e=0;e<this.pins.number;e++){if(c>=d&&c<=d+b){a=e;break}d+=b}"clockwise"==this.animation.direction&&(a++,a>this.pins.number&&(a=0))}return a};Winwheel.prototype.getRotationPosition=function(){var a=this.rotationAngle;0<=a?360<a&&(a-=360*Math.floor(a/360)):(-360>a&&(a-=360*Math.ceil(a/360)),a=360+a);return a};
    Winwheel.prototype.startAnimation=function(){if(this.animation){this.computeAnimation();winwheelToDrawDuringAnimation=this;var a=Array(null);a[this.animation.propertyName]=this.animation.propertyValue;a.yoyo=this.animation.yoyo;a.repeat=this.animation.repeat;a.ease=this.animation.easing;a.onUpdate=winwheelAnimationLoop;a.onComplete=winwheelStopAnimation;this.tween=TweenMax.to(this,this.animation.duration,a)}};
    Winwheel.prototype.stopAnimation=function(a){winwheelToDrawDuringAnimation&&(winwheelToDrawDuringAnimation.tween&&winwheelToDrawDuringAnimation.tween.kill(),winwheelStopAnimation(a));winwheelToDrawDuringAnimation=this};Winwheel.prototype.pauseAnimation=function(){this.tween&&this.tween.pause()};Winwheel.prototype.resumeAnimation=function(){this.tween&&this.tween.play()};
    Winwheel.prototype.computeAnimation=function(){this.animation&&("spinOngoing"==this.animation.type?(this.animation.propertyName="rotationAngle",null==this.animation.spins&&(this.animation.spins=5),null==this.animation.repeat&&(this.animation.repeat=-1),null==this.animation.easing&&(this.animation.easing="Linear.easeNone"),null==this.animation.yoyo&&(this.animation.yoyo=!1),this.animation.propertyValue=360*this.animation.spins,"anti-clockwise"==this.animation.direction&&(this.animation.propertyValue=
    0-this.animation.propertyValue)):"spinToStop"==this.animation.type?(this.animation.propertyName="rotationAngle",null==this.animation.spins&&(this.animation.spins=5),null==this.animation.repeat&&(this.animation.repeat=0),null==this.animation.easing&&(this.animation.easing="Power3.easeOut"),this.animation._stopAngle=null==this.animation.stopAngle?Math.floor(359*Math.random()):360-this.animation.stopAngle+this.pointerAngle,null==this.animation.yoyo&&(this.animation.yoyo=!1),this.animation.propertyValue=
    360*this.animation.spins,"anti-clockwise"==this.animation.direction?(this.animation.propertyValue=0-this.animation.propertyValue,this.animation.propertyValue-=360-this.animation._stopAngle):this.animation.propertyValue+=this.animation._stopAngle):"spinAndBack"==this.animation.type&&(this.animation.propertyName="rotationAngle",null==this.animation.spins&&(this.animation.spins=5),null==this.animation.repeat&&(this.animation.repeat=1),null==this.animation.easing&&(this.animation.easing="Power2.easeInOut"),
    null==this.animation.yoyo&&(this.animation.yoyo=!0),this.animation._stopAngle=null==this.animation.stopAngle?0:360-this.animation.stopAngle,this.animation.propertyValue=360*this.animation.spins,"anti-clockwise"==this.animation.direction?(this.animation.propertyValue=0-this.animation.propertyValue,this.animation.propertyValue-=360-this.animation._stopAngle):this.animation.propertyValue+=this.animation._stopAngle))};
    Winwheel.prototype.getRandomForSegment=function(a){var c=0;if(a)if("undefined"!==typeof this.segments[a]){var b=this.segments[a].startAngle;a=this.segments[a].endAngle-b-2;0<a?c=b+1+Math.floor(Math.random()*a):console.log("Segment size is too small to safely get random angle inside it")}else console.log("Segment "+a+" undefined");else console.log("Segment number not specified");return c};
    function Pin(a){var c={visible:!0,number:36,outerRadius:3,fillStyle:"grey",strokeStyle:"black",lineWidth:1,margin:3,responsive:!1},b;for(b in c)this[b]=null!=a&&"undefined"!==typeof a[b]?a[b]:c[b];if(null!=a)for(var d in a)"undefined"===typeof this[d]&&(this[d]=a[d])}
    function Animation(a){var c={type:"spinOngoing",direction:"clockwise",propertyName:null,propertyValue:null,duration:10,yoyo:!1,repeat:null,easing:null,stopAngle:null,spins:null,clearTheCanvas:null,callbackFinished:null,callbackBefore:null,callbackAfter:null,callbackSound:null,soundTrigger:"segment"},b;for(b in c)this[b]=null!=a&&"undefined"!==typeof a[b]?a[b]:c[b];if(null!=a)for(var d in a)"undefined"===typeof this[d]&&(this[d]=a[d])}
    function Segment(a){var c={size:null,text:"",fillStyle:null,strokeStyle:null,lineWidth:null,textFontFamily:null,textFontSize:null,textFontWeight:null,textOrientation:null,textAlignment:null,textDirection:null,textMargin:null,textFillStyle:null,textStrokeStyle:null,textLineWidth:null,image:null,imageDirection:null,imgData:null},b;for(b in c)this[b]=null!=a&&"undefined"!==typeof a[b]?a[b]:c[b];if(null!=a)for(var d in a)"undefined"===typeof this[d]&&(this[d]=a[d]);this.endAngle=this.startAngle=0}
    Segment.prototype.changeImage=function(a,c){this.image=a;this.imgData=null;c&&(this.imageDirection=c);winhweelAlreadyDrawn=!1;this.imgData=new Image;this.imgData.onload=winwheelLoadedImage;this.imgData.src=this.image};function PointerGuide(a){var c={display:!1,strokeStyle:"red",lineWidth:3},b;for(b in c)this[b]=null!=a&&"undefined"!==typeof a[b]?a[b]:c[b]}function winwheelPercentToDegrees(a){var c=0;0<a&&100>=a&&(c=a/100*360);return c}
    function winwheelAnimationLoop(){if(winwheelToDrawDuringAnimation){0!=winwheelToDrawDuringAnimation.animation.clearTheCanvas&&winwheelToDrawDuringAnimation.ctx.clearRect(0,0,winwheelToDrawDuringAnimation.canvas.width,winwheelToDrawDuringAnimation.canvas.height);var a=winwheelToDrawDuringAnimation.animation.callbackBefore,c=winwheelToDrawDuringAnimation.animation.callbackAfter;null!=a&&("function"===typeof a?a():eval(a));winwheelToDrawDuringAnimation.draw(!1);null!=c&&("function"===typeof c?c():eval(c));
    winwheelToDrawDuringAnimation.animation.callbackSound&&winwheelTriggerSound()}}
    function winwheelTriggerSound(){0==winwheelToDrawDuringAnimation.hasOwnProperty("_lastSoundTriggerNumber")&&(winwheelToDrawDuringAnimation._lastSoundTriggerNumber=0);var a=winwheelToDrawDuringAnimation.animation.callbackSound;var c="pin"==winwheelToDrawDuringAnimation.animation.soundTrigger?winwheelToDrawDuringAnimation.getCurrentPinNumber():winwheelToDrawDuringAnimation.getIndicatedSegmentNumber();c!=winwheelToDrawDuringAnimation._lastSoundTriggerNumber&&("function"===typeof a?a():eval(a),winwheelToDrawDuringAnimation._lastSoundTriggerNumber=
    c)}var winwheelToDrawDuringAnimation=null;function winwheelStopAnimation(a){0!=a&&(a=winwheelToDrawDuringAnimation.animation.callbackFinished,null!=a&&("function"===typeof a?a(winwheelToDrawDuringAnimation.getIndicatedSegment()):eval(a)))}var winhweelAlreadyDrawn=!1;
    function winwheelLoadedImage(){if(0==winhweelAlreadyDrawn){for(var a=0,c=1;c<=winwheelToDrawDuringAnimation.numSegments;c++)null!=winwheelToDrawDuringAnimation.segments[c].imgData&&winwheelToDrawDuringAnimation.segments[c].imgData.height&&a++;a==winwheelToDrawDuringAnimation.numSegments&&(winhweelAlreadyDrawn=!0,winwheelToDrawDuringAnimation.draw())}}
    function winwheelResize(){var a=40;"undefined"!==typeof winwheelToDrawDuringAnimation._responsiveMargin&&(a=winwheelToDrawDuringAnimation._responsiveMargin);var c=window.innerWidth-a,b=winwheelToDrawDuringAnimation._responsiveMinWidth;a=winwheelToDrawDuringAnimation._responsiveMinHeight;c<b?c=b:c>winwheelToDrawDuringAnimation._originalCanvasWidth&&(c=winwheelToDrawDuringAnimation._originalCanvasWidth);c/=winwheelToDrawDuringAnimation._originalCanvasWidth;winwheelToDrawDuringAnimation.canvas.width=
    winwheelToDrawDuringAnimation._originalCanvasWidth*c;winwheelToDrawDuringAnimation._responsiveScaleHeight&&(b=winwheelToDrawDuringAnimation._originalCanvasHeight*c,b<a?b=a:b>winwheelToDrawDuringAnimation._originalCanvasHeight&&(b=winwheelToDrawDuringAnimation._originalCanvasHeight),winwheelToDrawDuringAnimation.canvas.height=b);winwheelToDrawDuringAnimation.scaleFactor=c;winwheelToDrawDuringAnimation.draw()};
```

### Fields

(Json Format)

```json
{
  "testButton": {
    "type": "button",
    "label": "LOAD TEST DATA",
    "group": "Testing"
  },
  "showWheelOnLoadFD": {
    "type": "dropdown",
    "label": "Show Wheel On Load",
    "value": "yes",
    "options": {
      "yes": "Yes",
      "no": "No"
    },
    "group": "Testing"
  },
  "showTestDataOnLoadFD": {
    "type": "checkbox",
    "label": "Show Test Data On Load",
    "group": "Testing"
  },
  "spinCommandFD": {
    "type": "text",
    "label": "Broadcaster Spin Command",
    "value": "!spin",
    "group": "Chat Commands"
  },
  "wheelShowCommandFD": {
    "type": "text",
    "label": "Broadcaster Show Wheel Command",
    "value": "!showwheel",
    "group": "Chat Commands"
  },
  "wheelHideCommandFD": {
    "type": "text",
    "label": "Broadcaster Hide Wheel Command",
    "value": "!hidewheel",
    "group": "Chat Commands"
  },
  "wheelClearCommandFD": {
    "type": "text",
    "label": "Broadcaster Clear Wheel Command",
    "value": "!clearwheel",
    "group": "Chat Commands"
  },
  "foregroundVideo": {
    "type": "dropdown",
    "label": "Overlay Video",
    "value": "https://raw.githubusercontent.com/pjonp/pjTestBot/master/modules/.SE_Overlays/chatterWheel/assets/JayniusGamingTV_demo.webm",
    "options": {
      "https://raw.githubusercontent.com/pjonp/pjTestBot/master/modules/.SE_Overlays/chatterWheel/assets/JayniusGamingTV_demo.webm": "Wheel Of Kappa",
      "none": "None"
    },
    "group": "Visual Set Up"
  },
  "foregroundImage": {
    "type": "dropdown",
    "label": "Overlay Image",
    "value": "none",
    "options": {
      "https://github.com/Jonesckevin/Bar_loader_Colored/blob/master/BarBellWeights/StreamIcons/AmmoniaSmellCenter_500px.png?raw=true": "Skeleton Ammonia",
      "none": "None"
    },
    "group": "Visual Set Up"
  },
  "fontNameFD": {
    "type": "googleFont",
    "label": "Select a font:",
    "value": "Open Sans",
    "group": "Visual Set Up"
  },
  "textSize": {
    "type": "number",
    "label": "Text Size",
    "value": 20,
    "max": 100,
    "group": "Visual Set Up"
  },
  "maxChattersFD": {
    "type": "slider",
    "label": "Max Chatters",
    "value": 50,
    "min": 3,
    "max": 100,
    "steps": 1,
    "group": "Visual Set Up"
  },
  "spins": {
    "type": "slider",
    "label": "Spin speed",
    "value": 10,
    "min": 3,
    "max": 50,
    "steps": 1,
    "group": "Visual Set Up"
  },
  "duration": {
    "type": "slider",
    "label": "Duration (s)",
    "value": 10,
    "min": 5,
    "max": 20,
    "steps": 1,
    "group": "Visual Set Up"
  },
  "removeWinnersFD": {
    "type": "dropdown",
    "label": "Ignore Winners From Future Spins",
    "value": "yes",
    "options": {
      "yes": "Yes",
      "no": "No"
    },
    "group": "Game Set Up"
  },
  "ignoredChattersFD": {
    "type": "text",
    "label": "Ignored Chatters (comma separated)",
    "value": "streamelements,commanderroot",
    "group": "Game Set Up"
  },
  "privileges": {
    "type": "dropdown",
    "label": "Who is added",
    "value": "everybody",
    "options": {
      "everybody": "Everybody",
      "subs": "Subs",
      "vips": "VIPS",
      "mods": "Mods"
    },
    "group": "Game Set Up"
  },
  "listener": {
    "type": "dropdown",
    "label": "Trigger Goal Event",
    "value": "tip-latest",
    "options": {
      "tip-latest": "Tips",
      "cheer-latest": "Cheers",
      "chatCommandOnly": "Chat Command Only"
    },
    "group": "Game Set Up"
  },
  "minAmountFD": {
    "type": "number",
    "label": "Goal Amount",
    "step": 1,
    "value": 10,
    "group": "Game Set Up"
  },
  "multipleSpinsFD": {
    "type": "dropdown",
    "label": "Allow Multiple Spins On Large Donations",
    "value": "yes",
    "options": {
      "yes": "Yes",
      "no": "No"
    },
    "group": "Game Set Up"
  },
  "playSoundFD": {
    "type": "dropdown",
    "label": "Play Sound On Ticks",
    "value": "yes",
    "options": {
      "yes": "Yes",
      "no": "No"
    },
    "group": "Game Set Up"
  },
  "soundEffectFD": {
    "type": "sound-input",
    "label": "Sound Effect",
    "value": "https://raw.githubusercontent.com/zarocknz/javascript-winwheel/master/examples/wheel_of_fortune/tick.mp3",
    "group": "Game Set Up"
  },
  "triggerToJoinCommandFDInfo1": {
    "type": "hidden",
    "label": "Require a 'raffle' word to join",
    "group": "Raffle Mode"
  },
  "triggerToJoinCommandFDInfo2": {
    "type": "hidden",
    "label": "e.g. !wheelword join",
    "group": "Raffle Mode"
  },
  "triggerToJoinCommandFD": {
    "type": "text",
    "label": "Command to Enable/Set Raffle Word",
    "value": "!wheelword",
    "group": "Raffle Mode"
  },
  "middleware1": {
    "type": "hidden",
    "label": "Middleware provided by lx",
    "group": "Middleware Setup"
  },
  "jebaitedAPITokenInfoFD": {
    "type": "hidden",
    "label": "https://jebaited.net/tokens/ ->",
    "group": "Middleware Setup"
  },
  "jebaitedAPITokenFD": {
    "type": "text",
    "label": "Token",
    "value": "need: botMsg",
    "group": "Middleware Setup"
  },
  "sayToChatFD": {
    "type": "dropdown",
    "label": "Announce winner to chat",
    "value": "no",
    "options": {
      "yes": "Yes",
      "no": "No"
    },
    "group": "Middleware Setup"
  },
  "chatResponseFD": {
    "type": "text",
    "label": "Chat Winner Text",
    "value": "{chatter} wins! PorscheWIN",
    "group": "Middleware Setup"
  },
  "chatResponseDelayFD": {
    "type": "slider",
    "label": "Chat Response (stream) Delay (s)",
    "value": 5,
    "min": 0,
    "max": 10,
    "steps": 1,
    "group": "Middleware Setup"
  },
  "frame1": {
    "type": "hidden",
    "label": "Animated gradient webcam frame",
    "group": "Animated Gradient Frame"
  },
  "frame2": {
    "type": "hidden",
    "label": "by Kagrayz",
    "group": "Animated Gradient Frame"
  },
  "mask": {
    "type": "dropdown",
    "label": "Mask Image",
    "value": "none",
    "options": {
      "https://raw.githubusercontent.com/pjonp/pjTestBot/master/modules/.SE_Overlays/chatterWheel/assets/demo1.png": "Solid Border",
      "https://raw.githubusercontent.com/pjonp/pjTestBot/master/modules/.SE_Overlays/chatterWheel/assets/demo2.png": "Faded Border",
      "https://raw.githubusercontent.com/pjonp/pjTestBot/master/modules/.SE_Overlays/chatterWheel/assets/demo3.png": "Faded Border With Center Plug",
      "none": "None"
    },
    "group": "Animated Gradient Frame"
  },
  "firstColor": {
    "type": "colorpicker",
    "label": "First color",
    "value": "#00abff",
    "group": "Animated Gradient Frame"
  },
  "secondColor": {
    "type": "colorpicker",
    "label": "Second color",
    "value": "#6701a5",
    "group": "Animated Gradient Frame"
  },
  "frameDuration": {
    "type": "number",
    "label": "Rotating duration, sec",
    "value": 2.5,
    "group": "Animated Gradient Frame"
  },
  "cacheMask": {
    "type": "checkbox",
    "label": "Cache mask",
    "group": "Animated Gradient Frame"
  },
  "gradientOverrideFD": {
    "type": "hidden",
    "value": 40,
    "group": "Animated Gradient Frame"
  },
  "wheelSize": {
    "type": "hidden",
    "value": 900,
    "group": "Animated Gradient Frame"
  },
  "wheelStartingPositionX": {
    "type": "hidden",
    "value": 50,
    "group": "Animated Gradient Frame"
  },
  "wheelStartingPositionY": {
    "type": "hidden",
    "value": 50,
    "group": "Animated Gradient Frame"
  },
  "foregroundVideoSizeFD": {
    "type": "hidden",
    "value": 110,
    "group": "Animated Gradient Frame"
  },
  "foregroundImageSizeFD": {
    "type": "hidden",
    "value": 25,
    "group": "Animated Gradient Frame"
  },
  "foregroundImageRadiusFD": {
    "type": "hidden",
    "value": 50,
    "group": "Animated Gradient Frame"
  }
}
```

### Data

(Json Format)

```json
{
  "eventsLimit": 5,
  "includeFollowers": "yes",
  "includeRedemptions": "yes",
  "includeHosts": "yes",
  "minHost": 1,
  "includeRaids": "yes",
  "minRaid": 1,
  "includeSubs": "yes",
  "includeTips": "yes",
  "minTip": 1,
  "includeCheers": "yes",
  "minCheer": 1,
  "direction": "top",
  "textOrder": "nameFirst",
  "fadeoutTime": 999,
  "fontColor": "rgb(255, 255, 255)",
  "theme": "texture",
  "backgroundOpacity": 50,
  "backgroundColor": "rgba(36, 6, 73, 0.15)",
  "iconColor": "rgb(255, 255, 255, 255)",
  "locale": "en-US",
  "showWheelOnLoadFD": "yes",
  "showTestDataOnLoadFD": true,
  "spinCommandFD": "!spina",
  "wheelShowCommandFD": "!showwheela",
  "wheelHideCommandFD": "!hidewheela",
  "wheelClearCommandFD": "!clearwheel",
  "foregroundVideo": "none",
  "foregroundImage": "https://github.com/Jonesckevin/Bar_loader_Colored/blob/master/BarBellWeights/StreamIcons/AmmoniaSmellCenter_500px.png?raw=true",
  "fontNameFD": "Alegreya SC",
  "textSize": 30,
  "maxChattersFD": 50,
  "spins": 20,
  "duration": 20,
  "removeWinnersFD": "yes",
  "ignoredChattersFD": "streamelements,commanderroot",
  "privileges": "everybody",
  "listener": "chatCommandOnly",
  "minAmountFD": 10,
  "multipleSpinsFD": "yes",
  "playSoundFD": "yes",
  "soundEffectFD": "https://cdn.streamelements.com/uploads/50f35788-66bd-4f2c-8d36-97d4f14eca0c.mp3",
  "triggerToJoinCommandFD": "!wheelword Orange",
  "jebaitedAPITokenFD": "need: botMsg",
  "sayToChatFD": "yes",
  "chatResponseFD": "{chatter} wins! PorscheWIN",
  "chatResponseDelayFD": 9,
  "mask": "https://raw.githubusercontent.com/pjonp/pjTestBot/master/modules/.SE_Overlays/chatterWheel/assets/demo2.png",
  "firstColor": "#ff9f00",
  "secondColor": "#6701a5",
  "frameDuration": 3,
  "gradientOverrideFD": 40,
  "wheelSize": 900,
  "wheelStartingPositionX": 50,
  "wheelStartingPositionY": 50,
  "foregroundVideoSizeFD": 110,
  "foregroundImageSizeFD": 25,
  "foregroundImageRadiusFD": 50,
  "cacheMask": false
}
```