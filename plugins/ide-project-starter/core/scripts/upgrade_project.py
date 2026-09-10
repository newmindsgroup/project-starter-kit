#!/usr/bin/env python3
# Version-Timestamp: 2026-09-08T17:48:04.992939-04:00
"""Stage and verify reviewed project-copy upgrades. Never replaces project files."""
import argparse
import difflib
import json
from pathlib import Path
import subprocess
import sys
from project_learning import Store,Invalid,require,fields,digest,encode,stamp
from start_project import BASE,destination,workspace_root
from project_feedback import sealed,checked

RECEIPTS='.starter/upgrade-receipts'

def candidates():
    kit=Store(BASE);release=kit.json('config/plugin-release.json');result={}
    mapping={'.starter/'+n:'scripts/'+n for n in ['project_learning.py','project_memory.py','project_client.py','project_feedback.py']}
    mapping['config/learning-skills.json']='config/learning-skills.json'
    mapping['context/STORAGE.md']='template/skeleton/context/STORAGE.md.jinja'
    for name in ['start-project','resume-project','checkpoint-project','review-project']:mapping['workflows/'+name+'.md']='template/skeleton/workflows/'+name+'.md.jinja'
    for tool in ['.agents','.claude']:
        for name in ['starter-resume','starter-checkpoint','starter-review']:mapping[f'{tool}/skills/{name}/SKILL.md']='skills/'+name+'/SKILL.md'
    for target,source in mapping.items():
        value=kit.read(source).decode('utf-8').replace('{{ version_timestamp }}',release['Version-Timestamp'])
        require('{{' not in value and '{%' not in value,'Unsupported upgrade template; use reviewed migration')
        result[target]=value
    return release['version'],result

def baseline(dst):
    initial=dst.json('.starter/installation.json');require(initial['project_id']==dst.manifest()['project_id'],'Installation identity mismatch')
    result=dict(initial['hashes']);parent=None;records=[]
    for index,p in enumerate(dst.entries(RECEIPTS),1):
        require(p.name==f'{index:04d}.json','Upgrade receipt sequence mismatch');r=checked(dst.json(dst.relative(p)))
        require(r['parent']==parent and r['project_id']==initial['project_id'],'Upgrade receipt chain mismatch')
        result.update(r['hashes']);parent=r['sha256'];records.append(r)
    return result,records

def protected(dst):
    names=['project.json','.starter/installation.json']
    for name in ['AGENTS.md','CLAUDE.md','README.md','PROJECT.md','QUALITY.md','.gitignore']:
        if dst.path(name).exists():names.append(name)
    for folder in ['memory','context']:
        root=dst.path(folder)
        if root.exists():
            for p in root.rglob('*'):
                require(not p.is_symlink(),'Symlink protected record refused')
                if p.is_file() and dst.relative(p)!='context/STORAGE.md':names.append(dst.relative(p))
    require(len(names)<=2000,'Protected record inventory too large; use a reviewed migration')
    return {n:digest(dst.read(n)) for n in sorted(names)}

def preview(store,target,stage):
    dst=Store(destination(store,target));stage_path=store.path(stage)
    require(not stage_path.is_relative_to(dst.root) and not dst.root.is_relative_to(stage_path),'Upgrade staging must be outside the project')
    require(not stage_path.exists(),'Upgrade staging already exists; preserve or choose a new path')
    version,files=candidates();known,records=baseline(dst);before={};conflicts=[]
    for name in files:
        actual=digest(dst.read(name)) if dst.path(name).exists() else None;expected=known.get(name)
        if actual!=expected:conflicts.append(name)
        before[name]=actual
    require(not conflicts,'Customized or missing managed files require manual migration: '+', '.join(conflicts))
    original={n:dst.read(n).decode('utf-8') for n in files if before[n] is not None}
    plan=sealed({'schema':'upgrade-plan.v1','Version-Timestamp':stamp(),'workspace':str(store.root),'target':target,'project_id':dst.manifest()['project_id'],'version':version,'parent':records[-1]['sha256'] if records else None,'before':before,'after':{n:digest(v.encode()) for n,v in files.items()},'protected':protected(dst),'changes':[n for n,v in files.items() if before[n]!=digest(v.encode())]})
    # Plan is the recovery anchor, published before staging other files. Retry uses a new stage if incomplete.
    store.create(stage+'/plan.json',plan)
    for name,value in files.items():store.create_bytes(stage+'/candidate/'+name,value.encode())
    for name,value in original.items():store.create_bytes(stage+'/original/'+name,value.encode())
    diff=''.join(''.join(difflib.unified_diff(original.get(n,'').splitlines(True),files[n].splitlines(True),fromfile=n+' (original)',tofile=n+' (candidate)')) for n in plan['changes'])
    store.create_bytes(stage+'/changes.diff',diff.encode())
    return {'status':'staged','version':version,'changes':plan['changes'],'plan':stage+'/plan.json','next_action':'Review changes.diff and run check before applying exact candidate changes manually.'}

