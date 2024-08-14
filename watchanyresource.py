import os
import argparse
import urllib3
import requests
from kubernetes import config
from kubernetes.client import configuration

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

apiversion = "v1"
# ksajdlksjadsa/v1beta1
apiresource = "services"
namespace = "default"

def get_kubeapi_request(httpsession,path,header):
    response = httpsession.get(path, headers=header, verify=False)
    if response.ok:
        response.encoding = 'utf-8'
        return response.json()
    else:
        return 0

def get_kubeapi_request_streaming(httpsession,path,header):
    response = httpsession.get(path, headers=header, verify=False, stream=True)
    if response.ok:
        response.encoding = 'utf-8'
        return response.json()
    else:
        return 0


def main():
    k8s_host = ""
    k8s_token = ""
    k8s_headers = ""
    defjson = dict()

    if not os.environ.get('INCLUSTER_CONFIG'):
        config.load_kube_config()
    else:
        config.load_incluster_config()

    k8s_host = configuration.Configuration()._default.host
    k8s_token = configuration.Configuration()._default.api_key['authorization']
    k8s_headers = {"Accept": "application/json, */*", "Authorization": k8s_token}
    k8s_session = requests.session()

    if apiversion == "v1":
        api_path = 'api/'+apiversion
    else:
        api_path = 'apis/'+apiversion

    if namespace:
        api_obj = 'namespaces/'+namespace+'/'+apiresource
    else:
        api_obj = apiresource

    uri = api_path+'/'+api_obj
 
    init_res_version_data = get_kubeapi_request(k8s_session,k8s_host + '/' + uri, k8s_headers)
    if init_res_version_data:
        resource_version=init_res_version_data['metadata']['resourceVersion']
        print(resource_version)
    else:
        print("error: Unable to get the default resource version. Exiting...")
    cmd_opt='resourceVersion='+resource_version+'&allowWatchBookmarks=false&watch=true'

    while True:
        stream_data = get_kubeapi_request_streaming(k8s_session,k8s_host + '/' + uri + '?' + cmd_opt, k8s_headers)


if __name__ == "__main__":
    main()
