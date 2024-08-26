import os
import argparse
import json
import urllib3
import requests
import websocket, ssl
import subprocess
from kubernetes import config
from kubernetes.client import configuration
from subprocess import Popen

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#groupversion = os.environ.get('GROUPANDVERSION')
#resourcetype = os.environ.get('RESOURCETYPE')
#namespace = os.environ.get('NAMESPACE',"")

groupversion = "v1"
resourcetype = "services"
namespace = ""
# cluster.x-k8s.io/v1beta1

def get_kubeapi_request(httpsession,path,header):
    response = httpsession.get(path, headers=header, verify=False)
    if response.ok:
        response.encoding = 'utf-8'
        return response.json()
    else:
        return 0

def get_kubeapi_request_streaming(path,header):
    ws = websocket.create_connection(path, header=header, sslopt={"cert_reqs": ssl.CERT_NONE})
    if ws:    
        return ws
    else:
        return 0

def main():
    k8s_host = ""
    k8s_token = ""
    k8s_headers = ""
 
    if not os.environ.get('INCLUSTER_CONFIG'):
        config.load_kube_config()
    else:
        config.load_incluster_config()

    k8s_host:str = configuration.Configuration()._default.host
    k8s_token = configuration.Configuration()._default.api_key['authorization']
    k8s_headers = {"Accept": "application/json, */*", "Authorization": k8s_token}
    k8s_session = requests.session()

    if groupversion == "v1":
        api_path = 'api/'+groupversion
    else:
        api_path = 'apis/'+groupversion

    if namespace:
        api_obj = 'namespaces/'+namespace+'/'+resourcetype
    else:
        api_obj = resourcetype

    uri = api_path+'/'+api_obj
    print("Connecting to - "+k8s_host+"/"+uri)

    init_res_version_data = get_kubeapi_request(k8s_session,k8s_host + '/' + uri, k8s_headers)
    if init_res_version_data:
        resource_version=init_res_version_data['metadata']['resourceVersion']
        # print(resource_version)
    else:
        print("error: Unable to get the default resource version. Exiting...")
        exit
    
    cmd_opt='resourceVersion='+resource_version+'&allowWatchBookmarks=false&watch=true'
    ws_stream = get_kubeapi_request_streaming(k8s_host.replace("https://","wss://") + '/' + uri + '?' + cmd_opt,k8s_headers)

    while True:
#        try:
            msg = ws_stream.recv()
            
            json_msg = json.loads(msg)
            os.environ["CHANGED_VARIABLE"] = json.dumps(json_msg['object'])

            if json_msg['type'] == "ADDED":
                #for name, value in os.environ.items():
                #    print("{0}: {1}".format(name, value))
                #files = [f for f in files if os.path.isfile(Direc+'/'+f)]
                print("There was an ADD event for the resource of type "+resourcetype+". Executing user provided scripts in the \"added\" subfolder... ")
                for file in sorted(os.listdir('added')):
                    print("Now executing file - added/"+file+" ...")
                    p = Popen(['added/'+file],start_new_session=True,stdin=subprocess.DEVNULL)
                    #p.terminate()
            elif json_msg['type'] == "MODIFIED":
                print("There was an MODIFY event for the resource of type "+resourcetype+". Executing user provided scripts in the \"modified\" subfolder... ")
                for file in sorted(os.listdir('modified')):
                    print("Now executing file - modified/"+file+" ...")
                    p = Popen(['modified/'+file],start_new_session=True,stdin=subprocess.DEVNULL)
            elif json_msg['type'] == "DELETED":
                print("There was an DELETE event for the resource of type "+resourcetype+". Executing user provided scripts in the \"deleted\" subfolder... ")
                for file in sorted(os.listdir('deleted')):
                    print("Now executing file - deleted/"+file+" ...")
                    p = Popen(['deleted/'+file],start_new_session=True,stdin=subprocess.DEVNULL)
            else:
                pass

            metadata = json_msg['object']['metadata']
            if metadata:
                resource_version = json_msg['object']['metadata']['resourceVersion']

#        except Exception:
#            cmd_opt='resourceVersion='+resource_version+'&allowWatchBookmarks=false&watch=true'
#            ws_stream = get_kubeapi_request_streaming(k8s_host.replace("https://","wss://") + '/' + uri + '?' + cmd_opt,k8s_headers)

#    while True:
#        stream_data = get_kubeapi_request_streaming(k8s_session,k8s_host + '/' + uri + '?' + cmd_opt, k8s_headers)\

if __name__ == "__main__":
    main()
