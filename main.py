from pyPdf import PdfFileWriter, PdfFileReader
import os
import urlparse
import urllib
from bs4 import BeautifulSoup
import re
from collections import OrderedDict
import sys
import optparse
import requests

def main():

    # Global variables ------------------
    global tgtWeb
    global tgtDir

    # Create Option Parser ------------------
    parser = optparse.OptionParser(Header + 'Usage: MetaXtractor ' + '-w <Target website> -d <Download Directory> -o <filename> ' + Footer)
    parser.add_option('-w', dest='tgtWeb', type='string',help='Specify Target Website')
    parser.add_option('-d', dest='tgtDir', type='string', help='Specify Directory Name')
    (options, args) = parser.parse_args()
    tgtWeb = options.tgtWeb
    tgtDir = options.tgtDir


    # Check if Parser options not set ------------------
    if (tgtWeb == None) | (tgtDir == None):
        print parser.usage
        sys.exit(0)

    # Check if http or https is not set ------------------
    if not re.search('^(http|https)://', tgtWeb):
        print parser.usage
        print "Note: Use HTTP or HTTPS before domain name.\nExample: http://<domain.xy>"
        sys.exit(0)

# Metadata Crawler Function ------------------
def MetadataCrawler(url):

    # Check if domain exists ------------------
    try:
        requests.get(tgtWeb)
    except requests.exceptions.ConnectionError as e:
        print "[!] Sorry domain %s" % tgtWeb + " is not available. Please check the spelling."
        sys.exit(0)

    # Check if OS is Linux or Windows for correct syntax in path.
    if (os.name == "posix"):
      Slashes = "/"
    else:
      Slashes = "\\"

    # Initiating lists ------------------
    urls = [url]
    visited = [url]
    username = []
    program = []
    email = []
    name = []

    # Create Directory for downloading ------------------
    try:
        if not os.path.exists(tgtDir):
            os.makedirs(tgtDir)
            print "[i] Creating Directory %s" % tgtDir + "..."
    except:
        print "[!] Problem Creating Directory %s" % tgtDir + "..."
        pass
        sys.exit(0)

    # Display message to terminal ------------------
    print "[i] Start Web Crawling @ %s " % tgtWeb

    # While list [urls] is larger then 0, run the while loop ------------------
    while len(urls) > 0:

        # Try to read the url from list [urls] ------------------
        try:
            htmltext = urllib.urlopen(urls[0]).read()
        except:
            pass

        # Use BeautifulSoup to parse the HTML ------------------
        try:
            soup = BeautifulSoup(htmltext)
        except:
            pass

        # Descending  urls from  list [urls] ------------------
        urls.pop(0)

        # Find all a href tags and create a complete url with domain name ------------------
        for tag in soup.findAll('a', href=True):
            tag['href'] = urlparse.urljoin(url,tag['href'])

            # Check urls in the [urls] list and compare with list [visited] ------------------
            if url in tag['href'] and tag['href'] not in visited:
                urls.append(tag['href'])
                visited.append(tag['href'])

                # Search for links (a href) with extension pdf ------------------
                extensions = re.search('([^\s]+(\.(?i)(pdf))$)', tag['href'])

                # If match above ------------------
                if extensions:

                    # Split filename
                    URLFilename = urlparse.urlsplit(tag['href']).path.split('/')[-1]


                    # Display message to terminal ------------------
                    print "[i] Downloading %s" % URLFilename+"..."

                    # Try to download the file ------------------
                    try:
                        urllib.urlretrieve(tag['href'], tgtDir + Slashes + URLFilename)
                    except:
                        pass

                    # Try to open document for Metadata extraction ------------------
                    try:
                        pdfFile = PdfFileReader(file(tgtDir + Slashes + URLFilename, 'rb'))
                        docInfo = pdfFile.getDocumentInfo()
                        for metaItem in docInfo:
                            # Check if there is a e-mail address ------------------
                            if re.search(r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", docInfo[metaItem]):
                                # Append to email-list
                                email.append(docInfo[metaItem])
                            if "Author" in metaItem:
                                print "    [+] ---> " + docInfo[metaItem]
                                # Check if not space and e-mail exists to create a unique list with usernames ------------------
                                if not re.search(r"\s", docInfo[metaItem]) and not re.search(r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", docInfo[metaItem]):
                                    # Append to user-list
                                    username.append(docInfo[metaItem])
                                # If space assume there is firstname and lastname
                                if re.search(r"\s", docInfo[metaItem]):
                                    # Append to name-list
                                    name.append(docInfo[metaItem])
                            # Extract information about programs ------------------
                            if "Creator" in metaItem:
                                print "    [+] ---> " + docInfo[metaItem]
                                program.append(docInfo[metaItem])
                    except:
                        pass

    # Displaying report on terminal ------------------
    print "\n\nUsernames:\n===================================="
    for usrname in list(OrderedDict.fromkeys(username)):
        count = username.count(usrname)
        print usrname + " [" + str(count) + "]"


    print "\n\nNames:\n===================================="
    for names in list(OrderedDict.fromkeys(name)):
        count = name.count(names)
        print names + " [" + str(count) + "]"


    print "\n\nPrograms:\n===================================="
    for pgm in list(OrderedDict.fromkeys(program)):
        count = program.count(pgm)
        print pgm + " [" + str(count) + "]"


    print "\n\nEmails:\n===================================="
    for mail in list(OrderedDict.fromkeys(email)):
        count = email.count(mail)
        print mail + " [" + str(count) + "]"

if __name__ == '__main__':
    main()

MetadataCrawler(tgtWeb)
