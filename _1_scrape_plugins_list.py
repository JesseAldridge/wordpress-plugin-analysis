import re, time, os, shutil, csv, json

import requests

CACHE_DIR_PATH = os.path.expanduser('~/wordpress_plugin_pages_cache')

def run_with_config(func):
  with open('config.json') as f:
    text = f.read()
  config_dict = json.loads(text)
  config_dict['csv-filename'] = os.path.expanduser(
    config_dict['csv-filename'].format(**config_dict)
  )
  func(config_dict)

def cached_pull(url, secs_sleep_after_request=None):
  url_filename = re.sub(r'[^A-Za-z0-9_\-]', '_', url)
  cache_file_path = os.path.join(CACHE_DIR_PATH, url_filename)
  if os.path.exists(cache_file_path):
    with open(cache_file_path) as f:
      return f.read()
  if not os.path.exists(CACHE_DIR_PATH):
    os.mkdir(CACHE_DIR_PATH)

  resp = requests.get(url)
  out_str = resp.content.decode('utf-8')
  with open(cache_file_path, 'w') as f:
    f.write(out_str)

  if secs_sleep_after_request:
    time.sleep(secs_sleep_after_request)
  return out_str

'''
<h2 class="entry-title">
  <a href="https://wordpress.org/plugins/contact-form-7/" rel="bookmark">Contact Form 7</a>
</h2>
'''

class Writer:
  def __init__(self, path, column_labels):
    self.path = os.path.expanduser(path)
    if os.path.exists(path):
      shutil.move(path, path + '.old')
    self.column_labels = column_labels

  def __enter__(self):
    self.f = open(self.path, 'w')
    self.writer = csv.writer(self.f, lineterminator='\n')
    self.writer.writerow(self.column_labels)
    return self

  def __exit__(self, type, value, traceback):
    self.f.close()
    print('wrote to path:', self.path)

  def write(self, vals):
    self.writer.writerow(vals)

def scrape_plugins(config_dict):
  labels = ['title', 'slug', 'active_installs', 'relevance']
  with Writer(config_dict['csv-filename'], labels) as writer:
    scrape(config_dict, writer)

def scrape(config, writer):
  num_pulls = 50
  slugs_seen = set()

  for i in range(1, num_pulls):
    print('pulling page:', i)

    html = cached_pull(config.get('url').format(page=i, **config))

    if 'Showing results for:' not in html:
      break

    plugin_links = []
    title_regex = (
      '<h2 class="entry-title"><a href="https://wordpress.org/plugins/(.+?)/" '
      'rel="bookmark">(.+?)</a></h2>'
    )
    active_installs_regex = r'([/0-9,a-zA-Z \+]+?) active installations\s+</span>'
    for title_match, active_installs_match in zip(
      re.finditer(title_regex, html),
      re.finditer(active_installs_regex, html),
    ):
      slug, title = title_match.group(1), title_match.group(2)
      slugs_seen.add(slug)
      relevance = 0
      query_str = config.get("query_str")
      if query_str:
        for term in query_str.split():
          if term in title.lower():
            relevance = 1
            break
      print("title:", title)
      print("active_installs:", active_installs_match.group(1))
      active_installs_str = re.sub('Fewer than 10', '0', active_installs_match.group(1))
      active_installs_str = re.sub('N/A', '0', active_installs_str)
      active_installs_str = re.sub(r'\+ million', '000000', active_installs_str)
      active_installs_str = re.sub(',', '', active_installs_str)
      active_installs_str = re.sub(r'\+', '', active_installs_str)
      writer.write([title, slug, int(active_installs_str), relevance])

def test():
  try:
    print("testing")
    path = "plugins-test.csv"
    assert not os.path.exists(path)
    print('writing to path:', path)
    with Writer(path, ['title', 'slug', 'active_installs', 'relevance']) as writer:
      writer.write([0,0,0,0])
    with open(path) as f:
      text = f.read()
    assert text == "title,slug,active_installs,relevance\n0,0,0,0\n"
  finally:
    os.remove('plugins-test.csv')

if __name__ == '__main__':
  test()
  run_with_config(scrape_plugins)
