#!/usr/bin/env python
#
#####################################################################
#                                                                   #
#  File: gaecookie.py                                               #
#                                                                   #
#  Copyright (C) 2012 Min Xiang <cff29546@gmail.com>                #
#                                                                   #
#  Home: https://gae-cookie-processor.googlecode.com/               #
#                                                                   #
#  This file is part of GAECookieProcessor project.                 #
#                                                                   #
#  This project is released under the MIT License. See COPYING in   #
#  the project.                                                     #
#                                                                   #
#####################################################################

import re,urllib2

# This regex is implemented according to RFC2109, RFC2068 and RFC6265
NS_COOKIE=re.compile(r'''
(?P<name>[!#-'*+.0-9a-z^_`|~-]+)             # cookie-name = token (defined in RFC2068)
= (?P<value>[^\x00-\x20\x7f-\xff",;\\]+ |    # cookie-octet (defined in RFC6265)
            "(?:[^"\\]|\\.)*"   )            # cookie-value = *cookie-octet | quoted-string
\s*
(?P<cookieavs>
 (;\s*                                       # begin of a cookie-av
  (?:comment=(?P<comment>                    # comment = token | quoted-string
      [!#-'*+.0-9a-z^_`|~-]+ | 
      "(?:[^"\\]|\\.)*")
    | max-age=(?P<maxage>[0-9]+)             # max-age
    | domain=(?P<domain>[0-9a-z.-]+)         # domain
    | path=(?P<path>                         # path
       [^\x00-\x1f\x7f-\xff;,]+              # path-value in RFC6265, but with assumption
      )                                      #   that commas do not exist.
                                             #   As GAE use ',' as header line separator,
                                             #   including comma will ruin the path-value
                                             #   as well as next cookie when path-av is
                                             #   the last cookie-av. And in common cases
                                             #   path won't contain any comma
    | (?P<secure>secure)                     # secure
    | (?P<httponly>httponly)                 # httponly
    | version=(?P<version>\d+)               # version
    | expires=(?P<expires>                   # Expires and rfc1123-date
       (?:Mon|Tue|Wed|Thu|Fri|Sat|Sun),\s+   # wkday
       (?P<day>\d+)(?:\s+|[-\/])             # day
       (?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul # month
        |Aug|Sep|Oct|Nov|Dec)(?:\s+|[-\/]) 
       (?P<year>\d+)\s*                      # year
       (?P<hour>\d\d?):(?P<minute>\d\d):     # time
       (?P<second>\d\d)?\s* (?:GMT|UTC)      # time zone
      )
    | (?P<extensionav>                       # extension-av in RFC6265, but with assumption
       [^\x00-\x1f\x7f-\xff;,]+              #   that commas do not exist.
      )                                      #   Same reason as path-value
  )
 )*                                          # end of a cookie-av
)\s*''',re.X | re.I)

# Obsoleted "set-cookie2" headers defined by RFC2965
# support comma separated cookies by definition
# so there is nothing to fix with "set-cookie2" cookies

class GAECookieProcessor(urllib2.HTTPCookieProcessor):
  def __init__(self, cookiejar=None):
    import cookielib
    if cookiejar is None:
      cookiejar = cookielib.CookieJar()
    self.cookiejar = cookiejar

  def http_request(self, request):
    self.cookiejar.add_cookie_header(request)
    return request

  def http_response(self, request, response):
    
    #recover setcookie before extract cookies
    recovered_hdrs=[]
    for h in response.info().headers:
      if h[0:10].lower().startswith('set-cookie'):
        for c in NS_COOKIE.finditer(h):
          recovered_hdrs.append('Set-Cookie: %s' % c.group(0))
      else:
        recovered_hdrs.append(h)
    response.info().headers=recovered_hdrs

    self.cookiejar.extract_cookies(response, request)
    return response

  https_request = http_request
  https_response = http_response

def test():
  i=raw_input()
  while i !='':
    print i
    for s in NS_COOKIE.finditer(i):
      print 'Set-Cookie: %s' % s.group(0)
      print s.group('name'),'=',s.group('value')
      print '  path   =',s.group('path')
      print '  domain =',s.group('domain')
      print '  expires=',s.group('expires')
      print '  max-age=',s.group('maxage')
    try:
      i=raw_input()
    except:
      i=''

if __name__ == '__main__':
  test()
