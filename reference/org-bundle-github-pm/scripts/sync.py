from pathlib import Path
import datetime as dt
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LIMIT = 1000


def run(*args):
    return subprocess.check_output(args, text=True, cwd=ROOT).strip()


def query(*args):
    return json.loads(run('gh', *args))


def sync_repo(name):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', name) or any(p in ('.','..') for p in name.split('/')):
        raise ValueError(f'Invalid repository: {name}')
    meta = query('repo','view',name,'--json','nameWithOwner,url,defaultBranchRef')
    branch = meta['defaultBranchRef']['name']
    path = ROOT / 'repos' / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        run('gh','repo','clone',name,str(path),'--','--single-branch','--branch',branch)
    else:
        if not (path / '.git').exists():
            raise RuntimeError(f'Not a lab clone: {path}')
        if run('git','-C',str(path),'status','--porcelain'):
            raise RuntimeError(f'Uncommitted changes in {path}; refusing to update')
        if run('git','-C',str(path),'branch','--show-current') != branch:
            raise RuntimeError(f'Not on default branch in {path}; refusing to update')
        run('git','-C',str(path),'pull','--ff-only')
    issues = query('issue','list','-R',name,'--state','all','--limit',str(LIMIT),'--json','number,title,state,assignees,labels,milestone,createdAt,updatedAt,closedAt,url')
    prs = query('pr','list','-R',name,'--state','all','--limit',str(LIMIT),'--json','number,title,state,isDraft,author,reviewDecision,createdAt,updatedAt,mergedAt,url')
    return {'repository':meta,'issues':issues,'pull_requests':prs,'limit_reached':len(issues)>=LIMIT or len(prs)>=LIMIT}


def main():
    cfg = json.loads((ROOT/'config.json').read_text())
    run('gh','auth','status')
    repos = [sync_repo(name) for name in cfg['repositories']]
    projects = []
    for p in cfg['projects']:
        number = int(p['number'])
        owner = p['owner']
        items = query('project','item-list',str(number),'--owner',owner,'--limit',str(LIMIT),'--format','json')
        projects.append({'owner':owner,'number':number,'data':items,'limit_reached':len(items.get('items',[]))>=LIMIT})
    snapshot = {'synced_at':dt.datetime.now(dt.timezone.utc).isoformat(),'repositories':repos,'projects':projects,'record_limit_per_list':LIMIT}
    out = ROOT/'data'/'snapshot.json'
    out.parent.mkdir(exist_ok=True)
    tmp = out.with_suffix('.tmp')
    tmp.write_text(json.dumps(snapshot,indent=2))
    tmp.replace(out)
    print(f'Snapshot saved to {out}')


if __name__ == '__main__':
    try: main()
    except (ValueError, KeyError, subprocess.CalledProcessError, RuntimeError, FileNotFoundError) as exc:
        print(f'Sync failed; previous snapshot preserved: {exc}',file=sys.stderr)
        sys.exit(1)
