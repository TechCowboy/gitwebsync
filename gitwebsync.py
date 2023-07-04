import requests
from bs4 import BeautifulSoup

print("In Progress...")
account = "https://github.com/TechCowboy"
URL = account + "?tab=repositories"
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")

results = soup.find_all("div", class_="d-inline-block mb-1")

repository_links = []
for repository in results:
    a_href=repository.find("a").get("href")
    repository_links.append("https://github.com" + a_href)

repositories_to_update = []

for repository in repository_links:
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
if len(repositories_to_update) == 0:
    print("Everything is up to date.")
else:
    print("need to update:")
    for repository in repositories_to_update:
        print(repository)
        
