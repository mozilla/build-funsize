#from flask import Flask, request, Response
import flask
import core

import flasktask
import db
import tasks

app = flask.Flask(__name__)

@app.route('/')
def index():
    return "Index"

@app.route('/hello')
def hello():
    flasktask.hello()
    return 'Hello World'

@app.route('/partial', methods=['POST'])
def trigger_partial():
    """ 
    Needs params: mar_from, mar_to, mar_from_hash, mar_to_hash
    """

    required_params = ['mar_from', 'mar_to', 'mar_from_hash', 'mar_to_hash']
    # Check we have all params
    if not all([param in flask.request.form.keys() for param in required_params]):
        flask.abort(400)
    #print request.headers

    # TODO: Validate params and values in form Ideally
    #pprint.pprint(flask.request.form)
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
        #db.insert(identifier=None, url=url, status=db.status_code['IN_PROGRESS'])

        db.insert(identifier=identifier, url=url, status=db.status_code['IN_PROGRESS'])
    except db.IntegrityError, e:
        #print "Couldn't insert, got error: %s" % e
        # Lookup and get url and return it
        partial = db.lookup(identifier=identifier)
        resp = flask.Response(
                "{'result': '%s'}" % partial.url,
                status=201,
                mimetype='application/json'
                )
        return resp
    else:
        print "calling generation functions"
        # Call generation functions here
        resp = flask.Response("{'result' : '%s'" % url, status=202, mimetype='application/json')

        tasks.build_partial_mar.delay(mar_to, mar_to_hash, mar_from, mar_from_hash)

        return resp

    # If record exists, just say done
    # If other major error, do something else
    # TODO: Hook responses up with relengapi -- https://api.pub.build.mozilla.org/docs/development/api_methods/
    return resp

@app.route('/partial/<identifier>', methods=['GET'])
def get_partial(identifier):
    # Check DB state corresponding to URL
    # if "Completed", return blob and hash
    # if "Started", stall by inprogress error code
    # if "Invalid", return error code
    # if "does not exist", return different error code
    print flask.request.headers
    print "id:",identifier
    partial = db.lookup(identifier=identifier)
    if not partial:
        print "Record does not exist"
        resp = flask.Response("partial does not exist\n", status_code=404)
        return resp
    else:
        print partial.status

    return 'Got called'

if __name__ == '__main__':
    app.run(debug=True)
