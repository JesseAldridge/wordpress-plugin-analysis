import re, time, os, shutil, HTMLParser

import requests

cache_dir_path = os.path.expanduser('~/wordpress_plugin_pages_cache')

def cached_pull(url, secs_sleep_after_request=None):
  url_filename = re.sub(r'[^A-Za-z0-9_\-]', '_', url)
  cache_file_path = os.path.join(cache_dir_path, url_filename)
  if os.path.exists(cache_file_path):
    with open(cache_file_path) as f:
      return f.read()
  if not os.path.exists(cache_dir_path):
    os.mkdir(cache_dir_path)

  resp = requests.get(url)
  if secs_sleep_after_request:
    time.sleep(secs_sleep_after_request)
  with open(cache_file_path, 'w') as f:
    f.write(resp.content)
  return resp.content

'''
<h2 class="entry-title"><a href="https://wordpress.org/plugins/contact-form-7/" rel="bookmark">Contact Form 7</a></h2>
'''

class Writer:
  def __init__(self, filename, field_names):
    self.filename = filename
    if os.path.exists(filename):
      shutil.move(filename, filename + '.old')

    with open(filename, 'w') as f:
      f.write('{}\n'.format(','.join(field_names)))

  def write(self, vals):
    with open(self.filename, 'a') as f:
      f.write('{}\n'.format(','.join([str(x) for x in vals])))

def main():
  url = 'https://wordpress.org/plugins/browse/popular/page/{}/'
  num_pulls = 50
  filename = 'plugins1.csv'

  writer = Writer(filename, ['slug', 'active_installs'])
  for i in range(1, num_pulls):
    print 'pulling page:', i
    html = cached_pull(url.format(i), secs_sleep_after_request=2)

    plugin_links = []
    link_regex = '<h2 class="entry-title"><a href="https://wordpress.org/plugins/(.+?)/"'
    active_installs_regex = r'([0-9,a-zA-Z \+]+?) active installations\s+</span>'
    for link_match, active_installs_match in zip(
      re.finditer(link_regex, html),
      re.finditer(active_installs_regex, html),
    ):
      slug = link_match.group(1)
      active_installs_str = re.sub(r'\+ million', '000000', active_installs_match.group(1))
      active_installs_str = re.sub(',', '', active_installs_str)
      active_installs_str = re.sub(r'\+', '', active_installs_str)
      writer.write([slug, int(active_installs_str)])

if __name__ == '__main__':
  main()
