import sys
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
import requests


# loop through links on page


def get_links():
    req = Request(host_site)
    html_page = urlopen(req)
    soup = BeautifulSoup(html_page, "lxml")

    links = []
    for link in soup.findAll('a'):
        links.append(link.get('href'))

    for url in links:
        if url is not None and url.find(usr_str) != -1 and url.find("/") == -1:
            usr_links.append(url)

    print("===============================================================================")


# Calculate file size from url
def calc_space(url):
    response = requests.head(url, allow_redirects=True)
    size = response.headers.get('content-length', -1)
    print(size)
    return int(size)


# Download file from url
def download(url, filename):
    # print("Downloading next file: " + filename)
    # r = requests.get(url, allow_redirects=True)
    # open(filename, 'wb').write(r.content)
    # print("Complete.")
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


# Call downloads for each link in list
def loop_links(flag):
    if flag == 0:
        space = 0
        for link_name in usr_links:
            space += calc_space(host_site + "/" + link_name)
        print(space)
        print("Do you want you continue? Y/N")
        confirm = input()
        if confirm == ("y" or "Y"):
            print("Cool")
        if confirm == ("n" or "N"):
            print("Not so Cool")

    if flag == 1:
        for link_name in usr_links:
            download(host_site + "/" + link_name,
                     link_name.replace("%20", " ").replace("%21", "!").replace("%28", "(").replace("%29", ")").replace(
                         "%2C", ",").replace("%2D", "-").replace("%5B", "[").replace("%5D", "]"))

        print("===============================================================================")
        print("Downloads Complete")


# Initial function to prompt user for dl info
def get_user_info():
    print("Select the archive you want to pull from")
    print("0) MANUAL LINK")
    print("1) OG Gameboy")
    print("2) Gameboy Color")
    print("3) Gameboy Advance")
    print("4) NES")
    print("5) SNES")
    print("6) Nintendo64")
    print("7) NYF-Gamecube")
    print("8) NYF-Wii")
    print("9) NYF-WiiU")
    print("10) Nintendo DS")
    print("11) DS Download Play")
    print("12) DSi")
    print("13) DSi Ware")
    print("14) NYF-Nintendo 3DS")
    print("Please make a selection above:")

    global host_site
    global usr_str
    host_sel = int(input())

    if host_sel == 0:
        host_site = input()
    else:
        if host_sel != 7 and host_sel != 8 and host_sel != 9 and host_sel != 14 and host_sel < len(archives):
            host_site = archives[host_sel - 1]
            print(host_sel)
            print(host_site)

    print("Enter a string to filter results:")
    usr_str = input()


usr_links = []
usr_str = ""
host_site = ""

archives = ["https://archive.org/download/nointro.gb",
            "https://archive.org/download/nointro.gbc",
            "https://archive.org/download/nointro.gba",
            "https://archive.org/download/nointro.nes",
            "https://archive.org/download/nointro.snes",
            "https://archive.org/download/nointro.n64",
            "NA",
            "NA",
            "NA",
            "https://archive.org/download/no-intro-nintendo-nintendo-ds-decrypted",
            "https://archive.org/download/no-intro-nintendo-nintendo-ds-download-play",
            "https://archive.org/download/no-intro-nintendo-nintendo-dsi-decrypted",
            "https://archive.org/download/no-intro-nintendo-nintendo-dsi-digital",
            "NA"
            ]

# start funtion
get_user_info()

# get list of links from url containing filter string
get_links()

# calc space of download / confirm you want to proceed
loop_links(0)

# start download from created and approved list
# loop_links(1)
