import pymysql.cursors
import urllib
import json
from unidecode import unidecode
from Bio import Medline

url_prefix = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term='

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='innovindex',
                             password='innovindex2017',
                             db='innovindex',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

import linecache
import sys

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)


def insert_to_db(row):
    for k in row:
        row[k] = row[k].encode("utf-8")
    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `medline_with_location_and_abstract` (`uid`, `doi`, `category`, `pubdate`, `epubdate`, `source`, `authors`, `lastauthor`, " + \
                    "`title`, `sorttitle`, `volume`, `issue`, `pages`, `lang`, `nlmuniqueid`, `issn`, `essn`, " + \
                    "`pubtype`, `recordstatus`, `pubstatus`,  `fulljournalname`, `sortfirstauthor`, `sortpubdate`, " + \
                    "`vernaculartitle`, `medline_ad`, `abstract`) " + \
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

            sql_data = ( row['uid'], row['doi'], row['category'], row['pubdate'], row['epubdate'], row['source'], row['authors'], \
                         row['lastauthor'], row['title'], row['sorttitle'], row['volume'], row['issue'],\
                         row['pages'], row['lang'], row['nlmuniqueid'], row['issn'], row['essn'],\
                         row['pubtype'], row['recordstatus'], row['pubstatus'], row['fulljournalname'], row['sortfirstauthor'],\
                         row['sortpubdate'], row['vernaculartitle'], row['medline_ad'], row['abstract'])

            cursor.execute(sql, sql_data)
        connection.commit()
    except Exception as e:
        print 'error while inserting: '
        print e
        # import pdb;pdb.set_trace()
        PrintException()
        return
        # connection.close()


def insert_uid_category(uid, category):
    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `category_uid_ad_abs` (`uid`, `category`) " + \
                    "VALUES (%s, %s)"
            sql_data = (uid, category)

            cursor.execute(sql, sql_data)
        connection.commit()
    except Exception as e:
        print 'error while insert_uid_category: '
        print e
        return


def get_medline_ad(uid):
    try:
        url = 'https://www.ncbi.nlm.nih.gov/pubmed/' + uid + '?report=medline'
        response = urllib.urlopen(url)
        medline_uid = response.read()
        lines = medline_uid.split('\n')
        ADs = ""
        address_begin = 'false'
        for line in lines:
            if address_begin == 'true':
                if line[0:6] == '      ':
                    ADs += line[6:] + ' '
                    continue
                else:
                    address_begin = 'false'
                    ADs += ' | '
            if line[0:6] == 'AD  - ':
                address_begin = 'true'
                ADs += line[6:] + ' '

        if len(ADs) > 5000:
            ADs = ADs[0:5000]
        return unidecode(ADs)
    except:
        PrintException()
        return ''


def get_abstract(uid):
    try:
        abs_base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=text&rettype=abstract&id='
        abs_url = abs_base_url + uid
        response = urllib.urlopen(abs_url)
        abs_response = response.read()

        if len(abs_response) > 5000:
            abs_response = abs_response[0:5000]

        if isinstance(abs_response, str):
            input_string = abs_response.decode('ascii', 'ignore').encode('ascii')
        elif isinstance(abs_response, unicode):
            input_string = abs_response.encode('ascii', 'ignore')
        return input_string
    except:
        PrintException()
        return ''


