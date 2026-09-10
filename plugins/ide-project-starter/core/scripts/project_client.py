#!/usr/bin/env python3
# Version-Timestamp: 2026-09-08T16:25:41.675029-04:00
"""Explicit client inventory and source subscriptions. No network or content copying."""
import argparse
import json
import os
from pathlib import Path
import sys
import uuid
from project_learning import Store, Invalid, require, fields, text, strings, stamp, digest, encode

LINKS='context/client-links'
EXCLUDED={'node_modules','credentials','secrets','__pycache__','.venv'}
TEXT_SUFFIXES={'.md','.txt','.json','.csv','.yaml','.yml'}

def root_store(value):
    path=Path(value).absolute()
    require(not any(p.is_symlink() for p in (path,*path.parents)), 'Use a canonical root without symlink ancestry')
    return Store(path)

def client_manifest(store):
    record=store.json('CLIENT.json')
    fields(record,{'schema','client_id','name','sharing','Version-Timestamp'})
    require(record['schema']=='client.v1','Unsupported client schema')
    require(str(uuid.UUID(record['client_id']))==record['client_id'],'Invalid client identity')
    text(record['name'],'client name',200);text(record['Version-Timestamp'],'timestamp')
    require(record['sharing'] in {'internal','shared','unknown'},'Invalid sharing classification')
    return record

def init_client(store,name,sharing):
    require(not store.path('.git').exists(), 'Client root is a Git repository; select the client parent or review the repository boundary')
    text(name,'client name',200)
    require(sharing in {'internal','shared','unknown'},'Invalid sharing classification')
    if not store.path('CLIENT.json').exists():
        store.create('CLIENT.json',{'schema':'client.v1','client_id':str(uuid.uuid4()),'name':name,'sharing':sharing,'Version-Timestamp':stamp()})
    record=client_manifest(store)
    require(record['name']==name and record['sharing']==sharing,'Existing client identity/classification differs; preserve and review')
    return record

def inventory(store,limit=500):
    require(type(limit)==int and 1<=limit<=2000,'Inventory limit must be 1 to 2000')
    files=[];projects=[];repositories=[{'path':'.'}] if store.path('.git').exists() else [];pending=[store.root];seen=0;skipped=0;truncated=False
    while pending and not truncated:
        folder=pending.pop()
        with os.scandir(folder) as entries:
            for entry in entries:
                seen+=1
                if seen>limit:truncated=True;break
                if entry.name.startswith('.') or entry.name.casefold() in EXCLUDED or entry.is_symlink():skipped+=1;continue
                p=Path(entry.path);relative=p.relative_to(store.root).as_posix()
                if entry.is_dir(follow_symlinks=False):
                    # A nested client is its own intake boundary.
                    if (p/'CLIENT.json').exists():skipped+=1;continue
                    if (p/'.git').exists():repositories.append({'path':relative})
                    pending.append(p)
                elif entry.is_file(follow_symlinks=False):
                    if p.suffix.lower() in {'.pem','.key','.p12','.pfx'}:skipped+=1;continue
                    files.append({'path':relative,'coverage':'not_read' if p.suffix.lower() in TEXT_SUFFIXES else 'requires_reader_or_connector'})
                    if entry.name=='project.json':
                        try:
                            manifest=Store(p.parent).manifest()
                            projects.append({'path':p.parent.relative_to(store.root).as_posix(),'project_id':manifest['project_id'],'name':manifest['name']})
                        except (Invalid,OSError,ValueError):projects.append({'path':p.parent.relative_to(store.root).as_posix(),'error':'invalid_project_manifest'})
    return {'Version-Timestamp':stamp(),'files':files,'projects':projects,'repositories':repositories,'selected_project':None,'content_read':False,'metadata_read':'Valid project.json identity fields only','skipped_entries':skipped,'truncated':truncated,'sharing':'unverified','authority':'Inventory is not source understanding or permission to publish'}

def relative_source_path(value):
    require(isinstance(value,str) and value and not value.startswith('/') and '\\' not in value,'Invalid client-relative source path')
    require(all(part not in {'','.','..'} for part in value.split('/')),'Invalid client-relative source path')

def check_client_ancestry(store,levels):
    for parent in list(store.root.parents)[:levels-1]:
        require(not any((parent/name).exists() or (parent/name).is_symlink() for name in ('CLIENT.json','project.json','.git')),'Intervening client, project or Git boundary requires separate selection')

def link_history(store):
    records=[];parent=None
    for index,p in enumerate(store.entries(LINKS),1):
        require(p.name==f'{index:04d}.json','Invalid client link sequence')
        record=store.json(store.relative(p))
        fields(record,{'schema','project_id','client_id','client_manifest_sha256','ancestor_levels','sources','revision','parent','sha256','Version-Timestamp'})
        store.check_meta(record,'client-link.v1')
        require(record['revision']==index and record['parent']==parent,'Client link chain mismatch')
        require(type(record['ancestor_levels'])==int and 1<=record['ancestor_levels']<=20,'Invalid client ancestor')
        require(str(uuid.UUID(record['client_id']))==record['client_id'],'Invalid client identity')
        require(isinstance(record['sources'],list) and 0<len(record['sources'])<=100,'Invalid source list')
        for source in record['sources']:
            fields(source,{'path','sha256'});relative_source_path(source['path'])
            require(isinstance(source['sha256'],str) and len(source['sha256'])==64,'Invalid source hash')
        parent=digest(encode({k:v for k,v in record.items() if k!='sha256'}))
        require(parent==record['sha256'],'Client link changed; preserve and reconcile')
        if records:require(record['client_id']==records[0]['client_id'] and record['ancestor_levels']==records[0]['ancestor_levels'],'Client association changed; preserve and review')
        records.append(record)
    return records

