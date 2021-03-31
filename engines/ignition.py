"""
Engine that uses the built-in Ignition system.net functions to send requests.
"""


from . import BaseEngine


class IgnitionEngine(BaseEngine):
    def __init__(self, system, **options):
        self.system = system
        BaseEngine.__init__(self, **options)
        

    
    def create_session(self, **options):
        p = {}#'proxy':"https://localhost:1880", 'bypass_cert_validation':True}
        self.headers = options.get('headers')
        self.params = options.get('params')
        if options.get('key') is not None:
            self.key = options['key']
        else:
            self.key = None
            
        if options.get('username') is not None and options.get('password') is not None:
            return self.system.net.httpClient(username=options['username'], password=options['password'],**p)
        else:
            return self.system.net.httpClient(**p)
        

    def request(self, method, url, headers={}, params={}, data=None):
        """
        Makes a single request to Redmine and returns processed response.

        :param string method: (required). HTTP verb to use for the request.
        :param string url: (required). URL of the request.
        :param dict headers: (optional). HTTP headers to send with the request.
        :param dict params: (optional). Params to send in the query string.
        :param data: (optional). Data to send in the body of the request.
        :type data: dict, bytes or file-like object
        """

        

        headers = dict(self.headers.items() + headers.items())
        if headers.get('Content-Type') == "application/octet-stream":
            # data = data.payload
            headers['nodered'] = 'yes'
            headers['Content-Type'] = "application/json"           
            data = {'base64':data.payload}
        else:
            headers['nodered'] = "no"
        params = dict(self.params.items() + params.items())        
        kwargs = self.construct_request_kwargs(method, headers, params, data)
        resp = self.session.request(url, method=method.upper(), **kwargs)

        class IgnitionResponseWrapper:
            def __init__(self, response):
                self.history = None
                self.status_code = response.statusCode
                self.content = response.getBody().tostring()
                self.jsondata = response.getJson()
            def json(self):
                return self.jsondata
            def iter_content(self, chunk_size=1, decode_unicode=False):
                return self.content

        return self.process_response(IgnitionResponseWrapper(resp))


    def process_bulk_request(self, method, url, container, bulk_params):
        return [resource for params in bulk_params for resource in self.request(method, url, params=params)[container]]
