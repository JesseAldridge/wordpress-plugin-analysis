
config.json should look something like this:
```
{
  "url": "https://wordpress.org/plugins/search/video/page/{}/",
  "csv-filename": "plugins-video.csv",
  "query_str": "video youtube player"
}
```

./run.sh

Then upload the generated csv file to Google Sheets.

# run on remote server
ssh my-server
nohup sh -c 'python3 _1_scrape_plugins_list.py; python3 _2_scrape_plugin_pages.py' &
