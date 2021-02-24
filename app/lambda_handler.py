import base64
import json


def echo_request(cf_request):
    ''' Processes a Cloudfront request and returns the contents as a response '''
    print(f'REQUEST: {json.dumps(cf_request)}')
    cf_response_body = (
        f'{cf_request["method"]} {cf_request["uri"]}\n'
        f'queryString: {cf_request["querystring"]}\n'
        f'clientIp: {cf_request["clientIp"]}\n'
        '\n'
    )
    for hdr in cf_request.get('headers', {}):
        for hdr_obj in cf_request['headers'][hdr]:
            hdr_key = hdr_obj['key']
            hdr_val = hdr_obj['value']
            cf_response_body += f'REQUEST HEADER {hdr_key}: {hdr_val}\n'
    request_body_raw = cf_request.get('body', {}).get('data')
    if request_body_raw:
        if cf_request['body'].get('encoding') == 'base64':
            request_body = base64.b64decode(request_body_raw).decode()
        else:
            request_body = request_body_raw
        print(f'REQUEST BODY: {request_body}')
        if cf_request['body'].get('inputTruncated'):
            cf_response_body += f'\nREQUEST BODY (trunated)\n{request_body}\n'
        else:
            cf_response_body += f'\nREQUEST BODY\n{request_body}\n'
    return {
        'status': 200,
        'headers': {
            'content-type': [{'key': 'Content-Type', 'value': 'text/plain'}],
            'cache-control': [{'key': 'Cache-Control', 'value': 'no-cache'}]
        },
        'body': cf_response_body
    }


def cf_request(event, context):
    ''' Lambda Handler for a Cloudfront event '''
    cf_event = event['Records'][0]['cf']
    cf_config = cf_event['config']
    cf_request = cf_event['request']
    event_type = cf_config.get('eventType', 'unknown-request')
    dist_domain_name = cf_config.get('distributionDomainName', 'unknown')
    dist_id = cf_config.get('distributionId', 'unknown-id')
    request_id = cf_config.get('requestId', 'unspecified-request-id')
    request_method = cf_request.get('method')
    request_uri = cf_request.get('uri')
    client_ip = cf_request.get('clientIp', 'unknown-ip')
    print(f'{client_ip} [{request_id}] {event_type} {dist_domain_name}/{dist_id} "{request_method} {request_uri}"')
    if request_uri == '/api/echo':
        return echo_request(cf_request)
    return {'status': 404, 'headers': {'cache-control': [{'key': 'Cache-Control', 'value': 'public, max-age=60'}]}}


if __name__ == '__main__':
    response = cf_request({
        "Records": [{
            "cf": {
                "config": {"distributionId": "EXAMPLE"},
                "request": {
                    "uri": "/test",
                    "querystring": "size=LARGE&color=RED",
                    "method": "GET",
                    "clientIp": "2001:cdba::3257:9652",
                    "headers": {
                        "host": [{"key": "Host", "value": "d123.cf.net"}],
                        "user-agent": [{"key": "User-Agent", "value": "Test Agent"}],
                        "user-name": [{"key": "User-Name", "value": "aws-cloudfront"}]
                    }
                }
            }
        }]
    }, None)
    print(f'\n{response}')

    response = cf_request({
        "Records": [{
            "cf": {
                "config": {"distributionId": "EXAMPLE"},
                "request": {
                    "uri": "/api/echo",
                    "querystring": "size=LARGE&color=RED",
                    "method": "GET",
                    "clientIp": "2001:cdba::3257:9652",
                    "headers": {
                        "host": [{"key": "Host", "value": "d123.cf.net"}],
                        "user-agent": [{"key": "User-Agent", "value": "Test Agent"}],
                        "user-name": [{"key": "User-Name", "value": "aws-cloudfront"}]
                    }
                }
            }
        }]
    }, None)
    print(f'\n{response}')
