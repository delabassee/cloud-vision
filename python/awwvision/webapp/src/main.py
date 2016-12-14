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

from flask import Flask, render_template
from gcloud import pubsub
import psq
import logging

from storage import Storage


app = Flask(__name__)
app.debug = True

storage = Storage()
q = psq.Queue(pubsub.Client(), 'images')


@app.route('/')
def index():
    labels = storage.get_labels()
    labels_and_images = storage.get_repr_image_for_labels(labels)
    return render_template('index.html', labels=labels_and_images)


@app.route('/label/<label>')
def label(label):
    images = storage.get_images(label)
    return render_template('label.html', images=images)


@app.route('/upload', methods=['POST'])
def upload():
    logging.warning('enque before')
    q.enqueue('main.process_url_task', 'https://www.google.be/imgres?imgurl=https://cdn.pixabay.com/photo/2014/03/29/09/17/cat-300572_960_720.jpg&imgrefurl=https://pixabay.com/en/photos/cat/&h=720&w=858&tbnid=HR3uWxjt9lIc-M:&vet=1&tbnh=168&tbnw=200&docid=GNgiwtR-iQNmZM&itg=1&usg=__QbLr_alJUc4HRCx-zHC_MfDXnHY=&sa=X&ved=0ahUKEwiqlJiMuvPQAhWKLsAKHXWsDzMQ_B0IdjAM')
    logging.warning('enque after')
    return render_template('crawler_started.html')


@app.route('/start_crawler', methods=['POST'])
def start_crawler():
    q.enqueue('main.scrape_reddit_task', 'aww', pages=20)
    return render_template('crawler_started.html')


if __name__ == '__main__':
    app.run(port=8080, debug=True)
