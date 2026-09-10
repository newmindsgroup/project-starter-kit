#!/usr/bin/env python3
# Version-Timestamp: 2026-09-08T17:52:11.763839-04:00
"""Preview and apply the bundled template within an explicit workspace boundary."""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import uuid
from project_learning import Store, Invalid, require, fields, text, strings, digest, encode, stamp
from project_memory import make_checkpoint

BASE=Path(__file__).resolve().parents[1]

def spec_check(spec):
    fields(spec,{'name','profile','objective','audience','constraints','success_criteria'})
    for key in ['name','objective','audience']:text(spec[key],key,2000)
    require(spec['profile'] in {'business','software'},'Unsupported profile')
    strings(spec['constraints'],'constraints',minimum=0);strings(spec['success_criteria'],'success criteria')

def workspace_root(value):
    require(os.name=='posix', 'Initializer requires a POSIX filesystem; Windows support is not validated')
    path=Path(value).expanduser().absolute()
    require('..' not in path.parts, 'Workspace traversal is not supported')
    require(not any(p.is_symlink() for p in (path, *path.parents)), 'Workspace symlinks are not supported; choose the canonical directory path')
    root=path.resolve(strict=True)
    require(root.is_dir() and root!=Path(root.anchor) and root!=Path.home().resolve(), 'Choose a dedicated project workspace')
    return root

def destination(store,relative):
    path=store.path(relative)
    protected={'scripts','template','skills','tests','research','memory','config','docs','validation','recovery-evaluation','.git','.codex','.agents','.claude','.starter','.starter-work','.starter-tools'}
    require(not any(part.casefold() in {'.git','.codex','.agents','.claude','.starter','.starter-work','.starter-tools'} for part in Path(relative).parts), 'Target overlaps protected metadata')
    candidate=str(path.resolve()).casefold()
    base=str(BASE.resolve()).casefold()
    require(candidate!=base and not base.startswith(candidate+'/'), 'Target overlaps starter source')
    for name in protected:
        source=str(BASE/name).casefold()
        require(candidate!=source and not candidate.startswith(source+'/'), 'Target overlaps starter source')
    require(path.is_dir(), 'Target must be an existing child folder')
    return path

def render(spec,project_id,timestamp,scratch=None):
    # Use only the bundled template, no remote source or caller-supplied template.
    from copier import run_copy, Settings
    import copier
    require(copier.__version__=='9.18.2','Use the tested Copier 9.18.2 environment')
    tmp=scratch if scratch is not None else BASE/'experiments/.tmp';tmp.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=tmp,prefix='render-') as folder:
        folder=Path(folder);source=folder/'template';output=folder/'output'
        shutil.copytree(BASE/'template',source,symlinks=True)
        require(not any(p.is_symlink() for p in source.rglob('*')),'Template symlinks are not supported')
        runtime=source/'skeleton/.starter';runtime.mkdir(parents=True,exist_ok=True)
        for name in ['project_learning.py','project_memory.py','project_client.py','project_feedback.py']:
            (runtime/name).write_bytes((BASE/'scripts'/name).read_bytes())
        (source/'skeleton/config').mkdir(parents=True,exist_ok=True)
        (source/'skeleton/config/learning-skills.json').write_bytes((BASE/'config/learning-skills.json').read_bytes())
        for skill in ['starter-resume','starter-checkpoint','starter-review']:
            content=(BASE/'skills'/skill/'SKILL.md').read_bytes()
            for tool in ['.agents','.claude']:
                path=source/'skeleton'/tool/'skills'/skill/'SKILL.md'
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(content)
        data={**spec,'version_timestamp':timestamp}
        previous_env=os.environ.get('TMPDIR');previous_temp=tempfile.tempdir
        try:
            os.environ['TMPDIR']=str(tmp);tempfile.tempdir=str(tmp)
            run_copy(str(source),output,data=data,defaults=True,quiet=True,settings=Settings(defaults={},trust=[]),unsafe=False)
        finally:
            tempfile.tempdir=previous_temp
            if previous_env is None:os.environ.pop('TMPDIR',None)
            else:os.environ['TMPDIR']=previous_env
        target_store=Store(output)
        target_store.create('project.json',{'schema':'project.v1','project_id':project_id,'name':spec['name'],'Version-Timestamp':timestamp})
        state={'objective':spec['objective'],'constraints':spec['constraints'],'decisions':[], 'completed':[],
               'checks':[],'blockers':['Existing context and project-specific quality commands need review.'],
               'next_action':'Review context/INDEX.md and define the first milestone.', 'external_actions':[],
               'sources':['PROJECT.md','context/INDEX.md','QUALITY.md']}
        initial=make_checkpoint(target_store,state,1,None)
        initial['Version-Timestamp']=timestamp
        initial['sha256']=digest(encode({k:v for k,v in initial.items() if k!='sha256'}))
        target_store.create('memory/checkpoints/0001.json',initial)
        files={p.relative_to(output).as_posix():target_store.read(p.relative_to(output).as_posix()).decode('utf-8') for p in output.rglob('*') if p.is_file()}
        require(len(files)<100 and sum(len(v.encode()) for v in files.values())<800000,'Template exceeds bounded plan size')
        return files

