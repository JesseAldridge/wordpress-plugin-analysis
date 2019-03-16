import os, re, shutil

import scrape_plugins_list

with open('plugin_links.txt') as f:
  text = f.read()
lines = text.splitlines()

# https://wordpress.org/plugins/contact-form-7/
# https://wordpress.org/support/plugin/contact-form-7/reviews/

review_count_regex = (
  '<div class="reviews-total-count"><span itemprop="reviewCount">([0-9,]+)</span> reviews?</div>'
)

avg_rating_regex = r'([0-9\.]+) out of <span itemprop="bestRating">5</span> stars'

if os.path.exists('plugins.csv'):
  shutil.move('plugins.csv', 'plugins_old.csv')

with open('plugins.csv', 'w') as f:
  f.write('slug,review_count,avg_rating\n')

for base_url in lines:
  print 'base_url:', base_url
  plugin_slug = base_url.split('/')[-2]
  reviews_url = 'https://wordpress.org/support/plugin/{}/reviews/'.format(plugin_slug)
  html = scrape_plugins_list.cached_pull(reviews_url, secs_sleep_after_request=2)
  match = re.search(review_count_regex, html)
  review_count_str = match.group(1)
  review_count = int(re.sub(',', '', review_count_str))
  match = re.search(avg_rating_regex, html)
  avg_rating_str = match.group(1)
  with open('plugins.csv', 'a') as f:
    f.write('{},{},{}\n'.format(plugin_slug, review_count, avg_rating_str))
