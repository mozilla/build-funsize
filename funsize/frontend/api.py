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
import time

import funsize.cache.cache as cache
import funsize.database.database as db
import funsize.backend.tasks as tasks
import funsize.utils.oddity as oddity

from funsize.database.models import status_code

DB_URI = None
CACHE_URI = None

__here__ = os.path.dirname(os.path.abspath(__file__))

app = flask.Flask(__name__)


@app.route('/')
def index():
    """ Mockup message to fill in the index page """

    return "Welcome to Senbonzakura, the Partial MAR on demand Web-Service."\
           "Please see https://wiki.mozilla.org/User:Ffledgling/Senbonzakura"


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

    dbo = db.Database(app.config['DB_URI'])

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

    if dbo.lookup(identifier=identifier):
        logging.info('Partial has already been triggered')
        resp = flask.Response(str({
            'result': url
            }),
            status=201,
            mimetype='application/json'
        )
        dbo.close()
        return resp

    try:
        dbo.insert(identifier=identifier,
                   status=status_code['IN_PROGRESS'],
                   start_timestamp=time.time())
    except oddity.DBError:
        logging.error('Error while processing trigger request for URL: %s\n',
                      url)
        resp = flask.Response(str({
            'result': 'Error while processing request %s' % url,
            }),
            status=500,
            mimetypge='application/json'
        )
    else:
        logging.info('Calling generation functions')
        logging.critical('Call build - should see immediate return after this')

        tasks.build_partial_mar.delay(mar_to, mar_to_hash, mar_from,
                                      mar_from_hash, identifier,
                                      channel_id, product_version)

        logging.critical('Called build and moved on')
        resp = flask.Response(str({
            'result': '%s' % url,
            }),
            status=202,
            mimetype='application/json'
        )
    finally:
        dbo.close()

    # TODO: Hook responses up with relengapi ?
    # https://api.pub.build.mozilla.org/docs/development/api_methods/
    return resp


@app.route('/cache/<identifier>', methods=['GET'])
def get_from_cache(identifier):
    """ URL to allow direct access to cache """
    raise oddity.FunsizeNotImplementedError()


@app.route('/partial/<identifier>', methods=['GET'])
def get_partial(identifier, version='latest'):
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
    dbo = db.Database(app.config['DB_URI'])

    logging.debug('looking up record with identifier %s', identifier)
    partial = dbo.lookup(identifier=identifier)

    if partial is None:
        logging.info('Invalid partial request')
        resp = flask.Response(str({
            'result': 'Partial with identifier %s not found' % identifier,
            }),
            status=400,
        )
        dbo.close()
        return resp

    logging.debug('Record ID: %s', identifier)

    status = partial.status
    if status == status_code['COMPLETED']:
        logging.info('Record found, status: COMPLETED')
        # TODO ROUGHEDGE stream data to client differently
        resp = flask.Response(cacheo.retrieve(identifier, 'partial'),
                              status=200,
                              mimetype='application/octet-stream')

    elif status == status_code['ABORTED']:
        logging.info('Record found, status: ABORTED')
        resp = flask.Response(str({
            'result': 'Something went wrong while generating this partial',
            }),
            status=204,
        )

    elif status == status_code['IN_PROGRESS']:
        logging.info('Record found, status: IN PROGRESS')
        resp = flask.Response(str({
            'result': 'wait',
            }),
            status=202,
        )

    elif status == status_code['INVALID']:
        logging.info('Record found, status: INVALID')
        resp = flask.Response(str({
            'result': 'Invalid partial',
            }),
            status=204,
        )

    else:
        logging.error('Record found, status: UNKNOWN')
        resp = flask.Response(str({
            'result': 'Status of this partial is unknown',
            }),
            status=400,
        )

    dbo.close()
    return resp


def main(argv):
    """
    Parse args, config files and perform configuration
    """
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

    logging.basicConfig(level=logging.INFO)
    app.run(debug=False, host='0.0.0.0', processes=6)
