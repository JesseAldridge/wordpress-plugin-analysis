import os, re, shutil

import _1_scrape_plugins_list

with open('plugins1.csv') as f:
  text = f.read()
lines = text.splitlines()

review_count_regex = (
  '<div class="reviews-total-count"><span itemprop="reviewCount">([0-9,]+)</span> reviews?</div>'
)

avg_rating_regex = r'([0-9\.]+) out of <span itemprop="bestRating">5</span> stars'

writer = _1_scrape_plugins_list.Writer('plugins2.csv', [
  'slug', 'active_installs', 'review_count', 'avg_rating'
])

for line in lines[1:]:
  plugin_slug, active_installs = line.split(',')
  reviews_url = 'https://wordpress.org/support/plugin/{}/reviews/'.format(plugin_slug)
  html = _1_scrape_plugins_list.cached_pull(reviews_url, secs_sleep_after_request=2)
  match = re.search(review_count_regex, html)
  review_count_str = match.group(1)
  review_count = int(re.sub(',', '', review_count_str))
  match = re.search(avg_rating_regex, html)
  avg_rating_str = match.group(1)
  writer.write([plugin_slug, active_installs, review_count, avg_rating_str])
