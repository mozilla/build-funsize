#from flask import Flask, request, Response
import flask
import logging
import os
import shutil
import tempfile
import time

import core
import cache
import flasktask
import db
import tasks
import oddity

# FIXME: Load this from a preference file
DB_URI = 'sqlite:///test.db'
CACHE_URI = '/perma/cache/'

dbo = db.Database(DB_URI)
cacheo = cache.Cache(CACHE_URI)

app = flask.Flask(__name__)

@app.route('/')
def index():
    return "Welcome Senbonzakura, the Partial MAR on demand Web-Service."\
           "Please see https://wiki.mozilla.org/User:Ffledgling/Senbonzakura"

@app.route('/partial', methods=['POST'])
def trigger_partial():
    """
    Needs params: mar_from, mar_to, mar_from_hash, mar_to_hash
    """

    logging.debug('Parameters passed in : %s' % flask.request.form)

    required_params = ('mar_from', 'mar_to', 'mar_from_hash', 'mar_to_hash')
    # Check we have all params
    if not all(param in flask.request.form.keys() for param in required_params):
        logging.info('Parameters could not we validated')
        flask.abort(400)

    # TODO: Validate params and values in form Ideally
    mar_from = flask.request.form['mar_from']
    mar_to = flask.request.form['mar_to']
    mar_from_hash = flask.request.form['mar_from_hash']
    mar_to_hash = flask.request.form['mar_to_hash']
    # TODO: Verify hashes and URLs are valid before returning the URL with a 201
    #       or return the concat anyway and just return a 202?

    # Try inserting into DB, if it fails, check error
    identifier = mar_from_hash+'-'+mar_to_hash
    url = flask.url_for('get_partial', identifier=identifier)

    try:
        # error testing and parameter validation, maybe do this up close to checking
        # existence

        dbo.insert(identifier=identifier, status=db.status_code['IN_PROGRESS'], start_timestamp=time.time())
    except db.IntegrityError, e:
        # Lookup and get url and return it
        partial = dbo.lookup(identifier=identifier)
        print "**"*10
        print partial
        print "**"*10
        resp = flask.Response(
                "{'result': '%s'}" % url,
                status=201,
                mimetype='application/json'
                )
        return resp
    else:
        logging.info('calling generation functions')
        # Call generation functions here
        resp = flask.Response("{'result' : '%s'}" % url, status=202, mimetype='application/json')

        tasks.build_partial_mar.delay(mar_to, mar_to_hash, mar_from,
                mar_from_hash, identifier)

        return resp

    # If record exists, just say done
    # If other major error, do something else
    # TODO: Hook responses up with relengapi -- https://api.pub.build.mozilla.org/docs/development/api_methods/
    return resp

@app.route('/cache/<identifier>', methods=['GET'])
def get_from_cache(identifier):
    """ URL to allow direct access to cache """
    raise oddity.NotImplementedError()


@app.route('/partial/<identifier>', methods=['GET'])
def get_partial(identifier):
    # Check DB state corresponding to URL
    # if "Completed", return blob and hash
    # if "Started", stall by inprogress error code
    # if "Invalid", return error code
    # if "does not exist", return different error code

    logging.debug('Request recieved with headers : %s' % flask.request.headers)
    logging.info('Request recieved for identifier %s' % identifier)
    try:
        partial = dbo.lookup(identifier=identifier)
    except oddity.DBError:
        logging.info('Record corresponding to identifier %s does not exist.' % identifier)
        resp = flask.Response("{'result':'partial does not exist'}", status=404)
    else:
        logging.info('Record corresponding to identifier %s found.' % identifier)
        status = partial.status
        print status
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
            return cacheo.retrieve(identifier, )

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

    return resp

if __name__ == '__main__':
    app.run(debug=True)
