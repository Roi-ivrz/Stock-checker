
import schedule
import time

class mainObj():
    def __init__(self):
        pass
    def mainFunc(self):
        print('yeah yeah')

schedule.every().day.at("21:46").do(mainObj().mainFunc())
schedule.every().day.at("21:58").do(mainObj().mainFunc())

while 1:
   schedule.run_pending()
   time.sleep(1)
