import time
import source

def tick():
  value = 0
  while True:
    source.send("test/tick", value)
    value += 1
    time.sleep(1.0)

def now():
  import datetime
  while True:
    source.send("test/now", datetime.datetime.utcnow().isoformat())
    time.sleep(1.0)

if __name__ == "__main__":
  source.add(tick)
  source.add(now)
  source.run()
