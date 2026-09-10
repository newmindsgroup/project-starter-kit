#!/usr/bin/env python3
# Version-Timestamp: 2026-09-08T17:48:04.992939-04:00
"""Local pilot reports, explicitly reviewed export and a deduplicated kit inbox."""
import argparse
import json
import sys
from project_learning import Store,Invalid,require,fields,text,strings,slug,digest,encode,stamp

def sealed(record):
    return {**record,'sha256':digest(encode(record))}

def checked(record):
    require(isinstance(record,dict) and record.get('sha256')==digest(encode({k:v for k,v in record.items() if k!='sha256'})),'Feedback record changed; preserve and reconcile')
    return record

def report(store,payload):
    fields(payload,{'id','event_id','mode','outcome','lesson','scope','sources'})
    slug(payload['id']);text(payload['event_id'],'event');text(payload['lesson'],'lesson')
    require(payload['mode'] in {'new','adopt','resume','upgrade'},'Invalid pilot mode')
    require(payload['outcome'] in {'pass','partial','fail'},'Invalid outcome')
    require(payload['scope'] in {'project','kit'},'Invalid scope')
    evidence=store.sources(payload['sources'])
    record=sealed({**store.meta('pilot-feedback.v1'),**payload,'evidence':evidence})
    store.create('memory/feedback/'+payload['id']+'.json',record);return record

def export_packet(store,payload):
    fields(payload,{'report_id','kind','summary','approved_for_kit'});slug(payload['report_id'])
    require(payload['approved_for_kit'] is True,'Review and approve sanitized text for the kit before export')
    require(payload['kind'] in {'docs','skill','template','helper','test'},'Invalid improvement kind');text(payload['summary'],'sanitized summary')
    r=checked(store.json('memory/feedback/'+payload['report_id']+'.json'))
    require(r['project_id']==store.manifest()['project_id'] and r['scope']=='kit','Report is not a kit-scoped observation from this project')
    require(store.sources(r['sources'])==r['evidence'],'Feedback evidence changed; review a new report')
    return sealed({'schema':'kit-feedback.v1','Version-Timestamp':stamp(),'kind':payload['kind'],'summary':payload['summary'],'event_key':digest(encode({'project_id':r['project_id'],'event_id':r['event_id']})),'approved_for_kit':True})

def packet_check(packet):
    fields(packet,{'schema','Version-Timestamp','kind','summary','event_key','approved_for_kit','sha256'});checked(packet)
    require(packet['schema']=='kit-feedback.v1' and packet['approved_for_kit'] is True,'Invalid reviewed packet')
    require(packet['kind'] in {'docs','skill','template','helper','test'},'Invalid kind');text(packet['summary'],'summary');text(packet['Version-Timestamp'],'timestamp')
    require(isinstance(packet['event_key'],str) and len(packet['event_key'])==64 and all(c in '0123456789abcdef' for c in packet['event_key']),'Invalid event key')

def submit(store,packet):
    packet_check(packet)
    # Exact normalized proposals share an inbox item; the first packet is retained without recurrence counting.
    identity=digest(encode({'kind':packet['kind'],'summary':' '.join(packet['summary'].casefold().split())}))
    path='improvements/inbox/'+identity+'.json'
    if store.path(path).exists():
        previous=checked(store.json(path));packet_check(previous['packet']);require(previous['id']==identity,'Inbox identity mismatch')
        return {'status':'duplicate','id':identity,'note':'Use the existing item; duplicate packets do not prove independent recurrence.'}
    store.create(path,sealed({'schema':'improvement.v1','Version-Timestamp':stamp(),'id':identity,'packet':packet}))
    return {'status':'submitted','id':identity}

def history(store,identity):
    require(len(identity)==64 and all(c in '0123456789abcdef' for c in identity),'Invalid inbox identity')
    item=checked(store.json('improvements/inbox/'+identity+'.json'));require(item['id']==identity,'Inbox identity mismatch')
    packet_check(item['packet'])
    records=[];parent=None
    for index,p in enumerate(store.entries('improvements/decisions/'+identity),1):
        require(p.name==f'{index:04d}.json','Decision sequence mismatch');r=checked(store.json(store.relative(p)))
        require(r['id']==identity and r['parent']==parent,'Decision chain mismatch');parent=r['sha256'];records.append(r)
    return records

def decide(store,identity,payload,expected_head):
    fields(payload,{'status','reason','evidence','release'});text(payload['reason'],'reason');strings(payload['evidence'],'evidence',minimum=0)
    records=history(store,identity);head=records[-1]['sha256'] if records else 'none';require(head==expected_head,'Stale inbox head; inspect before retry')
    previous=records[-1]['status'] if records else 'open'
    allowed={'open':{'triaged','rejected'},'triaged':{'implemented','rejected'},'implemented':{'released','triaged','rejected'},'released':set(),'rejected':set()}
    require(payload['status'] in allowed[previous],'Invalid improvement transition')
    if payload['status'] in {'implemented','released'}:require(payload['evidence'],'Implementation/release requires recorded evidence')
    if payload['status']=='released':text(payload['release'],'release')
    else:require(payload['release'] is None,'Only a released decision records a release')
    evidence=store.sources(payload['evidence']) if payload['evidence'] else []
    r=sealed({'schema':'improvement-decision.v1','Version-Timestamp':stamp(),'id':identity,'parent':None if head=='none' else head,**payload,'evidence_hashes':evidence})
    store.create(f'improvements/decisions/{identity}/{len(records)+1:04d}.json',r);return r

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',required=True);sub=parser.add_subparsers(dest='command',required=True)
    for name in ['report','export','submit','decide']:
        p=sub.add_parser(name);p.add_argument('--input',required=True)
        if name=='export':p.add_argument('--output',required=True)
        if name=='decide':p.add_argument('--id',required=True);p.add_argument('--expected-head',required=True)
    p=sub.add_parser('status');p.add_argument('--id',required=True);args=parser.parse_args()
    try:
        store=Store(args.root)
        if args.command=='status':r=history(store,args.id);value={'status':r[-1]['status'] if r else 'open','head':r[-1]['sha256'] if r else 'none'}
        else:
            payload=store.json(args.input)
            if args.command=='report':value=report(store,payload)
            elif args.command=='export':value=export_packet(store,payload);store.create(args.output,value)
            elif args.command=='submit':value=submit(store,payload)
            else:value=decide(store,args.id,payload,args.expected_head)
        print(json.dumps(value,indent=2));return 0
    except (Invalid,OSError,ValueError,TypeError,KeyError,AttributeError) as error:
        print('Feedback error: '+(str(error) if isinstance(error,Invalid) else 'Invalid or inaccessible record; preserve and inspect'),file=sys.stderr);return 1
if __name__=='__main__':sys.exit(main())
