ps aux | grep mon_client | grep python | awk '{print $2}' | xargs kill -9
