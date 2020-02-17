import sqlite3
import os
import platform
from datetime import datetime

now = datetime.now()
current_os = platform.system()

conn = sqlite3.connect("app.db")
c = conn.cursor()


class Setting(object):
  """docstring for Setting"""

  def __init__(self, name, value):
    super(Setting, self).__init__()
    self.name = name
    self.value = value

  def set(self):
    with conn:
      c.execute("INSERT INTO settings (name, value) VALUES (:name, :value);", {'name': self.name, 'value': self.value})


create_table_settings = """
                CREATE TABLE settings (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                      name TEXT,
                                      value TEXT);
               """

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

if __name__ == "__main__":
  if current_os.lower() == "windows":
    print("Installing win10toast...")
    try:
      os.system("python3 -m pip install win10toast")
    except:
      os.system("python -m pip install win10toast")
    print("win10toast installed!")

  elif current_os.lower() == "linux":
    print("Installing pgi...")
    os.system("python3 -m pip install pgi")
    print("pgi installed!")

  print("Installing other requirements from requirements.txt")
  try:
    os.system("python3 -m pip install -r requirements.txt")
  except:
    os.system("python -m pip install -r requirements.txt")

  print("Done installing requirements.!")

  print("Setting up database...")
  with conn:
    c.execute(create_table_settings)
    c.execute(create_table_widgets)
    c.execute(create_table_pub_vals)
    c.execute(create_table_sub_vals)
  date_installed = Setting("date-installed", now)
  default_broker = Setting("default-broker", "broker.mqttdashboard.com")
  port = Setting("port", "1883")
  window_width = Setting("window-width", "800")
  window_height = Setting("window-height", "600")

  settings = [date_installed, default_broker, port, window_width, window_height]
  for setting in settings:
    setting.set()

  conn.close()
  print("Done installing the application!")
