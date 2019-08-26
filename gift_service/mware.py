import json
import falcon


class JSONprocess:

    def process_request(self, req, resp):
        if req.content_length in (None, 0):
            return

        body = req.stream.read()

        if not body:
            raise falcon.HTTPBadRequest(
                'Empty request body. A valid JSON document is required.')

        try:
            req.context['request'] = json.loads(body)
        except:
            raise falcon.HTTPBadRequest(
                'Malformed JSON. Could not decode the request body.')

    def process_response(self, req, resp, resource, req_succeeded):
        if 'response' not in resp.context:
            return

        resp.body = json.dumps({
            'data': resp.context['response']
        })
