import os
import sys
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
import requests
import json


# Initial function to show main menu

# voicebox = dict(MB80="################################################################################\r\n",
#                     MB2="##",
#                     START='Start Download',
#                     HOME='Main Menu',
#                     SETTINGS='Change Settings',
#                     )
#
# home_menu = ['{START}{SETTINGS}', '{HOME}']
#
#
# def main_menu():
#     print_content(home_menu)
#
#
# def print_content(menu):
#     print('{MB80}'.format(**voicebox))
#     for line in menu:
#         print('{MB2}'.format(**voicebox), end='')
#         print('{}'.format(line), end='')
#         print('{MB2}'.format(**voicebox))
#
# main_menu()


def get_archive_list():
    f = open('archiveurls.json')
    data = json.load(f)
    cnt = 1
    for i in data['ArchiveList']:
        name = i["console"]
        lst_consoles.append(name)
        print("{}) {}".format(cnt, name))
        cnt = cnt + 1


# Initial function to prompt user for dl info
def get_user_info():
    with open('data.json') as file:
        data = json.load(file)

        print("Select the archive you want to pull from")


        cnt = 0
        sys_list = list(data['ArchiveList'])
        print("{}) MANUAL LINK".format(cnt))
        for i in sys_list:
            for j in i:
                cnt = cnt + 1
                lst_consoles.append(j)
                print("{}) {}".format(cnt, j))

    print("Please make a selection above:")

    global dl_dirs
    global dl_filter
    host_sel = int(input())

    if host_sel == 0:
        print("enter url:")
        dl_dirs.append(input())
    else:
        for i in sys_list:
            for j in i:
                if j == lst_consoles[int(host_sel) - 1]:
                    for k in i[j]:
                        dl_dirs.append(k)


    print("Enter a string to filter results (Blank for no filter):")
    dl_filter = input()

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
        if url is not None and url.find(dl_filter) != -1 and url.find("/") == -1:
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
                 entry[1].replace("%20", " ").replace("%21", "!").replace("%24", "$").replace("%27", "'").replace("%28",
                                                                                                                  "(").replace(
                     "%29", ")").replace(
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
lst_consoles = []
usr_links = []
dl_dirs = []
dl_filter = ""
usr_path = ""

# start function
get_user_info()

# get list of links from url containing filter string
for dir in dl_dirs:
    get_links(dir)

# calc space of download / confirm you want to proceed
print("\nTotal number of files selected:\n{}".format(len(usr_links)))
print("Calculating space of files...")
loop_space()
print("")

# start downloading files or skip and end.
if continue_dl == 1:
    loop_download()
