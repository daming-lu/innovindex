import sqlite3
import json
from pprint import pprint
json_data=open('crawler_config.json').read()
data = json.loads(json_data)
pprint(data['retmax'])
retmax = data['retmax']
import urllib, json
from dateutil.parser import parse

sqlite_file = '../db.sqlite3'    # name of the sqlite database file

conn = sqlite3.connect(sqlite_file)
c = conn.cursor()

def crawl_paper(category_name, key_words, url, lastrowid):
    url_with_retmax = url + '&retmax=' + str(retmax)
    response = urllib.urlopen(url_with_retmax)
    data = response.read()
    # print json.loads(data)['esearchresult']['idlist']
    # print data

    data = json.loads(data)
    idlist_arr= data['esearchresult']['idlist']
    idlist = ','.join(data['esearchresult']['idlist'])
    # print 'idlist_arr'
    # print idlist_arr

    # we need to separate ids into 100 a batch
    batch_size = 100
    start_index = 0
    while start_index < len(idlist_arr):
        cur_idlist = ','.join(data['esearchresult']['idlist'][start_index:min(start_index+batch_size, len(idlist_arr))])
        start_index = min(start_index+batch_size, len(idlist_arr))

        metadata_base_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&rettype=abstract&id='
        metadata_url = metadata_base_url + cur_idlist
        response = urllib.urlopen(metadata_url)
        metadata = response.read()

        metadata = json.loads(metadata)
        while 'result' not in metadata:
            # print 'llll'
            response = urllib.urlopen(metadata_url)
            metadata = response.read()
        result = metadata['result']
        # print 'metadata'
        # print metadata
        table_name = 'pubmed_paper'

        for id in idlist_arr:
            if id not in result:
                continue
            paper = result[id]

            authors = ', '.join(map(lambda a: a['name'], paper['authors']))
            # import pdb; pdb.set_trace()
            if 'sortpubdate' in paper:
                year = parse(paper['sortpubdate']).year
            else:
                year = 1000

            try:
                c.execute(
                    "INSERT INTO {tn} (uid, pubdate, source, authors, title, sortpubdate, year, category_id) VALUES (?,?,?,?,?,?,?,?)".format(
                        tn=table_name), (paper['uid'], paper['pubdate'], paper['source'], authors, paper['title'], paper['sortpubdate'], year, lastrowid))
            except sqlite3.IntegrityError:
                print('ERROR: ID already exists in PRIMARY KEY column {}'.format('crawl_paper'))


def insert_category(category_name, url, key_words):
    table_name = "pubmed_category"
    # import pdb; pdb.set_trace()
    try:
        c.execute(
            "INSERT INTO {tn} (category_name, keywords, url) VALUES (?,?,?)".format(
                tn=table_name), (category_name, ','.join(key_words), url))
        conn.commit()

        crawl_paper(category_name, key_words, url, c.lastrowid)
    except sqlite3.IntegrityError:
        print('ERROR: ID already exists in PRIMARY KEY column {}'.format('insert_category'))


for category in data['categories']:
    # print 'category'
    # print category
    # import pdb; pdb.set_trace()
    insert_category(category['category name'], category['url'], category['key words'])



conn.close()
