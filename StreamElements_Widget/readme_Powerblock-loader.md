# Stream Icons

These are legacy for some old stream elements projects which streamers may be using. Unlikely but I keep it here just in case.

## Usage

To use a simple power block load app in an overlay which can be modified and activated in chat, use the following code in the appropriate place for the overlay item.

### Html

```html
  <section>
            <div class="bar-weight">
<!--                <div id="loadLBS">x lbs</div>
                <div id="loadKG">x kg</div> -->
            </div>

            <div class="bar-img">
                <img class="barbell" id="barbell" src="https://github.com/Jonesckevin/Bar_loader_Colored/blob/master/BarBellWeights/dumbell_powerblock/0.png?raw=true" />
            </div>
 </section>
```

### CSS

```css
body {
  margin: 0px;
  padding: 0px;
}


header {
  padding: 20px;
}

section {
  padding: 20px;
  width: 370px;
  display: flex;
  margin: 1px; 
  /* background-color: blueviolet; */
}

section.form div{
  padding: 10px 20px;
}

footer {
  padding: 10px 20px;

}

div {
  padding: 0px;
  margin: 0px;
}

div div {
  padding: 20px 0px;
}

.bar-weight {
  margin: auto;
  font-size: xx-large;
  font-family: 'Teko', sans-serif;
  /* width: 40%; */
  /* background-color: blue; */
}

img.barbell {
  max-height: 200px;
  /* border: 1px solid #ffffff; */
}

.reveal-if-active {
  opacity: 0;
  max-height: 0;
  overflow: hidden;
  transition: 0.5s;
}

input[type="radio"]:checked ~ .reveal-if-active,
input[type="checkbox"]:checked ~ .reveal-if-active {
    opacity: 1;
    /* max-height: 100px; */
    overflow: visible;
}

.centerCell {
  text-align: center;
}
```

### JavaScript

```js
const imgUrl="https://github.com/Jonesckevin/Bar_loader_Colored/tree/master/BarBellWeights/dumbell_powerblock/";
let cooldown = 0;
let t = setInterval(function () {
    cooldown--;
}, 1000);
function round5(x)
{
    return (x % 5) >= 2.5 ? parseInt(x / 5) * 5 + 5 : parseInt(x / 5) * 5;
}


function updateWeights(weight) {
    var kg = weight / 2.20462;
    document.getElementById("loadKG").innerHTML = Math.round(kg * 10) / 10 + " kg";
    document.getElementById("loadLBS").innerHTML = weight + " lbs";  
}

function updateWeightsKG(weight) {
    var lbs = weight * 2.20462;
    document.getElementById("loadKG").innerHTML = weight + " kg";
    document.getElementById("loadLBS").innerHTML = Math.round(lbs * 10) / 10 + " lbs";  
}

function round25(x)
{
    return 2.5 * Math.ceil(x/2.5);
}



function changeImage(weight,label,collars)
{
    // var howmany = $("input[name='amt']").val();
    //var weight = document.getElementById("weight").value;
    //var units = document.getElementsByName("units");
    //var collars = document.getElementById("kgCollars").checked;

    if(!isNaN(weight)) {
       
        if (label === "lbs") {
            // weight = round5(weight);
            if (weight > 90) {
                weight = 90;
            }
            if (weight < 5) {
                weight = 0;
            }

            document.getElementById("barbell").src = imgUrl + round5(weight) + ".png?raw=true";
            updateWeights(weight);

        } else if (label === "kg") {
            if (!collars) {
                // weight = round25(weight);

                if (weight > 90) {
                    weight = 90;
                }
                if (weight < 5) {
                    weight = 0;
                }

                document.getElementById("barbell").src = imgUrl + round25(weight) + ".png?raw=true";
                updateWeightsKG(weight)

            } else {
                // weight = round25(weight);

                if (weight > 90) {
                    weight = 90;
                }

                if (weight < 5) {
                    weight = 0;
                }

                document.getElementById("barbell").src = imgUrl + round25(weight) + ".png?raw=true";
                updateWeightsKG(weight)
            }
        }
    }
}

function tryMe(arg) {
    document.write(arg);
}


let checkPrivileges = (data) => {
    let required=fieldData.privileges;
    let userState = {
        'mod': parseInt(data.tags.mod),
        'sub': parseInt(data.tags.subscriber),
        'vip': (data.tags.badges.indexOf("vip") !== -1),
        'badges': {
            'broadcaster': (data.userId === data.tags['room-id']),
        }
    };
    if (userState.badges.broadcaster) return true;
    else if (required === "mods" && userState.mod) return true;
    else if (required === "vips" && (userState.mod || userState.vip)) return true;
    else if (required === "subs" && (userState.mod || userState.vip || userState.sub)) return true;
    else if (required === "everybody") return true;
    else return false;
};
window.addEventListener('onEventReceived', function (obj) {
    if (obj.detail.listener !== "message") return;
    let data = obj.detail.event.data;
	let message = data["text"];
  	console.log("Entered",data);
  	if (!message.startsWith(fieldData.command)) return;
  	console.log("Command correct");
    if (!checkPrivileges(data)) {
        return;
    }
  	console.log("Privileges OK");
  	if (cooldown > 0) return;
  	console.log("Cooldown OK");
  	cooldown=fieldData.cooldown;
    
    let words = message.split(" ");
  	if (typeof words[2] ==="undefined") words[2]="kg"
  	if (typeof words[3] ==="undefined" || words[3]!=="no"){
      words[3]=false;
    }
  	else {
   	  words[3]=true; 
  	}
  	console.log(words);
    changeImage(words[1],words[2],words[3]);

});
window.addEventListener('onWidgetLoad', function (obj) {
    fieldData = obj['detail']['fieldData'];
    channelName = obj['detail']['channel']['username'];
});
```

### Fields

(Json Format)

```json
{
  "command": {
    "type": "text",
    "label": "Command",
    "value": "!db"
  },
  "privileges": {
    "type": "dropdown",
    "label": "Who can participate:",
    "value": "Mods",
    "options": {
      "everybody": "Everybody",
      "subs": "Subs",
      "vips": "VIPS",
      "mods": "Mods",
      "broadcaster": "Broadcaster"
    }
  },
  "globalCooldown": {
    "type": "number",
    "label": "Global cooldown (s)",
    "value": 60
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
  "privileges": "mods",
  "globalCooldown": 60,
  "command": "!db"
}
```