def load(store,stage):
    plan=checked(store.json(stage+'/plan.json'))
    fields(plan,{'schema','Version-Timestamp','workspace','target','project_id','version','parent','before','after','protected','changes','sha256'})
    require(plan['schema']=='upgrade-plan.v1' and plan['workspace']==str(store.root),'Upgrade workspace mismatch')
    dst=Store(destination(store,plan['target']));require(not store.path(stage).is_relative_to(dst.root) and not dst.root.is_relative_to(store.path(stage)),'Stage overlaps project')
    version,files=candidates();require(version==plan['version'] and {n:digest(v.encode()) for n,v in files.items()}==plan['after'],'Toolkit changed; preserve stage and prepare a fresh reviewed plan')
    require(set(plan['before'])==set(files),'Plan managed paths changed')
    require(plan['changes']==[n for n in files if plan['before'][n]!=plan['after'][n]],'Plan change list mismatch')
    require(dst.manifest()['project_id']==plan['project_id'],'Project identity changed')
    for n in files:require(store.read(stage+'/candidate/'+n)==files[n].encode(),'Staged candidate changed: '+n)
    for n,h in plan['before'].items():
        if h is not None:require(digest(store.read(stage+'/original/'+n))==h,'Staged original changed: '+n)
    require(protected(dst)==plan['protected'],'Protected project records changed; reconcile before upgrade')
    return plan,dst

def run_checks(store,stage,dst):
    results=[]
    for name,command in [('project_memory.py','resume'),('project_learning.py','validate')]:
        r=subprocess.run([sys.executable,'-B',str(store.path(stage+'/candidate/.starter/'+name)),'--root',str(dst.root),command],capture_output=True,text=True,timeout=30)
        require(r.returncode==0,'Candidate '+command+' failed; inspect project records')
        output=json.loads(r.stdout)
        if command=='resume':require(output['status']=='ready_for_context_review','Resolve stale or unavailable context before upgrading')
        results.append({'command':command,'result':output})
    return results

def check(store,stage):
    plan,dst=load(store,stage);known,records=baseline(dst)
    require((records[-1]['sha256'] if records else None)==plan['parent'],'Upgrade baseline changed')
    for n,h in plan['before'].items():require((digest(dst.read(n)) if dst.path(n).exists() else None)==h,'Project changed before candidate check: '+n)
    results=run_checks(store,stage,dst)
    require(protected(dst)==plan['protected'],'Project records changed during checks')
    r=sealed({'schema':'upgrade-check.v1','Version-Timestamp':stamp(),'plan_id':plan['sha256'],'results':results})
    store.create(stage+'/checks.json',r)
    return {'status':'candidate_checked','results':results,'next_action':'Apply only reviewed changed candidates, then run finish. Originals are retained for recovery.'}

def finish(store,stage):
    plan,dst=load(store,stage);known,records=baseline(dst)
    if records and records[-1]['plan_id']==plan['sha256']:return {'status':'already_upgraded','version':plan['version']}
    require((records[-1]['sha256'] if records else None)==plan['parent'],'Upgrade baseline changed')
    require(store.path(stage+'/checks.json').exists(),'Run check before finishing this upgrade')
    receipt=checked(store.json(stage+'/checks.json'));require(receipt['plan_id']==plan['sha256'],'Candidate check is missing or for another plan')
    for n,h in plan['after'].items():require(dst.path(n).exists() and digest(dst.read(n))==h,'Candidate not applied exactly: '+n)
    results=run_checks(store,stage,dst)
    require(protected(dst)==plan['protected'],'Project records changed during verification')
    r=sealed({'schema':'upgrade-receipt.v1','Version-Timestamp':stamp(),'plan_id':plan['sha256'],'project_id':plan['project_id'],'version':plan['version'],'parent':plan['parent'],'hashes':plan['after'],'checks':results})
    dst.create(f'{RECEIPTS}/{len(records)+1:04d}.json',r)
    return {'status':'upgraded','version':plan['version'],'receipt_head':r['sha256'],'note':'This records project-copy upgrade only, not plugin installation.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--workspace',required=True);sub=parser.add_subparsers(dest='command',required=True)
    for name in ['preview','check','finish']:
        p=sub.add_parser(name);p.add_argument('--stage',required=True)
        if name=='preview':p.add_argument('--target',required=True)
    args=parser.parse_args()
    try:
        store=Store(workspace_root(args.workspace));value=preview(store,args.target,args.stage) if args.command=='preview' else {'check':check,'finish':finish}[args.command](store,args.stage)
        print(json.dumps(value,indent=2));return 0
    except (Invalid,OSError,ValueError,TypeError,KeyError,AttributeError,subprocess.SubprocessError) as error:
        print('Upgrade error: '+(str(error) if isinstance(error,Invalid) else 'Invalid or inaccessible upgrade record; preserve stage and inspect'),file=sys.stderr);return 1
if __name__=='__main__':sys.exit(main())
