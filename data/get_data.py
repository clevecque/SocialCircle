import http.cookiejar
import urllib.request
import json
import argparse
import requests
import bs4
import time

#-------------------------------------------------------------------------------
#|                                                                             |
#|                   PART I - GETTING YOUR FRIENDS' DATA                       |
#|                                                                             |
#-------------------------------------------------------------------------------

# This code is mainly written for a French Facebook even though not many parts need
# a change.
# We use the mobile version of Facebook online which is easier to log in and crawl.

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('email',
                    help='your email associated to Facebook account')
parser.add_argument('passwd',
                    help='password of your Facebook account')
parser.add_argument('id',
                    help='your id on Facebook, often like name.lastname')
parser.add_argument('timestamp',
                    help='location of your file with your friends timestamps')

args = parser.parse_args()

# Credits to https://www.mycodingzone.net
# for the logging to Facebook part

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

#-------------------------------------------------------------------------------
#|                            GET FRIENDS LIST                                 |
#-------------------------------------------------------------------------------

def get_friends_list(url):
  """
  Get a list of all your Facebook friends.
  Input: url = a string of your facebook id that you gave in argument
  Output: friends_list = a list of dic, for each friends the dictionary contains
                         two keys {'id': facebook's id, 'name': facebook's name}
  """

  # Access to your list of friends
  url = "https://m.facebook.com/" + url + "/friends"
  data = requests.get(url, cookies=cj)
  soup = bs4.BeautifulSoup(data.text, 'html.parser')

  friends_list = []

  # This is the number of friends you have, we will use it to stop the loop
  nb_friends = int(soup.find('h3').text.split('(')[1].split(')')[0])

  # Retrieve all the friends present on the original page
  for i in soup.find_all('a', {'class':'ce'}):
    # the [:-12] is used because every friend's adress ends by useless '?fref=tab'
    link = i.get('href')[:-12]
    name = i.text
    friends_list += [{'id': link, 'name': name}]

  # Save the link to "See more"
  for link in soup.find_all('div', {'id':'m_more_friends'}):
    more_friends = link.find('a').get('href')

  # While the friends' list is not full, iterate
  while len(friends_list) < nb_friends:
    # and use the previous link to "See more" to access the following pages
    url = 'https://m.facebook.com' + more_friends
    data = requests.get(url, cookies=cj)
    soup = bs4.BeautifulSoup(data.text, 'html.parser')

    # Redo as previously but since we don't exactly which links matches
    # friends' adresses we find them all and check they have the good format
    for i in soup.find_all('a'):
      link = i.get('href')
      if link[-3:]=='tab':
        name = i.text
        friends_list += [{'id': link[:-12], 'name':name}]

    # We keep saving the updated link to "See more"
    for link in soup.find_all('div', {'id':'m_more_friends'}):
      more_friends = link.find('a').get('href')

  return friends_list


#-------------------------------------------------------------------------------
#|                            GET USER INFO                                    |
#-------------------------------------------------------------------------------

def get_section_interest(name, soup):
  """
  On a Facebook's profile you might want to get different informations. The 'About'
  page is written in a way that if you give the header of the section you can get
  the information.
  Input: name = name of the section you want to get the info from
         soup = the page as a BeautifulSoup object
  Output: info = a string with the info if it exists, None if it doesn't. (For
                 instance some people don't write their birthday)
  """
  try:
    for element in soup.find_all('div', {'title': name}):
      for subelement in element.find_all('div'):
        info = subelement.text
    return info
  except UnboundLocalError:
    return None

def get_user_info(url):
  """
  Retrieves information about a facebook user
  Input: url = the facebook url of the user's profile
  Output: info = dictionnary with keys ['birthyear', 'current city', 'sex']

  Warning: code written for a French Facebook
  """

  # Access the user's profile (About section)
  url = 'https://m.facebook.com' + url + '/about'
  data = requests.get(url, cookies=cj)
  soup = bs4.BeautifulSoup(data.text, 'html.parser')

  info = {}

  # Birthday info
  birthday = get_section_interest('Date de naissance', soup)

  try:
    # we are actually interested only by the birthyear
    if len(birthday.split(' ')) == 3:
      year = birthday.split(' ')[-1]

    info['birthyear'] = year
  except:
    info['birthyear'] = None


  # Current city
  info['city'] = get_section_interest('Ville actuelle', soup)

  # Sex
  info['sex'] = get_section_interest('Sexe', soup)

  return info

#-------------------------------------------------------------------------------
#|                            GET USER LIKES                                   |
#-------------------------------------------------------------------------------


