
from haive import model

def test_can_create():
	assert model.Model() is not None

def test_can_str():
	assert str(model.Model()) is not None