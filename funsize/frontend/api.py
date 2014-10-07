"""
funsize.frontend.api
~~~~~~~~~~~~~~~~~~

This module contains all the Flask related code for routing and handling the
API call parameters

"""

import argparse
import ConfigParser
import flask
import logging
import os
import sys
try:
    import simplejson
except ImportError:
    import json

import funsize.cache.cache as cache
import funsize.backend.tasks as tasks
import funsize.utils.oddity as oddity
import funsize.utils.csum as csum

CACHE_URI = None

__here__ = os.path.dirname(os.path.abspath(__file__))

app = flask.Flask(__name__)


def _get_patch_identifier(path1, path2):
    """ Function to generate the identifier of a patch based on two files given
        by their paths on disk
    """
    id1 = csum.getsha512(path1, True)
    id2 = csum.getsha512(path2, True)

    return '-'.join([id1, id2])


@app.route('/')
def index():
    """ Mockup message to fill in the index page """
    return "Welcome to Funsize, the Partial MAR on demand Web-Service."\
           "Please see https://wiki.mozilla.org/User:Ffledgling/Senbonzakura"


@app.route('/cache', methods=['POST'])
def save_patch():
    """ Function to save a patch based on its different versions in cache """
    logging.debug('Parameters passed in : %s', flask.request.form)

    required_params = ('path_from', 'path_to', 'path_patch')
    if not all(param in flask.request.form.keys() for param in required_params):
        logging.info('Parameters could not be validated')
        flask.abort(400)

    if not all(os.path.isfile(param) for param in flask.request.form.values()):
        logging.info('Parameters passed could not be found on disk')
        flask.abort(400)

    form = flask.request.form
    path_from, path_to = form['path_from'], form['path_to']
    identifier = _get_patch_identifier(path_from, path_to)

    cacheo = cache.Cache(app.config['CACHE_URI'])
    path_patch = flask.request.form['path_patch']

    logging.info('Saving patch file %s to cache with key %s',
                 path_patch, identifier)
    cacheo.save(flask.request.form['path_patch'],
                identifier, 'patch', isfile=True)

    url = flask.url_for('get_patch', path_from=path_from, path_to=path_to)
    return flask.Response(json.dumps({
        "result": url,
        }),
        status=200,
        mimetype='application/json'
    )


@app.route('/cache/', methods=['GET'])
def get_patch():
    """ Function to return a patch from cache """
    logging.debug('Request received with args : %s', flask.request.args)

    required_params = ('path_from', 'path_to')
    if not all(param in flask.request.args.keys() for param in required_params):
        logging.info('Arguments could not be validated')
        flask.abort(400)

    if not all(os.path.isfile(param) for param in flask.request.args.values()):
        logging.info('Arguments paths passed could not be found on disk')
        flask.abort(400)

    identifier = _get_patch_identifier(flask.request.args['path_from'],
                                       flask.request.args['path_to'])
    cacheo = cache.Cache(app.config['CACHE_URI'])

    logging.debug('looking up record with identifier %s', identifier)
    if not cacheo.find(identifier, 'patch'):
        logging.info('Invalid partial request')
        resp = flask.Response(json.dumps({
            "result": "Patch with identifier %s not found" % identifier,
            }),
            status=400,
        )
        return resp

    logging.info('Patch found, retrieving ...')
    return flask.Response(cacheo.retrieve(identifier, 'patch'),
                          status=200,
                          mimetype='application/octet-stream')


