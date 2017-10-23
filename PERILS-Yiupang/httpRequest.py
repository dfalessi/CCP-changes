from urllib.request import Request, urlopen
import credentials # this file contains personal credentials on github, it's not being committed on purpose.

def requestByGitAPI(url):
  request = Request(url)
  request.add_header("Authorization", "token %s" % credentials.personal_access_tokens)
  response = urlopen(request)
  return response.read()