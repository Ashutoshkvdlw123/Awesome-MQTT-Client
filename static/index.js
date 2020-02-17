console.log("hello!");

//sets default-broker from python side into the form text box
function set_broker(b) {
    $("#widget-broker").val(b);
    console.log(b);
}

//spawns an alert msg
function spawnAlert(type, alertMsg){
    alert_class = "alert alert-{} alert-dismissible fade show".replace("{}", type)
    alert = "<div class='{0}'>{1}<a class='close' data-dismiss='alert'>&times;</a></div>"
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
    constructor(type, name, topic, broker, sub_type){
        this.type = type;
        this.name = name;
        this.topic = topic;
        this.broker = broker;
        this.sub_type = sub_type;
        console.log(this.sub_type);
    }
    add(){
        if(this.type == "permanent"){
            eel.add_widget("per",
                           this.sub_type,
                           this.name,
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
                           this.sub_type,
                           this.name,
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

//Class for loading widgets from python side
class SysWidPer{
    constructor(Wid){
        this.name = Wid.name;
        this.id = Wid.id;
        this.alias = Math.random().toString(36).slice(2);
        this.elem = document.getElementById(this.alias_name);
        this.topic = Wid.topic;
        this.broker = Wid.broker;
        this.type = Wid.type;
        this.sub_type = Wid.sub_type;
        //this html code block shows a widget from python side
        if (this.type == "per"){
            this.widTag = "<div id='{5}'>\
                            <div class='btn-group row' role='group' aria-label='Basic example' style='margin:10px 20px 10px 20px;'>\
                                <button class='btn btn-success'><i class='fa fa-circle-o'></i></button>\
                                <button class='btn btn-primary {0}'>{3}</button>\
                                <button class='btn btn-primary'>{2}</button>\
                                <button class='btn btn-primary'><i class='fa fa-snowflake-o'> {1}</i></button>\
                                <button class='btn btn-danger delete-{4}'>\
                                    <i class='fa fa-trash'></i>\
                                </button>\
                            </div>\
                        </div>"
                        .replace("{0}", this.alias)
                        .replace("{1}", this.broker)
                        .replace("{3}", this.name)
                        .replace("{4}", this.alias)
                        .replace("{5}", this.alias);
        }else{
            this.widTag = "<div id='{5}'>\
                            <div class='btn-group row' role='group' aria-label='Basic example' style='margin:10px 20px 10px 20px;'>\
                                <button class='btn btn-success'><i class='fa fa-circle'></i></button>\
                                <button class='btn btn-primary {0}'>{3}</button>\
                                <button class='btn btn-primary'>{2}</button>\
                                <button class='btn btn-primary'><i class='fa fa-snowflake-o'> {1}</i></button>\
                                <button class='btn btn-danger delete-{4}'>\
                                    <i class='fa fa-trash'></i>\
                                </button>\
                            </div>\
                        </div>"
                        .replace("{0}", this.alias)
                        .replace("{1}", this.broker)
                        .replace("{3}", this.name)
                        .replace("{4}", this.alias)
                        .replace("{5}", this.alias);
        }

    }display(name, sub_type){
        $("span").remove(".empty-placeholder");
        $(".widgets-area").append(this.widTag.replace("{2}", sub_type));

        $("."+this.alias).click(function(){

            if(sub_type == "Publisher"){
                var raw_title = $("#modal-title-pubsub").html();
                console.log(raw_title);
                var new_title = raw_title.replace("{widget_name}", name);
                $("#modal-title-pubsub").html(new_title);
                console.log(this.sub_type);
                console.log(this.name);
                this.pub_msg = eel.get_pubsub(this.type, this.id, "pub_vals");
                $("#widgetInfoModal-pub #broker-setting-pub").val(this.broker);
                $("#widgetInfoModal-pub #broker-setting-pub").val(this.topic);
                $("#widgetInfoModal-pub #msg-pub").val(this.pub_msg);
                $("#widgetInfoModal-pub").modal("show");

            }if(sub_type == "Subscriber"){
                var raw_title = $("#modal-title-pubsub").html();
                console.log(raw_title);
                var new_title = raw_title.replace("{widget_name}", name);
                $("#modal-title-pubsub").html(new_title);
                console.log(this.sub_type);
                console.log(this.name);
                this.type_notify = eel.get_pubsub(this.type, this.id, "sub_vals");
                $("#widgetInfoModal-sub #broker-setting-sub").val(this.broker);
                $("#widgetInfoModal-sub #broker-setting-sub").val(this.topic);
                $("#widgetInfoModal-sub #notify-type").val(this.type_notify);
                $("#widgetInfoModal-sub").modal("show");
            }

        });

    }delete_on_trash_click(name){
        $(".delete-"+this.alias).click(function(e){
            console.log(name);
            eel.delete_widget(name, this.type)
            window.location.reload();
        });
    }
}

//loads all permanent widgets from python
wids = [];
per_wids = eel.load_widgets("per")(function(pw){
    for(var i = 0; i < pw.length; i++){
        wids[i] = new SysWidPer(pw[i], pw[i].name, pw[i].sub_type);
        console.log(wids[i]);
        wids[i].display(wids[i].name, wids[i].sub_type);
        wids[i].delete_on_trash_click(wids[i].name);
    }
});

wids2 = [];
temp_wids = eel.load_widgets("temp")(function(pw){
    for(var i = 0; i < pw.length; i++){
        wids2[i] = new SysWidPer(pw[i]);
        console.log(wids2[i].widTag);
        console.log(wids2[i].name);
        wids2[i].display(wids2[i].name, wids2[i].sub_type);
        wids2[i].delete_on_trash_click(wids2[i].name);
    }
});


//gets triggered when new widgets are created
function create_widget() {
    vals = [];
    let inputs = ["#widget-type", "#widget-name", "#widget-topic", "#widget-broker", "#widget-sub-type"];
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
    var subTypeWid = vals[4];

    //character-limit for each input
    var char_limit = 30;

    if (nameWid.length > char_limit){
        $("#add-widget-modal").modal("hide");
        spawnAlert("warning", "Your widget name exceeds the name limit of {} characters.".replace("{}", char_limit));
        return
    }else{
        console.log("Adding Widget!");
        var newWid = new Widget(typeWid, nameWid, topicWid, brokerWid, subTypeWid);
        newWid.add();
    }
}

function keyPress(e){
    console.log("modal triggered!");
    e = e || window.event;
    if ((e.which == 71 || e.keyCode == 71) && e.ctrlKey){
        $("#add-widget-modal").modal("show");
    }
}

$("body").keydown(keyPress);
