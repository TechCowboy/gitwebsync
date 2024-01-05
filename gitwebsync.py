# gitwebsync
# by Norman Davie

import requests
from bs4 import BeautifulSoup
import os
import subprocess
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

## Change this to your account
account = "https://github.com/TechCowboy"
## where to find the chrome driver
## Download from here:
## https://www.selenium.dev/documentation/webdriver/browsers/

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
    
def repositories_needing_updates(repositories_to_update):

    page_num = 0
    for repository in repository_links:
        page_num += 1
        
        #if page_num > 10:
        #    break
        
        print(str(page_num).rjust(5) + " of " + str(len(repository_links)).rjust(5) + "  ", end='')
        page = requests.get(repository)
        soup = BeautifulSoup(page.content, "html.parser")
        
        result = soup.find("div", class_="d-flex flex-auto")
        if result == None:
            print("Not fork'd " + repository)
            continue
        
        result = str(result)
        position =  result.find("This branch is up to date")
        if position == -1:
            position = result.find("commits behind")
            if position == -1:
                position = result.find("commit behind")
            if position != -1:
                print("Needs Sync " + repository)
                repositories_to_update.append(repository)
            else:
                print("Newer      " + repository)
        else:
                print("Up to date " + repository)

    print()
    
def web_sync_repositories(repositories_to_update, driver):

    if len(repositories_to_update) == 0:
        print("Everything is up to date.")
    else:
        for repository in repositories_to_update:
            element_found = False
            while not element_found:
                print(f"Syncing {repository} ", end='')
                
                driver.get(repository)
                time.sleep(1)
                #driver.maximize_window()
                #time.sleep(1)
                element_found = False
                try:
                    full_xpath = "/html/body/div[1]/div[6]/div/main/turbo-frame/div/div/div/div[2]/div[1]/react-partial/div/div/div[1]/div/div/div[2]/div[2]/div/div[3]/div[2]/div/button[2]/span[1]/span[2]"
                    xpath = '//*[@id=":rf:"]/span[1]/span[2]'
                    element = driver.find_element(By.XPATH, full_xpath) # was full_xpath
                    element_found = True

                except Exception as e:
                    print()
                    print("Could not find element:", full_xpath, "'")
                    print()
                    print(str(e))
                    print("You are probably not logged into your GitHub account on this profile")
                    print("Please sign in, close the browser, and re-run this application")
                    exit(-1)
                    
                if element_found:
                    print("<Clicking Sync> ", end='')
                    element.click()
                    time.sleep(1)
                else:
                    print("Could not find sync element")
                    continue

                element_found = False
                time.sleep(1)
                try:
                    full_xpath = "/html/body/div[4]/div/div/div/div/div[2]/button/span/span"
                    xpath = '//*[@id=":rf:"]/span[1]/span[2]'
                    element = driver.find_element(By.XPATH, full_xpath)
                    element_found = True

                except Exception as e:
                    element_found = False
                
                    
                if element_found:
                    print("<Clicking Update Branch>")
                    time.sleep(1)
                    element.click()
                    time.sleep(1)
                else:
                    print("Could not find update button - retry")
                    continue


            #while True:
            #    try:
            #        text = element.text
            #        print(f"text: {text}", end='')
            #    except:
            #        break

            print()
        

    print("Done Web Syncing.")


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
        
        behind = output.find("Your branch is behind") >= 0
        modified = output.find("modified:") >= 0
        untracked = output.find("Untracked files:") >= 0
        uptodate = output.find("Your branch is up to date with") >= 0
        
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



if __name__ == "__main__":
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
        print(str(e))
        exit(-2)
        
    os.chdir(old_path)
    driver.get(account)
    time.sleep(1)
    driver.maximize_window()
    time.sleep(1)
    
    repository_links = []
    collecting_web_repositories(repository_links)

    repositories_to_update = []
    repositories_needing_updates(repositories_to_update)
    
    web_sync_repositories(repositories_to_update, driver)
    
    driver.close()
    driver.quit()
    
    git_dirs = []
    get_local_repositories(git_dirs)

    sync_local_repositories(git_dirs)
    
    