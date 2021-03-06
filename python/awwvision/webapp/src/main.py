# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import Flask, render_template, request
from gcloud import pubsub
import psq
import logging
import time

from storage import Storage


app = Flask(__name__)
app.debug = True

storage = Storage()
q = psq.Queue(pubsub.Client(), 'images')


@app.route('/')
def index():
    ts = request.args.get('ts')
    if ts is None : 
        ts = str(time.time())
        logging.warning('initial timestamp: ' + ts)
    else:
        logging.warning('existing timestamp: ' + ts)

    labels = storage.get_labels()
    labels_and_images = storage.get_repr_image_for_labels(labels)
    return render_template('index.html', labels=labels_and_images, ts=ts)


@app.route('/label/<label>')
def label(label):
    images = storage.get_images(label)
    return render_template('label.html', images=images)


@app.route('/upload', methods=['POST'])
def upload():
    logging.warning('upload entry')
    ts = request.args.get('ts')
    #ts = str(time.time())
    logging.warning('/upload timestamp: ' + ts)
    url = request.form['url']+'?ts='+ts
    logging.warning('enque before - url: ' + url)
    q.enqueue('main.process_url_task', url)
    logging.warning('enque after')
    return render_template('image_accepted.html', ts=ts)


if __name__ == '__main__':
    app.run(port=8080, debug=True)
