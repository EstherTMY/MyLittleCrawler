from bs4 import BeautifulSoup
import requests

# Replaced with group member IDs
user_ids = ['','','']
# How many problems this group should solved today
threhold = 2

user_url_list = []
for id in user_ids:
    user_url = 'https://leetcode.com/{}/'.format(id)
    page = requests.get(user_url)
    soup = BeautifulSoup(page.text, 'lxml')
    recent_submissions = soup.find_all('a',attrs={'class':'list-group-item'})
    recent_submissions_list = []
    for item in recent_submissions:
        if(item.get('href') != None and item.find(attrs={'class':'badge'}) != None):
            recent_submissions_dic = {
                'problem_name' : item.get('href').split('/')[2],
                'submission_msg' : item.find(attrs={'class':'badge'}).get_text().strip(),
                'programming_lan' : item.find(attrs={'class':'badge progress-bar-info'}).get_text().strip(),
                'time' : item.find(attrs={'class':'text-muted'}).get_text().strip()
            }
            recent_submissions_list.append(recent_submissions_dic)
    finished_today = []
    for recent_submissions in recent_submissions_list:
        time = recent_submissions['time']
        time = time.split(",")[0]
        time = time.split(" ")[0]
        if(time[-5:] == 'hours' or time[-4:] == 'hour'):
            if(recent_submissions['submission_msg'] == 'Accepted'):
                finished_today.append(recent_submissions)
    if(len(finished_today) >= threhold):
        print (id + " finished today's work!!!")
        for submission in finished_today:
            print (submission)
    else:
        print (id + " should give", threhold - len(finished_today), "red pocket!!!")
        for submission in finished_today:
            print (submission)



