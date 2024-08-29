# gitwebsync
# by Norman Davie

import requests
from bs4 import BeautifulSoup
import os
import subprocess
import time
from pathlib import Path
import pyautogui as pag
import clipboard as cb

from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

## Change this to your account
account = "https://github.com/TechCowboy"
## where to find the chrome driver
## Download from here:
## https://www.selenium.dev/documentation/webdriver/browsers/
## https://googlechromelabs.github.io/chrome-for-testing/

chromedriver = "chromedriver"

def collecting_web_repositories(repository_links):
    
    print("Collecting Web Repositories...", end='')

    done = False
    page_number = 1
    while True:
        URL = account + "?page="+str(page_number) + "&tab=repositories"
        print(".", end='')
        page = requests.get(URL)

        soup = BeautifulSoup(page.content, "html.parser")

        results = soup.find_all("div", class_="d-inline-block mb-1")
        if results == []:
            break
        

        for repository in results:
            a_href=repository.find("a").get("href")
            repository_links.append("https://github.com" + a_href)
            
        page_number += 1
        


    print()
    
def top_of_page():
    for i in range(10):
        print("up")
        pag.hotkey('arrow up')
        
def find_first(desired_result, no_ctrl_enter=False, copy=True):

    cb.copy("")

    pag.hotkey('ctrl','f')
    pag.hotkey('backspace')
    
    pag.typewrite(desired_result)
    if no_ctrl_enter:
        pag.hotkey('enter')
    else:
        pag.hotkey('ctrl', 'enter')
    
    if copy:
        pag.hotkey('esc')
    
        pag.hotkey('ctrl','c')
        result = cb.paste()
    else:
        result = ""
        
    return desired_result == result


def find_occurance(desired_result, occurance):

    #top_of_page()
    pag.PAUSE=0.3
    cb.copy("")
    pag.hotkey('ctrl','f')
    pag.hotkey('backspace')
    pag.typewrite(desired_result)
    
    pag.hotkey('tab')
    pag.hotkey('tab')
    for i in range(occurance-1):
        pag.hotkey("enter")

    pag.hotkey('shift','tab')
    pag.hotkey('shift','tab')
        
    pag.hotkey('ctrl','enter')
    
    pag.PAUSE=0.3
    
    return 


def sync_repositories(repositories_to_update):

    notices = []
    
    page_num = 0
    for repository in repository_links:
        page_num += 1
        
        print(str(page_num).rjust(5) + " of " + str(len(repository_links)).rjust(5) + "  ", end='')
        print(repository)
        
        driver.get(repository)
        
        window_title = repository
        
        desired_result = "forked from"
        forked = find_first(desired_result, no_ctrl_enter=True)
        if not forked:
            print("Not forked")
            continue
        
        
        desired_result = "This branch is up to date with"
        already_synced = find_first(desired_result)
        
        if already_synced:
            print("Up to date")
            continue
         
        desired_result = "commits behind"
        commits_behind = find_first(desired_result, no_ctrl_enter=True)
        
        desired_result = "commit behind"
        commit_behind = find_first(desired_result, no_ctrl_enter=True)
        
        sync_required = commits_behind or commit_behind
           
        if sync_required:
            print("Syncing...")
            
            desired_result = 'Sync fork'
            sync_branch = find_first(desired_result, copy=False)
            
            desired_result = 'Update branch'
            update_branch = find_occurance(desired_result, 2)
            
            desired_result1 = "commits behind"
            desired_result2 = "commit behind"
            not_yet_synced = True
            
            retry = 0
            while not_yet_synced:
                time.sleep(2)
                not_yet_synced = find_first(desired_result1)
                if not_yet_synced:
                    not_yet_synced = find_first(desired_result2)
                
                retry += 1
                if retry == 10:
                    retry = 0
                    pag.hotkey('F5')
                    time.sleep(3)
                    
            
        else:
            
            desired_result = "commits ahead"
            commits_ahead = find_first(desired_result, no_ctrl_enter=True)
            
            desired_result = "commit ahead"
            commit_ahead = find_first(desired_result, no_ctrl_enter=True)
            if commit_ahead or commits_ahead:
                print("We have uncommited commits.")
                notices.append(f"missing commits {repository}")
            
            
    print()
    
    for n in notices:
        print(n)
    
    