def classify(target,files):
    store=Store(target);conflicts=[];create=[];same=[]
    for path,content in files.items():
        try:
            p=store.path(path)
            if p.exists():
                (same if store.read(path)==content.encode() else conflicts).append(path)
            else:
                for ancestor in p.parents:
                    if ancestor==target:break
                    require(not ancestor.exists() or ancestor.is_dir(),'Blocked target directory')
                create.append(path)
        except (Invalid,OSError):conflicts.append(path)
    return {'create':sorted(create),'same':sorted(same),'conflicts':sorted(conflicts)}

def preview(store,args):
    spec=store.json(args.input);spec_check(spec);target=destination(store,args.target)
    plan_path=store.path(args.plan)
    require(not plan_path.is_relative_to(target),'Plan must be outside target')
    pid=str(uuid.uuid4());timestamp=stamp();files=render(spec,pid,timestamp,scratch=store.path('.starter-work/render'))
    plan={'schema':'starter-plan.v2','workspace':str(store.root),'Version-Timestamp':timestamp,'project_id':pid,'spec':spec,'target':args.target,
          'hashes':{k:digest(v.encode()) for k,v in files.items()}}
    plan['plan_id']=digest(encode(plan))
    store.create(args.plan,plan)
    return {'plan':args.plan,'plan_id':plan['plan_id'],**classify(target,files),'existing_content':'Unrelated files preserved; content inventory remains a human/agent intake step.'}

def apply(store,args):
    plan=store.json(args.plan)
    fields(plan,{'schema','Version-Timestamp','project_id','spec','target','hashes','plan_id'} | ({'workspace'} if plan.get('schema')=='starter-plan.v2' else set()))
    require(plan['schema'] in {'starter-plan.v1','starter-plan.v2'} and digest(encode({k:v for k,v in plan.items() if k!='plan_id'}))==plan['plan_id'],'Plan integrity mismatch')
    require((plan['schema']=='starter-plan.v1' and store.root==BASE) or (plan['schema']=='starter-plan.v2' and plan['workspace']==str(store.root)), 'Plan belongs to a different workspace; preview again')
    require(str(uuid.UUID(plan['project_id']))==plan['project_id'],'Invalid planned identity')
    spec_check(plan['spec']);text(plan['Version-Timestamp'],'timestamp')
    target=destination(store,plan['target']);dst=Store(target)
    receipt_path='.starter/installation.json'
    if dst.path(receipt_path).exists():
        receipt=dst.json(receipt_path)
        require(receipt.get('plan_id')==plan['plan_id'] and dst.manifest()['project_id']==plan['project_id'],'Different initialization exists; preserve and reconcile')
        return {'status':'already_initialized','project_id':plan['project_id'],'note':'Existing edits preserved; run resume and validate separately.'}
    files=render(plan['spec'],plan['project_id'],plan['Version-Timestamp'],scratch=store.path('.starter-work/render'))
    require({k:digest(v.encode()) for k,v in files.items()}==plan['hashes'],'Template changed after preview; create a new plan')
    result=classify(target,files);require(not result['conflicts'],'Target conflicts; no files applied. Review preview or use a new folder.')
    # Create-only publication. Repeating this same plan can complete matching partial output.
    for relative in sorted(files):
        if relative in result['same']:continue
        dst.create_bytes(relative,files[relative].encode())
    dst.create(receipt_path,{'schema':'installation.v1','Version-Timestamp':stamp(),'plan_id':plan['plan_id'],'project_id':plan['project_id'],'hashes':plan['hashes']})
    return {'status':'initialized','project_id':plan['project_id'],'created':result['create']}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--workspace',default=str(BASE));sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('preview');p.add_argument('--target',required=True);p.add_argument('--input',required=True);p.add_argument('--plan',required=True)
    sub.add_parser('apply').add_argument('--plan',required=True);args=parser.parse_args()
    try:
        store=Store(workspace_root(args.workspace));value=preview(store,args) if args.command=='preview' else apply(store,args)
        print(json.dumps(value,ensure_ascii=False,indent=2));return 0
    except (Invalid,OSError,ValueError,TypeError,KeyError,AttributeError,ImportError) as error:
        print('Starter error: '+(str(error) if isinstance(error,Invalid) else 'Missing dependency or invalid/inaccessible record; inspect partial output before retry'),file=sys.stderr);return 1

if __name__=='__main__':sys.exit(main())
