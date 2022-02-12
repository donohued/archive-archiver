import os
import sys
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
import requests
import json


# Initial function to prompt user for dl info
def get_user_info():
    f = open('archiveurls.json')
    data = json.load(f)

    print("Select the archive you want to pull from")
    print("0) MANUAL LINK")

    cnt = 1
    for i in data['ArchiveList']:
        name = i["console"]
        consoles.append(name)
        print("{}) {}".format(cnt, name))
        cnt = cnt + 1

    print("Please make a selection above:")

    global host_site
    global usr_str
    host_sel = int(input())

    if host_sel == 0:
        print("enter url:")
        host_site.append(input())
    else:
        for i in data["ArchiveList"]:
            if i["console"] == consoles[int(host_sel) - 1]:
                for j in i["link"]:
                    host_site.append(j)

    print("Enter a string to filter results:")
    usr_str = input()

    global usr_path

    print("Choose a directory to save the files (press ENTER to skip):")
    print("Current Directory: {}".format(os.getcwd()))
    dirstr = input()
    if dirstr != "":
        os.chdir(dirstr)
    print("new path-> {}".format(os.getcwd()))


# loop through links on page
def get_links(i):
    req = (i)
    html_page = urlopen(req)
    soup = BeautifulSoup(html_page, "lxml")

    links = []
    for link in soup.findAll('a'):
        links.append(link.get('href'))

    for url in links:
        if url is not None and url.find(usr_str) != -1 and url.find("/") == -1:
            usr_links.append([i + "/" + url, url])


# Calculate file size from url
def calc_space(url):
    response = requests.head(url, allow_redirects=True)
    size = response.headers.get("content-length", -1)
    return int(size)


# Get the total count and size of files and display for conformation
def loop_space():
    space = 0
    filecnt = 0
    for entry in usr_links:
        space += calc_space(entry[0])
        filecnt += 1
        print("\r{} / {}".format(filecnt, len(usr_links)), end="")

    print("")
    if int(space) / KBFACTOR < 1024:
        print("{}: {:.2f} KB".format("Total size of selected files ", int(space) / KBFACTOR))
    elif int(space) / MBFACTOR < 1024:
        print("{}: {:.2f} MB".format("Total size of selected files ", int(space) / MBFACTOR))
    else:
        print("{}: {:.2f} GB".format("Total size of selected files ", int(space) / GBFACTOR))

    print("Do you want you continue? Y/N")
    global continue_dl
    while continue_dl == 0:
        confirm = input()
        if confirm == "y" or confirm == "Y":
            print("Starting download of files.")
            continue_dl = 1
        elif confirm == "n" or confirm == "N":
            print("Download cancelled..")
            continue_dl = 2


# loop through the list of links and download each one individually.
def loop_download():
    for entry in usr_links:
        print("\r\r", end="")
        download(entry[0],
                 entry[1].replace("%20", " ").replace("%21", "!").replace("%24", "$").replace("%27", "'").replace("%28", "(").replace("%29", ")").replace(
                     "%2C", ",").replace("%2B", "+"))

    print("Downloads Complete")


# Download file from url
def download(url, filename):
    # print(url)
    # print("Downloading next file: " + filename)
    # r = requests.get(url, allow_redirects=True)
    # open(filename, 'wb').write(r.content)
    with open(filename, "wb") as f:
        print("Downloading %s" % filename)
        response = requests.get(url, stream=True)
        total_length = response.headers.get('content-length')

        if total_length is None:  # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                sys.stdout.flush()
    print("\n")


KBFACTOR = float(1 << 10)
MBFACTOR = float(1 << 20)
GBFACTOR = float(1 << 30)
continue_dl = 0;
consoles = []
usr_links = []
host_site = []
usr_str = ""
usr_path = ""

# start function
get_user_info()

# get list of links from url containing filter string
for src in host_site:
    get_links(src)

# calc space of download / confirm you want to proceed
print("\nTotal number of files selected:\n{}".format(len(usr_links)))
print("Calculating space of files...")
loop_space()
print("")

# start downloading files or skip and end.
if continue_dl == 1:
    loop_download()
