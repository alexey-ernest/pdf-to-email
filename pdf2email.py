"""
pdf2email.py: extracts all email addresses from pdf files.

pdfminer package required: pip install pdfminer.
"""

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFSyntaxError
from cStringIO import StringIO
import re
import sys
from os import walk, path

def get_emails(text):
    """Parses email addresses from text.

    Args:
        text: input text string.

    Returns:
        Set of parsed email addresses.
    """

    parsed_emails = set()
    for line in text.split():
        match = re.findall(r'[\w\.\-]+@[\w\.-]+', line)
        for address in match:
            parsed_emails.add(address)
    return parsed_emails

def get_pdf_data(file_path):
    """Retrieves text data from pdf file yielding one page at a time.
    
    Args:
        file_path: pdf file path.

    Returns:
        File text contents iterable page by page.
    """

    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    password = ''
    maxpages = 0
    caching = True
    pagenos = set()
    try:
        file_data = file(file_path, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for file_page in PDFPage.get_pages(file_data, pagenos, 
                                           maxpages=maxpages, 
                                           password=password, 
                                           caching=caching, 
                                           check_extractable=True):
            interpreter.process_page(file_page)
            yield retstr.getvalue()
    except PDFSyntaxError:
        yield ''
    finally:
        file_data.close()
        device.close()
        retstr.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        PATH = sys.argv[1]
        EMAILS = set()

        def read_file_emails(file_name, emails_filter=None):
            """
            Reads file and parses all emails from it's content.
            """
            if not emails_filter:
                emails_filter = set()
            emails = set()

            for page in get_pdf_data(file_name):
                page_emails = get_emails(page)
                for email in [e for e in page_emails if e not in emails_filter]:
                    emails.add(email)
                    print email
                emails_filter = emails_filter | emails
            return emails

        if path.isdir(PATH):
            # read files in directory
            for (dirpath, dirnames, filenames) in walk(PATH):
                for filename in filenames:
                    EMAILS = EMAILS | read_file_emails('% s/%s' % (dirpath, filename), EMAILS)
        else:
            # read file
            EMAILS = read_file_emails(PATH)
