import argparse, asyncio, uuid
from pathlib import Path
import yaml
from .orchestrator import Orchestrator


def load_config(path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))

async def run_checkpoint(args, orch):
    notes=Path(args.file).read_text(encoding="utf-8") if args.file else args.notes
    result=await orch.checkpoint(args.project,args.session,notes)
    print(result)

def main():
    p=argparse.ArgumentParser(prog="agent-memory")
    p.add_argument("--config",default="config.yaml")
    sub=p.add_subparsers(dest="cmd",required=True)
    s=sub.add_parser("start"); s.add_argument("project"); s.add_argument("--session",default=None)
    r=sub.add_parser("recover"); r.add_argument("project"); r.add_argument("query")
    m=sub.add_parser("remember"); m.add_argument("project"); m.add_argument("kind"); m.add_argument("content"); m.add_argument("--importance",type=int,default=3); m.add_argument("--session")
    e=sub.add_parser("event"); e.add_argument("project"); e.add_argument("event_type"); e.add_argument("content"); e.add_argument("--session"); e.add_argument("--verified",action="store_true")
    c=sub.add_parser("checkpoint"); c.add_argument("project"); c.add_argument("--session",default=None); c.add_argument("--notes",default=""); c.add_argument("--file")
    args=p.parse_args(); config=load_config(args.config); orch=Orchestrator(config)
    if args.cmd=="start":
        sid=args.session or str(uuid.uuid4()); orch.start(args.project,sid); print(f"Session: {sid}")
    elif args.cmd=="recover": print(orch.recover(args.project,args.query))
    elif args.cmd=="remember": orch.remember(args.project,args.kind,args.content,args.session,args.importance); print("Saved")
    elif args.cmd=="event": orch.event(args.project,args.event_type,args.content,args.session,verified=args.verified); print("Saved")
    elif args.cmd=="checkpoint":
        if not args.session: args.session=str(uuid.uuid4())
        asyncio.run(run_checkpoint(args,orch))

if __name__=="__main__": main()
