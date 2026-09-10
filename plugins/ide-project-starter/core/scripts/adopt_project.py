#!/usr/bin/env python3
# Version-Timestamp: 2026-09-09T17:55:08.294286-04:00
"""Adopt an existing project with create-only files and reviewed instruction appends."""
import argparse
import json
from pathlib import Path
import sys
import uuid
from project_learning import Store, Invalid, require, fields, digest, encode, stamp, text, SECRET
from project_memory import state_check, make_checkpoint
from start_project import destination, workspace_root, render, spec_check, classify

PRESERVE={'README.md','PROJECT.md','QUALITY.md','context/INDEX.md','business/WORK.md','software/WORK.md','.gitignore'}
ENTRY={'AGENTS.md','CLAUDE.md'}
PENDING='.starter/adoption-pending.json'
RECEIPT='.starter/installation.json'

def argument_path(store,value,flag):
    examples={'--input':'adoption-input.json','--plan':'adoption-plan.json','--target':'existing-project'}
    try:return store.path(value)
    except OSError as error:
        raise Invalid(f'{flag}: {type(error).__name__} checking workspace-relative path {safe_path(value)}') from error
    except Invalid:
        raise Invalid(f"{flag} must be a workspace-relative path, not an absolute path, traversal or symlink. Example: {flag} {examples[flag]} (relative to --workspace).") from None

def safe_path(value):
    return '[redacted path]' if SECRET.search(str(value)) else repr(str(value))

def argument_json(store,value,flag):
    argument_path(store,value,flag)
    try:return store.json(value)
    except OSError as error:
        raise Invalid(f"{flag}: {type(error).__name__} reading {safe_path(value)} relative to --workspace. Check that the file exists and is readable.") from error
    except Invalid as error:
        raise Invalid(f"{flag}: {error}; record {safe_path(value)} relative to --workspace.") from error

def selected_sources(dst,state):
    sources=dst.sources(state['sources']) if state['sources'] else []
    for item in sources:
        text(dst.read(item['path']).decode('utf-8'),'selected adoption source',1024*1024)
    return sources

def materialize(store,plan):
    files=render(plan['brief'],plan['project_id'],plan['Version-Timestamp'],scratch=store.path('.starter-work/render'))
    del files['memory/checkpoints/0001.json']
    append={}
    ignore_rules=files[".gitignore"] if ".gitignore" in plan["preserved"] else None
    for name,content in plan['preserved'].items():
        require(name in PRESERVE|ENTRY,'Unsupported preserved path')
        if name not in files:continue
        if name in ENTRY:
            block='\n\n<!-- STARTER ADOPTION '+plan['project_id']+' -->\n'+files[name]+'\n<!-- END STARTER ADOPTION -->\n'
            append[name]=block
        del files[name]
    return files,append,ignore_rules

def verify_plan(store,relative):
    plan=argument_json(store,relative,'--plan')
    fields(plan,{'schema','workspace','Version-Timestamp','project_id','brief','state','target','preserved','sources','hashes','append','plan_id'})
    require(plan['schema']=='adoption-plan.v1' and plan['workspace']==str(store.root),'Adoption workspace mismatch')
    require(digest(encode({k:v for k,v in plan.items() if k!='plan_id'}))==plan['plan_id'],'Adoption plan integrity mismatch')
    require(str(uuid.UUID(plan['project_id']))==plan['project_id'],'Invalid planned identity')
    spec_check(plan['brief']);state_check(plan['state'])
    dst=Store(destination(store,plan['target']))
    require(not store.path(relative).is_relative_to(dst.root),'Plan must be outside target')
    files,append,ignore_rules=materialize(store,plan)
    require({k:digest(v.encode()) for k,v in files.items()}==plan['hashes'] and append==plan['append'],'Toolkit changed since preview; preserve partial output and reconcile')
    return plan,dst,files,ignore_rules

def check_originals(dst,plan,finished=False):
    for name,original in plan['preserved'].items():
        actual=dst.read(name).decode('utf-8');after=original+plan['append'].get(name,'')
        require(actual==after if finished else actual in {original,after},'Existing file changed or entry append incomplete: '+name)
    require(selected_sources(dst,plan['state'])==plan['sources'],'Selected sources changed; review before adoption')

