#from flask import Flask, request, Response
import argparse
import ConfigParser
import flask
import logging
import os
import shutil
import sys
import tempfile
import time

import senbonzakura.backend.core as core
import senbonzakura.cache.cache as cache
import senbonzakura.database.db as db
import senbonzakura.backend.tasks as tasks
import senbonzakura.utils.oddity as oddity

DB_URI = None
CACHE_URI = None

__here__ = os.path.dirname(os.path.abspath(__file__))

app = flask.Flask(__name__)

# Turn off werkzeug logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.INFO)

@app.route('/')
def index():
    return "Welcome to Senbonzakura, the Partial MAR on demand Web-Service."\
           "Please see https://wiki.mozilla.org/User:Ffledgling/Senbonzakura"

@app.route('/partial', methods=['POST'])
def trigger_partial(version='latest'):
    """
    Needs params: mar_from, mar_to, mar_from_hash, mar_to_hash
    """

    print "Version: %s" % version
    if version in app.config['unsupported_versions']:
        return flask.Response("{'result': 'Version %s of API is no longer supported'}" % version, status=410)
    # Flask's URL routing should prevent this from happening.
    if version not in app.config['supported_versions']:
        return flask.Response("{'result': 'Version %s of API does not exist'}" % version, status=400)
    else:
        # Some version specific code here?
        # We have nothing at the moment so leaving it as a stub
        pass

    cacheo = cache.Cache(app.config['CACHE_URI'])
    dbo = db.Database(app.config['DB_URI'])

    logging.debug('Parameters passed in : %s' % flask.request.form)

    required_params = ('mar_from', 'mar_to', 'mar_from_hash', 'mar_to_hash', 'channel_id', 'product_version')
    # Check we have all params
    if not all(param in flask.request.form.keys() for param in required_params):
        logging.info('Parameters could not we validated')
        flask.abort(400)

    # TODO: Validate params and values in form Ideally
    # These params are being pased to shell directly, we should probably sanitize them at some point.
    mar_from = flask.request.form['mar_from']
    mar_to = flask.request.form['mar_to']
    mar_from_hash = flask.request.form['mar_from_hash']
    mar_to_hash = flask.request.form['mar_to_hash']
    channel_id = flask.request.form['channel_id']
    product_version = flask.request.form['product_version']

    # TODO: Verify hashes and URLs are valid before returning the URL with a 201
    #       or return the concat anyway and just return a 202?

    # Try inserting into DB, if it fails, check error
    identifier = mar_from_hash+'-'+mar_to_hash
    url = flask.url_for('get_partial', identifier=identifier)

    if dbo.lookup(identifier=identifier):
        logging.info('Partial has already been triggered')
        resp = flask.Response(
                "{'result': '%s'}" % url,
                status=201,
                mimetype='application/json'
                )
        return resp

    try:
        # error testing and parameter validation, maybe do this up close to checking
        # existence

        # If record already exists it makes no difference and the insert
        # 'proceeds' as expected. (It is logged at the DB level)
        dbo.insert(identifier=identifier, status=db.status_code['IN_PROGRESS'], start_timestamp=time.time())
    #except oddity.DBError, e:
    except: # Any sort of error should result in a 500 on the client side and
            # nothing more, do we retry in such a situation or do we raise
            # warning bells? Ideally no error should reach this place.
            # Going with warning bells.
        logging.error('Error raised while processing trigger request for URL:',
                    '%s\n' % url)
        resp = flask.Response(
                "{'result': 'Error processing request'}" % url,
                status=500,
                mimetype='application/json'
                )
        return resp
    else:
        logging.info('calling generation functions')
        # Call generation functions here
        resp = flask.Response("{'result' : '%s'}" % url, status=202, mimetype='application/json')

        logging.critical('Calling build, should see immediate return after this')
        tasks.build_partial_mar.delay(mar_to, mar_to_hash, mar_from,
                mar_from_hash, identifier, channel_id, product_version)
        logging.critical('Called and moved on')

        return resp

    # If record exists, just say done
    # If other major error, do something else
    # TODO: Hook responses up with relengapi -- https://api.pub.build.mozilla.org/docs/development/api_methods/
    dbo.close()
    return resp

@app.route('/cache/<identifier>', methods=['GET'])
def get_from_cache(identifier):
    """ URL to allow direct access to cache """
    raise oddity.NotImplementedError()


