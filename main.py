import eel
import platform
import os
import sqlite3
import json
import datetime
import paho.mqtt as mqtt

current_os = platform.system()

# Permanent datbase in app.db
conn = sqlite3.connect("app.db")
c = conn.cursor()

# Database on RAM
conn_temp = sqlite3.connect(":memory:")
c_temp = conn_temp.cursor()

# create table in RAM database
with conn_temp:
    c_temp.execute("""
                CREATE TABLE widgets (name TEXT,
                                      broker TEXT,
                                      topic TEXT);
               """)

# directories
cwd = os.getcwd()
static_dir = os.path.join(cwd, "static")
img_dir = os.path.join(static_dir, "imgs")

# imgs
jarvis_icon = os.path.join(img_dir, "jarvis-png-3.png")

# for updating a setting in app.db


@eel.expose
def update_setting(name, value):
    with conn:
        c.execute("UPDATE settings SET name=:name AND value=:value;", {"name": name, "value": value})

# returns a setting from db


@eel.expose
def get_setting(name):
    c.execute("SELECT * FROM settings WHERE name=?;", (name,))
    setting = c.fetchall()[0][2]
    print(setting)
    return setting

# returns a widget from db


@eel.expose
def get_widget(name, wid_type):
    # to add temporary widget
    if wid_type == "temp":
        c_temp.execute("SELECT * FROM widgets WHERE name=?;", (name,))
        return c_temp.fetchall()
    # to add permanent widgets
    else:
        c.execute("SELECT * FROM widgets WHERE name=?;", (name,))
        return c.fetchall()

# adds widget by modifying the db


@eel.expose
def add_widget(wid_type, name, msg, topic, broker):
    exist = get_widget(name=name, wid_type=wid_type)
    print(exist)
    if exist:
        return "Widget already exists!"
    else:
        print("Adding widget!")
        if wid_type == "temp":
            with conn_temp:
                c_temp.execute("INSERT INTO widgets (name, broker,topic) VALUES (:name, :broker, :topic);", {"name": name, "broker": broker, "topic": topic})
                last_id = c_temp.lastrowid
                c_temp.execute("INSERT INTO wid_choices (wid_id, pub, sub) VALUES (:wid_id, :pub, :sub);", {"wid_id": last_id, "pub": 0, "sub": 0})
        else:
            with conn:
                c.execute("INSERT INTO widgets (name, broker,topic) VALUES (:name, :broker, :topic);", {"name": name, "broker": broker, "topic": topic})
                last_id = c.lastrowid
                c.execute("INSERT INTO wid_choices (wid_id, pub, sub) VALUES (:wid_id, :pub, :sub);", {"wid_id": last_id, "pub": 0, "sub": 0})
        return "1"

# for deleting a widget from db


@eel.expose
def delete_widget(name, wid_type):
    print("deleting widget:", name)
    if wid_type == "temp":
        with conn_temp:
            c_temp.execute("DELETE FROM widgets WHERE name=:name;", {"name": name})
    else:
        with conn:
            c.execute("DELETE FROM widgets WHERE name=:name;", {"name": name})

# loading all widgets from db in a dictionary format (js-object on js side)


@eel.expose
def load_widgets(wid_type):
    data = []
    if wid_type == "temp":
        c_temp.execute("SELECT * FROM widgets;")
        res = c_temp.fetchall()
    else:
        c.execute("SELECT * FROM widgets;")
        res = c.fetchall()
    for wid in res:
        d = {
            "type": wid_type,
            "id": wid[0],
            "name": wid[1],
            "broker": wid[2],
            "topic": wid[3]
        }
        data.append(d.copy())
    return data


@eel.expose
def get_pubsub(wid_type, wid_id, table):
    if wid_type == "temp":
        c_temp.execute(f"SELECT * FROM {table} WHERE wid_id=:wid_id;", {"wid_id": wid_id})
        res = c_temp.fetchall()
        return res
    else:
        c.execute(f"SELECT * FROM {table} WHERE wid_id=:wid_id;", {"wid_id": wid_id})
        res = c.fetchall()
        return res


