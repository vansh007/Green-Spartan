from flask import Flask, render_template, request, Response, stream_with_context

import os

import pandas as pd
import numpy as np
import json
from pandas.core.common import SettingWithCopyWarning
#warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

import sys 
print(sys.version)

# create an instance of Flask

app = Flask(__name__, template_folder='templates')

# to populate country buttons
def list_countries():
	df = pd.read_csv("static/data/data.csv")
	dataset = pd.DataFrame({"country": list(df['country'])})\
		.drop_duplicates()
	countries = dataset['country']
	return countries

def list_decades():
	df = pd.read_csv("static/data/data.csv")
	dataset = pd.DataFrame({"year": np.floor(df['Year'].divide(10)).multiply(10)}) \
		.drop_duplicates()
	year = dataset['year'].sort_values()
	return year

COUNTRY_LIST = list_countries()
DECADE_LIST = list_decades()
DEFAULT_COUNTRY = "United States"
START_YEAR = 2010
END_YEAR = 2020

def get_data(country, start_year, end_year):
	df = pd.read_csv("static/data/data.csv")
	subset = df[df["country"] == country]
	result = subset[(subset["Year"]>start_year-1)&(subset['Year']<end_year+1)]

	# return just year and annual temperatures
	dataset = pd.DataFrame({"date": list(result['Year']), "value": list(result['Annual'])})
	# remove nulls, sort by date and format at JSON
	dataset = dataset.where(pd.notnull(dataset), None).to_json()
	return dataset

@app.route('/')
def home():
	data = get_data(DEFAULT_COUNTRY, START_YEAR, END_YEAR)
	return render_template("visualization.html"
		, countries=COUNTRY_LIST
		, country=DEFAULT_COUNTRY
		, decades=DECADE_LIST
		, startyear=START_YEAR
		, endyear=END_YEAR
		, data=data
	)

@app.route('/visualization', methods = ['POST'])
def Visualization():
	if request.method == 'POST':
		#get form data
		country = request.form['country'] # read the value of the clicked button
		
		start_year = int(request.form.get('startyear', 1840))
		end_year = int(request.form.get('endyear', 1860))
		
		try:
			data = get_data(country, start_year, end_year)
			# re-render the page with new data
			return render_template("visualization.html"
				, countries=COUNTRY_LIST
				, country=country
				, decades=DECADE_LIST
				, startyear = start_year
				, endyear = end_year
				, data=data
			)
		except ValueError:
			pass

if __name__ == '__main__':
	app.run(debug=True, threaded=True)
