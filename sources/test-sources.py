import time
import artcast

def tick():
  value = 0
  while True:
    artcast.send("test/tick", value)
    value += 1
    time.sleep(1.0)

def now():
  import datetime
  while True:
    artcast.send("test/now", datetime.datetime.utcnow().isoformat())
    time.sleep(1.0)

if __name__ == "__main__":
  artcast.add(tick)
  artcast.add(now)
  artcast.run()
