# hAIve
A Hive clone with AI

Run the tests with `python setup.py pytest`

State is stored as {location: token} where location is a 3-tuple and token is a 2-tuple of colour and kind (both strings)

State is stringified into the form 'x,y,z:colour:kind|x,y,z:colour:kind|<etc>'