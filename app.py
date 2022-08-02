import time
from flask import Flask, redirect, jsonify
from bs4 import BeautifulSoup
import requests
import urllib3
from threading import Thread
from database import Ieu_sfl, Ieu_announcement, Ieu_news

urllib3.disable_warnings()


ieu_sfl_announcements = []
ieu_announcements = []
ieu_news = []


def ieusfl():
    while True:
        website = requests.get("https://sfl.ieu.edu.tr/tr/announcements/type/all", verify=False)
        soup = BeautifulSoup(website.content.decode("utf-8"), features="html.parser")
        alldata = soup.select("body > main > div:nth-child(4) > div > div.col-xs-12.col-sm-12.col-md-8.col-lg-9.text-primary-color-content > div:nth-child(3) > div.card-body", href=True)[0]
        i = 1
        while True:
            data = alldata.select(f"a:nth-child({i})")
            if data == []:
                break
            url = str(data[0]["href"])
            date = data[0].select("div > p > strong")[0].text.strip()
            title = data[0].select("div > p")[0].text
            title = title.replace(date, "").strip()

            announcement = {"title": title, "url": url, "date": date}
            if announcement not in ieu_sfl_announcements:
                ieu_sfl_announcements.append(announcement)

            i += 1
        time.sleep(60)


def ieuannouncement():
    while True:
        website = requests.get("https://www.ieu.edu.tr/tr/announcements/type/all", verify=False)
        soup = BeautifulSoup(website.content.decode("utf-8"), features="html.parser")
        alldata = soup.select("#page-top > main > div.col-lg-10.offset-lg-1.pagecontent-top.mb-5.pt-5.pb-5.mainpage > div > div.col-lg-9.text-primary-color-content.border-left-2px-primary > div:nth-child(3) > div.card-body", href=True)[0]
        i = 1
        while True:
            data = alldata.select(f"a:nth-child({i})")
            if data == []:
                break
            url = str(data[0]["href"])
            date = data[0].select("div > p > strong")[0].text.strip()
            title = data[0].select("div > p")[0].text
            title = title.replace(date, "").strip()

            announcement = {"title": title, "url": url, "date": date}
            if announcement not in ieu_announcements:
                ieu_announcements.append(announcement)

            i += 1
        time.sleep(60)


def ieunews():
    while True:
        website = requests.get("https://www.ieu.edu.tr/tr/news/type/all", verify=False)
        soup = BeautifulSoup(website.content.decode("utf-8"), features="html.parser")
        alldata = soup.select("#page-top > main > div.col-lg-10.offset-lg-1.pagecontent-top.mb-5.pt-5.pb-5.mainpage > div > div.col-lg-9.text-primary-color-content.border-left-2px-primary", href=True)[0]
        i = 3
        while True:
            data = alldata.select(f"div:nth-child({i}) > div > div > div.card-body > div > div.col-.\\31 2.col-lg-9 > a")
            if data == []:
                break
            url = str(data[0]["href"])
            news = data[0].select("div > p")[0].text.strip()
            title = data[0].select("h2")[0].text.strip()

            announcement = {"title": title, "news": news, "url": url}
            if announcement not in ieu_news:
                ieu_news.append(announcement)

            i += 1
        time.sleep(60)


def telegram():
    botapi = ""
    chatid = ""
    while True:
        time.sleep(60)
        if ieu_sfl_announcements != []:
            for announcement in ieu_sfl_announcements:
                data = Ieu_sfl.select().where(Ieu_sfl.title == announcement["title"], Ieu_sfl.url == str(announcement["url"]), Ieu_sfl.date == announcement["date"])
                exist = False
                for x in data:
                    exist = True
                if exist == False:
                    Ieu_sfl.create(title=announcement["title"], url=announcement["url"], date=announcement["date"]).save()
                    message = f"<b>IEU SFL Announcement</b>\n<i>{announcement['title']}</i>\n{announcement['url']}\n<i>{announcement['date']}</i>"
                    requests.post(url=f"https://api.telegram.org/bot{botapi}/sendMessage", data={"chat_id": chatid, "text": message, "parse_mode": "html"}).json()

        if ieu_announcements != []:
            for announcement in ieu_announcements:
                exist = False
                data = Ieu_announcement.select().where(Ieu_announcement.title == announcement["title"], Ieu_announcement.url == announcement["url"], Ieu_announcement.date == announcement["date"])
                for x in data:
                    exist = True
                if exist == False:
                    Ieu_announcement.create(title=announcement["title"], url=announcement["url"], date=announcement["date"]).save()
                    message = f"<b>IEU Announcement</b>\n<i>{announcement['title']}</i>\n{announcement['url']}\n<i>{announcement['date']}</i>"
                    requests.post(url=f"https://api.telegram.org/bot{botapi}/sendMessage", data={"chat_id": chatid, "text": message, "parse_mode": "html"}).json()

        if ieu_news != []:
            for announcement in ieu_news:
                exist = False
                data = Ieu_news.select().where(Ieu_news.title == announcement["title"], Ieu_news.news == announcement["news"], Ieu_news.url == announcement["url"])
                for x in data:
                    exist = True
                if exist == False:
                    Ieu_news.create(title=announcement["title"], news=announcement["news"], url=announcement["url"]).save()
                    message = f"<b>IEU News</b>\n<b>{announcement['title']}</b>\n<i>{announcement['news']}</i>\n{announcement['url']}"
                    requests.post(url=f"https://api.telegram.org/bot{botapi}/sendMessage", data={"chat_id": chatid, "text": message, "parse_mode": "html"}).json()


app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False


@app.route("/")
def home():
    return """
    <h1>İzmir University of Economics</h1>
    <ul>
        <caption>API Service</caption>
        <li><a href='/ieu-announcements'>ieu-announcements</a></li>
        <li><a href='/ieu-news'>ieu-news</a></li>
        <li><a href='/ieu-sfl-announcements'>ieu-sfl-announcements</a></li>
    </ul>
    """


@app.route("/ieu-sfl-announcements")
def route_ieu_sfl_announcements():
    return jsonify(ieu_sfl_announcements)


@app.route("/ieu-announcements")
def route_ieu_announcements():
    return jsonify(ieu_announcements)


@app.route("/ieu-news")
def route_ieu_news():
    return jsonify(ieu_news)


@app.route("/<x>")
def error(x):
    return redirect("/")


def run_thread():
    Thread(target=ieusfl).start()
    Thread(target=ieuannouncement).start()
    Thread(target=ieunews).start()
    Thread(target=telegram).start()


if __name__ == "__main__":
    run_thread()
    app.run(host="0.0.0.0", port=8080)
