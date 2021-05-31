import requests # request the data in the api from (https://www.worldometers.info/coronavirus/)
import json # import JavaScript Object Notation to parse data from the server to our api
import pyttsx3 # import text to speech lib --> https://pypi.org/project/pyttsx3/
import speech_recognition as sr 
import re #import regx(regular expression) https://docs.python.org/3/library/re.html
import threading 
import time

# Api passkey
API_KEY = "t6aGcvs6znYT"
PROJECT_TOKEN = "tu_P6BDsauDr"
RUN_TOKEN = "tbSPf_TEPnwK"


class Data: # creating a class for the whole project to use
	def __init__(self, api_key, project_token): # return data from the api 
		self.api_key = api_key
		self.project_token = project_token
		self.params = {
			"api_key": self.api_key
		}
		self.data = self.get_data()

	def get_data(self): # return the data from the api 
		response = requests.get(f'https://www.parsehub.com/api/v2/projects/{PROJECT_TOKEN}/last_ready_run/data', params={"api_key": API_KEY})
		data = json.loads(response.text)
		return data

	def get_total_cases(self): # return total cases 
		data = self.data['total']

		for content in data:
			if content['name'] == "Coronavirus Cases:":
				return content['value']

	def get_total_deaths(self): # return total deaths 
		data = self.data['total']

		for content in data:
			if content['name'] == "Deaths":
				return content['value']

		return "0"

	def get_country_data(self, country): # return data from a specific country
		data = self.data['country']

		for content in data:
			if content['name'].lower() == country.lower():
				return content

		return "0"

	def get_list_of_countries(self): # return a list of countries that are affected by covid 19
		countries = []
		for country in self.data['country']:
			countries.append(country['name'].lower())

		return countries

	def update_data(self): #live updating the data of covid19 
		response = requests.post(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/run', params=self.params)

		def poll():
			time.sleep(0.1)
			old_data = self.data
			while True:
				new_data = self.get_data()
				if new_data != old_data:
					self.data = new_data
					print("Data updated...")
					break
				time.sleep(5)

		t = threading.Thread(target=poll)
		t.start()

def speak(text):
	engine = pyttsx3.init()
	engine.say(text)
	engine.runAndWait()
#speak("hello") test audio 

def get_audio():
	r = sr.Recognizer()
	with sr.Microphone() as source:
		audio = r.listen(source)
		said = ""

		try:
			said = r.recognize_google(audio)
		except Exception as e:
			print("speak again....", str(e))

	return said.lower()
#print(get_audio()) test recording 

def main():
	print("Started Program")
	data1 = Data(API_KEY, PROJECT_TOKEN)
	END_PHRASE = "stop"
	country_list = set(data1.get_list_of_countries())

	TOTAL_PATTERNS = {
					re.compile("[\w\s]+ total [\w\s]+ cases"):data1.get_total_cases,
					re.compile("[\w\s]+ total cases"): data1.get_total_cases,
                    re.compile("[\w\s]+ total [\w\s]+ deaths"): data1.get_total_deaths,
                    re.compile("[\w\s]+ total deaths"): data1.get_total_deaths
					}
	COUNTRY_PATTERNS = {
					re.compile("[\w\s]+ cases [\w\s]+"): lambda country: data1.get_country_data(country)['total_cases'],
                    re.compile("[\w\s]+ deaths [\w\s]+"): lambda country: data1.get_country_data(country)['total_deaths'],
					}
	UPDATE_COMMAND = "update"

	while True:
		print("Listening.....")
		text = get_audio()
		print(text)
		result = None

		for pattern, func in COUNTRY_PATTERNS.items():
			if pattern.match(text):
				words = set(text.split(" "))
				for country in country_list:
					if country in words:
						result = func(country)
						break

		for pattern, func in TOTAL_PATTERNS.items():
			if pattern.match(text):
				result = func()
				break
		if text == UPDATE_COMMAND:
			result = "Data is being updated. This may take a moment"
			data1.update_data()
		if result:
			speak(result)

		if text.find(END_PHRASE) != -1: # stop loop
			break

main()
