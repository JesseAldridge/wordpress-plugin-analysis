import re, time, os, shutil, HTMLParser

import requests

cache_dir_path = os.path.expanduser('~/plugin_pages_cache')

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

def main():
  url = 'https://wordpress.org/plugins/browse/popular/page/{}/'
  num_pulls = 50
  shutil.move('plugin_links.txt', 'plugin_links_old.txt')
  for i in range(1, num_pulls):
    print 'pulling page:', i
    html = cached_pull(url.format(i), secs_sleep_after_request=2)

    plugin_links = []
    plugin_regex = '<h2 class="entry-title"><a href="(https://wordpress.org/plugins/.+?/)"'
    for plugin_match in re.finditer(plugin_regex, html):
      plugin_links.append(plugin_match.group(1))

    with open('plugin_links.txt', 'a') as f:
      f.write('\n'.join(plugin_links) + '\n')

if __name__ == '__main__':
  main()
