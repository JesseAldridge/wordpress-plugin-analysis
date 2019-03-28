import os, re, shutil

import _1_scrape_plugins_list

plugin_slug = 'elementor'

if not os.path.exists('reviews'):
  os.mkdir('reviews')

# <a class="bbp-topic-permalink" href="https://wordpress.org/support/topic/excellent-plugin-a-great-help-for-anyone/">Excellent plugin…! a great help for anyone <div class="wporg-ratings" title="5 out of 5 stars" style="color:#ffb900;"><span class="dashicons dashicons-star-filled"></span><span class="dashicons dashicons-star-filled"></span><span class="dashicons dashicons-star-filled"></span><span class="dashicons dashicons-star-filled"></span><span class="dashicons dashicons-star-filled"></span></div></a>


review_url_regex = '<a class="bbp-topic-permalink" href="(.+?)">'

'''
<div class="bbp-topic-content">
        <p>Excellent plugin…! a great help for anyone</p>
</div>
'''
review_text_regex =  '<div class="bbp-topic-content">(.+?)</div>'

review_stars_regex = "title='([0-5]) out of 5 stars'"

# <h1 class="page-title">Excellent plugin…! a great help for anyone</h1>
review_title_regex = '<h1 class="page-title">(.+?)</h1>'

out_path = 'reviews/{}_reviews.csv'.format(plugin_slug)
column_names = ['title', 'stars', 'url', 'text']

with _1_scrape_plugins_list.Writer(out_path, column_names) as writer:
  for page_number in range(1, 50):
    reviews_url = (
      'https://wordpress.org/support/plugin/{}/reviews/page/{}'.format(plugin_slug, page_number)
    )
    list_html = _1_scrape_plugins_list.cached_pull(reviews_url, secs_sleep_after_request=2)

    # https://wordpress.org/support/plugin/elementor/reviews/page/1
    # ~/wordpress_plugin_pages_cache/https___wordpress_org_support_plugin_elementor_reviews_

    for review_url_match in list(re.finditer(review_url_regex, list_html)):
      review_url = review_url_match.group(1)
      print("pulling:", review_url)
      review_html = _1_scrape_plugins_list.cached_pull(review_url, secs_sleep_after_request=2)

      # https://wordpress.org/support/topic/excellent-plugin-a-great-help-for-anyone/

      review_title = re.search(review_title_regex, review_html).group(1)
      review_text = re.search(review_text_regex, review_html, flags=re.DOTALL).group(1)
      review_stars = int(re.search(review_stars_regex, review_html).group(1))
      writer.write([review_title, review_stars, review_url, review_text])
