from flask import Flask, request, render_template
import pymongo
import urllib.request, json
import pandas as pd
import ssl

app=Flask(__name__)

myclient = pymongo.MongoClient('mongodb+srv://Kundan:Kundan123@cluster0.b4uinke.mongodb.net/?retryWrites=true&w=majority')

def get_platform():
    url = 'http://api.rawg.io/api/platforms?key=028f66a2165f4301b23c8f6cb0256f38'
    response = urllib.request.urlopen(url)
    data = response.read()
    dict = json.loads(data)
    platform_data = {}
    for platform in dict['results']:
        platforms = {}
        id = platform['id']
        platforms['slug'] = platform['slug']
        platforms['name'] = platform['name']
        platforms['games_count'] = platform['games_count']
        platform_data[id] = platforms
    platform_df = pd.DataFrame.from_dict(platform_data)
    platform_df = platform_df.to_json()
    platform_info = json.loads(platform_df)
    return platform_info

def get_game():
    url = 'http://api.rawg.io/api/games?key=028f66a2165f4301b23c8f6cb0256f38'
    response = urllib.request.urlopen(url)
    data = response.read()
    dict = json.loads(data)
    game_data = {}
    for game in dict['results']:
        games = {}
        id = game['id']
        games['slug'] = game['slug']
        games['name'] = game['name']
        games['publish_date'] = game['released']
        games['rating'] = game['rating']
        platform_type = []
        platform_num = 0
        for platform in game['platforms']:
            platform_type.append(platform['platform']['name'])
            platform_num += 1
        games['platform'] = platform_type
        games['platform_count'] = platform_num
        game_data[id] = games
        
    game_df = pd.DataFrame.from_dict(game_data)
    game_df = game_df.to_json()
    game_info = json.loads(game_df)
    return game_info

def update_platform():
  mydb = myclient['platforms']
  platform_list = mydb.list_collection_names()
  platform_info = get_platform()

  for platform in platform_info:
    mycol = mydb[platform]
    value = platform_info[platform]
    if platform in platform_list:
      mycol.drop()
      mycol.insert_one(value)
      print(platform + ' is updated')
    else:
      mycol.insert_one(value)
      print(platform + 'is created')

def updated_game():
  mydb = myclient['game']
  game_list = mydb.list_collection_names()
  game_info = get_game()

  for game in game_info:
    mycol = mydb[game]
    value = game_info[game]
    if game in game_list:
      mycol.drop()
      mycol.insert_one(value)
      print(game + ' is updated')
    else:
      mycol.insert_one(value)
      print(game + ' is created')

# update_platform()
# updated_game()
mydb = myclient['platforms']


@app.route('/')
def index():
	return render_template('index.html') 

@app.route('/platforms')
def platforms_chart():
  mydb = myclient['platforms']
  platform_list = mydb.list_collection_names()
  data = { "Platforms" : "Games count"}
  print(type(data))

  for platform in platform_list:
      mycol = mydb[platform]
      platform_info = mycol.find_one()
      platform_data = {platform_info['name'] : platform_info['games_count']}
      data = {**data, **platform_data}

  return render_template('platforms.html', data=data) 

@app.route('/games')
def game_chart():
  mydb = myclient['game']
  game_list = mydb.list_collection_names()
  data = { "Game" : "Review"}
  print(type(data))

  for game in game_list:
      mycol = mydb[game]
      game_info = mycol.find_one()
      game_data = {game_info['name'] : game_info['rating']}
      data = {**data, **game_data}

  return render_template('games.html', data=data) 

if __name__ == "__main__":
  app.run()