<html>
<head>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
<script type="text/javascript">
$( document ).ready(function() {
    var ws = new WebSocket("ws://" + location.host + "/websocket");
    ws.onopen = function() {
        ws.send("Hello, world");
    };
    ws.onmessage = function (evt) {
        var msg = JSON.parse(evt.data);
        $(".garage1").html(msg.garagedoor.isopen == "1" ? "door open":"door closed");
        $(".garage1").css("background-color", msg.garagedoor.isopen == "1" ? "red":"green");
        $(".garage2").html("irval: "+msg.garagedoor.irval)

        for (var i = 0; i < msg.plugs.length; i++) {
            var of = msg.plugs[i].of;
            var btn = msg.plugs[i].btn;
            var status = msg.plugs[i].status;
            $("#plug"+i)
                .html(of+"<br>"+btn+"<br>"+status)
                .attr("of",of)
                .attr("btn",btn)
                .attr("state",status)
        }

        var daylight = msg.sensors.daylight == "1" ? "daytime" : "nighttime";
        daylight += "<br>for another ";
        daylight += msg.sensors.timeleft
        $("#plug8").html(daylight);
        $("#plug8").css("background-color", msg.sensors.daylight == "1" ? "yellow":"blue");
    };

    $("#btn").click(function() {
        $.ajax({
          url: "/garagedoor",
          method: "PUT",
          data: { value : 1 },
        }).done(function( html ) {
          console.log(html);
        });
    });
    $(".plug").on("click", function(){
        var of = $(this).attr("of");
        var btn = $(this).attr("btn");
        var value = $(this).attr("state") == "on" ? "off":"on" ;
        var url = "/rf433/"+of+"/"+btn;
        $.ajax({
          url: url,
          method: "PUT",
          data: { "value" : value }
        });
    });
});
</script>
<style>
body { width: auto; font-size: 48px; }
/*html { margin: 0 auto; }*/
#btn { cursor: pointer; }
#btn:hover { background-color: gray; }
.container {
  display: grid;
  grid-gap: 5px;
  grid-template-columns: repeat(3, auto);
  grid-template-rows: repeat(10, 220px);
  grid-auto-flow: row;
}

.plug:hover { background-color: gray; }
.container div { background-color: #eee; padding: 20px; border-radius: 5px;}
</style>
</head>
<body>
<div class="container">
    <div class="garage1">1</div>
    <div class="garage2">2</div>
    <div class="garage3"><div id="btn">toggle</div></div>
    <div class="plug" id="plug0">4</div>
    <div class="plug" id="plug1">5</div>
    <div class="plug" id="plug2">6</div>
    <div class="plug" id="plug3">7</div>
    <div class="plug" id="plug4">8</div>
    <div class="plug" id="plug5">9</div>
    <div class="plug" id="plug6">10</div>
    <div class="plug" id="plug7">11</div>
    <div class="plug" id="plug8">day/night</div>
</div>
</body>
</html>