import time, os, sys
import yfinance as yf
import dateutil.relativedelta
import datetime
from datetime import date, timedelta
import numpy as np
from getStocklist import NasdaqController
from send_email import send_email
from tqdm import tqdm
from joblib import Parallel, delayed, parallel_backend
import multiprocessing

# how many month to look back
MONTH_CUTOFF = 3
# acceptable range if anomalies are found 
HOUR_CUTOFF = 7
# how many standard deviations away 
STD_CUTOFF = 8



class MainObj:
    def __init__(self):
        pass

    def getData(self, ticker):
        sys.stdout = open(os.devnull, "w")
        data = yf.download(ticker, period='3mo', interval='60m')
        # data = yf.download(ticker, start=pastDate, end=currentDate, interval='60m')
        sys.stdout = sys.__stdout__
        data = data[['Volume']]
        return data
    
    def new_log_found(self):
        with open ('results_log.txt', 'r') as file:
            for line in file:
                if line.__contains__('ticker'):
                    print('contains ticker')
                    return True

    def market_hours(self):
        hour = datetime.datetime.now().strftime('%H')
        weekday = datetime.datetime.now().strftime('%w')
        if hour in range (6, 2):
            if weekday in range (1, 6):
                return True


    def find_anomalies(self, data):
        global STD_CUTOFF
        indexs = []
        outliers = []
        data_stdev = np.std(data['Volume'])
        data_mean = np.mean(data['Volume'])
        anomaly_range = data_stdev * STD_CUTOFF
        upper_bound = data_mean + anomaly_range
        data.reset_index(level=0, inplace=True)

        for i in range (len(data)):
            temp = data['Volume'].iloc[i]
            if temp > upper_bound:
                indexs.append(str(data['Datetime'].iloc[i])[:-9])
                outliers.append(temp)
        d = {'Dates':indexs, 'Volume':outliers}
        return d, upper_bound
    
    def costomPrint(self, d, ticker, upper_bound):
        print('\n****** ticker is: ' + ticker.upper() + ' ******')
        description = 'Upper Bound: {}'.format(int(upper_bound))
        print(description)
        with open('results_log.txt', 'a+') as results:
                results.write('\n\n' + 'ticker: ' + ticker.upper() + ':  ')
                results.write(str(description) + '\n')


        for i in range(len(d['Dates'])):
            str1 = str(d['Dates'][i][:16])
            str2 = str(d['Volume'][i])
            print(str1 + " - " + str2)
            with open('results_log.txt', 'a+') as results:
                results.write(str(d['Dates'][i][:19]) + ', ')
        print("****************************\n")
        
    def hours_between(self, d1, d2):
        date1 = datetime.datetime.strptime(d1[:10], "%Y-%m-%d")
        date2 = datetime.datetime.strptime(d2[:10], "%Y-%m-%d")
        hour1 = datetime.datetime.strptime(d1[11:], "%H:%M")
        hour2 = datetime.datetime.strptime(d2[11:], "%H:%M")
        hour_difference = int((hour1 - hour2).seconds) / 3600
        if hour1 < hour2:
            day_difference = abs((date1 - date2).days - 1)
        else:
            day_difference = abs((date1 - date2).days)
        return round((day_difference*24 + hour_difference), 2)
    
    def parallel_wrapper(self, x, currentDate, positive_scans):
        global HOUR_CUTOFF
        d, upper_bound = (self.find_anomalies(self.getData(x)))
        now = datetime.datetime.now()
        currentTime = now.strftime('%Y-%m-%d %H:%M')
        dateList, volumeList = [], []
        ticker_discovered = False
        if d['Dates']:
            for i in range(len(d['Dates'])):
                if self.hours_between(str(currentTime), str(d['Dates'][i])) <= HOUR_CUTOFF:
                    dateList.append(d['Dates'][i])
                    volumeList.append(d['Volume'][i])
                    stonk = dict()
                    stonk['Ticker'] = x
                    stonk['TargetDate'] = d['Dates'][0]
                    stonk['TargetVolume'] = str(
                        '{:,.2f}'.format(d['Volume'][0]))[:-3]
                    positive_scans.append(stonk)
                    ticker_discovered = True
            if ticker_discovered:
                appendList = dict()
                appendList['Dates'] = dateList
                appendList['Volume'] = volumeList  
                self.costomPrint(appendList, x, upper_bound)

    def main_func(self):
        with open('results_log.txt', 'w') as results:
            results.write('')
        
        stockController = NasdaqController(True)
        ticker_list  = stockController.get_list()
        currentDate = datetime.datetime.strptime(date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
        start_time = time.time()

        manager = multiprocessing.Manager()
        positive_scans = manager.list()
        
        # multiprocessing version
        with parallel_backend('loky', n_jobs=multiprocessing.cpu_count()):
            Parallel()(delayed(self.parallel_wrapper)(ticker, currentDate, positive_scans)
                       for ticker in tqdm(ticker_list))

        print('\n\n------this took %s seconds to run------' %(round((time.time() - start_time), 2)))
        return positive_scans

def iteration():
    if __name__ == '__main__':
        MainObj().main_func()
        currentTime = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        subject = str(currentTime) + '  stocks to watch'
        if MainObj().new_log_found():
            message = ''
            with open ('results_log.txt', 'r+') as file:
                for line in file:
                    message += line

            send_email().send(subject, message)
            print('email sent')
        else:
            print('not sending email, no new log found')


iteration()
'''
import schedule
import time

schedule.every().day.at("22:00").do(iteration)
schedule.every().day.at("22:07").do(iteration)

while 1:
   schedule.run_pending()
   time.sleep(1)
'''