def query_one_paper(uids, category):
    # print 'inserting : '
    # print uids

    combined_uids = ','.join(uids)
    one_paper_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&rettype=abstract&id='
    response = urllib.urlopen(one_paper_url+combined_uids)
    paper = response.read()

    paper_json = json.loads(paper)

    for uid in uids:
        try:
            if 'result' not in paper_json or uid not in paper_json['result']:
                return
            insert_uid_category(uid, category)

            cur_paper = paper_json['result'][uid]

            row = {}

            # uid
            row['uid'] = ''
            if 'uid' in cur_paper:
                try:
                    row['uid'] = unidecode(unidecode(cur_paper['uid']))
                except:
                    row['uid'] = ''

            # category
            row['category'] = unidecode(category)

            # pubdate
            row['pubdate'] = ''
            if 'pubdate' in cur_paper:
                row['pubdate'] = unidecode(cur_paper['pubdate'])

            # epubdate
            row['epubdate'] = ''
            if 'epubdate' in cur_paper:
                row['epubdate'] = unidecode(cur_paper['epubdate'])

            # source
            row['source'] = ''
            if 'source' in cur_paper:
                row['source'] = unidecode(cur_paper['source'])

            # authors
            row['authors'] = ''
            if 'authors' in cur_paper and len(cur_paper['authors']) > 0:
                try:
                    authors = cur_paper['authors']
                    row['authors'] = ','.join(unidecode(x['name']) for x in authors)
                    if len(row['authors']) > 1023:
                        row['authors'] = row['authors'][:1023]
                    # row = row[:1023]
                except:
                    row['authors'] = ''

            # lastauthor
            row['lastauthor'] = ''
            if 'lastauthor' in cur_paper:
                try:
                    row['lastauthor'] = unidecode(cur_paper['lastauthor'])
                except:
                    row['lastauthor'] = ''

            # title
            row['title'] = ''
            if 'title' in cur_paper:
                row['title'] = unidecode(cur_paper['title'].encode('ascii', 'ignore'))

            # sorttitle
            row['sorttitle'] = ''
            if 'sorttitle' in cur_paper:
                row['sorttitle'] = unidecode(cur_paper['sorttitle'])

            # volume
            row['volume'] = ''
            if 'volume' in cur_paper:
                row['volume'] = unidecode(cur_paper['volume'])

            # issue
            row['issue'] = ''
            if 'issue' in cur_paper:
                row['issue'] = unidecode(cur_paper['issue'])

            # pages
            row['pages'] = ''
            if 'pages' in cur_paper:
                row['pages'] = unidecode(cur_paper['pages'])

            # lang
            row['lang'] = ''
            if 'lang' in cur_paper and len(cur_paper['lang']) > 0:
                langs = cur_paper['lang']
                row['lang'] = ','.join(unidecode(l) for l in langs)

            # nlmuniqueid
            row['nlmuniqueid'] = ''
            if 'nlmuniqueid' in cur_paper:
                row['nlmuniqueid'] = unidecode(cur_paper['nlmuniqueid'])

            # issn
            row['issn'] = ''
            if 'issn' in cur_paper:
                row['issn'] = unidecode(cur_paper['issn'])

            # essn
            row['essn'] = ''
            if 'essn' in cur_paper:
                row['essn'] = unidecode(cur_paper['essn'])

            # pubtype
            row['pubtype'] = ''
            if 'pubtype' in cur_paper and len(cur_paper['pubtype']) > 0:
                pubtype = cur_paper['pubtype']
                row['pubtype'] = ','.join(unidecode(p) for p in pubtype)

            # recordstatus
            row['recordstatus'] = ''
            if 'recordstatus' in cur_paper:
                row['recordstatus'] = unidecode(cur_paper['recordstatus'])

            # pubstatus
            row['pubstatus'] = ''
            if 'pubstatus' in cur_paper:
                row['pubstatus'] = unidecode(cur_paper['pubstatus'])

            # doi
            row['doi'] = ''
            if 'articleids' in cur_paper:
                for elem in cur_paper['articleids']:
                    if 'idtype' in elem and elem['idtype'] == 'doi' and 'value' in elem:
                        row['doi'] = unidecode(elem['value'])

            # fulljournalname
            row['fulljournalname'] = ''
            if 'fulljournalname' in cur_paper:
                row['fulljournalname'] = unidecode(cur_paper['fulljournalname'])

            # sortfirstauthor
            row['sortfirstauthor'] = ''
            if 'sortfirstauthor' in cur_paper:
                try:
                    row['sortfirstauthor'] = unidecode(cur_paper['sortfirstauthor'])
                except:
                    row['sortfirstauthor'] = ''

            # sortpubdate
            row['sortpubdate'] = '2000/01/01 00:00'
            if 'sortpubdate' in cur_paper:
                row['sortpubdate'] = unidecode(cur_paper['sortpubdate'])

            # vernaculartitle
            row['vernaculartitle'] = ''
            if 'vernaculartitle' in cur_paper:
                row['vernaculartitle'] = unidecode(cur_paper['vernaculartitle'])

            row['medline_ad'] = get_medline_ad(uid)
            row['abstract'] = get_abstract(uid)

            insert_to_db(row)
        except Exception as e:
            print 'error while building row'
            print e.message
            PrintException()
            continue

total_count = 0
line_cnt = 0
with open('all_count_all_year.txt','w') as out_fp:
    with open('CDE.txt') as fp:
        for line in fp:
            try:
                pieces = line.split(';')
                if len(pieces) != 2:
                    continue
                category = pieces[1].strip()
                url = url_prefix + pieces[0] + '+2015:2016[pdat]' + '&retmode=json'
                # print 'url: ', url
                response = urllib.urlopen(url)
                metadata = response.read()
                metadata = json.loads(metadata)

                cur_total_count = metadata['esearchresult']['count']
                # print category, " + ", cur_total_count
                url = url_prefix + pieces[0] + '+2015:2016[pdat]' + '&retmode=json' + '&retmax=' + cur_total_count
                response = urllib.urlopen(url)
                metadata = response.read()
                metadata = json.loads(metadata)

                idlist = metadata['esearchresult']['idlist']
                step_size = 500
                start_idx = 0
                while start_idx < len(idlist):
                    end = min(start_idx+step_size, len(idlist))
                    uids = idlist[start_idx:end]
                    start_idx = end
                    query_one_paper(uids, category)
                    # break

                to_write = line.rstrip() + ';'+cur_total_count+'\n'
                total_count += int(cur_total_count)
                out_fp.write(to_write)
                line_cnt += 1
                # break
            except:
                continue
print 'total_count: ', total_count


"""
CREATE TABLE `medline` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `uid` varchar(255) DEFAULT NULL,
  `category` varchar(255) DEFAULT NULL,
  `pubdate` varchar(255) DEFAULT NULL,
  `epubdate` varchar(255) DEFAULT NULL,
  `source` varchar(255) DEFAULT NULL,
  `authors` varchar(1024) DEFAULT NULL,
  `lastauthor` varchar(255) DEFAULT NULL,
  `title` varchar(1024) DEFAULT NULL,
  `sorttitle` varchar(1024) DEFAULT NULL,
  `volume` varchar(32) DEFAULT NULL,
  `issue` varchar(32) DEFAULT NULL,
  `pages` varchar(32) DEFAULT NULL,
  `lang` varchar(32) DEFAULT NULL,
  `nlmuniqueid` varchar(32) DEFAULT NULL,
  `issn` varchar(32) DEFAULT NULL,
  `essn` varchar(32) DEFAULT NULL,
  `pubtype` varchar(255) DEFAULT NULL,
  `recordstatus` varchar(1024) DEFAULT NULL,
  `pubstatus` varchar(32) DEFAULT NULL,
  `fulljournalname` varchar(1024) DEFAULT NULL,
  `sortfirstauthor` varchar(255) DEFAULT NULL,
  `sortpubdate` date DEFAULT NULL,
  `vernaculartitle` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

"""
