console.log("hello!");

//sets default-broker from python side into the form text box
function set_broker(b) {
    $("#widget-broker").val(b);
    console.log(b);
}

//spawns an alert msg
function spawnAlert(type, alertMsg){
    alert_class = "alert alert-{} alert-dismissible fade show".replace("{}", type)
    alert = "<div class='{0}'>{1}<button type='button' data-dismiss='alert' aria-label='Close'><span aria-hidden='true'>&times;</span></button></div>"
    .replace("{0}", alert_class)
    .replace("{1}", alertMsg);
    console.log(alert_class)
    $(".alerts").append(alert)
                .attr("role", "alert");
}

//set default broker from database
eel.get_setting("default-broker")(set_broker);

//widget class for new widget created by user
class Widget {
    constructor(type, name, topic, broker, msg){
        this.type = type;
        this.name = name;
        this.topic = topic;
        this.broker = broker;
        this.msg = msg;
    }
    add(){
        if(this.type == "permanent"){
            eel.add_widget("per",
                           this.name,
                           this.msg,
                           this.topic,
                           this.broker)(function(s){
                            if (s == "1"){
                                $("#add-widget-modal").modal("hide");
                                window.location.reload(true);
                                spawnAlert("success", "Widget successfully added");
                            }else{
                                $("#add-widget-modal").modal("hide");
                                spawnAlert("danger", s);
                            }
                           });

        }if(this.type == "temporary"){
            eel.add_widget("temp",
                           this.name,
                           this.msg,
                           this.topic,
                           this.broker)(function(s){
                            if (s == "1"){
                                $("#add-widget-modal").modal("hide");
                                window.location.reload(true);
                                spawnAlert("success", "Widget successfully added");
                            }else{
                                $("#add-widget-modal").modal("hide");
                                spawnAlert("danger", s);
                            }
                           });
    }
    }
}

//Class for loading permanent widget from python side
class SysWidPer{
    constructor(Wid){
        this.name = Wid.name;
        this.alias = Math.random().toString(36).slice(2);
        this.elem = document.getElementById(this.alias_name);
        this.msg = Wid.msg;
        this.topic = Wid.topic;
        this.broker = Wid.broker;
        //this html code block shows a widget from python side
        this.widTag = "<div id='{5}'>\
                            <div class='btn-group row {0}' role='group' aria-label='Basic example' style='margin:10px 20px 10px 20px;'>\
                                <button class='btn btn-success'><i class='fa fa-circle-o'></i></button>\
                                <button class='btn btn-primary'>{3}</button>\
                                <button class='btn btn-primary'><i class='fa fa-snowflake-o'> {1}</i></button>\
                                <button class='btn btn-primary'><i class='fa fa-envelope'></i> {2}</button>\
                                <button class='btn btn-secondary delete-{4}'>\
                                    <i class='fa fa-trash'></i>\
                                </button>\
                            </div>\
                        </div>".replace("{0}", this.alias).replace("{1}", this.broker).
                        replace("{2}", this.msg).replace("{3}", this.name).replace("{4}", this.alias)
                        .replace("{5}", this.alias);
    }display(){
        $("span").remove(".empty-placeholder");
        $(".widgets-area").append(this.widTag);

    }delete_on_trash_click(name){
        $(".delete-"+this.alias).click(function(e){
            console.log(this.name);
            eel.delete_widget(name, "per");
            window.location.reload(true);
        });
    }
}

//loads all permanent widgets from python
per_wids = eel.load_widgets("per")(function(pw){
    for(var i = 0; i < pw.length; i++){
        wid = new SysWidPer(pw[i]);
        console.log(wid.widTag);
        console.log(wid.name)
        wid.display();
        wid.delete_on_trash_click(wid.name);
    }
});

var newWid;
var inputs = ["#widget-type", "#widget-name", "#widget-topic", "#widget-broker", "#widget-msg"];

//gets triggered when new widgets are created
function create_widget() {
    vals = [];
    console.log("Adding widget...");
    for(i = 0; i < inputs.length; i++){
        var val = $(inputs[i]).val();
        if (val.length > 1){
            vals.push(val);
        }else{
            $("#add-widget-modal").modal("hide");
            spawnAlert("warning", "Something is wrong with your info! Please try again.")
            return
        }
    }
    var typeWid = vals[0];
    var nameWid = vals[1];
    var topicWid = vals[2];
    var brokerWid = vals[3];
    var msgWid = vals[4];

    console.log("Adding Widget!");
    var newWid = new Widget(typeWid, nameWid, topicWid, brokerWid, msgWid);
    newWid.add();
}