def preview(store,args):
    for flag,value in [('--input',args.input),('--target',args.target),('--plan',args.plan)]:argument_path(store,value,flag)
    payload=argument_json(store,args.input,'--input');fields(payload,{'brief','state'});spec_check(payload['brief']);state_check(payload['state'])
    require(not any(name in ENTRY for name in payload['state']['sources']),'state.sources must exclude AGENTS.md and CLAUDE.md because those instruction files are appended during adoption; select existing project/context documents instead')
    require(payload['brief']['objective']==payload['state']['objective'],'brief.objective and state.objective must match exactly, including whitespace and punctuation; copy the same objective string into both fields')
    dst=Store(destination(store,args.target))
    require(not store.path(args.plan).is_relative_to(dst.root),'Plan must be outside target')
    for name in ['project.json','.starter','memory/checkpoints','memory/learning']:
        require(not dst.path(name).exists(),'Existing identity or memory runtime requires a reviewed upgrade, not adoption: '+name)
    preserved={}
    for name in sorted(PRESERVE|ENTRY):
        if dst.path(name).exists():
            try:value=dst.read(name).decode('utf-8')
            except UnicodeError:raise Invalid('Existing document must be UTF-8 for adoption: '+name) from None
            require(not SECRET.search(value),'Suspected credential in existing document; inspect without copying into the plan: '+name)
            preserved[name]=value
            require(len(encode(preserved))<=400000,'Preserved documents exceed adoption plan budget at '+name+'; use a reviewed manual migration')
    # Source documents are already present; new template files are added separately to checkpoint evidence.
    plan={'schema':'adoption-plan.v1','workspace':str(store.root),'Version-Timestamp':stamp(),'project_id':str(uuid.uuid4()),'brief':payload['brief'],'state':payload['state'],'target':args.target,'preserved':preserved,'sources':selected_sources(dst,payload['state'])}
    # Instruction files change during the explicit merge, so cannot be baseline source inputs.
    require(not any(s['path'] in ENTRY for s in plan['sources']),'Use project/context documents as adoption sources, not instruction files being merged')
    files,append,ignore_rules=materialize(store,plan);result=classify(dst.root,files)
    require(not result['conflicts'] and not result['same'],'Owned path collision; preserve and prepare a manual migration')
    plan['hashes']={k:digest(v.encode()) for k,v in files.items()};plan['append']=append
    plan['plan_id']=digest(encode(plan));store.create(args.plan,plan)
    return {'status':'previewed','plan':args.plan,'plan_id':plan['plan_id'],'create':sorted(files),'preserve':sorted(preserved),'review_and_append':append,'unapplied_ignore_rules':ignore_rules,'warning':'Plan contains reviewed project context and original instructions; keep it in an approved private workspace.'}

def apply(store,args):
    plan,dst,files,ignore_rules=verify_plan(store,args.plan)
    if dst.path(RECEIPT).exists():return finish(store,args)
    if dst.path(PENDING).exists():require(dst.json(PENDING)['plan_id']==plan['plan_id'],'Different adoption pending')
    check_originals(dst,plan)
    result=classify(dst.root,files);require(not result['conflicts'],'Adoption output conflict; no files applied')
    # Guard competing plans before publishing any project records.
    if not dst.path(PENDING).exists():dst.create(PENDING,{'schema':'adoption-pending.v1','Version-Timestamp':stamp(),'plan_id':plan['plan_id']})
    for name in sorted(files):
        if name not in result['same']:dst.create_bytes(name,files[name].encode())
    return {'status':'needs_entry_review','plan_id':plan['plan_id'],'created':result['create'],'append':plan['append'],'unapplied_ignore_rules':ignore_rules,'next_action':'Review and append exact blocks preserving original bytes, then run finish. No checkpoint exists yet.'}

def finish(store,args):
    plan,dst,files,ignore_rules=verify_plan(store,args.plan)
    require(dst.path(PENDING).exists(),'Run apply first; no adoption is pending')
    require(dst.json(PENDING)['plan_id']==plan['plan_id'],'Different adoption pending')
    if dst.path(RECEIPT).exists():
        require(dst.json(RECEIPT).get('plan_id')==plan['plan_id'] and dst.manifest()['project_id']==plan['project_id'],'Different installation exists')
        return {'status':'already_adopted','project_id':plan['project_id'],'next_action':'Run resume and validate current work separately.'}
    check_originals(dst,plan,finished=True)
    actual=classify(dst.root,files)
    require(not actual['create'] and not actual['conflicts'],'Generated additions changed or missing; inspect and reapply the same plan before finishing')
    state=dict(plan['state']);state['sources']=list(dict.fromkeys(state['sources']+['PROJECT.md','context/INDEX.md','QUALITY.md']))
    record=make_checkpoint(dst,state,1,None)
    record['Version-Timestamp']=plan['Version-Timestamp']
    record['sha256']=digest(encode({k:v for k,v in record.items() if k!='sha256'}))
    checkpoint='memory/checkpoints/0001.json'
    if dst.path(checkpoint).exists():require(dst.json(checkpoint)==record,'Different checkpoint exists; preserve and reconcile')
    else:dst.create(checkpoint,record)
    dst.create(RECEIPT,{'schema':'installation.v1','Version-Timestamp':stamp(),'mode':'adopt-existing','plan_id':plan['plan_id'],'project_id':plan['project_id'],'hashes':plan['hashes']})
    return {'status':'adopted','project_id':plan['project_id'],'checkpoint_head':record['sha256'],'next_action':'Run resume and validate; recorded check claims have not been rerun.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--workspace',required=True);parser.add_argument('--debug',action='store_true',help='Show a local diagnostic traceback; it may contain private paths or content');sub=parser.add_subparsers(dest='command',required=True)
    for name in ['preview','apply','finish']:
        p=sub.add_parser(name);p.add_argument('--plan',required=True);p.add_argument('--debug',action='store_true',default=argparse.SUPPRESS)
        if name=='preview':p.add_argument('--target',required=True);p.add_argument('--input',required=True)
    args=parser.parse_args()
    try:
        value={'preview':preview,'apply':apply,'finish':finish}[args.command](Store(workspace_root(args.workspace)),args)
        print(json.dumps(value,ensure_ascii=False,indent=2));return 0
    except (Invalid,OSError,ValueError,TypeError,KeyError,AttributeError,ImportError) as error:
        if args.debug:raise
        detail=str(error) if isinstance(error,Invalid) else f'{type(error).__name__} during {args.command}'
        if isinstance(error,OSError) and error.filename:detail+=' at '+safe_path(Path(error.filename).name)
        print('Adoption error: '+detail+'. Preserve partial work. Use --debug for a local traceback; review it for private data before sharing.',file=sys.stderr);return 1
if __name__=='__main__':sys.exit(main())
