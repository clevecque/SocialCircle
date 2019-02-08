# Inspired from https://www.youtube.com/watch?v=OVpXdYBnZt8
import http.cookiejar
import urllib.request
import requests
import bs4
import json
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('email',
                    help='your email associated to Facebook account')
parser.add_argument('passwd',
                    help='password of your Facebook account')
parser.add_argument('id',
                    help='your id on Facebook, often like name.lastname')

args = parser.parse_args()


# Store the cookies and create an opener that will hold them
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Add our headers
opener.addheaders = [('User-agent', 'dfdf')]

# Install our opener (note that this changes the global opener to the one
# we just made, but you can also just call opener.open() if you want)
urllib.request.install_opener(opener)

# The action/ target from the form
authentication_url = 'https://m.facebook.com/login.php'

# Input parameters we are going to send
payload = {
  'email': args.email,
  'pass': args.passwd
  }

# Use urllib to encode the payload
data = urllib.parse.urlencode(payload).encode("utf-8")

# Build our Request object (supplying 'data' makes it a POST)
req = urllib.request.Request(authentication_url, data)

# Make the request and read the response
resp = urllib.request.urlopen(req)
contents = resp.read()
# print(contents)

full_list = []
full_dico = {}

url = "https://m.facebook.com/" + args.id + "/friends"
data = requests.get(url, cookies=cj)
soup = bs4.BeautifulSoup(data.text, 'html.parser')
#print(soup.prettify())

length = int(soup.find('h3').text.split('(')[1].split(')')[0])

for i in soup.find_all('a', {'class':'ce'}):
  link = i.get('href')
  full_list += [link]

for link in soup.find_all('div', {'id':'m_more_friends'}):
  more_friends = link.find('a').get('href')


# iterate
while len(full_list) < length:
  url = 'https://m.facebook.com' + more_friends
  print(url)
  data = requests.get(url, cookies=cj)
  soup = bs4.BeautifulSoup(data.text, 'html.parser')

  for i in soup.find_all('a'):
    link = i.get('href')
    if link[-3:]=='tab':
      print(link)
      full_list += [link]-
      name = i.text
      full_dico[name] = link

  for link in soup.find_all('div', {'id':'m_more_friends'}):
    more_friends = link.find('a').get('href')

  print(len(full_list))


with open('friend_list.json', 'w') as fp:
  json.dump(full_dico, fp, sort_keys=True, indent=4)
