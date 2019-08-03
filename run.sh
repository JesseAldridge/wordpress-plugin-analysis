mkdir -p ~/wordpress-plugin-output
python3 -u _1_scrape_plugins_list.py | tee ~/wordpress-plugin-output/out1.txt
python3 -u _2_scrape_plugin_pages.py | tee ~/wordpress-plugin-output/out2.txt
python3 -u _3_checkout_repo.py  | tee ~/wordpress-plugin-output/out3.txt
