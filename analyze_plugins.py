import collections

with open('config.json') as f:
  text = f.read()
config_dict =  json.loads(text)

with open(config_dict.get('csv-filename')) as f:
  text = f.read()
lines = text.splitlines()

def rank_plugin(line):
  slug, review_count, avg_rating = line.split(',')
  return float(avg_rating) * 8000 + int(review_count)

# for line in sorted(lines[1:], key=rank_plugin, reverse=True)[:100]:
#   print int(rank_plugin(line)), line

histo = collections.defaultdict(list)
for line in lines[1:]:
  slug, review_count, avg_rating = line.split(',')
  avg_rating = float(avg_rating)
  if avg_rating < 2:
    histo[1].append(slug)
  elif avg_rating < 3:
    histo[2].append(slug)
  elif avg_rating < 4:
    histo[3].append(slug)
  elif avg_rating < 4.25:
    histo[4].append(slug)
  elif avg_rating < 4.5:
    histo[4.25].append(slug)
  elif avg_rating < 4.75:
    histo[4.5].append(slug)
  elif avg_rating < 4.9:
    histo[4.75].append(slug)
  else:
    histo[4.9].append(slug)

for k in sorted(histo.keys()):
  print k, len(histo[k])
