from urllib.request import Request, urlopen
import credentials

def gitAPIRequest(url):
  request = Request(url)
  request.add_header("Authorization", "token %s" % credentials.personal_access_tokens)
  response = urlopen(request)
  return response.read()