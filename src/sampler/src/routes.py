import os, random, string
from flask import Blueprint, Response
from flask import request
from werkzeug.utils import secure_filename
from sampler import app
from sampler.model_cache import model_cache
from mko import MKO
from network.model import Model
import numpy as np

@app.route('/upload_mko', methods=['POST'])
def upload_mko():
  file = request.files['file']

  if file:
    key = "".join(random.choices(string.ascii_uppercase + string.digits, k=16))
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], "mko{}".format(key)))
    return Response("success: {}.format(filename)", 200)
  else:
    return Response("no file attached", 200)

@app.route("/queue_up", methods=['POST'])
def queue_up():
  key = request.values.get('key')
  if key not in model_cache:
    try:
      mko = MKO.load(os.path.join(app.config['UPLOAD_FOLDER'], "mko{}".format(key)))
      model_cache[key] = Model(mko)
    except:
      return Response("Problem loading MKO", 418)
  return Response("Model {} queued up".format(key), 200)

@app.route('/get_samples', methods=['POST'])
def get_samples():
  key = request.values.get('key')
  x_infer = request.values.getlist('x_infer')
  n_samples = request.values.get('n_samples')
  if key not in model_cache:
    return Response("Model {} not queued".format(key), 418)

  x_infer = np.array(x_infer).repeat(n_samples, axis=0)
  
  y_infer = model_cache[key].predict(x_infer)

  return Response(str(y_infer), 200)
