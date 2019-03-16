import re, os

active_installs_regex = r'([0-9,a-z \+]+?) active installations\s+</span>'
path = os.path.expanduser(
  '~/wordpress_plugin_pages_cache/https___wordpress_org_plugins_browse_popular_page_1_'
)
with open(path) as f:
  html = f.read()

for match in re.finditer(active_installs_regex, html):
  print match.group(1), int(match.group(1))
