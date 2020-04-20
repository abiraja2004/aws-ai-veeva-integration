# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
  
#   Licensed under the Apache License, Version 2.0 (the "License").
#   You may not use this file except in compliance with the License.
#   A copy of the License is located at
  
#       http://www.apache.org/licenses/LICENSE-2.0
  
#   or in the "license" file accompanying this file. This file is distributed 
#   on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either 
#   express or implied. See the License for the specific language governing 
#   permissions and limitations under the License.

import sys
sys.path.insert(0, '/opt')
import boto3
import requests
from requests_aws4auth import AWS4Auth
from urllib.parse import unquote_plus
import json
import os

my_session = boto3.session.Session()
region = my_session.region_name

#region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

# host = 'https://search-mayank-sandstone-demo-ur4mhmhgsmkhwdjz4uzuwtrznu.us-east-1.es.amazonaws.com' # Replace with the elasticsearch host name 
host =  'https://{0}'.format(unquote_plus(os.environ['ES_DOMAIN']))


index = 'avai_index'
type = '_doc'
url = host + '/' + index + '/' + type + '/'

headers = { "Content-Type": "application/json" }

def lambda_handler(event, context):
    # print(json.dumps(event))
    count = 0
    for record in event['Records']:
        # Get the primary key for use as the Elasticsearch ID
        # id = record['dynamodb']['Keys']['BucketName']['S'] + '/' + record['dynamodb']['Keys']['KeyName']['S']
        id = record['dynamodb']['Keys']['ROWID']['S'] 
        
        
        
        # print(id)

        if record['eventName'] == 'REMOVE':
            r = requests.delete(url + id, auth=awsauth)
        else:
            document = record['dynamodb']['NewImage']
            # create index document
            item = {}
            item['AssetType'] = document['AssetType']['S']
            item['Confidence'] = float(document['Confidence']['N'])
            item['Operation'] = document['Operation']['S']
            item['Tag'] = document['Tag']['S']
            item['ROWID'] = document['ROWID']['S']
            item['TimeStamp'] = int(document['TimeStamp']['N'])
            if 'Face_Id' in document:
                item['Face_Id'] = int(document['Face_Id']['N'])
            if 'Value' in document:
                item['Value'] = document['Value']['S']
            item['Location'] = document['Location']['S']
            # print(json.dumps(item))
            r = requests.put(url + id, auth=awsauth, json=item, headers=headers)
        count += 1
        print(str(count) + ' records processed.')
    return str(count) + ' records processed.'