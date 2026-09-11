#!/usr/bin/env python3
# Version-Timestamp: 2026-09-11 16:14:13 AST
"""Move a 0.6 starter project to the 0.7 lowercase record layout.

preview requires resume to be ready, then stages a sealed plan, exact candidate
instruction files and their originals outside the project. Review each
candidate against its original before running apply. apply checks every record,
every instruction file and every target name before changing anything. It then
renames each record through a temporary name derived from the plan, so a
case-only rename works on case-insensitive filesystems and an interrupted run
can be completed, and replaces each instruction file with its reviewed
candidate only while the file still matches its staged original. finish
verifies the result and that no source changed since the last checkpoint,
appends a checkpoint whose state uses the new names, and records a chained
receipt. Record content never changes."""
import argparse
import json
import os
import re
import subprocess
import sys
from project_learning import Store,Invalid,require,fields,digest,stamp,LEGACY_LAYOUT,exact_exists
from project_memory import Continuity
from start_project import destination,workspace_root
from project_feedback import sealed,checked

RECEIPTS='.starter/migration-receipts'
CANDIDATES=('AGENTS.md','CLAUDE.md','README.md','PROJECT.md','QUALITY.md')
BLOCK=re.compile(r'(<!-- STARTER ADOPTION [0-9a-f-]{36} -->\r?\n)(.*?)(<!-- END STARTER ADOPTION -->)',re.S)
PAIRS=set(LEGACY_LAYOUT.items())

def rename_text(text):
    for old,new in LEGACY_LAYOUT.items():text=text.replace(old,new)
    return text

def rewrite(text):
    """Inside an adoption block: new names, and headings one level down so the
    host file keeps a single title. Elsewhere: new names only."""
    if not BLOCK.search(text):return rename_text(text)
    def fix(match):
        body=rename_text(match.group(2))
        # Demote only while a top-level heading remains. An already migrated
        # block has none, so running the migration again changes nothing.
        if re.search(r'^# ',body,re.M):body=re.sub(r'^(#{1,5}) ',r'#\1 ',body,flags=re.M)
        return match.group(1)+body+match.group(3)
    return BLOCK.sub(fix,text)

def map_state(state):
    result={}
    for key,value in state.items():
        if key=='sources':result[key]=[LEGACY_LAYOUT.get(v,v) for v in value]
        elif isinstance(value,str):result[key]=rename_text(value)
        elif isinstance(value,list):result[key]=[rename_text(v) if isinstance(v,str) else v for v in value]
        else:result[key]=value
    return result

def survey(dst):
    renames=[];both=[]
    for old,new in LEGACY_LAYOUT.items():
        has_old,has_new=exact_exists(dst.root,old),exact_exists(dst.root,new)
        if has_old and has_new:both.append(old)
        elif has_old:
            require(not dst.path(old).is_symlink(),'Symlink record refused')
            renames.append({'from':old,'to':new,'sha256':digest(dst.read(old))})
    require(not both,'Old and new names both exist; reconcile manually: '+', '.join(both))
    edits={};skipped=[]
    for name in CANDIDATES:
        if not exact_exists(dst.root,name):continue
        # Checked on the raw path because Store.path refuses symlinks outright; the
        # name comes from the fixed CANDIDATES list, so this cannot traverse.
        if (dst.root/name).is_symlink():skipped.append(name);continue
        before=dst.read(name);after=rewrite(before.decode('utf-8')).encode('utf-8')
        if after!=before:edits[name]={'before':digest(before),'after':digest(after),'original':before,'content':after}
    return renames,edits,skipped

def outside(store,stage,dst):
    stage_path=store.path(stage)
    require(not stage_path.is_relative_to(dst.root) and not dst.root.is_relative_to(stage_path),'Migration staging must be outside the project')
    return stage_path

def preview(store,target,stage):
    dst=Store(destination(store,target));project_id=dst.manifest()['project_id']
    stage_path=outside(store,stage,dst)
    require(not stage_path.exists(),'Migration staging already exists; preserve or choose a new path')
    memory=Continuity(dst.root)
    require(memory.resume()['status']=='ready_for_context_review','Resume reports needs_review; reconcile changed sources and save a checkpoint before migrating')
    head=memory.history()[-1]['sha256']
    renames,edits,skipped=survey(dst)
    plan=sealed({'schema':'layout-migration-plan.v1','Version-Timestamp':stamp(),'workspace':str(store.root),'target':target,'project_id':project_id,
                 'checkpoint_head':head,'renames':renames,'edits':{n:{'before':e['before'],'after':e['after']} for n,e in edits.items()}})
    store.create(stage+'/plan.json',plan)
    for n,e in edits.items():
        store.create_bytes(stage+'/candidate/'+n,e['content']);store.create_bytes(stage+'/original/'+n,e['original'])
    result={'status':'nothing_to_migrate' if not renames and not edits else 'staged','plan':stage+'/plan.json','skipped':skipped}
    if result['status']=='staged':
        result.update({'renames':[r['from']+' to '+r['to'] for r in renames],'candidates':sorted(edits),
                       'next_action':'Review each file under candidate/ against original/, then run apply. Apply renames the records and replaces an instruction file only while it still matches original/. Then run finish.'})
    return result