@app.route('/partial', methods=['POST'])
def trigger_partial(version='latest'):
    """
    Function to trigger a  partial generation
    Needs params: mar_from, mar_to, mar_from_hash, mar_to_hash
    """

    api_result = {
        'result': 'Version %s of API ' % version
    }
    if version in app.config['unsupported_versions']:
        api_result['result'] += ' no longer supported'
        return flask.Response(str(api_result), status=410)
    if version not in app.config['supported_versions']:
        api_result['result'] += ' does not exist'
        return flask.Response(str(api_result), status=400)

    cacheo = cache.Cache(app.config['CACHE_URI'])

    logging.debug('Parameters passed in : %s', flask.request.form)

    required_params = ('mar_from', 'mar_to', 'mar_from_hash',
                       'mar_to_hash', 'channel_id', 'product_version')
    if not all(param in flask.request.form.keys() for param in required_params):
        logging.info('Parameters could not be validated')
        flask.abort(400)

    # TODO: Validate params and values through a form - saniteze needed?

    mar_from = flask.request.form['mar_from']
    mar_to = flask.request.form['mar_to']
    mar_from_hash = flask.request.form['mar_from_hash']
    mar_to_hash = flask.request.form['mar_to_hash']
    channel_id = flask.request.form['channel_id']
    product_version = flask.request.form['product_version']

    # TODO: Verify hashes and URLs are valid ?

    identifier = '-'.join([mar_from_hash, mar_to_hash])
    url = flask.url_for('get_partial', identifier=identifier)

    if cacheo.find(identifier, 'partial'):
        logging.info('Partial has already been triggered')
        resp = flask.Response(json.dumps({
            "result": url
            }),
            status=201,
            mimetype='application/json'
        )
        return resp

    try:
        cacheo.save_blank_file(identifier, 'partial')
    except oddity.CacheError:
        logging.error('Error while processing trigger request for URL: %s\n',
                      url)
        resp = flask.Response(json.dumps({
            "result": "Error while processing request %s" % url,
            }),
            status=500,
            mimetypge='application/json'
        )
        return resp

    logging.info('Calling generation functions')

    # TODO - here we should get try-except thing to retry + ack late
    # catch LCA exception
    tasks.build_partial_mar.delay(mar_to, mar_to_hash, mar_from,
                                    mar_from_hash, identifier,
                                    channel_id, product_version)

    logging.critical('Called build and moved on')
    resp = flask.Response(json.dumps({
        "result": url,
        }),
        status=202,
        mimetype='application/json'
    )

    # TODO: Hook responses up with relengapi ?
    # https://api.pub.build.mozilla.org/docs/development/api_methods/
    return resp


@app.route('/partial/<identifier>', methods=['GET'])
def get_partial(identifier, version='latest'):
    """ Function to return a generated partial """
    logging.debug('Request received with headers : %s', flask.request.headers)
    logging.debug('Got request with version %s', version)

    api_result = {
        'result': 'Version %s of API ' % version
    }
    if version in app.config['unsupported_versions']:
        api_result['result'] += ' no longer supported'
        return flask.Response(str(api_result), status=410)
    if version not in app.config['supported_versions']:
        api_result['result'] += ' does not exist'
        return flask.Response(str(api_result), status=400)

    cacheo = cache.Cache(app.config['CACHE_URI'])

    logging.debug('looking up record with identifier %s', identifier)
    if not cacheo.find(identifier, 'partial'):
        logging.info('Invalid partial request')
        resp = flask.Response(json.dumps({
            "result": "Partial with identifier %s not found" % identifier,
            }),
            status=400,
        )
        return resp

    logging.debug('Record ID: %s', identifier)

    if cacheo.is_blank_file(identifier, 'partial'):
        logging.info('Record found, status: IN PROGRESS')
        resp = flask.Response(json.dumps({
            "result": "wait",
            }),
            status=202,
        )
    else:
        logging.info('Record found, status: COMPLETED')
        # TODO ROUGHEDGE stream data to client differently
        resp = flask.Response(cacheo.retrieve(identifier, 'partial'),
                              status=200,
                              mimetype='application/octet-stream')

    return resp


def main(argv):
    """ Parse args, config files and perform configuration """
    parser = argparse.ArgumentParser(description='Some description')
    parser.add_argument('-c', '--config-file', type=str,
                        default='../configs/default.ini',
                        required=False, dest='config_file',
                        help='The application config file. INI format')
    args = parser.parse_args(argv)
    config_file = os.path.join(__here__, args.config_file)

    config = ConfigParser.ConfigParser()
    config.read(config_file)
    app.config['LOG_FILE'] = config.get('log', 'file_path')
    app.config['DB_URI'] = config.get('db', 'uri')
    app.config['CACHE_URI'] = config.get('cache', 'uri')
    app.config['supported_versions'] = [
        x.strip() for x in config.get('version', 'supported_versions').split(',')
    ]
    app.config['unsupported_versions'] = [
        x.strip() for x in config.get('version', 'unsupported_versions').split(',')
    ]
    logging.info('Flask config at startup: %s' % app.config)


if __name__ == '__main__':

    main(sys.argv[1:])

    for version in app.config['unsupported_versions'] + app.config['supported_versions']:
        app.add_url_rule('/%s/partial' % version,
                         'trigger_partial',
                         trigger_partial,
                         methods=['POST'],
                         defaults={
                             'version': version
                         })
        app.add_url_rule('/%s/partial/<identifier>' % version,
                         'get_partial',
                         view_func=get_partial,
                         methods=['GET'],
                         defaults={
                             'version': version
                         })

    logging.basicConfig(filename=app.config['LOG_FILE'], level=logging.INFO)
    app.run(debug=False, host='0.0.0.0', processes=6)
