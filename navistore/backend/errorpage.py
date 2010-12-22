from twisted.web.resource import Resource
from twisted.web import http

class ErrorPage(Resource):
    """
    L{ErrorPage} is a resource which responds with a particular
    (parameterized) status and a body consisting of HTML containing some
    descriptive text.  This is useful for rendering simple error pages.

    @ivar template: A C{str} which will have a dictionary interpolated into
        it to generate the response body.  The dictionary has the following
        keys:

          - C{"code"}: The status code passed to L{ErrorPage.__init__}.
          - C{"brief"}: The brief description passed to L{ErrorPage.__init__}.
          - C{"detail"}: The detailed description passed to
            L{ErrorPage.__init__}.

    @ivar code: An integer status code which will be used for the response.
    @ivar brief: A short string which will be included in the response body.
    @ivar detail: A longer string which will be included in the response body.
    """

    template = """
<html>
  <head><title>%(code)s - %(brief)s</title></head>
  <body>
    <h1>%(brief)s</h1>
    <p>%(detail)s</p>
  </body>
</html>
"""

    def __init__(self, status, brief, detail):
        Resource.__init__(self)
        self.code = status
        self.brief = brief
        self.detail = detail


    def render(self, request):
        request.setResponseCode(self.code)
        request.setHeader("content-type", "text/html")
        return self.template % dict(
            code=self.code,
            brief=self.brief,
            detail=self.detail)


    def getChild(self, chnam, request):
        return self



class NoResource(ErrorPage):
    """
    L{NoResource} is a specialization of L{ErrorPage} which returns the HTTP
    response code I{NOT FOUND}.
    """
    def __init__(self, message="Sorry. No luck finding that resource."):
        ErrorPage.__init__(self, http.NOT_FOUND,
                           "No Such Resource",
                           message)
