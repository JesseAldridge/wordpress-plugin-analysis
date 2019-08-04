import os, re, shutil, json, csv, math

import _1_scrape_plugins_list

def _augment_csv(config_dict, process_row, new_labels):
  with open(config_dict['csv-filename']) as f:
    rows = [row for row in csv.reader(f)][1:]

  if not rows:
    print("no rows")
    return

  new_rows = []
  start = config_dict.get('start') or 1
  limit = config_dict.get('limit')
  end = len(rows)
  if limit:
    end = min(start + limit, end)
  for irow in range(start, end):
    row = rows[irow]
    print("{:>4}/{:<4}: {}".format(irow + 1, len(rows), row))
    new_rows.append(process_row(row))
    if irow % 100 == 0:
      write_results(new_rows, new_labels, config_dict)
  write_results(new_rows, new_labels, config_dict)

def pull_plugin_details(row):
  review_count_regex = (
    '<div class="reviews-total-count"><span itemprop="reviewCount">([0-9,]+)</span> reviews?</div>'
  )

  avg_rating_regex = r'([0-9\.]+) out of <span itemprop="bestRating">5</span> stars'

  title, plugin_slug, active_installs, relevance = row[:4]
  active_installs, relevance = int(active_installs), float(relevance)
  reviews_url = 'https://wordpress.org/support/plugin/{}/reviews/'.format(plugin_slug)
  html = _1_scrape_plugins_list.cached_pull(reviews_url, secs_sleep_after_request=0)
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
  return [round(x, 2) if hasattr(x, '__round__') else x for x in new_row]

def write_results(new_rows, new_labels, config_dict):
  path = config_dict.get('csv-filename')
  with _1_scrape_plugins_list.Writer(path, new_labels) as writer:
    for row in sorted(new_rows, key=lambda row: -row[2]):
      print('writing row:', row)
      writer.write(row)
  print('wrote to:', path)

def augment_csv(pull_plugin_details, new_labels):
  _1_scrape_plugins_list.run_with_config(
    lambda config_dict: _augment_csv(config_dict, pull_plugin_details, new_labels)
  )

def main():
  new_labels = [
    'title', 'slug', 'my_score', 'weighted', 'active_installs', 'weighted', 'relevance',
    'weighted', 'review_count', 'weighted', 'avg_rating',
  ]
  augment_csv(pull_plugin_details, new_labels)

if __name__ == '__main__':
  main()