def source_record(client,relative):
    path=client.path(relative)
    require(not any(p.startswith('.') or p.casefold() in EXCLUDED for p in Path(relative).parts),'Sensitive source path refused')
    require(path.suffix.lower() in TEXT_SUFFIXES,'Source requires an approved text extraction or connector first')
    for parent in path.parents:
        if parent==client.root:break
        require(not (parent/'project.json').exists() and not (parent/'CLIENT.json').exists() and not (parent/'.git').exists(),'Another project or nested client cannot be a shared source')
    data=client.read(relative)
    # Inspect selected text only, never copy its contents into a project link.
    text(data.decode('utf-8'),'selected source',1024*1024)
    return {'path':relative,'sha256':digest(data)}

def link_client(store,client,sources,expected_head):
    strings(sources,'selected sources')
    require(store.root.is_relative_to(client.root) and store.root!=client.root,'Project must be inside the explicitly selected client')
    levels=len(store.root.relative_to(client.root).parts)
    require(levels<=20,'Client is too far above project')
    check_client_ancestry(store,levels)
    manifest=client_manifest(client);history=link_history(store);head=history[-1]['sha256'] if history else 'none'
    require(head==expected_head,'Stale client link head; inspect before retry')
    if history:require(history[0]['client_id']==manifest['client_id'] and history[0]['ancestor_levels']==levels,'Different client association; preserve and review')
    record={**store.meta('client-link.v1'),'client_id':manifest['client_id'],'client_manifest_sha256':digest(encode(manifest)),
            'ancestor_levels':levels,'sources':[source_record(client,p) for p in sources],'revision':len(history)+1,'parent':None if not history else head}
    record['sha256']=digest(encode(record));store.create(f'{LINKS}/{record["revision"]:04d}.json',record)
    return record

def client_status(store):
    history=link_history(store)
    if not history:return {'status':'unlinked','head':'none'}
    latest=history[-1];result={'head':latest['sha256'],'revision':latest['revision'],'client_id':latest['client_id'],'stale_sources':[],'source_issues':[]}
    try:
        check_client_ancestry(store,latest['ancestor_levels'])
        client=root_store(store.root.parents[latest['ancestor_levels']-1]);manifest=client_manifest(client)
        require(manifest['client_id']==latest['client_id'],'Client identity mismatch')
    except (Invalid,OSError,ValueError,IndexError):return {**result,'status':'unavailable','reason':'Expected client ancestor is missing, inaccessible, has a different identity or crosses a new boundary'}
    result['sharing']=manifest['sharing'];result['client_metadata_changed']=digest(encode(manifest))!=latest['client_manifest_sha256']
    for source in latest['sources']:
        reason=None
        try:
            if source_record(client,source['path'])!=source:reason='changed'
        except FileNotFoundError:reason='missing'
        except PermissionError:reason='permission_denied'
        except UnicodeError:reason='invalid_text_encoding'
        except Invalid:reason='unsafe_empty_or_invalid_source'
        except OSError:reason='unreadable'
        if reason:
            result['stale_sources'].append(source['path'])
            result['source_issues'].append({'path':source['path'],'reason':reason})
    result['status']='needs_review' if result['stale_sources'] or result['client_metadata_changed'] else 'current'
    result['authority']='Source hashes and declared sharing only; no actual permission or content approval is inferred'
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',default='.')
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('inventory');p.add_argument('--limit',type=int,default=500)
    p=sub.add_parser('init');p.add_argument('--name',required=True);p.add_argument('--sharing',required=True,choices=['internal','shared','unknown'])
    sub.add_parser('status')
    p=sub.add_parser('link');p.add_argument('--client-root',required=True);p.add_argument('--input',required=True);p.add_argument('--expected-head',required=True)
    args=parser.parse_args()
    try:
        store=root_store(args.root)
        if args.command=='inventory':value=inventory(store,args.limit)
        elif args.command=='init':value=init_client(store,args.name,args.sharing)
        elif args.command=='status':value=client_status(store)
        else:
            selection=store.json(args.input);fields(selection,{'sources'})
            value=link_client(store,root_store(args.client_root),selection['sources'],args.expected_head)
        print(json.dumps(value,ensure_ascii=False,indent=2));return 0
    except (Invalid,OSError,ValueError,TypeError,KeyError,AttributeError) as error:
        print('Client context error: '+(str(error) if isinstance(error,Invalid) else 'Invalid or inaccessible record; preserve and inspect'),file=sys.stderr);return 1

if __name__=='__main__':sys.exit(main())