def get_all_likes(url):
  """
  For the purpose of the project we are interested in all the pages each user has
  likes.
  This function is linked to the following (get_likes).
  Input: url = a string with the Facebook's id of the user, in the format
              retrieved by function get_friends_list
  """

  # Two kinds of people exist: those with a readable id in the format name.lastname
  # or sth like it, and those with a number which look like profile?id=complex_number
  # The two kinds won't react in the same way.
  if 'id=' in url:
    id_user = url.split('?')[1]
    new_url = 'https://m.facebook.com/profile.php?v=likes&' + id_user
  else:
    new_url = 'https://m.facebook.com' + url +'?v=likes'

  # Access to the user's page of likes
  data = requests.get(new_url, cookies=cj)
  soup = bs4.BeautifulSoup(data.text, 'html.parser')

  all_likes = []
  try:
    get_likes(soup, all_likes)
  except :
    print("Error with", url)
  return all_likes

def get_likes(soup, liste_likes):
  """
  Recursive function to get all the pages one user has liked.
  Input: soup = the page we want to crawl in BeautifulSoup format
         liste_likes = since it is a recursive function, this list stores all
                       the data we crawl and then is incremented at each step
  Output: liste_likes = input and output, a list of strings, each string is the
                        id of the page liked
  """

  # Since we supposedly are on a page with a list of all the liked pages we
  # roughly get all links and then sort them out.
  for link in soup.find_all('a'):

    # This is the kind of link we want to keep. It is a bit wider so we will get
    # some links useless but we will get rid of them later
    if 'fref=none' in link.get('href').split('?')[-1] :
      real_link = link.get('href').split('?')[0]
      liste_likes.append(real_link)

    # Some pages such as movies are not written the same way out but we are still
    # interested so we store them in the main list too.
    elif link.get('href').split('/')[0] == '' and link.get('href').split('/')[-1] == '':
      liste_likes.append(link.get('href'))

    # And finally we are interested in another kind of links : the "See more" ones
    # it's quite complicated to get but it's just the way Facebook has made it
    elif any(['startindex' in value for c, value in enumerate(link.get('href').split(';')[-1].split('&'))]):

      # The links to change language have the same format but we don't want them
      if 'language' not in link.get('href') and 'privacyx' not in link.get('href'):

        data = requests.get('https://m.facebook.com'+link.get('href'), cookies=cj)
        soup = bs4.BeautifulSoup(data.text, 'html.parser')

        # Recursive loop
        get_likes(soup, liste_likes)

    # Just as before, some sections such as movies don't have the same adresses
    elif 'timeline/app_section' in link.get('href'):

      data = requests.get('https://m.facebook.com'+link.get('href'), cookies=cj)
      soup = bs4.BeautifulSoup(data.text, 'html.parser')

      # Recursive loop
      get_likes(soup, liste_likes)

#-------------------------------------------------------------------------------
#|                            GET COMMON FRIENDS                               |
#-------------------------------------------------------------------------------


def get_all_common_friends(url):
  """
  For drawing an interesting graph we need to know the relationship between our friends.
  This function is linked to the following (get_common_friends).
  Input: url = a string with the Facebook's id of the user, in the format
              retrieved by function get_friends_list
  """
  # Just as before, two kinds of url adresses: readable id and numerical id
  if 'id=' in url:
    id_user = url.split('?')[1]
    new_url = 'https://m.facebook.com/profile.php?v=friends&mutual=1&' + id_user
  else:
    new_url = 'https://m.facebook.com' + url +'/friends?mutual=1'

  # Access the mutual friends' page
  data = requests.get(new_url, cookies=cj)
  soup = bs4.BeautifulSoup(data.text, 'html.parser')

  common_friends = []
  try:
    get_common_friends(soup, common_friends)
  except :
    print("Error with", url)
  return common_friends


def get_common_friends(soup, common_friends):
  """
  Recursive function to get all the common friends
  Input: soup = the page we want to crawl in BeautifulSoup format
         common_friends = since it is a recursive function, this list stores all
                       the data we crawl and then is incremented at each step
  Output: common_friends = input and output, a list of strings, each string is the
                        id of the common friend
  """

  # We get all links present on the page
  for link in soup.find_all('a'):
    try:
      # We select only the ones that interest us
      adr = link.get('href')
      if 'fref=fr_tab' in adr :
        # We get rid of that last ugly part
        index = adr.index('fref=fr_tab')-1
        common_friends.append(adr[:index])
    except TypeError:
      continue

  # And we save also the "See more" link
  for element in soup.find_all('div',{'id':'m_more_mutual_friends'}):
    for link in element.find_all('a'):

      data = requests.get('https://m.facebook.com'+link.get('href'), cookies=cj)
      soup = bs4.BeautifulSoup(data.text, 'html.parser')

      # So that we can iterate
      get_common_friends(soup, common_friends)