@app.route('/partial/<identifier>', methods=['GET'])
def get_partial(identifier, version='latest'):

    print "Version %s" % version
    if version in app.config['unsupported_versions']:
        return flask.Response("{'result': 'Version %s of API is no longer supported'}" % version, status=410)
    # Flask's URL routing should prevent this from happening.
    if version not in app.config['supported_versions']:
        return flask.Response("{'result': 'Version %s of API does not exist'}" % version, status=400)
    else:
        # Some version specific code here?
        # We have nothing at the moment so leaving it as a stub
        pass

    cacheo = cache.Cache(app.config['CACHE_URI'])
    dbo = db.Database(app.config['DB_URI'])

    # Check DB state corresponding to URL
    # if "Completed", return blob and hash
    # if "Started", stall by inprogress error code
    # if "Invalid", return error code
    # if "does not exist", return different error code

    logging.debug('Request recieved with headers : %s' % flask.request.headers)
    try:
        partial = dbo.lookup(identifier=identifier)
    except oddity.DBError:
        logging.info('Record corresponding to identifier %s does not exist.' % identifier)
        resp = flask.Response("{'result':'partial does not exist'}", status=404)
    else:
        logging.info('Record corresponding to identifier %s found.' % identifier)
        status = partial.status
        if status == db.status_code['COMPLETED']:
            # Lookup DB and return blob
            # Call relevant functions from the core section.
            # We'll want to stream the data to the client eventually, right now,
            # we can just throw it at the client just like that.

            # Our older way of sending the file
            #identifier = partial.identifier
            #resp = flask.Response("{'result': '%s'}" % identifier, status=200)

            # Testing some stuff, see -- http://stackoverflow.com/questions/7877282/how-to-send-image-generated-by-pil-to-browser
            ### # Generate temp file and a temp file desc
            ### _, mar_to_return = tempfile.mkstemp()
            ### temp_file_desc = tempfile.TemporaryFile()
            ### print "TMP:!!!!!",temp_file_desc
            ### # Get partial mar from cache into temp file
            ### print identifier,
            ### print cacheo.__dict__
            ### cacheo.retrieve(identifier, output_file=mar_to_return)
            ### # Copy contents into temp desc
            ### with open(mar_to_return, 'rb') as f:
            ###     print "FILE DESC", f
            ###     shutil.copyfileobj(f , temp_file_desc)
            ### temp_file_desc.seek(0,0)
            ### # Cleanup file
            ### #os.remove(mar_to_return)
            ### # Let flask return the file from the temp desc
            ### print "TYPE:", type(temp_file_desc)
            ### #flask.send_file(temp_file_desc)
            ### flask.send_file(mar_to_return)
            return cacheo.retrieve(identifier, 'partial')

        elif status == db.status_code['ABORTED']:
            # Something went wrong, what do we do?
            resp = flask.Response("{'result': '%s'}" %
                        "Something went wrong while generating this partial",
                        status=204)

        elif status == db.status_code['IN_PROGRESS']:
            # Stall still status changes
            resp = flask.Response("{'result': '%s'}" % "wait", status=202)

        elif status == db.status_code['INVALID']:
            # Not sure what this status code is even for atm.
            resp = flask.Response("{'result': '%s'}" % "invalid partial", status=204)


        else:
            # This should not happen
            resp = flask.Response("{'result':'%s'}" % 
                                  "Status of this partial is unknown",
                                  status=400)

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
    app.config['LOG_FILE']=config.get('log', 'file_path')
    app.config['DB_URI']=config.get('db', 'uri')
    app.config['CACHE_URI']=config.get('cache', 'uri')
    app.config['supported_versions']=[x.strip() for x in config.get('version', 'supported_versions').split(',')]
    app.config['unsupported_versions']=[x.strip() for x in config.get('version', 'unsupported_versions').split(',')]
    logging.info('Flask config at startup: %s' % app.config)
    

if __name__ == '__main__':

    main(sys.argv[1:])

    # Setup version handling based on versions specified in config file
    for version in app.config['unsupported_versions'] + app.config['supported_versions']:
        app.add_url_rule('/%s/partial' % version, 'trigger_partial', trigger_partial, methods=['POST'], defaults={'version':version})
        app.add_url_rule('/%s/partial/<identifier>' % version, 'get_partial', view_func=get_partial, methods=['GET'], defaults={'version':version})

    # Configure logging
    # TODO: Make logging configurabe from config file instead
    logging.basicConfig(level=logging.DEBUG)
    file_handler = logging.FileHandler(app.config['LOG_FILE'], mode='a', encoding='UTF-8', delay=False)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s '
                                 '[in %(pathname)s:%(lineno)d]')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)

    # Start the application
    app.run(debug=False, processes=6)
