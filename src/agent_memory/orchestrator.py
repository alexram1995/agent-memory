from .memory.store import Store
from .scheduler import InferenceScheduler
from .ollama_client import OllamaClient
from .context_builder import ContextBuilder
from .checkpoint_manager import CheckpointManager

class Orchestrator:
    def __init__(self, config):
        self.store=Store(config["database"])
        oc=config["ollama"]; ic=config.get("inference",{})
        self.scheduler=InferenceScheduler(ic.get("max_queue",20))
        self.ollama=OllamaClient(oc["base_url"],oc["model"],oc.get("context_length",8192),oc.get("keep_alive","30m"),ic.get("timeout_seconds",180))
        self.context=ContextBuilder(self.store)
        self.checkpoints=CheckpointManager(self.store,self.ollama,self.scheduler)

    def start(self, project, session): self.store.start_session(project,session)
    def recover(self, project, query): return self.context.build(project,query)
    def remember(self, project, kind, content, session=None, importance=3): return self.store.add_memory(project,kind,content,session,importance)
    def event(self, project, event_type, content, session=None, task=None, verified=False): return self.store.add_event(project,event_type,content,session,task,verified)
    async def checkpoint(self, project, session, notes): return await self.checkpoints.checkpoint(project,session,notes)