def load(store,stage):
    plan=checked(store.json(stage+'/plan.json'))
    fields(plan,{'schema','Version-Timestamp','workspace','target','project_id','checkpoint_head','renames','edits','sha256'})
    require(plan['schema']=='layout-migration-plan.v1' and plan['workspace']==str(store.root),'Migration workspace mismatch')
    dst=Store(destination(store,plan['target']));outside(store,stage,dst)
    require(dst.manifest()['project_id']==plan['project_id'],'Project identity changed')
    for r in plan['renames']:
        fields(r,{'from','to','sha256'})
        require((r['from'],r['to']) in PAIRS,'Plan renames a path outside the 0.6 layout')
        require(isinstance(r['sha256'],str) and len(r['sha256'])==64,'Invalid record digest')
    require(len({r['from'] for r in plan['renames']})==len(plan['renames']),'Duplicate rename in plan')
    require(set(plan['edits'])<=set(CANDIDATES),'Plan edits a file outside the instruction files')
    for n,e in plan['edits'].items():
        fields(e,{'before','after'})
        require(digest(store.read(stage+'/candidate/'+n))==e['after'],'Staged candidate changed: '+n)
        require(digest(store.read(stage+'/original/'+n))==e['before'],'Staged original changed: '+n)
    return plan,dst

def temp_name(plan,index,record):
    return record['from'].rsplit('/',1)[0]+'/.migrate-'+plan['sha256'][:12]+'-'+str(index)

def condition(dst,record,temp):
    present=[exact_exists(dst.root,p) for p in (record['to'],record['from'],temp)]
    if present.count(True)!=1:return 'conflict'
    index=present.index(True);path=(record['to'],record['from'],temp)[index]
    return ('done','pending','interrupted')[index] if digest(dst.read(path))==record['sha256'] else 'changed'

def apply(store,stage):
    plan,dst=load(store,stage)
    temps=[temp_name(plan,i,r) for i,r in enumerate(plan['renames'])]
    states=[condition(dst,r,t) for r,t in zip(plan['renames'],temps)]
    bad=[r['from'] for r,s in zip(plan['renames'],states) if s in ('changed','conflict')]
    require(not bad,'Records changed or in an unexpected state; reconcile manually: '+', '.join(bad))
    for n,e in plan['edits'].items():
        current=digest(dst.read(n)) if exact_exists(dst.root,n) else None
        require(current in (e['before'],e['after']),'Instruction file changed since preview; preview again: '+n)
    for r,s in zip(plan['renames'],states):
        if s=='done':continue
        folder,new=r['to'].rsplit('/',1);old=r['from'].rsplit('/',1)[1]
        clash=[n for n in os.listdir(dst.path(folder)) if n.casefold()==new.casefold() and n not in (old,new)]
        require(not clash,'Another file already uses the name '+r['to']+' in another letter case; reconcile manually')
    renamed=[]
    for r,t,s in zip(plan['renames'],temps,states):
        if s=='done':continue
        source,temp,final=dst.path(r['from']),dst.path(t),dst.path(r['to'])
        if s=='pending':os.rename(source,temp)
        try:
            # With the old name moved aside, this ordinary check also sees case
            # variants of the new name, which exact_exists deliberately ignores.
            require(not final.exists(),'Another file already uses the name '+r['to']+'; reconcile manually')
            os.rename(temp,final)
        except BaseException:
            os.rename(temp,source);raise
        renamed.append(r['to'])
    replaced=[]
    for n,e in plan['edits'].items():
        current=digest(dst.read(n))
        if current==e['after']:continue
        # Checked immediately before the replacement, so an edit made after
        # preview is never overwritten; the staged original stays for recovery.
        require(current==e['before'],'Instruction file changed since preview; preview again: '+n)
        temp=dst.root/('.migrate-'+plan['sha256'][:12]+'-'+n)
        temp.write_bytes(store.read(stage+'/candidate/'+n))
        os.replace(temp,dst.path(n));replaced.append(n)
    return {'status':'applied','renamed':renamed,'replaced':replaced,'next_action':'Run finish.'}

