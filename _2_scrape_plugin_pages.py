import os, re, shutil, json, csv, math

import _1_scrape_plugins_list

def main():
  with open('config.json') as f:
    text = f.read()
  config_dict = json.loads(text)

  with open(config_dict.get('csv-filename').format(**config_dict)) as f:
    rows = [row for row in csv.reader(f)]

  review_count_regex = (
    '<div class="reviews-total-count"><span itemprop="reviewCount">([0-9,]+)</span> reviews?</div>'
  )

  avg_rating_regex = r'([0-9\.]+) out of <span itemprop="bestRating">5</span> stars'

  new_rows = []
  for irow, row in enumerate(rows[1:]):
    title, plugin_slug, active_installs, relevance = row[:4]
    active_installs, relevance = int(active_installs), int(relevance)
    reviews_url = 'https://wordpress.org/support/plugin/{}/reviews/'.format(plugin_slug)
    print("{:>4}/{:<4} reviews_url: {}".format(irow + 1, len(rows), reviews_url))
    html = _1_scrape_plugins_list.cached_pull(reviews_url, secs_sleep_after_request=2)
    match = re.search(review_count_regex, html)
    review_count_str = match.group(1)
    review_count = int(re.sub(',', '', review_count_str))
    match = re.search(avg_rating_regex, html)
    avg_rating = float(match.group(1))
    weighted_active_installs = math.log(active_installs) if active_installs != 0 else 0
    weighted_relevance = relevance * 10
    weighted_review_count = math.log(review_count) if review_count != 0 else 0
    weighted_avg_rating = avg_rating
    my_score = (
      weighted_active_installs + weighted_relevance + weighted_review_count + weighted_avg_rating
    )
    new_row = [
      title,
      plugin_slug,
      my_score,
      weighted_active_installs,
      active_installs,
      weighted_relevance,
      relevance,
      weighted_review_count,
      review_count,
      weighted_avg_rating,
      avg_rating,
    ]
    new_rows.append([round(x, 2) if hasattr(x, '__round__') else x for x in new_row])
    if irow % 100 == 0:
      write_results(new_rows, config_dict)
  write_results(new_rows, config_dict)

def write_results(new_rows, config_dict):
  with _1_scrape_plugins_list.Writer(config_dict.get('csv-filename').format(**config_dict), [
    'title', 'slug', 'my_score', 'weighted', 'active_installs', 'weighted', 'relevance',
    'weighted', 'review_count', 'weighted', 'avg_rating',
  ]) as writer:
    for row in sorted(new_rows, key=lambda row: -row[2]):
      writer.write(row)

if __name__ == '__main__':
  main()
