import pymysql.cursors
import urllib
import json

url_prefix = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term='

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='innovindex',
                             password='innovindex2017',
                             db='innovindex',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


def insert_to_db(row):
    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `medline` (`uid`, `doi`, `category`, `pubdate`, `epubdate`, `source`, `authors`, `lastauthor`, " + \
                    "`title`, `sorttitle`, `volume`, `issue`, `pages`, `lang`, `nlmuniqueid`, `issn`, `essn`, " + \
                    "`pubtype`, `recordstatus`, `pubstatus`,  `fulljournalname`, `sortfirstauthor`, `sortpubdate`, " + \
                    "`vernaculartitle`) " + \
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

            sql_data = ( row['uid'], row['doi'], row['category'], row['pubdate'], row['epubdate'], row['source'], row['authors'], \
                         row['lastauthor'], row['title'], row['sorttitle'], row['volume'], row['issue'],\
                         row['pages'], row['lang'], row['nlmuniqueid'], row['issn'], row['essn'],\
                         row['pubtype'], row['recordstatus'], row['pubstatus'], row['fulljournalname'], row['sortfirstauthor'],\
                         row['sortpubdate'], row['vernaculartitle'])

            cursor.execute(sql, sql_data)
        connection.commit()
    except:
        connection.close()


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
            cur_paper = paper_json['result'][uid]

            row = {}

            # uid
            row['uid'] = ''
            if 'uid' in cur_paper:
                try:
                    row['uid'] = str(cur_paper['uid'])
                except:
                    row['uid'] = ''

            # category
            row['category'] = str(category)

            # pubdate
            row['pubdate'] = ''
            if 'pubdate' in cur_paper:
                row['pubdate'] = str(cur_paper['pubdate'])

            # epubdate
            row['epubdate'] = ''
            if 'epubdate' in cur_paper:
                row['epubdate'] = str(cur_paper['epubdate'])

            # source
            row['source'] = ''
            if 'source' in cur_paper:
                row['source'] = str(cur_paper['source'])

            # authors
            row['authors'] = ''
            if 'authors' in cur_paper and len(cur_paper['authors']) > 0:
                try:
                    authors = cur_paper['authors']
                    row['authors'] = ','.join(str(x['name']) for x in authors)
                except:
                    row['authors'] = ''

            # lastauthor
            row['lastauthor'] = ''
            if 'lastauthor' in cur_paper:
                try:
                    row['lastauthor'] = str(cur_paper['lastauthor'])
                except:
                    row['lastauthor'] = ''

            # title
            row['title'] = ''
            if 'title' in cur_paper:
                row['title'] = str(cur_paper['title'])

            # sorttitle
            row['sorttitle'] = ''
            if 'sorttitle' in cur_paper:
                row['sorttitle'] = str(cur_paper['sorttitle'])

            # volume
            row['volume'] = ''
            if 'volume' in cur_paper:
                row['volume'] = str(cur_paper['volume'])

            # issue
            row['issue'] = ''
            if 'issue' in cur_paper:
                row['issue'] = str(cur_paper['issue'])

            # pages
            row['pages'] = ''
            if 'pages' in cur_paper:
                row['pages'] = str(cur_paper['pages'])

            # lang
            row['lang'] = ''
            if 'lang' in cur_paper and len(cur_paper['lang']) > 0:
                langs = cur_paper['lang']
                row['lang'] = ','.join(str(l) for l in langs)

            # nlmuniqueid
            row['nlmuniqueid'] = ''
            if 'nlmuniqueid' in cur_paper:
                row['nlmuniqueid'] = str(cur_paper['nlmuniqueid'])

            # issn
            row['issn'] = ''
            if 'issn' in cur_paper:
                row['issn'] = str(cur_paper['issn'])

            # essn
            row['essn'] = ''
            if 'essn' in cur_paper:
                row['essn'] = str(cur_paper['essn'])

            # pubtype
            row['pubtype'] = ''
            if 'pubtype' in cur_paper and len(cur_paper['pubtype']) > 0:
                pubtype = cur_paper['pubtype']
                row['pubtype'] = ','.join(str(p) for p in pubtype)

            # recordstatus
            row['recordstatus'] = ''
            if 'recordstatus' in cur_paper:
                row['recordstatus'] = str(cur_paper['recordstatus'])

            # pubstatus
            row['pubstatus'] = ''
            if 'pubstatus' in cur_paper:
                row['pubstatus'] = str(cur_paper['pubstatus'])

            # doi
            row['doi'] = ''
            if 'articleids' in cur_paper:
                for elem in cur_paper['articleids']:
                    if 'idtype' in elem and elem['idtype'] == 'doi' and 'value' in elem:
                        row['doi'] = str(elem['value'])

            # fulljournalname
            row['fulljournalname'] = ''
            if 'fulljournalname' in cur_paper:
                row['fulljournalname'] = str(cur_paper['fulljournalname'])

            # sortfirstauthor
            row['sortfirstauthor'] = ''
            if 'sortfirstauthor' in cur_paper:
                try:
                    row['sortfirstauthor'] = str(cur_paper['sortfirstauthor'])
                except:
                    row['sortfirstauthor'] = ''

            # sortpubdate
            row['sortpubdate'] = '2000/01/01 00:00'
            if 'sortpubdate' in cur_paper:
                row['sortpubdate'] = str(cur_paper['sortpubdate'])

            # vernaculartitle
            row['vernaculartitle'] = ''
            if 'vernaculartitle' in cur_paper:
                row['vernaculartitle'] = str(cur_paper['vernaculartitle'])

            insert_to_db(row)
        except Exception as e:
            print e.message
            continue

    print 'inserted ', len(uids)

total_count = 0
line_cnt = 0
with open('all_count_all_year.txt','w') as out_fp:
    with open('CDE.txt') as fp:
        for line in fp:
            try:
                # print 'current category line: ',
                # print line
                # print line_cnt
                pieces = line.split(';')
                if len(pieces) != 2:
                    continue
                # print pieces
                category = pieces[1].strip()
                # print 'category:[', category,']'
                # print 'cateory name: ', pieces[0]
                url = url_prefix + pieces[0] + '&retmode=json'
                print 'url: ', url
                response = urllib.urlopen(url)
                metadata = response.read()
                metadata = json.loads(metadata)

                cur_total_count = metadata['esearchresult']['count']
                # print 'cur_total_count: ', cur_total_count
                url = url_prefix + pieces[0] + '&retmode=json' + '&retmax=' + cur_total_count
                response = urllib.urlopen(url)
                metadata = response.read()
                metadata = json.loads(metadata)

                idlist = metadata['esearchresult']['idlist']
                # print 'len: ', len(idlist)
                step_size = 500
                start_idx = 0
                while start_idx < len(idlist):
                    end = min(start_idx+step_size, len(idlist))
                    uids = idlist[start_idx:end]
                    start_idx = end
                    query_one_paper(uids, category)

                to_write = line.rstrip() + ';'+cur_total_count+'\n'
                total_count += int(cur_total_count)
                out_fp.write(to_write)
                line_cnt += 1
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
