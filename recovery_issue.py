import qrcode
import serial
import adafruit_thermal_printer
import subprocess
import time
from PIL import Image, ImageDraw
from bitlyshortener import Shortener
import re
from github import Github
import github
import sqlite3
import os

class Printer() :
    def __init__(self,url,title,reponame) :
         ThermalPrinter = adafruit_thermal_printer.get_printer_class(2.69)
         uart = serial.Serial("/dev/ttyS0", baudrate=19200, timeout=3000)
         self._printer = ThermalPrinter(uart)
         self._printer.warm_up()
         tokens_pool = [os.environ['TOKEN_BITLY']]
         shortener = Shortener(tokens=tokens_pool, max_cache_size=8192)
         urls = [url]
         self._urlshort = shortener.shorten_urls(urls)
         self._last = url.rfind('/')
         self._n_issue = url[self._last+1:len(url)]
         qrcode_image = qrcode.make(self._urlshort[0])
         self._qrcode_logo = '/home/pi/qrcode1.png'
         qrcode_image.save(self._qrcode_logo)
         self._title = title
         self._repository = reponame
    def print_receipt(self) :
         if len((self._repository).strip())<15:
             self._printer.size = adafruit_thermal_printer.SIZE_LARGE
             self._printer.justify = adafruit_thermal_printer.JUSTIFY_CENTER
             self._printer.print((self._repository).strip()+' #'+ self._n_issue )
             self._printer.size = adafruit_thermal_printer.SIZE_MEDIUM
             self._printer.justify = adafruit_thermal_printer.JUSTIFY_LEFT
             time.sleep(2)
             if len(self._title) < 75:
                 self._printer.print(self._title)
             else :
                 self._printer.print(self._title[0:74]+'...')
         else :
             self._printer.size = adafruit_thermal_printer.SIZE_LARGE
             self._printer.justify = adafruit_thermal_printer.JUSTIFY_CENTER
             self._printer.print(self._repository[0:14]+'...')
             self._printer.size = adafruit_thermal_printer.SIZE_MEDIUM
             self._printer.justify = adafruit_thermal_printer.JUSTIFY_LEFT
             time.sleep(2)
             if len(self._title) < 75:
                 self._printer.print(self._title)
             else :
                 self._printer.print(self._title[0:74]+'...')
             time.sleep(7)
             self._printer.feed(1)
             self._printer.size = adafruit_thermal_printer.SIZE_MEDIUM
             self._printer.justify = adafruit_thermal_printer.JUSTIFY_CENTER         
             self._printer.print(' #'+self._n_issue )
         time.sleep(5)
         self._printer.feed(1)
         subprocess.run(['lp','-d','thermalprinter', '-o', 'fit-to-page',self._qrcode_logo ])
         self._printer.feed(1)
         time.sleep(7)
         
def recovery_url(url1,title1,reponame1) :
     f=open("url.txt", "r")
     if f.mode == 'r':
         url_recovery =f.read()
     if url1==url_recovery:
         print(url1)
         print('to print')
         printer = Printer(url1,title1,reponame1)
         printer.print_receipt()
     else:
         print('issue not found')  
def select_url():
    g = Github(os.environ['TOKEN_GITHUB'])
    org = g.get_organization(os.environ['NAME_ORGANIZZATION'])
    for repo in org.get_repos():
        all_url = []
        all_title=[]
        reponame = str(repo.name)
        url = repo.issues_url
        url_base = url[0:8]+url[12:22]+url[28:-9]
        for  issue in repo.get_issues():
          if issue.pull_request == None:
                 issue_title=issue.title
                 match2=issue.title
                 all_title.append(match2)
                 match = issue.number
                 all_url.append([url_base+'/'+str(match)])            
        i = 0
        while i < len(all_url) :
             urli = (str(all_url[i]))
             url = urli[2:-2]
             title = (str(all_title[i]))
             recovery_url(url,title,reponame)
             i += 1
