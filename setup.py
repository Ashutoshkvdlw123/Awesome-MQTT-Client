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
      c.execute("INSERT INTO settings VALUES (:name, :value);", {'name': self.name, 'value': self.value})


create_table_settings = """
                CREATE TABLE settings (name TEXT,
                                       value TEXT);
               """

create_table_widgets = """
                CREATE TABLE widgets (name TEXT,
                                      broker TEXT,
                                      topic TEXT);
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
