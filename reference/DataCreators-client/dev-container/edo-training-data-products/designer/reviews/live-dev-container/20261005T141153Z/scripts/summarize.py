import csv, collections, sys
rows = list(csv.DictReader(open(sys.argv[1]), delimiter='\t'))
c = collections.Counter((r['journey'], r['mode'], r['result']) for r in rows)
for k in sorted(c): print(*k, c[k], sep='\t')
print('total', len(rows))
for r in rows:
    if r['mode'] == 'live' and r['journey'] in ('baseline', 'solution') and r['result'] not in ('pass',):
        print('LIVE-NONPASS', r['journey'], r['tool'], r['phase'], r['action'], r['result'], r['note'][:140], sep='\t')
    if r['journey'] == 'starter' and r['result'] == 'pass':
        print('STARTER-ACCEPTED', r['tool'], r['phase'], r['mode'], sep='\t')
