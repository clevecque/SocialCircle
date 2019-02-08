import json

with open("friend_list_cat.json", 'r') as fp:
  data = json.load(fp)

  new_json = {}

  for user in data:
    data_user = data[user]
    user_sex = data_user['sex']
    user_city = data_user['current city']
    user_age = data_user['birthday year']
    user_likes = data_user['likes']
    print(user_sex, user_city, user_age)

    for like in user_likes: # on parcourt tous les likes par user
      print(like)

      cat = user_likes[like]['category']
      if cat in new_json: # on check si la catégorie existe déjà
        if like in new_json[cat]: # on check si l'url existe déjà dans la catégorie
          like_info = new_json[cat][like]
          # on ajoute les infos concernant le sexe
          if user_sex in like_info['sex']:
            like_info['sex'][user_sex] += 1
          else:
            like_info['sex'][user_sex] = 1

          # on ajoute les infos concernant la ville
          if user_city in like_info['city']:
            like_info['city'][user_city] += 1
          else:
            like_info['city'][user_city] = 1

          # on ajoute les infos concernant l'année de naissance
          if user_age in like_info['year']:
            like_info['year'][user_age] += 1
          else:
            like_info['year'][user_age] = 1

          # total
          like_info['total'] += 1

        else: # la page n'est pas encore renseignée
          cat_info = new_json[cat]
          cat_info[like] = {'name': data_user['likes'][like]['name'],
                            'sex': {user_sex: 1},
                            'city': {user_city: 1},
                            'year': {user_age: 1},
                            'total': 1}

      else:
          new_json[cat] = {like: {'sex': {user_sex: 1},
                                  'city': {user_city: 1},
                                  'year': {user_age: 1},
                                  'total': 1}}


with open('likes_list.json', 'w') as fp:
    json.dump(new_json, fp, sort_keys=True, indent=4, ensure_ascii=False)


