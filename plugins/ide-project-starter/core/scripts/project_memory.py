#!/usr/bin/env python3
# Version-Timestamp: 2026-09-08T16:25:41.675029-04:00
"""Portable immutable continuity checkpoints. Run with Python 3.10 or newer."""
import argparse
import json
import sys
from project_learning import Store, Invalid, require, fields, text, strings, digest, encode, stamp

STATE_FIELDS={'objective','constraints','decisions','completed','checks','blockers','next_action','external_actions','sources'}

def state_check(value):
    fields(value,STATE_FIELDS)
    for name in ['objective','next_action']:text(value[name],name)
    for name in STATE_FIELDS-{'objective','next_action'}:strings(value[name],name,minimum=0)

class Continuity(Store):
    def history(self):
        result=[];parent=None
        for index,p in enumerate(self.entries('memory/checkpoints'),1):
            require(p.is_file() and p.name==f'{index:04d}.json','Invalid checkpoint sequence')
            record=self.json(self.relative(p))
            fields(record,{'schema','project_id','Version-Timestamp','checkpoint_id','parent','state','evidence','sha256'})
            self.check_meta(record,'continuity.v1')
            require(record['checkpoint_id']==index and record['parent']==parent,'Checkpoint chain mismatch')
            state_check(record['state'])
            require(isinstance(record['evidence'],list),'Invalid checkpoint evidence')
            require([s['path'] for s in record['evidence']]==record['state']['sources'],'Checkpoint source mismatch')
            for source in record['evidence']:
                fields(source,{'path','sha256'});self.path(source['path'])
                require(isinstance(source['sha256'],str) and len(source['sha256'])==64,'Invalid evidence digest')
            parent=digest(encode({k:v for k,v in record.items() if k!='sha256'}))
            require(record['sha256']==parent,'Checkpoint changed; preserve and reconcile')
            result.append(record)
        require(result,'No continuity checkpoint exists')
        return result

    def checkpoint(self,state,expected_head):
        state_check(state)
        records=self.history()
        require(records[-1]['sha256']==expected_head,'Stale checkpoint head; resume and reconcile before retry')
        record=make_checkpoint(self,state,len(records)+1,expected_head)
        self.create(f'memory/checkpoints/{record["checkpoint_id"]:04d}.json',record)
        return record

    def resume(self):
        latest=self.history()[-1];stale=[]
        for source in latest['evidence']:
            try:
                require(digest(self.read(source['path']))==source['sha256'],'Changed source')
            except (Invalid,OSError):stale.append(source['path'])
        client={'status':'unlinked','head':'none'}
        if self.path('context/client-links').exists():
            try:
                from project_client import client_status
            except ImportError:
                client={'status':'unavailable','reason':'Client helper missing or incompatible; complete the reviewed runtime upgrade'}
            else:
                client=client_status(self)
        return {'schema':'resume.v1','Version-Timestamp':stamp(),'status':'needs_review' if stale or client['status'] in {'needs_review','unavailable'} else 'ready_for_context_review',
                'client_context':client,
                'project':self.manifest(),'checkpoint_id':latest['checkpoint_id'],'head':latest['sha256'],
                'state':latest['state'],'stale_sources':stale,'authority':'Recorded state and check claims only; grants no external action authority',
                'read_next':['PROJECT.md','context/index.md','QUALITY.md'],
                'gaps':['Verify current files and applicable Git state before action.','Recorded checks are claims, not checks executed by resume.']}

def make_checkpoint(store,state,index,parent):
    state_check(state)
    record={**store.meta('continuity.v1'),'checkpoint_id':index,'parent':parent,'state':state,
            'evidence':store.sources(state['sources']) if state['sources'] else []}
    record['sha256']=digest(encode(record))
    return record

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',default='.')
    sub=parser.add_subparsers(dest='command',required=True);sub.add_parser('resume')
    p=sub.add_parser('checkpoint');p.add_argument('--input',required=True);p.add_argument('--expected-head',required=True)
    args=parser.parse_args()
    try:
        store=Continuity(args.root)
        value=store.resume() if args.command=='resume' else store.checkpoint(store.json(args.input),args.expected_head)
        print(json.dumps(value,ensure_ascii=False,indent=2));return 0
    except (Invalid,OSError,ValueError,TypeError,KeyError,AttributeError) as error:
        print('Continuity error: '+(str(error) if isinstance(error,Invalid) else 'Invalid or competing record; preserve files and inspect before retry'),file=sys.stderr);return 1

if __name__=='__main__':sys.exit(main())
