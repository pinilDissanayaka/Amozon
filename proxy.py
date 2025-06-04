import os
import threading
import queue
import requests



q = queue.Queue()   

valid_proxies = []  


with open('proxy.txt', 'r') as file:
    proxies = file.read().split("\n")
    
    for p in proxies:
            q.put(p)
            
            
def check_proxy():
    global q
    
    while not q.empty():
        proxy = q.get()
        try:
            res=requests.get(
                "https://ipinfo.io/json",
                proxies={"http": proxy, "https": proxy},
            )
        except:
            continue
        
        if res.status_code == 200:
            print(f"Valid proxy found: {proxy}")
            with open('valid_proxies.txt', 'a') as valid_file:
                valid_file.write(proxy + "\n")
            
            
for _ in range(10):  # Adjust the number of threads as needed
    t = threading.Thread(target=check_proxy)
    t.start()