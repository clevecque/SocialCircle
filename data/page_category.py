import bs4
import urllib.request
import json
import time

#-------------------------------------------------------------------------------
#|                                                                             |
#|                   PART II - GETTING THE PAGES' CATEGORIES                   |
#|                                                                             |
#-------------------------------------------------------------------------------

# Now that we have a beautiful json with all the data on our friends we want to
# fill it with the data on the pages they like for later, create bigger categories


def get_page_category(url):
  """
  With the id of a Facebook page, get the category in which Facebook has stored it.
  Input: url = string, id of the page in the way it was retrieved before
  Outpu: title = the same id (you can update it to get the real name of the page
                 but it made me do another call to a new page and was useless)
         category = the category it has been stored into
  """
  title = url

  info_url = 'https://www.facebook.com' + url + 'about'
  resp = urllib.request.urlopen(info_url)
  contents = resp.read()
  soup = bs4.BeautifulSoup(contents, "lxml")

  for p in soup.find_all('div', {'class': '_4bl9 _5m_o'}):
    for link in p.find_all('a'):
      return title, link.text


# Here we are going to read and write into the same json file (thank you guys
# on StackOverflow for teaching me how to do it.)

# WARNING: if you thought the previous code was slow, stop now. Some of your friends
# have liked more than a thousand pages and it takes approx 1s for each page
# (if the connection is fine)
# There is surely a way to improve it like storing the values in a parallel list
# and not reopening the page if it has already been met but I don't have time rn.

with open('friends_data_test.json', 'r+') as fp:
  friends_data = json.load(fp)
  i = 0

  for friend in friends_data:

    print(friend)
    tstart = time.time()

    friend_likes = friends_data[friend]['likes']
    friend_likes_categorized = []

    for like in friend_likes:
      # this condition is just a security, if the like is a dictionnary then the
      # loop has already updated it
      if type(like) is str:
        # Like many people you might have, in your dark past, liked pages such as
        # 'I hate the last day of holidays blablabla' and it is not so relevant to us
        # 62 is not a precise number it just got us rid of a large amount of these pages
        if len(like) < 62 :
          try:
            title, category = get_page_category(like)
            friend_likes_categorized.append({'id': title, 'category': category})
          except UnicodeEncodeError: # for when there are problems of encoding
            pass
          except TypeError: # When we have stored a link of sth which is not really a page
            pass
          except urllib.error.HTTPError: # 404 Not Found
            pass
      # print('[', friend_likes.index(like)+1, '/', len(friend_likes), ']')

    # Update the field 'likes' of the data previously retrieved
    friends_data[friend]['likes'] = friend_likes_categorized
    fp.seek(0)
    json.dump(friends_data, fp, sort_keys=True, indent=4, ensure_ascii=False)
    fp.truncate()

    i += 1
    print('[', i, '/', len(friends_data),'] - ', round(time.time() - tstart, 2), 's')

    time.sleep(5)

