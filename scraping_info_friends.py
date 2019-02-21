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
parser.add_argument('friends',
                    help='path to your json file with your list of friends')

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

def get_user_info(url):
  url = 'https://m.facebook.com' + url[:-12] + '/about'
  data = requests.get(url, cookies=cj)
  soup = bs4.BeautifulSoup(data.text, 'html.parser')

  info = {}

  # Education info
  scol = []
  for element in soup.find_all('div', {'id':'education'}):
    for link in element.find_all('a'):
      if len(link.text) > 1:
        scol += [link.text]

  # Birthday info
  for element in soup.find_all('div', {'title':'Date de naissance'}):
    for subelement in element.find_all('div'):
      birthday = subelement.text

  try:
    if len(birthday.split(' ')) == 3:
      year = birthday.split(' ')[-1]

    info['birthday year'] = year
  except NameError:
    info['birthday year'] = ''

  try:
    info['birthday month'] = birthday.split(' ')[1]
  except NameError:
    info['birthday month'] = ''

  try:
    info['birthday day'] = birthday.split(' ')[0]
  except NameError:
    info['birthday day'] = ''


  # Work info
  work = []
  for element in soup.find_all('div', {'id':'work'}):
    for link in element.find_all('a'):
      if len(link.text) > 1:
        work += [link.text]

    info['work'] = work

  # Current city
  for element in soup.find_all('div', {'title': 'Ville actuelle'}):
    for subelement in element.find_all('div'):
      current_city = subelement.text

  try:
    info['current city'] = current_city
  except NameError:
    info['current city'] = ''

  # Home city
  for element in soup.find_all('div', {'title': 'Ville d’origine'}):
    for subelement in element.find_all('div'):
      home_city = subelement.text

  try:
    info['home city'] = home_city
  except NameError:
    info['home city'] = ''

  # Sex
  for element in soup.find_all('div', {'title': 'Sexe'}):
    for subelement in element.find_all('div'):
      sex = subelement.text

  try:
    info['sex'] = sex
  except NameError:
    info['sex'] = ''

  # Relationship
  try:
    relationship = soup.find('div', {'id':'relationship'}).text

    for i in range(len(relationship)-1):
      if relationship[i].islower() and relationship[i+1].isupper():
        relationship = relationship[i+1:]
        break
    info['relationship'] = relationship


  except AttributeError:
    info['relationship'] = ''

  for element in soup.find_all('div', {'id':'relationship'}):
    for link in element.find_all('a'):
      spouse = link.get('href')

  try:
    info['spouse'] = spouse
  except NameError:
    info['spouse'] = ''

  # Friends in common
  for link in soup.find_all('a'):
    if 'en commun' in link.text:
      nb_common_friends = link.text.split('(')[1].split(')')[0]

  try:
    info['nb common friends'] = nb_common_friends
  except NameError:
    info['nb common friends'] = ''

  return info

def get_user_likes(url):
  new_url = 'https://m.facebook.com' + url[:-12] +'?v=likes'
  data = requests.get(new_url, cookies=cj)
  soup = bs4.BeautifulSoup(data.text, 'html.parser')

  likes = []
  # Activities
  for element in soup.find_all('a'):
    if element.span:
      if element.span.text != 'En voir plus' and element.span.text != 'Voir plus':
        likes += [element.span.text]

  return likes

def get_all_likes(soup, liste_likes):

  for link in soup.find_all('a'):

    if 'fref=none' in link.get('href').split('?')[-1] :
      real_link = link.get('href').split('?')[0]
      liste_likes.append(real_link)


    elif link.get('href').split('/')[0] == '' and link.get('href').split('/')[-1] == '':
      liste_likes.append(link.get('href'))


    elif any(['startindex' in value for c, value in enumerate(link.get('href').split(';')[-1].split('&'))]):
      if 'language' not in link.get('href'):

        data = requests.get('https://m.facebook.com'+link.get('href'), cookies=cj)
        soup = bs4.BeautifulSoup(data.text, 'html.parser')

        get_all_likes(soup, liste_likes)

    elif 'timeline/app_section' in link.get('href'):

      data = requests.get('https://m.facebook.com'+link.get('href'), cookies=cj)
      soup = bs4.BeautifulSoup(data.text, 'html.parser')

      get_all_likes(soup, liste_likes)


def get_all_likes_categories(url):
  if 'id' in url:
    id_user = url.split('?')[1][:-12]
    new_url = 'https://m.facebook.com/profile.php?v=likes&' + id_user
  else:
    new_url = 'https://m.facebook.com' + url[:-12] +'?v=likes'

  data = requests.get(new_url, cookies=cj)
  soup = bs4.BeautifulSoup(data.text, 'html.parser')

  all_likes = []
  try:
    get_all_likes(soup, all_likes)
  except :
    print("Error with", url)
  return all_likes



def get_common_friends(soup, common_friends):
  for link in soup.find_all('a'):
    try:
      adr = link.get('href')
      if 'fref=fr_tab' in adr :
        common_friends.append(adr)
    except TypeError:
      continue

  for element in soup.find_all('div',{'id':'m_more_mutual_friends'}):
    for link in element.find_all('a'):

      data = requests.get('https://m.facebook.com'+link.get('href'), cookies=cj)
      soup = bs4.BeautifulSoup(data.text, 'html.parser')

      get_common_friends(soup, common_friends)

def get_all_common_friends(url):
  new_url = 'https://m.facebook.com' + url[:-12] +'/friends?mutual=1'

  data = requests.get(new_url, cookies=cj)
  soup = bs4.BeautifulSoup(data.text, 'html.parser')

  common_friends = []
  try:
    get_common_friends(soup, common_friends)
  except :
    print("Error with", url)
  return common_friends




with open(args.friends, 'r') as fr:

  data = json.load(fr)
  new_data = {}
  for user in data:
    user_url = data[user]
    user_info = get_user_info(user_url)
    user_likes = get_all_likes_categories(user_url)
    user_common_friends = get_all_common_friends(user_url)
    print(user, data[user], len(user_likes))
    user_info['likes'] = user_likes
    user_info['url'] = user_url
    user_info['common friends'] = user_common_friends
    new_data[user] = user_info
    with open('friend_list_more.json', 'w') as fw:
      json.dump(new_data, fw, sort_keys=True, indent=4, ensure_ascii=False)





  # # Detail of friends in common
  # url_friends = 'https://m.facebook.com' + url[:-12] + '/friends?mutual=1'
  # data_friends = requests.get(url_friends, cookies=cj)
  # soup_friends = bs4.BeautifulSoup(data_friends.text, 'html.parser')
  # common_friends = []
  # get_common_friends(soup_friends)

  # try:
  #   info['common friends'] = common_friends
  # except NameError:
  #   info['common friends'] = ''
