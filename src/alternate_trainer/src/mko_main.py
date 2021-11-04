import MKO
import json

with open("Tests/test.json", 'r') as file:
    loading = json.load(file)

m = MKO.MKO(loading)
print(m._model.to_json())