import os
import json
import urllib3
import datetime
from kubernetes import client, config, watch

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    if not os.environ.get('INCLUSTER_CONFIG'):
        config.load_kube_config()
    else:  
        config.load_incluster_config()

    v1 = client.CoreV1Api()
    api_response = v1.list_service_for_all_namespaces()
    resource_version = api_response.metadata.resource_version
    
    while True:
        w = watch.Watch()
        for event in w.stream(v1.list_service_for_all_namespaces,resource_version=resource_version,allow_watch_bookmarks=False,timeout_seconds=30):
            print("Event: %s %s" % (event['type'], event['object'].metadata.name))
            
            metadata = event['object'].metadata
            if metadata:
                resource_version = metadata.resource_version

        now = datetime.datetime.now()    
        print(now.strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    main()
