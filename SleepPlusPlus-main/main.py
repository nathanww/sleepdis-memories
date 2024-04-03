import datetime

from flask import Flask, render_template, request,redirect
from google.cloud import datastore
dc = datastore.Client()

app = Flask(__name__)

#data=request.args.get('keyword')

def qualtrics():
    return redirect('''https://mit.co1.qualtrics.com/jfe/form/SV_bOgIpx4VGTUrvW6?pid='''+request.cookies.get("pid",default='')+"&condition="+request.cookies.get("condition",default='')+"&session="+request.cookies.get("session",default='')+"&totalStim="+request.cookies.get("totalStim",default='')+"&appVersion=5")

@app.route('/')
def root():

    conditions_to_assert = ["pid","negativeKeyword","condition","neutralKeyword"]
    if all(condition in request.cookies for condition in conditions_to_assert):
        if "sleep" in request.cookies.get("stage",default=''):
            return render_template('jsleep.html', data=request.args.get('keyword'))
        elif "wake" in request.cookies.get("stage",default=''):
            return qualtrics()
        elif "presession" in request.cookies.get("stage",default=''):
            return render_template('presession.html')
    else: #no participant ID cookie exists, so make the person enter their user ID
        # Erase all cookies
        for cookie in request.cookies:
            response = app.make_response(redirect('/'))
            response.set_cookie(cookie, '', expires=0)
            return response
        return render_template('index.html')

@app.route('/jsleep')
def jsleep():
    if "wake" in request.cookies.get("stage",default=''):
        return qualtrics()
    return render_template('jsleep.html')

@app.route('/wake')
def wake():
    return qualtrics()
@app.route('/wakecomplete')
def wakecomplete():
    if "wake" in request.cookies.get("stage",default=''):
        return qualtrics() 
    return render_template('presession.html')


@app.route('/sleepdata',methods=['POST'])
def sleepdata():
    
    datasize=len(request.form['timestamps'])
    if (datasize > 4):
        entity = datastore.Entity(key=dc.key('sleepdata'),exclude_from_indexes=("motionHistory","summedMotion","timestamps","running","soundVolume"))
        entity.update({
            'pid': request.form['pid'],
            'session': request.form['session'],
            'activeMode': request.form['activeMode'],
            'motionHistory': request.form['motionHistory'],
            'summedMotion': request.form['summedMotion'],
            'timestamps': request.form['timestamps'],
            'running': request.form['running'],
            'soundVolume': request.form['soundVolume'],
            'appVersion': request.form['appVersion']
        })

        dc.put(entity)
        #check to see if we have any prior sessions with this same id and session but less data, if so remove it
        #query = dc.query(kind='sleepdata')
        #query = query.add_filter('pid', '=', request.form['pid'])
        #query = query.add_filter('session', '=', request.form['session'])
        #l = query.fetch()
        #for item in l:
        #    if len(item['timestamps']) < datasize:
        #        dc.delete(item.key)
                
    
    data = {"status": "success"}
    return data, 200
    



if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml
    app.run(host='localhost', port=8080, debug=True)