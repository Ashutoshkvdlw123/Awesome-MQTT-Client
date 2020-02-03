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
        this.msg = Wid.msg;
        this.topic = Wid.topic;
        this.broker = Wid.broker;
        this.widTag = "<div class=''>\
                            <div class='btn-group row' role='group' aria-label='Basic example' style='margin:10px 20px 10px 20px;'>\
                                <button class='btn btn-success'><i class='fa fa-circle-o'></i></button>\
                                <button class='btn btn-primary'>{0}</button>\
                                <button class='btn btn-primary'><i class='fa fa-snowflake-o'> {1}</i></button>\
                                <button class='btn btn-primary'><i class='fa fa-envelope'></i> {2}</button>\
                                <button class='btn btn-secondary delete-{3}'>\
                                    <i class='fa fa-trash'></i>\
                                </button>\
                            </div>\
                        </div>"//this html code block shows a widget from python side
                        .replace("{0}", this.name).replace("{1}", this.broker).
                        replace("{2}", this.msg).replace("{3}", this.name);
    }
    display(){
        $("span").remove(".empty-placeholder");
        $(".widgets-area").append(this.widTag);
    }
}

//loads all permanent widgets from python
per_wids = eel.load_widgets("per")(function(pw){
    for(var i = 0; i < pw.length; i++){
        wid = new SysWidPer(pw[i]);
        console.log(wid.widTag);
        wid.display();
    }
});

var newWid;

//gets triggered when new widgets are created
function create_widget() {
    console.log("Adding widget...")
    var typeWid = $("#widget-type").val();
    var nameWid = $("#widget-name").val();
    var topicWid = $("#widget-topic").val();
    var brokerWid = $("#widget-broker").val();
    var msgWid = $("#widget-msg").val();

    var newWid = new Widget(typeWid, nameWid, topicWid, brokerWid, msgWid);
    newWid.add();
}
