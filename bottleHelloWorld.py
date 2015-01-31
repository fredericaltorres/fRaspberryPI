# http://bottlepy.org/docs/dev/tutorial.html#installation
#from bottle import route, run, template, response, request
import bottle

hostIp = "192.168.1.2"

# Web Api Home Page
@bottle.route('/')
def home():
    bottle.response.content_type = 'text; charset=UTF8'
    tpl = [
        "ActivityTracker Web api",
        "-----------------------",
        "http://{{hostIp}}:8080/api/lights/on",
        "http://{{hostIp}}:8080/api/lights/off"
    ]
    return bottle.template("\n".join(tpl), hostIp = hostIp)

@bottle.route('/api/lights/<onOff>')
def LightWebApi(onOff = None):
    tpl = bottle.template('Set Lights {{onOff}}', onOff = onOff)
    if onOff == "on":
        print "set-light-on"
    elif onOff == "off":
        print "set-light-off"
    else:
        print "set-light invalid parameter"
    return tpl

bottle.run(host=hostIp, port=8080, debug=True)

#http://localhost:8080/hello
#http://192.168.1.2:8080/
#http://192.168.1.2:8080/api/lights/on

