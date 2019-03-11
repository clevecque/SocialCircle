import json
from datetime import datetime

#-------------------------------------------------------------------------------
#|                                                                             |
#|                   PART III - REORGANISING EVERYTHING                        |
#|                                                                             |
#-------------------------------------------------------------------------------

# Now we have all the data we wanted but we want it to be fit for our graph

# The categories defined here have been made by hand and fit the visualisation
# If you want to change them, do whatever but it might not work anymore

with open("likes_categories.json") as fp:
  categories = json.load(fp)
# categories = {'cinema': ['Film', 'Acteur'], 'music':['Musicien/Groupe']}

def intersection(list1, list2):
  """
  Get the number of common elements between two lists.
  Input: list1, list2 = two Python lists
  Output: an int = length of the intersection

  N.B: the function is kept simple here since the lists we will use all have ids
  in them and never have twice the same element.
  """
  return len(list(set(list1) & set(list2)))

def distance(list1, list2):
  """
  Calculate a distance between two lists. This distance have been thought specifically
  for this problem of trying to find an affinity based on the pages liked.
  So it takes into account if one person liked way many more pages than another.
  0 if no pages in common, 1 if as many pages and all in common.
  Input: list1, list2 = two Python lists
  Output: float between 0 and 1
  """
  inter = intersection(list1, list2)
  if list1 == [] or list2 == []:
    return 0
  return 0.5*(inter/len(list1) +  inter/len(list2))

def is_present(el, liste):
  """
  Check if an element is in a list.
  Input: el = element
         list = list
  Output: boolean (1 if True)
  """
  liste = [str(val) for val in liste]
  if el in liste:
    return 1
  return 0


def get_specific_category(categories_names, data):
  """
  Based on the list of friends previously created, we are creating a similar list
  but keeping only the pages whom categories are in a specific field.
  Input: categories_names = list of categories linked to a specific field. For
                            instance ['Band', 'Musician'] for 'music'
         data = the list of friends with all the data
  Output: a dictionary similar to data but with only the matching pages
  """
  out = {}
  for (key, value) in data.items():
    category = []
    likes = value['likes']

    for like in likes:
      if like['category'] in categories_names:
        if like['id'] not in category:
          category.append(like['id'])

    # Yes it is long, but avoid duplicate problems
    info = {'year': value['birthyear'],
            'common friends': value['common friends'],
            'timestamp': value['timestamp'],
            'city': value['city'],
            'name': value['name'],
            'sex': value['sex'],
            'pages': category}

    out[key] = info
  return out

def get_data_w_categories(file, categories=categories):
  """
  It is a generalization of the previous function. We create a dictionary of
  dictionnaries, each for a specific field like 'music', 'sport' etc.
  Input: file = the location of the friends data json file
         categories = the dictionary of categories previously created, up to you
                      to change it.
  Output: data_categoris = a dictionary whom keys are the main categories and values
                           are dictionaries with the matching data
  """
  with open(file, "r") as fp:
    data = json.load(fp)

  data_categories = {}
  for (category, liste) in categories.items():
    data_categories[category] = get_specific_category(liste, data)
  return data_categories

def make_categorical_dic(dic_categories):
  """
  Last step, modify the data so that is has the shape of nodes/links and is ready
  for the visualisation.
  Input: dic_categories = the dictionnary of dictionnaries with the matching
                          categories and data
  Output: out = dictionnary with keys like nodes_music, links_music, nodes_sport,
                links_sport etc depending on the categories created
  """
  out = {}
  for (category, data) in dic_categories.items():


    nodes = []
    links = []
    for key in data:
      nbr_pages = len(data[key]['pages'])
      # If the user has not liked any page in the category, we don't consider it
      if nbr_pages != 0:
        # We keep the same global info, plus an information on the number of pages
        # liked in this category

        # We also update the timestamp to keep only the year
        if data[key]['timestamp'] is not None:
          date = datetime.fromtimestamp(data[key]['timestamp']).year


          nodes.append({'id': key,
                        'name': data[key]['name'],
                        'size': len(data[key]['pages']),
                        'timestamp': date,
                        'city': data[key]['city'],
                        'sex': data[key]['sex']})

        else:
          print(data[key]['name'], data[key]['timestamp'])
          # You can change to break or just fix null, for easier fix now i will use break
          # date = None
          pass

    # To limit the size of the file (not so important but still), we create two loops
    # and the second one take only the remaining friends. So we will have always
    # one way links.
    for i in range(len(nodes)):
      source = nodes[i]['id']
      for j in range(i+1, len(nodes)):
        target = nodes[j]['id']
        new_link = {'source': source,
                    'target': target}
        new_link['distance'] = distance(data[source]['pages'],
                                        data[target]['pages'])

        new_link['relation'] = is_present(source, data[target]['common friends'])
        links.append(new_link)

    out['nodes_'+category] = nodes
    out['links_'+category] = links
  return out



data_categories = get_data_w_categories('test_file_2.json')
graph_data = make_categorical_dic(data_categories)

with open('graph_test.json', 'w') as fw:
  json.dump(graph_data, fw, sort_keys=True, indent=4, ensure_ascii=False)