# get directories
def get_local_repositories(git_dirs):
    debug = 1

    print("Finding local git repositories...")
    cwd = os.getcwd()

    if debug:
        cwd = os.path.abspath(os.path.join(cwd, os.pardir))
        os.chdir(cwd)

    all_dirs = os.listdir(cwd)

    for dir in all_dirs:
        if os.path.isdir(dir):
            if os.path.exists(os.path.join(dir, ".git")):
                git_dirs.append(os.path.abspath(dir))

    total_dirs = len(git_dirs)
    print(f"{total_dirs} git directories found")
    
def sync_local_repositories(git_dirs):
    print("Getting the latest status on each remote repositories...")
    total_dirs = len(git_dirs)
    status_size = 45
    for dir in git_dirs:
        os.chdir(dir)
        count = f"{total_dirs}"
        print(f"{count:3} {dir:70}\r", end='')
        result = subprocess.run(['git', 'remote','-v','update'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        total_dirs -= 1
    print(f"{' ':75}\r")

    pull_info = ''
    total_up_to_date=0

    latest_but_modified = 'Lastest from remote but local files modified'

    for dir in git_dirs:
        os.chdir(dir)
        result = subprocess.run(['git', 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        
        behind    = output.find("Your branch is behind") >= 0
        modified  = output.find("modified:") >= 0
        untracked = output.find("Untracked files:") >= 0
        uptodate  = output.find("Your branch is up to date with") >= 0
        
        if uptodate:
            if modified:
                but_modified = "but modified"
                print(f"{latest_but_modified:45} {dir}")
            else:
                but_modified = ""
                total_up_to_date += 1
            
        else:
            
            if behind:           
                if modified:
                    print(f"{'Behind but files modified':45} {dir}")
                    result = subprocess.run(['git', 'pull'], stdout=subprocess.PIPE)
                    pull_info += result.stdout.decode('utf-8')
                    print(pull_info)
                else:
                    print(f"{'Pulling lastest files':45} {dir}")
                    result = subprocess.run(['git', 'pull'], stdout=subprocess.PIPE)
                    pull_info += result.stdout.decode('utf-8')
                    print(pull_info)
            else:
                total_up_to_date += 1

    print()
    print(f"{total_up_to_date} repositories are up to date")         

def get_urls_of_local_repositories(git_dirs, git_urls):
    
    print("Getting URLs from local repositories...")
    
    for dir in git_dirs:
        os.chdir(dir)
        
        result = subprocess.run(['git', 'remote','-v'], stdout=subprocess.PIPE)
        lines = result.stdout.decode('utf-8').split("\n")
        line = lines[0][:-8]
        columns = line.split('\t')
        url = columns[1]
        
        if columns[0] == 'origin':
            url = url.replace('git@github.com:', 'https://github.com/')
            print(url)
            git_urls.append(url)
            
    print()
    print(f"{len(git_urls)} repositories collected") 
    

if __name__ == "__main__":
    
    all = False
    
    if all:
        print("Updating all web repositories")
    else:
        print("Only updating web repositories with corresponding local repositories")
        
        
    ## create an object of the chrome webdriver
    
    option = webdriver.ChromeOptions()
    # line below needed for brave browser
    option.binary_location = '/usr/bin/brave-browser-stable'
    
    # create a profile that persists between sessons
    # log into your github account from this session the first time run
    option.add_argument("user-data-dir=home/ndavie2/.config/BraveSoftware/Brave-Browser");

    old_path = os.getcwd()
    print(f"{old_path}")
    home_path = Path.home()
    print(f"{home_path}")
    os.chdir(home_path)
    
    driver_path = os.path.join(home_path, chromedriver)
    print(f"{driver_path}")
    s = Service(driver_path)
    print("sleeping 2 seconds")
    time.sleep(2)


    try:
        driver = webdriver.Chrome(service=s, options=option)
    except Exception as e:
        print("webdriver failed.")
        print("Need new version? https://googlechromelabs.github.io/chrome-for-testing/#stable ")
        print(str(e))
        exit(-2)
        
    os.chdir(old_path)
    driver.get(account)
    time.sleep(1)
    #driver.maximize_window()
    #time.sleep(1)
    
    # get the names of the local git directories
    git_dirs = []
    get_local_repositories(git_dirs)
    
    # get the urls of the local git's
    repository_links = []
    if not all:
        get_urls_of_local_repositories(git_dirs, repository_links)
    else:
        collecting_web_repositories(repository_links)

    repositories_to_update = []
    sync_repositories(repositories_to_update)
    
    driver.close()
    driver.quit()
    
    

    sync_local_repositories(git_dirs)
    
    
