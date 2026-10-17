#!/usr/bin/env python3
"""Run and attest a fixed CosmoSIS reproducibility check."""
from __future__ import annotations
import argparse, hashlib, json, os, platform, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

def run(cmd, cwd, env, log):
    p = subprocess.run(cmd, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log.write_text(p.stdout)
    return p.returncode, p.stdout

def sha(path):
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--skip-tests', action='store_true')
    a=ap.parse_args(); repo=a.repo.resolve(); out=a.output.resolve(); out.mkdir(parents=True, exist_ok=True)
    env=os.environ.copy(); env['DYLD_LIBRARY_PATH']='/usr/lib:/opt/homebrew/Cellar/gcc/16.2.0/lib/gcc/current'
    meta={'created_at':datetime.now(timezone.utc).isoformat(),'repo':str(repo),'formal_pass':False}
    meta['commit']=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
    rc, version=run(['cosmosis','--version'],repo,env,out/'version.log'); meta['version_rc']=rc; meta['version']=version.strip()
    rc, e2e=run(['cosmosis','cosmosis/test/example.ini'],repo,env,out/'e2e.log'); meta['e2e_rc']=rc; meta['e2e_sha256']=sha(out/'e2e.log')
    if not a.skip_tests:
        rc, tests=run(['pytest','-q'],repo,env,out/'pytest.log'); meta['pytest_rc']=rc; meta['pytest_sha256']=sha(out/'pytest.log')
    (out/'manifest.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n')
    with (out/'SHA256SUMS').open('w') as f:
        for p in sorted(out.iterdir()):
            if p.name != 'SHA256SUMS': f.write(f'{sha(p)}  {p.name}\n')
    return 0 if rc==0 and meta['e2e_rc']==0 and meta['version_rc']==0 else 1
if __name__=='__main__': sys.exit(main())
