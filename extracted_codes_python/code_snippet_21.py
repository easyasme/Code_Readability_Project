#!//usr/bin/python
# KPSU "Podcast" to actual Podcast generator
# created for http://www.kpsu.org/category/static-and-distance/
#
# by Daniel Agans
#
import urllib2, html5lib, re
parser = html5lib.HTMLParser(tree=html5lib.getTreeBuilder("dom"))

urlobject = urllib2.urlopen('http://www.kpsu.org/category/static-and-distance/') # get site html
root_response = urlobject.read()
responses = root_response.splitlines( );

for response in responses:
  if 'http://www.kpsu.org/static-and-distance/' in response:
    links = response.split('<a href="')
    Titles = []
    Links = []
    for link in links:
      Title = link.split('" rel')
      Titles.append(Title[0])
    Titles = filter(None, Titles)
    for Link in Titles:
      urlobject2 = urllib2.urlopen(Link)
      root2 = urlobject2.read()
      responses2 = root2.splitlines( );
      Headings = []
      Subtitles = []
      Descriptions = []
      URLs = []
      MP3s = []
      for secondary in responses2:
        if 'og:title' in secondary:
          secondary = secondary.split('content="')
          secondary = secondary[1].split(' - KPSU"')
          print(secondary[0])
          Headings.append(secondary[0])
        if 'og:description' in secondary:
          secondary = secondary.split('content="')
          print(secondary[1])
          Descriptions.append(secondary[0])
        if 'og:url' in secondary:
          secondary = secondary.split('content="')
          secondary = secondary[1].split('" />')
          print(secondary[0])
          URLs.append(secondary[0])
        if 'Click here to download' in secondary:
          secondary = secondary.split('href="')
          secondary = secondary[1].split('"a class="count"')
          print(secondary[0])  
          MP3s.append(secondary[0])
                  
        
