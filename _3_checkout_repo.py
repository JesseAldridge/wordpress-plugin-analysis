import subprocess, os, math

import _2_scrape_plugin_pages

def main():
  new_labels = [
    'title', 'slug', 'my_score', 'weighted >', 'active_installs', 'weighted >', 'relevance',
    'weighted >', 'review_count', 'weighted >', 'avg_rating', 'lines_of_code',
  ]
  _2_scrape_plugin_pages.augment_csv(pull_svn, new_labels)


def pull_svn(row):
  plugin_slug = row[1]
  repos_dir = os.path.expanduser('~/wordpress-plugin-repos')
  if not os.path.exists(repos_dir):
    os.mkdir(repos_dir)
  repo_dir = os.path.join(repos_dir, plugin_slug)
  if(not os.path.exists(repo_dir)):
    command_svn = [
      'svn',
      'checkout',
      'https://plugins.svn.wordpress.org/{}/trunk'.format(plugin_slug),
      repo_dir,
    ]
    subprocess.Popen(command_svn).communicate()

  std_out_str = subprocess.Popen(['tokei', repo_dir], stdout=subprocess.PIPE).communicate()[0]
  lines_of_code = None
  for line in str(std_out_str, 'utf8').splitlines():
    print('line:', line)
    if line.startswith(' Total   '):
      lines_of_code = int(line.strip().split()[3])

  new_row = [x for x in row] + [lines_of_code]
  # go for low lines of code counts
  print('old score:', new_row[2])
  new_score = (float(new_row[2]) + -math.log(lines_of_code) if lines_of_code else 0) / 2
  new_row[2] = round(new_score, 2)
  print('new score:', new_row[2])
  return new_row

if __name__ == '__main__':
  main()
