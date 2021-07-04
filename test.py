import http.client
import json

mapURL   = "framacarte.org"
mapToken = "105198:GXLX0YOGXXku0yxuARN6G4v_DcE"
mapId    = "105198"

webMap = http.client.HTTPSConnection(mapURL)

webMap.request("GET", "/fr/map/anonymous-edit/{}".format(mapToken))

response1 = webMap.getresponse()

print(response1.status, response1.reason)
#print(response1.getheader("Location"))
response1.read()

newLocation = response1.getheader("Location")
print(newLocation)

webMap.request("GET", newLocation)

response2 = webMap.getresponse()

print(response2.status, response2.reason)
headers = response2.getheaders()
data = response2.read().decode("UTF-8")

xCSRFToken = None

for (headerName, headerValue) in headers:
    if headerName == "Set-Cookie":
        for value in headerValue.split("; "):
            if value.startswith("csrftoken="):
                xCSRFToken = value[len("csrftoken="):]

print("X-CSRF Token = {}".format(xCSRFToken))

startString = "var MAP = new L.U.Map("
stopString  = ");"

data = data[data.find(startString)+len(startString):]
data = data[:data.find(stopString)]

data = json.loads(data[7:])

userLayerId = -1

for layer in data['properties']['datalayers']:
    if(layer['name'] == 'User'):
        print("User ID {}".format(layer['id']))
        userLayerId = layer['id']


webMap.request("GET", "/fr/datalayer/{}/".format(userLayerId))
response3 = webMap.getresponse()

print(response3.status, response3.reason)
# print(response3.getheaders())

data = response3.read().decode("UTF-8")
data = json.loads(data)

#print(data)

data["features"] += [{'type': 'Feature', 'properties': {'_umap_options': {'iconClass': 'Circle'}, 'name': 'Robot'}, 'geometry': {'type': 'Point', 'coordinates': [0.0, 0.0]}}]

# print(data)

for user in data["features"]:
    userName = None
    userPos  = None
    
    print(user)
    if(user["type"] == "Feature"):
        if "name" in user["properties"]:
            userName = user["properties"]["name"]
        
        userPos = user["geometry"]["coordinates"]

#        print("Point {} at {}".format(userName, userPos))

sendHeaders = {
    "Content-Type": "multipart/form-data; boundary=---------------------------20468425193710838603597754818",
    "Host": "framacarte.org",
    "Origin": "https://framacarte.org",
    "Referer": "https://framacarte.org{}".format(newLocation),
    "X-CSRFToken": xCSRFToken,
    "X-Requested-With": "XMLHttpRequest"
}

print("\n", sendHeaders, "\n")

sendData  = b'boundary=---------------------------20468425193710838603597754818\r\n'
sendData += b'Content-Disposition: form-data; name="name"\r\n'
sendData += b'\r\n'
sendData += b'User\r\n'

sendData  = b'boundary=---------------------------20468425193710838603597754818\r\n'
sendData += b'Content-Disposition: form-data; name="display_on_load"\r\n'
sendData += b'\r\n'
sendData += b'true\r\n'

sendData  = b'boundary=---------------------------20468425193710838603597754818\r\n'
sendData += b'Content-Disposition: form-data; name="rank"\r\n'
sendData += b'\r\n'
sendData += b'0\r\n'

sendData  = b'boundary=---------------------------20468425193710838603597754818\r\n'
sendData += b'Content-Disposition: form-data; name="geojson"; filename="blob"\r\n'
sendData += b'Content-Type: application/json'
sendData += b'\r\n'
sendData += json.dumps(data).encode("UTF-8") + b'\r\n'
sendData += b'boundary=---------------------------20468425193710838603597754818--\r\n'

print("\n", sendData, "\n")

webMap.request("POST", "fr/map/{}/datalayer/update/{}/".format(mapId, userLayerId), sendData, sendHeaders)
response4 = webMap.getresponse()

print(response4.status, response4.reason)
print(response4.getheaders())
print(response4.read())

webMap.close()
