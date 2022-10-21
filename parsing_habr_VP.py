from pydoc import source_synopsis
import requests as req
from bs4 import BeautifulSoup
import json

page_n = 1
while True:
    url = "https://career.habr.com/vacancies?page=" + str(page_n) + "&q=python%20%D1%80%D0%B0%D0%B7%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D1%87%D0%BA&type=all"
    resp = req.get(url)
    soup = BeautifulSoup(resp.text, "lxml")
    #with open(str(page_n) + ".html", 'w', encoding='utf8') as htmlfile:
    #    htmlfile.write(resp.text)

    paginator = soup.find(class_="paginator").find("a", {"class":"next_page"})

    tags = soup.find_all(class_="vacancy-card__title-link")
    vac_list = []

    for iter in tags:
        vac_dict = {"Title":iter.text, "Employer":"", "Requirements":[], "Location":[]}
        locations_set = set()

        resp = req.get("https://career.habr.com" + iter.attrs["href"])
        with open(iter.attrs["href"][-10:] + ".html", 'w', encoding='utf8') as htmlfile:
            htmlfile.write(resp.text)

        inner_soup1 = BeautifulSoup(resp.text, "lxml")
        vac_dict["Employer"] = inner_soup1.find("div", {"class":"company_name"}).find("a").text;

        vac_reqs_and_loc = inner_soup1.find_all(class_="content-section")
        if vac_reqs_and_loc:
            for iter_title in vac_reqs_and_loc:
                section_title = iter_title.find("h2", {"class":"content-section__title"}).text
                if section_title == "Требования":
                    for required in iter_title.find_all("a"):
                        vac_dict["Requirements"].append(required.text)
        
                if section_title == "Местоположение и тип занятости":
                    vac_locations = iter_title.find_all("a")

                    if len(vac_locations) > 0:
                        for vac_loc in vac_locations:
                            if vac_loc.text not in locations_set:
                                locations_set.add(vac_loc.text)
                    else:

                        vac_locations = iter_title.find(class_="inline-list").find_all("span")
                        for vac_loc in vac_locations:
                            if "class" in vac_loc.attrs:
                                if vac_loc.attrs["class"][0] != 'inline-separator' and len(vac_loc.text) > 1 and "день" not in vac_loc.text.split():
                                    if vac_loc.text not in locations_set:
                                        locations_set.add(vac_loc.text)

                    vac_locations = iter_title.find(class_="inline-list").find_all("span")
                    for vac_loc in vac_locations:
                        if vac_loc.text == "Можно удалённо" or vac_loc.text == "Можно удаленно":
                            if vac_loc.text not in locations_set:
                                locations_set.add(vac_loc.text)
                    
        vac_dict["Location"] = [*locations_set,]
        print(vac_dict["Title"] + " @ " + vac_dict["Employer"]  + " : " + ", ".join(vac_dict["Requirements"])  + ". " + ", ".join(vac_dict["Location"]))
        vac_list.append(vac_dict)
        #break
    if paginator == None:
        break
    page_n += 1
    
with open("career_habr.json", 'w', encoding='utf8') as outfile:
    json.dump({"data":vac_list}, outfile, ensure_ascii=False, indent=4)
