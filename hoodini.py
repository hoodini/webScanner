import re
import time
import requests
import urllib
import ssl
import certifi
import time
import requests.exceptions
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from alive_progress import alive_bar
import urllib3
from requests.packages.urllib3.util.retry import Retry
from urllib.error import HTTPError
from functools import lru_cache
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Functions
def request_status(reqeust):
    """
        Checks if the request status is 200 OK.
        If so, returns True.
        """
    if reqeust.status_code == 200:
        return True
def get_scheme(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme
def check_url(url):
    r = requests.get(url)
    if r.status_code == 200:
        return True
    else:
        return False
def check_url_schema(url):
    """
    This function checks if a user entered a valid url (contains "http" or "https").
    If not, it is adding "https://" and returns a new url with the schema.
    """
    parsed_url = urlparse(url)
    if ("http" or "https") not in parsed_url:
        print(f"{bcolors.FAIL}[!] Invalid url: missing schema {bcolors.ENDC}")
        try:
            new = "https://" + url
            r = requests.get(new)
            if r.status_code == 200:
                return new
            else:
                new = "http://" + url
                r = requests.get(new)
                if r.status_code == 200:
                    return new
        except AttributeError:
            print("error")

        new_url = "https://www." + url
        print(f"{bcolors.OKBLUE}==> new url with schema is: {new_url}{bcolors.ENDC}".format(new_url))
        print(f"{bcolors.OKCYAN}-------------------------------------------------------{bcolors.ENDC}")
        return new_url
    else:
        print(f"{bcolors.OKGREEN}[V] Valid URL {bcolors.ENDC}")
        print(f"{bcolors.OKCYAN}-------------------------------------------------------{bcolors.ENDC}")
        return url
def search_substring(substring, content):
    """
        This function finds a substring in a given content (html page) and returns a list with all values
        """
    list = []
    soup = BeautifulSoup(content, features="html.parser")
    result = soup.find_all(substring)
    for substring in result:
        list.append(substring)
    return list
def get_info_by_name(search_value, requests_object):
    search_value = str(search_value)
    search_parameter = dict(filter(lambda item: search_value in item[0], requests_object.items()))
    array_to_send_back = []
    if search_parameter:
        print(f"{bcolors.OKCYAN}\n[*] '{search_value}' found... :\n{bcolors.ENDC}")
        for key_value in search_parameter.items():
            array_to_send_back.append(key_value)
        return array_to_send_back
def extract_links_from(url):
    respone = requests.get(url)
    return re.findall('(?:href=")(.*?)"', respone.content.decode(errors="ignore"))
@lru_cache(maxsize=100000)
def crawl(url):
    href_links = extract_links_from(url)
    for link in href_links:
        link = urljoin(url, link)

        # remove not valid links
        if "#" in link:
            link = link.split('#')[0]
        if "?" in link:
            link = link.split('?')[0]
        if "'" in link:
            link = link.split("'")[0]
        if " " in link:
            link = link.split(' ')[0]
        if "&" in link:
            link = link.split('&')[0]

        # remove external links and get only unique links and add it to list
        if test_url in link and link not in target_links:
            target_links.append(link)
            print(link)
            crawl(link)


while True:

    print(f"""{bcolors.OKGREEN}

hoodini -> a cool web scanner by Yuval Avidani                                                                                  
                                                                                                                                                                                                                                                                                              
""")

    url = input("\n************************************************ \nType in a website you wish to scan: ")
    test_url = check_url_schema(url)
    try:
        response = requests.get(test_url)
    except ConnectionRefusedError:
        print("Connection Refused Error")
    except requests.exceptions.ConnectionError:
        print("requests.exceptions.ConnectionError")

    if not "200" in str(response.status_code):
        print("not 200... quitting!!")
        break
    else:
        target_links = []

        # opening the url for reading
        # html_page = urllib.request.urlopen(test_url, context=ssl.create_default_context(cafile=certifi.where()))
        # soup = BeautifulSoup(html_page, features="html.parser")
        # res = soup.find_all(type="hidden")
        # for ele in res:
        #     print(ele)
        # break

        if request_status(response):
            headers = response.headers
            content = response.content

            # Get website's IP address

            with requests.get(test_url, stream=True) as r:
                remote_address = r.raw._original_response.fp.raw._sock.getpeername()[0]
                print("\n[*] The Remote IP Address for", test_url, "is:\n", remote_address)
                print(f"{bcolors.OKCYAN}-------------------------------------------------------{bcolors.ENDC}")
                #time.sleep(0.5)
            # Look for security.txt email address

            security_txt_url = test_url + "/.well-known/security.txt"
            security_txt_res = requests.get(security_txt_url)

            if security_txt_res.status_code != 200:
                print(f"{bcolors.OKCYAN}\n************************************************{bcolors.ENDC}")
                print("No security.txt here...")
                #time.sleep(0.5)
            else:
                security_regex = re.findall('(Contact:)(.*)', security_txt_res.content.decode(errors="ignore"))
                if security_regex:
                    print(f"{bcolors.OKCYAN}\n************************************************{bcolors.ENDC}")
                    print(f"{bcolors.OKCYAN}\n[*] security.txt information found... :\n{bcolors.ENDC}")
                    for k, v in security_regex:
                        print(k, v)
                        #time.sleep(0.5)
                    print(100 * "-")

            # Look for http headers that holds information about the web server

            server_information = dict(filter(lambda item: "Server" in item[0], headers.items()))
            if server_information:
                print(f"{bcolors.OKCYAN}\n************************************************{bcolors.ENDC}")
                print(f"{bcolors.OKCYAN}\n[*] Server information found... :\n{bcolors.ENDC}")
                for key_value in server_information.items():
                    print(key_value)
                    #time.sleep(0.5)

            # Look for disallow robots.txt paths

            robots_txt_url = test_url + "/robots.txt"
            robots_res = requests.get(robots_txt_url)

            if robots_res.status_code != 200:
                print(f"{bcolors.OKCYAN}\n************************************************{bcolors.ENDC}")
                print("No robots.txt here...")
                #time.sleep(1)
            else:
                robots_regex = re.findall('(Disallow)(.*)', robots_res.content.decode(errors="ignore"))
                if robots_regex:
                    print(f"{bcolors.OKCYAN}\n************************************************{bcolors.ENDC}")
                    print(f"{bcolors.OKCYAN}\n[*] Robots.txt information found... :\n{bcolors.ENDC}")
                    for k, v in robots_regex:
                        print(k, v)
                        #time.sleep(0.5)
                    print(100 * "-")


            # Look for HTML "hidden" tags

            soup = BeautifulSoup(content, features="html.parser")
            hidden_tags = soup.find_all(type="hidden")
            htags = []
            if not hidden_tags:
                print(f"{bcolors.OKCYAN}\n************************************************{bcolors.ENDC}")
                print(f"{bcolors.OKBLUE}\n[*] 'Hidden' tags NOT found... :\n{bcolors.ENDC}")
            elif hidden_tags:
                print(f"{bcolors.OKCYAN}\n************************************************{bcolors.ENDC}")
                print(f"{bcolors.OKCYAN}\n[*] 'Hidden' tags found... :\n{bcolors.ENDC}")
                for tag in hidden_tags:
                    htags.append(tag)
                    print(tag)
                    #time.sleep(1)

            print(f"{bcolors.OKCYAN}\n**********************\nCrawling website and getting urls... :\n{bcolors.ENDC}")
            crawl(test_url)

# if __name__ == '__main__':
#     main()
