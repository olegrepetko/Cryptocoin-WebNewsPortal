#!env/bin/python
from app import app

app.run(debug=True, port=8080,host='0.0.0.0')