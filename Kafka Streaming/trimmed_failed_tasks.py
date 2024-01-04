import pandas as pd
import json
class FailedTasks:
    def __init__(self):
        pass
    def save_to_json(self, video_url, video_name):
        failed_urls = []
        failed_video_name = []
        try: #if json available 
            f = open('failed_urls.json')
            data = json.load(f)
            for url, name in zip(data['failed_urls'],data['failed_video_names']):
                failed_urls.append(url)
                failed_video_name.append(name)
            f.close()
            
            failed_urls.append(video_url)
            failed_video_name.append(video_name)

            out_file = open("failed_urls.json", "a") 
            failed_url_data = {'failed_urls':failed_urls, 'failed_video_names':failed_video_name}
            json.dump(failed_url_data, out_file, indent = 4)
            out_file.close()
        except:
            out_file = open("failed_urls.json", "w")  
            failed_url_data = {'failed_urls':[video_url], 'failed_video_names':[video_name]}
            json.dump(failed_url_data, out_file, indent = 4)
            out_file.close()