import eel
import platform
import os
import sqlite3
import paho.mqtt as mqtt

current_os = platform.system()

# Permanent datbase in app.db
conn = sqlite3.connect("app.db")
c = conn.cursor()

# Database on RAM
conn_temp = sqlite3.connect(":memory:")
c_temp = conn_temp.cursor()

create_table_widgets = """
                CREATE TABLE widgets (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                      name TEXT,
                                      sub_type TEXT,
                                      broker TEXT,
                                      topic TEXT);
               """

create_table_pub_vals = """
                CREATE TABLE pub_vals (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                          wid_id INTEGER,
                                          msg TEXT,
                                          FOREIGN KEY(wid_id) REFERENCES widgets(id));
               """
create_table_sub_vals = """
                CREATE TABLE sub_vals (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                          wid_id INTEGER,
                                          type_notify TEXT,
                                          FOREIGN KEY(wid_id) REFERENCES widgets(id));
               """

# create table in RAM database
with conn_temp:
    c_temp.execute(create_table_widgets)
    c_temp.execute(create_table_pub_vals)
    c_temp.execute(create_table_sub_vals)


# directories' path
cwd = os.getcwd()
static_dir = os.path.join(cwd, "static")
img_dir = os.path.join(static_dir, "imgs")

# imgs
jarvis_icon = os.path.join(img_dir, "jarvis-png-3.png")

# updates an entry in the "settings" table


@eel.expose
def update_setting(name, value):
    with conn:
        c.execute("UPDATE settings SET name=:name AND value=:value;", {"name": name, "value": value})

# returns a list of settings from "settings" table using te "name" parameter


@eel.expose
def get_setting(name):
    c.execute("SELECT * FROM settings WHERE name=?;", (name,))
    setting = c.fetchall()[0][2]
    print(setting)
    return setting

# returns a list of widgets from "widgets" table using the "name" parameter


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

# adds an entry to "widgets" table


@eel.expose
def add_widget(wid_type, sub_type, name, topic, broker):
    print(sub_type)
    exist = get_widget(name=name, wid_type=wid_type)
    print(exist)
    if exist:
        return "Widget already exists!"
    else:
        print("Adding widget!")
        if wid_type == "temp":
            with conn_temp:
                c_temp.execute("INSERT INTO widgets (name, sub_type, broker, topic) VALUES (:name, :sub_type, :broker, :topic);",
                               {"name": name, "broker": broker, "topic": topic, "sub_type": sub_type})
        else:
            with conn:
                c.execute("INSERT INTO widgets (name, sub_type, broker, topic) VALUES (:name, :sub_type, :broker, :topic);",
                          {"name": name, 'sub_type': sub_type, "broker": broker, "topic": topic})
        return "1"

# for deleting an entry from the "widgets" table


@eel.expose
def delete_widget(name, wid_type):
    print("deleting widget:", name)
    if wid_type == "temp":
        with conn_temp:
            c_temp.execute("DELETE FROM widgets WHERE name=:name;", {"name": name})
    else:
        with conn:
            c.execute("DELETE FROM widgets WHERE name=:name;", {"name": name})

# loading all widgets from database in a dictionary format form
# interpreted as a js-object on the js side


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
        print(wid)
        d = {
            "type": wid_type,
            "sub_type": wid[2],
            "id": wid[0],
            "name": wid[1],
            "broker": wid[3],
            "topic": wid[4]
        }
        data.append(d.copy())
    return data

# returns a publisher or a subscriber from "wid_choices" table in the form of a list of tuples,
# empty if it does not exist


@eel.expose
def get_pubsub(wid_type, wid_id, table):
    if wid_type == "temp":
        c_temp.execute(f"SELECT * FROM {table} WHERE wid_id=:wid_id;", {"wid_id": wid_id})
        res = c_temp.fetchall()
        print(res)
    else:
        c.execute(f"SELECT * FROM {table} WHERE wid_id=:wid_id;", {"wid_id": wid_id})
        res = c.fetchall()
        print(res)


# Changes publisher settings
# from "pub_vals" table,
# adds a publisher to it if it does not exist
@eel.expose
def update_pub(wid_type, wid_id, msg):
    print("toggling pub!")
    if wid_type == "temp":
        with conn_temp:
            c_temp.execute("UPDATE pub_vals SET msg=:msg WHERE wid_id=:wid_id;", {"wid_id": wid_id, "msg": msg})
    else:
        with conn:
            c.execute("UPDATE pub_vals SET msg=:msg WHERE wid_id=:wid_id", {"wid_id": wid_id, "msg": msg})

# Changes subscriber-notification boolean
# from "sub_vals" table,
# adds a subscriber to it if it does not exist


@eel.expose
def update_sub(wid_type, wid_id, type_notify):
    print("toggling sub!")
    if wid_type == "temp":
        with conn_temp:
            c_temp.execute("UPDATE sub_vals SET type_notify=:type_notify WHERE wid_id=:wid_id;", {"wid_id": wid_id, "type_notify": type_notify})
    else:
        with conn:
            c.execute("UPDATE sub_vals SET type_notify=:type_notify WHERE wid_id=:wid_id", {"wid_id": wid_id, "type_notify": type_notify})

# adds an entry to "pub_vals" table


@eel.expose
def create_pub(wid_type, wid_id, msg):
    if wid_type == "temp":
        c_temp.execute("INSERT INTO pub_vals (wid_id, msg) VALUES (:wid_id :msg);", {"wid_id": wid_id, "msg": msg})
    else:
        c.execute("INSERT INTO pub_vals (wid_id, msg) VALUES (:wid_id :msg);", {"wid_id": wid_id, "msg": msg})


# adds an entry to "sub_vals" table


@eel.expose
def create_sub(wid_type, wid_id, type, msg, input_type):
    if wid_type == "temp":
        c_temp.execute("INSERT INTO sub_vals (wid_id, type_notify) VALUES (:wid_id :type_notify);", {"wid_id": wid_id, "type_notify": type_notify})
    else:
        c.execute("INSERT INTO sub_vals (wid_id, type_notify) VALUES (:wid_id :type_notify);", {"wid_id": wid_id, "type_notify": type_notify})

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
