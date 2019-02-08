import requests
import bs4
import json
import urllib.request
import requests
import time

def get_page_category(url):
  desktop_url = 'https://www.facebook.com' + url
  resp = urllib.request.urlopen(desktop_url)
  contents = resp.read()
  soup = bs4.BeautifulSoup(contents, "lxml")

  title = url

  for p in soup.find_all('div', {'class': 'userContentWrapper'}):
    for link in p.find_all('a'):
      if len(link.text) > 0:
        title = link.text
        break

  info_url = 'https://www.facebook.com' + url + 'about'
  resp = urllib.request.urlopen(info_url)
  contents = resp.read()
  soup = bs4.BeautifulSoup(contents, "lxml")

  for p in soup.find_all('div', {'class': '_5m_o'}):
    for link in p.find_all('a'):
      return title, link.text


with open("friend_list_info_full_short.json", 'r') as fp:
    data = json.load(fp)
    new_data = {}
    for user in data:
      print('----------------------', user, '----------------------')
      user_info = data[user]
      all_likes = user_info['likes']
      likes_categories = {}
      for like in all_likes:
        if len(like) < 62 :
          try:
            title, category = get_page_category(like)
            likes_categories[like] = {'category':category, 'name': title}
            print(like)
          except UnicodeEncodeError: # pour quand il y a des accents dans les liens
            print(like, 'Unicode Error')
          except TypeError: # pour quand la page n'est pas une vraie page de like
            print(like, 'Ignored')
          except urllib.error.HTTPError:
            print(like, '404 Not Found')

          user_info['likes'] = likes_categories
          new_data[user] = user_info
        else:
          print(like, 'Too long, ignored')
      with open('friend_list_info_cat.json', 'w') as fp:
        json.dump(new_data, fp, sort_keys=True, indent=4)



