import http.client
import json

mapURL   = "framacarte.org"
mapToken = "105198:GXLX0YOGXXku0yxuARN6G4v_DcE"

webMap = http.client.HTTPSConnection(mapURL)

webMap.request("GET", "/fr/map/anonymous-edit/{}".format(mapToken))

response1 = webMap.getresponse()

print(response1.status, response1.reason)
#print(response1.getheader("Location"))
response1.read()

webMap.request("GET", response1.getheader("Location"))

response2 = webMap.getresponse()

print(response2.status, response2.reason)
#print(response2.getheaders(), "\n")
data = response2.read().decode("UTF-8")

startString = "var MAP = new L.U.Map("
stopString  = ");"

data = data[data.find(startString)+len(startString):]
data = data[:data.find(stopString)]

data = json.loads(data[7:])

for layer in data['properties']['datalayers']:
    if(layer['name'] == 'User'):
        print("User ID {}".format(layer['id']))



webMap.close()