@eel.expose
def toggle_pub(wid_type, wid_id, val=True):
    print("toggling pub!")
    res = get_pubsub(wid_type, wid_id, "pub_vals")
    if wid_type == "temp":
        with conn_temp:
            if res:
                c_temp.execute("UPDATE wid_choices SET pub=:val WHERE wid_id=:wid_id;", {"wid_id": wid_id, "val": val})
            else:
                if val:
                    c_temp.execute("INSERT INTO wid_choices (wid_id, pub, sub) VALUES (:wid_id, :pub, 0);", {"wid_id": wid_id, "pub": val})
                else:
                    return
    else:
        with conn:
            if res:
                c.execute("UPDATE wid_choices SET pub=:val WHERE wid_id=:wid_id", {"wid_id": wid_id, "val": val})
            else:
                if val:
                    c.execute("INSERT INTO wid_choices (wid_id, pub, sub) VALUES (:wid_id, :pub, 0)", {"wid_id": wid_id, "pub": val})
                else:
                    return


@eel.expose
def toggle_sub(wid_type, wid_id, val=True):
    res = get_pubsub(wid_type, wid_id, "sub_vals")
    if wid_type == "temp":
        with conn_temp:
            if res:
                c_temp.execute("UPDATE wid_choices SET sub=:val WHERE wid_id=:wid_id", {"wid_id": wid_id, "val": val})
            else:
                if val:
                    c_temp.execute("INSERT INTO wid_choices (wid_id, pub, sub) VALUES (:wid_id, 0, :sub)", {"wid_id": wid_id, "sub": sub})
                else:
                    return
    else:
        with conn:
            if res:
                c.execute("UPDATE wid_choices SET sub=:val WHERE wid_id=:wid_id", {"wid_id": wid_id, "val": val})
            else:
                if val:
                    c.execute("INSERT INTO wid_choices (wid_id, pub, sub) VALUES (:wid_id, 0,:sub)", {"wid_id": wid_id, "sub": sub})
                else:
                    return


@eel.expose
def create_pub(wid_type, wid_id, type, msg, input_type):
    print("adding pub")
    toggle_pub(wid_type, wid_id, True)
    if wid_type == "temp":
        with conn_temp:
            c_temp.execute("INSERT INTO pub_vals (wid_id, wid_choices_id, type, msg, input_type) VALUES (:wid_id, :wid_choices_id, :type, :msg, :input_type);", {"wid_id": wid_id, "wid_choices_id": wid_id, "type": type, "msg": msg, "input_type": input_type})
    else:
        with conn:
            c.execute("INSERT INTO pub_vals (wid_id, wid_choices_id, type, msg, input_type) VALUES (:wid_id, :wid_choices_id, :type, :msg, :input_type);", {"wid_id": wid_id, "wid_choices_id": wid_id, "type": type, "msg": msg, "input_type": input_type})


@eel.expose
def create_sub(wid_type, wid_id, type, msg, input_type):
    toggle_pub(wid_type, wid_id, True)
    if wid_type == "temp":
        with conn_temp:
            c_temp.execute("INSERT INTO sub_vals (wid_id, wid_choices_id, type) VALUES (:wid_id, :wid_choices_id, :type);", {"wid_id": wid_id, "wid_choices_id": wid_id, "type": type, "msg": msg, "input_type": input_type})
    else:
        with conn:
            c.execute("INSERT INTO sub_vals (wid_id, wid_choices_id, type) VALUES (:wid_id, :wid_choices_id, :type);", {"wid_id": wid_id, "wid_choices_id": wid_id, "type": type, "msg": msg, "input_type": input_type})



    # setup app settings from db
BROKER = get_setting("default-broker")
PORT = str(get_setting("port"))
SIZE = (get_setting("window-width"), get_setting("window-height"))

print(SIZE)

# notify function for linux
if current_os.lower() == "linux":
    import pgi
    pgi.require_version('Notify', '0.7')
    from pgi.repository import Notify
    Notify.init("MQTT-Client")

    @eel.expose
    def notify(msg, head, ul=1, icon_file=jarvis_icon):
        notification = Notify.Notification.new(head,
                                               f"<i>{msg}</i>",
                                               icon_file)
        notification.set_urgency(ul)
        notification.show()

# notify function for windows
elif current_os.lower() == "windows":
    import win10toast as wtt

    toaster = wtt.ToastNotifier()

    @eel.expose
    def notify(msg, head, icon_file=jarvis_icon, ul=1, duration=5):
        toaster.show_toast(head, msg, icon_path=icon_file, threaded=True, duration=duration)

# publish a mqtt message


@eel.expose
def msg_pub(topic, msg, broker=BROKER, port=PORT):
    mqtt.publish.single(topic, hostname=broker, port=port)


if __name__ == "__main__":
    # initialise app on start
    eel.init(static_dir)
    eel.start("index.html", size=SIZE)
    conn.close()
    conn_temp.close()
