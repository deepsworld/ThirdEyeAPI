# extra
from flask import Flask, render_template, jsonify, request
from flask_wtf import FlaskForm as Form
from wtforms import StringField
from wtforms.validators import InputRequired, URL
import re
from string import printable
import traceback

#for importing our keras model
import keras.models
from keras.preprocessing import sequence

#system level operations (like loading files)
import sys 
#for reading operating system data
import os
from load import start


#tell our app where our saved model is
sys.path.append(os.path.abspath("./model"))

#initalize our flask app
app = Flask(__name__)
app.config['SECRET_KEY']= '123'
#global vars for easy reusability
global model, graph

#initialize these variables
model, graph = start()


class LoginForm(Form):
	url = StringField('Enter URL : ', validators=[InputRequired()])


@app.route('/', methods=['GET', 'POST'])
def index():
	form = LoginForm()
	if form.validate_on_submit():

		url = form.url.data

		l = re.compile(r"https?://(www\.)?")
		urls = [l.sub('', url).strip().strip('/')]

		# convert url to tokens
		url_int_tokens = [[printable.index(x) + 1 for x in url if x in printable] for url in urls]

		# Step 2: Cut URL string at max_len or pad with zeros if shorter
		max_len = 400

		X = sequence.pad_sequences(url_int_tokens, maxlen=max_len, padding='post')
		with graph.as_default():
			prediction = model.predict(X)
			if prediction[0] > 0.50:
				# prediction = "MALICIOUS"
				return render_template("success.html", url=form.url.data, status="Malicious", value = prediction[0])
			else:
				# prediction = "NOT MALICIOUS"
				return render_template("success.html", url=form.url.data, status="Not Malicious", value = prediction[0])

	# return render_template('success.html', url = form.url.data, prediction = prediction)
	return render_template('index.html', form=form)


@app.route('/home')
def hello():
	return "Why here bro?"


@app.route('/predict', methods=['GET', 'POST'])
def predict():
	if model:
		try:
			json_ = request.json

			url = json_[0]['url']
			l = re.compile(r"https?://(www\.)?")
			urls = [l.sub('', url).strip().strip('/')]
			print(url)

			# convert url to tokens
			url_int_tokens = [[printable.index(x) + 1 for x in url if x in printable ] for url in urls]
			print(url_int_tokens)
            
			# Step 2: Cut URL string at max_len or pad with zeros if shorter
			max_len = 400

			query = sequence.pad_sequences(url_int_tokens, maxlen=max_len, padding='post', truncating='post')

			with graph.as_default():
				prediction = model.predict(query)
				print(prediction[0])
				pred_proba = model.predict_proba(query)
				print(pred_proba)
				if prediction[0] > 0.50:
					return jsonify('bad:' + str(pred_proba[0]))
				else:
					return jsonify('good:' + str(pred_proba[0]))
		except:
			return jsonify({'trace': traceback.format_exc()})
	else:
		print('Train the model first')
		return ('No model here to use')


if __name__ == "__main__":

	#decide what port to run the app in
	port = int(os.environ.get('PORT', 5000))
	#run the app locally on the givn port
	app.run(host='0.0.0.0', port=port)
	#optional if we want to run in debugging mode
	#app.run(debug=True)
