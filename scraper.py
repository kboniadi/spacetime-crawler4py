import re
from collections import defaultdict
from pickle import TRUE
from urllib.parse import urlparse

import tldextract
from bs4 import BeautifulSoup
from nltk import download
from nltk.corpus import stopwords

from tokenizer import Tokenizer

f = open("out.txt", "w")
download('stopwords')

cache = set()
stops = set(stopwords.words('english'))

subdomainsHash = defaultdict(set)

hashWords = defaultdict(int)
accepted_urls = {".ics.uci.edu", ".cs.uci.edu",
                 ".informatics.uci.edu", ".stat.uci.edu"}

maxPage = ""
maxPageLength = 0


def scraper(url, resp):
    global maxPageLength
    global maxPage
    ret = []
    links, lineTokens = extract_next_links(url, resp)

    for link in links:
        valid, domain, subdomain = is_valid(link)
        if valid:
            ret.append(link)
            # adding to cache
            cache.add(link)

            if "ics.uci.edu" in domain:
                subdomainsHash[subdomain].add(link)

    # adding to most common words hash
    for val in lineTokens:
        if val.lower() not in stops:
            hashWords[val] += 1

    # getting maximum page
    if (len(lineTokens) > maxPageLength):
        maxPageLength = len(lineTokens)
        maxPage = url
    for url in ret:
        f.write(url + "\n")
    return ret


# Analysis questions #3
def mostCommon():
    return sorted(hashWords, key=lambda x: -hashWords[x])[:50]


# Analysis questions #4
def subdomainICS():
    list1 = sorted(subdomainsHash)

    for val in list1:
        print(val, len(subdomainsHash[val]))


# Analysis questions #2
def longestPage():
    return maxPage


# Analysis questions #1
def uniquePages():
    return len(cache)


def extract_next_links(url, resp):
    ret = []

    if resp.error is not None:
        print(resp.error)
        return [], []

    if resp.raw_response is None or\
            ("Content-Type" in resp.raw_response.headers and "application/pdf" in resp.raw_response.headers['Content-Type']):
        return [], []

    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    lineTokens = Tokenizer.tokenize(soup.get_text())

    # CHECK CONTENT
    tempChecker = defaultdict(int)
    stopsCount = 0
    for val in lineTokens:
        if val.lower() not in stops:
            tempChecker[val] += 1
        else:
            stopsCount += 1

    # CHECK IF HIGH TEXT CONTENT
    if (abs(len(lineTokens) - len(tempChecker)) < 1500) and len(lineTokens) - stopsCount >= 50:
        for link in soup.find_all('a'):
            url_link = link.get('href')
            if url_link is not None:
                index = url_link.find("#")
                if index != -1:
                    ret.append(url_link[0:index])
                else:
                    ret.append(url_link)
        return ret, lineTokens
    else:
        return [], []

    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content


def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        domains = tldextract.extract(url)
        fqdn = domains.fqdn

        if parsed.scheme not in set(["http", "https"])\
           or url in cache\
                or (fqdn != "today.uci.edu" and not any(s in fqdn for s in accepted_urls))\
                or ("today.uci.edu" == fqdn and "/department/information_computer_sciences/" not in parsed.path):
            return False, fqdn, domains.subdomain
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|ppsx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()),\
            fqdn,\
            domains.subdomain

    except TypeError:
        print("TypeError for ", parsed)
        raise