#-------------------------------------------------------------------------------
#|                            GET TIMESTAMP OF ADDING                          |
#-------------------------------------------------------------------------------

# So far you should have downloaded the file that Facebook provides on your friends.
# We are only interested in the file called "friends.json" which you should have
# indicated the location in the arguments of this ex.

# Problem is that the file doesn't like the accented characters and store them as
# a string and it's then impossible to use any encoding to get back to the real
# characters. So we modify the file by hand.

friends_timestamps = {}
with open(args.timestamp, 'r') as fp:
  list_timestamps = json.load(fp)['friends']
  for friend in list_timestamps:
    name = friend['name'].replace('Ã¨', 'è')\
                         .replace('Ã©', 'é')\
                         .replace('Ã¶', 'ö')\
                         .replace('Ã¯', 'ï')\
                         .replace('Ã«', 'ë')\
                         .replace('Ã¡', 'ã')\
                         .replace('Ã¸', 'ø')\
                         .replace('Å¡', 'š')\
                         .replace('Ä', 'ć')\
                         .replace('Ã£', 'á')\
                         .replace('Ã´', 'ô')\
                         .replace('Ã­', 'í')\
                         .replace('Ã¿', 'ë')\
                         .replace('Ã³', 'ó')\
                         .replace('á»', 'ễ')\
                         .replace('Ã', 'ß')
    friends_timestamps[name] = friend['timestamp']

def get_timestamp(name):
  """
  Only for a matter of aesthetics in the following lines.
  Input: name = name of a friend
  Output: timestamp = the matching timestamp if present in the Facebook file,
                      None otherwise.

  N.B : why the name wouldn't be in the file ? First answer, you downloaded and
  ran this code at different times and add new friends in between. Second answer,
  you have a friend with a name containing even weirder letters than the ones we
  explicitly changed before.
  """
  try:
    return friends_timestamps[name]
  except KeyError:
    return None

#-------------------------------------------------------------------------------
#|                            MAIN                                             |
#-------------------------------------------------------------------------------


# Here is the main part of the code
# WARNING: it does take some time, depending on how many pages your friends have
# liked it can go from 1s by friend up to 400s (depending on the connection too)

# First, we get the list of our friends
friends_list = get_friends_list(args.id)

# If you want to store it for not having to run it each time you can, but I'll be
# honest, it is the quickest part to run

# with open('friends_list.json', 'w') as fp:
#   json.dump(friends_list, fp, sort_keys=True, indent=4, ensure_ascii=False)


size = len(friends_list)
print('Found', size, 'friends.')
friends_data = {}


# Here is the creepy part where you create a file from your friends' informations
for friend in friends_list:

  tstart = time.time()

  # Get the id from the list of friends
  friend_url = friend['id']
  friend_info = get_user_info(friend_url)

  friend_name = friend['name']
  friend_info['name'] = friend_name

  friend_timestamp = get_timestamp(friend_name)
  friend_info['timestamp'] = friend_timestamp

  friend_common_friends = get_all_common_friends(friend_url)
  friend_info['common friends'] = friend_common_friends

  friend_likes = get_all_likes(friend_url)
  friend_info['likes'] = friend_likes

  print('[', friends_list.index(friend)+1, '/', size, '] -',
        round(time.time() - tstart, 2), 's',
        '(', friend_name, ')')

  # Finally adding to the main dictionnary
  friends_data[friend_url] = friend_info

  # If I were you I would store it step by step because if your connection ends
  # or some other mistakes you might not want to wait another 5 hours
  with open('friends_data.json', 'w') as fp:
    json.dump(friends_data, fp, sort_keys=True, indent=4, ensure_ascii=False)

#Adding your own information
own_url = '/' + args.id
own_info = get_user_info(own_url)
own_info['name'] = 'Moi'
own_info['timestamp'] = 0
own_info['common friends'] = []
own_likes = get_all_likes(own_url)
own_info['likes'] = own_likes
friends_data[own_url] = own_info

with open('friends_data.json', 'w') as fp:
    json.dump(friends_data, fp, sort_keys=True, indent=4, ensure_ascii=False)
