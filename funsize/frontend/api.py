"""
funsize.frontend.api
~~~~~~~~~~~~~~~~~~

This module contains all the Flask related code for routing and handling the
API call parameters

"""

import flask
import logging
import os
import json

import funsize.cache as cache
import funsize.backend.tasks as tasks
from funsize.frontend import _get_identifier, allow_from

CACHE_URI = None
app = flask.Flask("funsize")
log = logging.getLogger(__name__)


@app.route('/')
def index():
    """ Mockup message to fill in the index page """
    return """Welcome to Funsize, the Partial MAR on demand Web-Service.
           Please see https://wiki.mozilla.org/User:Ffledgling/Senbonzakura"""


@app.route('/cache', methods=['POST'])
# Restrict cache submission to localhost only
@allow_from("127.0.0.1")
def save_patch():
    """ Function to cache a patch in funsize """
    required_params = ('sha_from', 'sha_to')
    if not all(param in flask.request.form.keys() for param in required_params):
        log.info('Parameters could not be validated')
        flask.abort(400)

    files = flask.request.files
    if 'patch_file' not in files.keys():
        log.debug('Parameters passed could not be found on disk')
        flask.abort(400)
    storage = files.get('patch_file')

    form = flask.request.form
    sha_from, sha_to = form['sha_from'], form['sha_to']
    identifier = _get_identifier(sha_from, sha_to)

    log.debug('Saving patch file to cache with key %s', identifier)
    cacheo = cache.Cache()
    cacheo.save(storage.stream, identifier, 'patch')

    url = flask.url_for('get_patch', sha_from=sha_from, sha_to=sha_to)
    return flask.Response(json.dumps({
        "result": url,
        }),
        status=200,
        mimetype='application/json')


@app.route('/cache', methods=['GET'])
def get_patch():
    """ Function to return a patch from cache """
    required_params = ('sha_from', 'sha_to')
    if not all(param in flask.request.args.keys() for param in required_params):
        log.info('Arguments could not be validated')
        flask.abort(400)

    identifier = _get_identifier(flask.request.args['sha_from'],
                                 flask.request.args['sha_to'])

    log.debug('Looking up record with identifier %s', identifier)
    cacheo = cache.Cache()
    if not cacheo.find(identifier, 'patch'):
        log.info('Invalid partial request')
        resp = flask.Response(json.dumps({
            "result": "Patch with identifier %s not found" % identifier,
            }),
            status=400,
        )
        return resp

    log.info('Patch found, retrieving ...')
    return flask.Response(cacheo.retrieve(identifier, 'patch'),
                          status=200,
                          mimetype='application/octet-stream')


@app.route('/partial', methods=['POST'])
def trigger_partial():
    """ Function to trigger a  partial generation """
    required_params = (
        'mar_from', 'sha_from',
        'mar_to', 'sha_to',
        'channel_id', 'product_version')
    form = flask.request.form
    if not all(param in form.keys() for param in required_params):
        log.info('Missing parameters from POST form call')
        flask.abort(400)

    mar_from = form['mar_from']
    sha_from = form['sha_from']
    mar_to = form['mar_to']
    sha_to = form['sha_to']
    channel_id = form['channel_id']
    product_version = form['product_version']

    identifier = _get_identifier(sha_from, sha_to)
    url = flask.url_for('get_partial', identifier=identifier)

    cacheo = cache.Cache()
    if cacheo.find(identifier, 'partial'):
        log.info('Partial has already been triggered/generated')
        resp = flask.Response(json.dumps({
            "result": url
            }),
            status=201,
            mimetype='application/json'
        )
        return resp

    try:
        cacheo.save_blank_file(identifier, 'partial')
    except cache.CacheError:
        log.error('Error processing trigger request for URL: %s\n', url)
        resp = flask.Response(json.dumps({
            "result": "Error while processing request %s" % url,
            }),
            status=500,
            mimetypge='application/json'
        )
        return resp

    log.info('Calling generation functions')

    tasks.build_partial_mar.delay(mar_to, sha_to, mar_from, sha_from,
                                  identifier, channel_id, product_version)

    log.critical('Called build and moved on')
    resp = flask.Response(json.dumps({
        "result": url,
        }),
        status=202,
        mimetype='application/json'
    )
    return resp


@app.route('/partial/<identifier>', methods=['GET', 'HEAD'])
def get_partial(identifier):
    """ Function to return a generated partial """
    cacheo = cache.Cache()
    if not cacheo.find(identifier, 'partial'):
        resp = flask.Response(json.dumps({
            "result": "Partial with identifier %s not found" % identifier,
            }),
            status=400,
        )
        return resp

    if cacheo.is_blank_file(identifier, 'partial'):
        log.debug('Record found, status: IN PROGRESS')
        resp = flask.Response(json.dumps({
            "result": "wait",
            }),
            status=202,
        )
    else:
        log.debug('Record found, status: COMPLETED')
        if flask.request.method == 'HEAD':
            url = flask.url_for('get_partial', identifier=identifier)
            resp = flask.Response(json.dumps({
                "result": url
                }),
                status=200,
            )
        else:
            resp = flask.Response(cacheo.retrieve(identifier, 'partial'),
                                  status=200,
                                  mimetype='application/octet-stream')
    return resp

if __name__ == '__main__':
    debug = os.environ.get("FUNSIZE_DEBUG", False)
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(level=level)
    logging.getLogger("boto").setLevel(logging.INFO)
    app.run(debug=debug, host='0.0.0.0', processes=6)