def verify_sources(dst,plan,checkpoint,mapped=True):
    for evidence in checkpoint['evidence']:
        current=LEGACY_LAYOUT.get(evidence['path'],evidence['path']) if mapped else evidence['path']
        if mapped and current in plan['edits']:
            require(plan['edits'][current]['before']==evidence['sha256'],'Source changed before migration: '+current)
        else:
            require(exact_exists(dst.root,current) and digest(dst.read(current))==evidence['sha256'],'Source changed since the last checkpoint: '+current)

def tracked_legacy(root):
    """Old names still recorded in Git. On a case-insensitive filesystem with
    core.ignorecase, git add -A does not record a rename that changes only
    letter case, so the repository keeps the old name while the disk has the new."""
    try:
        inside=subprocess.run(['git','-C',str(root),'rev-parse','--is-inside-work-tree'],capture_output=True,text=True,timeout=30)
        if inside.returncode!=0 or inside.stdout.strip()!='true':return []
        listed=subprocess.run(['git','-C',str(root),'ls-files','-z','--',*LEGACY_LAYOUT],capture_output=True,timeout=30).stdout
    except (OSError,subprocess.SubprocessError):return []
    names={n.decode('utf-8','replace') for n in listed.split(b'\0') if n}
    return [old for old in LEGACY_LAYOUT if old in names]

def finish(store,stage):
    plan,dst=load(store,stage);prior=dst.entries(RECEIPTS);parent=None
    for p in prior:
        receipt=checked(dst.json(dst.relative(p)))
        require(receipt['parent']==parent,'Migration receipt chain mismatch');parent=receipt['sha256']
        if receipt['plan_id']==plan['sha256']:return {'status':'already_migrated','checkpoint':receipt['checkpoint']}
    for r in plan['renames']:
        require(exact_exists(dst.root,r['to']) and not exact_exists(dst.root,r['from']),'Rename not applied: '+r['from'])
        require(digest(dst.read(r['to']))==r['sha256'],'Record changed during migration: '+r['to'])
    for n,e in plan['edits'].items():require(digest(dst.read(n))==e['after'],'Candidate not applied exactly: '+n)
    remaining=[old for old in LEGACY_LAYOUT if exact_exists(dst.root,old)]
    require(not remaining,'Old names remain: '+', '.join(remaining))
    memory=Continuity(dst.root);history=memory.history()
    base=next((c for c in history if c['sha256']==plan['checkpoint_head']),None)
    require(base is not None,'The checkpoint recorded at preview is missing; resume and reconcile')
    state=map_state(base['state']);latest=history[-1]
    needed=state!=base['state'] or bool(set(plan['edits'])&set(state['sources']))
    if latest['sha256']==plan['checkpoint_head']:
        verify_sources(dst,plan,base)
        checkpoint=memory.checkpoint(state,latest['sha256'])['checkpoint_id'] if needed else None
    elif needed and latest['parent']==plan['checkpoint_head'] and latest['state']==state:
        # A previous finish wrote this checkpoint and stopped before its receipt.
        verify_sources(dst,plan,latest,mapped=False);checkpoint=latest['checkpoint_id']
    else:
        raise Invalid('Checkpoints changed since preview; resume and reconcile')
    receipt=sealed({'schema':'layout-migration-receipt.v1','Version-Timestamp':stamp(),'plan_id':plan['sha256'],'project_id':plan['project_id'],
                    'parent':parent,'renames':plan['renames'],'edits':plan['edits'],'checkpoint':checkpoint})
    dst.create(f'{RECEIPTS}/{len(prior)+1:04d}.json',receipt)
    restage=[f'git rm --cached -q {old} && git add {LEGACY_LAYOUT[old]}' for old in tracked_legacy(dst.root)]
    action='Run upgrade_project.py preview, check and finish to receive the 0.7 helpers, workflows and skills.'
    if restage:action='Record the renames in Git first, from the project root, because git add -A misses case-only renames on macOS and Windows: '+'; '.join(restage)+'. Then '+action[0].lower()+action[1:]
    return {'status':'migrated','checkpoint':checkpoint,'receipt_head':receipt['sha256'],'git_restage':restage,'next_action':action}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--workspace',required=True);sub=parser.add_subparsers(dest='command',required=True)
    for name in ['preview','apply','finish']:
        p=sub.add_parser(name);p.add_argument('--stage',required=True)
        if name=='preview':p.add_argument('--target',required=True)
    args=parser.parse_args()
    try:
        store=Store(workspace_root(args.workspace))
        value=preview(store,args.target,args.stage) if args.command=='preview' else {'apply':apply,'finish':finish}[args.command](store,args.stage)
        print(json.dumps(value,indent=2));return 0
    except (Invalid,OSError,ValueError,TypeError,KeyError,AttributeError) as error:
        print('Migration error: '+(str(error) if isinstance(error,Invalid) else type(error).__name__+'; preserve the stage and inspect'),file=sys.stderr);return 1
if __name__=='__main__':sys.exit(main())
