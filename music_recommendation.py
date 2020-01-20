import csv
import math
import numpy as np

filename = "dataset.csv"

fields = []
rows = []
users = []


def find_distance(x,y):
    return math.sqrt(sum([(a-b)**2 for a,b in zip(x,y)]))

def find_k_neartest_songs(song, long_tail_songs, k):
    k_near_long_tail_songs = dict(sorted(long_tail_songs.items(), key=lambda x:find_distance(song,x[1]))[:k])
    return list(k_near_long_tail_songs.keys())

with open(filename,'r', encoding="utf8") as csvfile:
    csvreader = csv.reader(csvfile)
    fields = next(csvreader)
    for row in csvreader:
        for ind in range(len(row)):
            try:
                row[ind] = int(row[ind])
            except:
                users.append(row[ind])
        rows.append(row[1:])


test_data_length = int(0.3*len(rows))
test_users = users[:test_data_length]



del fields[0]

users_dict = {}
test_users_dict = {}
ind = 0
for user in users:
    users_dict[user] = rows[ind]
    ind += 1

ind = 0
for test_user in test_users:
    test_users_dict[test_user] = rows[ind]
    ind += 1

#print(test_users_dict)


songs = list(np.transpose(rows))
for ind in range(len(songs)):
    songs[ind] = list(songs[ind])

songs_dict = {}
ind = 0
for song in fields:
    songs_dict[song] = songs[ind]
    ind += 1


total_views =[sum(songs_dict[song]) for song in songs_dict]
width = (max(total_views)-min(total_views))//10

bins = [{} for i in range(3)]
for song in songs_dict:
    if sum(songs_dict[song]) < width:
        bins[0].update({song:songs_dict[song]})
    elif sum(songs_dict[song]) < width*2:
        bins[1].update({song:songs_dict[song]})
    else:
        bins[2].update({song:songs_dict[song]})

most_pop_songs = {}
med_pop_songs = {}
long_tail_pop_songs = {}

k = 3
for med_songs in bins[1]:
    long_tail_songs = find_k_neartest_songs(bins[1][med_songs], bins[0], k)
    med_pop_songs.update({med_songs: long_tail_songs})


for most_songs in bins[2]:
    long_tail_songs = find_k_neartest_songs(bins[2][most_songs], bins[1], k)
    most_pop_songs.update({most_songs: long_tail_songs})

for tail_songs in bins[0]:
    long_tail_songs = find_k_neartest_songs(bins[0][tail_songs], bins[0], k)
    long_tail_pop_songs.update({tail_songs: long_tail_songs[1:]})



def validate_model(user_name):
    user_songs_numbers = test_users_dict[user_name]
    user_songs_names = [ 's'+str(ind) for ind in range(len(user_songs_numbers)) if user_songs_numbers[ind]>0]
    rec_songs_list = set()
    head_songs = set()
    for song_input in user_songs_names:
        if song_input in most_pop_songs:
            head_songs.add(song_input)
            for med_song in most_pop_songs[song_input]:
              rec_songs_list.add(med_song)
              for tail_song in med_pop_songs[med_song]:
                  rec_songs_list.add(tail_song)

    user_songs_names = set(user_songs_names)
    user_songs_names_without_heads = user_songs_names-head_songs
    print('username:', user_name)
    print('recommended songs count:',len(rec_songs_list))
    #print('user songs count:',len(user_songs_names))
    print('user songs count without heads:', len(user_songs_names_without_heads))
    print('new recommendations count:',len(rec_songs_list-user_songs_names_without_heads))
    print('Recommendations that already viewed by user count:',len(rec_songs_list&user_songs_names_without_heads))
    print()
    result = {}
    result['user_songs'] = len(user_songs_names_without_heads)
    result['rec_songs'] = len(rec_songs_list)
    result['new_rec'] = len(rec_songs_list-user_songs_names_without_heads)
    result['matched'] = len(rec_songs_list&user_songs_names_without_heads)
    return result

total_user_songs = 0
total_recommendations = 0
total_new_recommendations = 0
total_match = 0

print('Test users:')
for test_user in test_users:
    result = validate_model(test_user)
    total_user_songs+=result['user_songs']
    total_recommendations+=result['rec_songs']
    total_new_recommendations+=result['new_rec']
    total_match+=result['matched']
print()
print('Total songs:',total_user_songs)
print('Total Recommendations:',total_recommendations)
print('Total New Recommendations:',total_new_recommendations)
print('Recommendations that already viewed by user:',total_match)

TP = total_match
FP = total_new_recommendations
FN = total_user_songs-total_match

print('TP:', TP)
print('FP:', FP)
print('FN:', FN)

precision = TP/(TP+FP)*100
recall = TP/(TP+FN)*100.

print('precision:',precision)
print('recall:',recall)



