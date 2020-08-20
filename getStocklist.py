from ftplib import FTP
import os
import errno

exportlist = []

class NasdaqController:
    def get_list(self):
        return exportlist

    def __init__(self, update = True):
        self.filenames = {
            'otherlisted': 'data/otherlisted.txt',
            'nasdaqlisted': 'data/nasdaqlisted.txt'
        }

        if update:
            self.ftp = FTP("ftp.nasdaqtrader.com")
            self.ftp.login()
            print("Nasdaq Controller: Welcome message: " + self.ftp.getwelcome())
            self.ftp.cwd('SymbolDirectory')
            
            for filename, filepath in self.filenames.items():
                if not os.path.exists(os.path.dirname(filepath)):
                    try:
                        os.makedirs(os.path.dirname(filepath))
                    except OSError as exc:
                        if exc.errno != errno.EEXIST:
                            raise

                self.ftp.retrbinary("RETR " + filename +
                                    ".txt", open(filepath, 'wb').write)

        all_listed = open('data/allListed.txt', 'w')

        for filename, filepath in self.filenames.items():
            with open(filepath, 'r') as fileReader:
                for i, line in enumerate(fileReader):
                    if i == 0:
                        continue
                    line = line.strip().split('|')

                    if line[0] == '' or line[1] == '' or (filename=='nasdaqlisted' and line[6]=='Y') or (filename == 'otherlisted' and line[4]=='Y'):
                        continue
                    
                    all_listed.write(line[0] + ',')
                    global exportlist
                    exportlist.append(line[0])
                    all_listed.write(line[0] + '|' + line[1] + '\n')


