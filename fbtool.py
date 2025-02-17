#!/usr/bin/env python
import base64
import re
import requests
import signal
import sys
import webbrowser

target = "No Target"
keyword = "*"
filters = []
URL_REGEX = re.compile(
    r"^(?:http|ftp)s?://"  # http:// or https://
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
    r"localhost|"  # localhost...
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
    r"(?::\d+)?"  # optional port
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE)


def get_fbid(fb_url):
    URL = "https://findmyfbid.com/"
    PARAMS = {'url': fb_url}
    try:
        r = requests.post(url=URL, params=PARAMS)
        return r.json().get("id")
    except Exception:
        return 0


def to_b64(data):
    encodedBytes = base64.b64encode(data.encode("utf-8"))
    return str(encodedBytes, "utf-8")


def helplist():
    print("Commands: settarget, setquery, addfilter, getposts, getpostsurl, listvars")


def buildURL(search_type):
    joined_filters = f"\u007b{','.join(filters)}\u007d"
    encoded_filters = to_b64(joined_filters).replace("=", "")
    search_url = f"https://www.facebook.com/search/{search_type}/?q="
    search_url += f"{keyword}&epa=FILTERS&filters={encoded_filters}"
    return search_url


def gotoURL(url):
    webbrowser.open_new_tab(url)


def printURL(url):
    print("URL: " + url)


def getID(arg):
    if len(arg) == 15:
        return arg
    if re.match(URL_REGEX, arg):
        return get_fbid(arg)
    return get_fbid("https://www.facebook.com/" + arg)


def set_target():
    print("Enter a username, url or ID to set the target")
    print("settarget>", end=" ")
    Target = getID(input())
    print("Target Set! (0 implies malformed input)")
    print("Target = " + str(Target))
    filters.append("\"rp_author\":{\"name\":\"author\",\"args\":\"" + str(Target) + "\"}")


def set_keyword():
    print("Enter a keyword to use in the search query...")
    print("setquery>", end=" ")
    global keyword
    keyword = input()
    print("Keyword set!")
    print("Keyword = " + str(keyword))


def add_filter():
    print("Enter filter type to add...")
    print("filters: (inGroup,)")
    print("addfilter>", end=" ")
    if input() == "inGroup":
        print("Enter the group name / url etc to enter as a filter...")
        group = input()
        filters.append("{\"rp_group\":\"{\"name\":\"group_posts\",\"args\":\"" + getID(group) + "\"}\"")
    print(f"Filters = {filters}")


def get_posts():
    gotoURL(buildURL("posts"))


def get_posts_url():
    printURL(buildURL("posts"))


def list_vars():
    print(f"Target = {target}")
    print(f"query = {keyword}")
    print(f"Filters = {filters}")


def parse_cmd(cmd):
    if cmd == "help":
        helplist()
    if cmd == "settarget":
        set_target()
    if cmd == "addfilter":
        add_filter()
    if cmd == "getposts":
        get_posts()
    if cmd == "getpostsurl":
        get_posts_url()
    if cmd == "setquery":
        set_keyword()
    if cmd == "listvars":
        list_vars()


def menu():
    print("Menu>", end=" ")
    parse_cmd(input().lower())


def exit_handle(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, exit_handle)

banner = '''
   ______ ____   ____   _____ _____ _   _ _______
  |  ____|  _ \\ / __ \\ / ____|_   _| \\ | |__   __|
  | |__  | |_) | |  | | (___   | | |  \\| |  | |
  |  __| |  _ <| |  | |\\___ \\  | | | . ` |  | |
  | |    | |_) | |__| |____) |_| |_| |\\  |  | |
  |_|    |____/ \\____/|_____/|_____|_| \\_|  |_|

'''
print(banner)
print("Welcome to the Facebook OSINT tool by Tom (@tomoneill19)")
list_vars()
print("Type \"help\" for a list of commands")

while True:
    menu()
