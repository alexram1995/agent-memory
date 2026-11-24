from .memory.store import Store
from .scheduler import InferenceScheduler

CHECKPOINT_SYSTEM="You are a memory checkpoint writer for a software agent. Extract concise, durable state. Distinguish verified facts from assumptions. Preserve file paths, commands, errors, decisions and next actions. Do not invent completion or tests. Return Markdown."

class CheckpointManager:
    def __init__(self, store: Store, ollama, scheduler: InferenceScheduler):
        self.store=store; self.ollama=ollama; self.scheduler=scheduler

    async def checkpoint(self, project_id, session_id, transcript_or_notes):
        prompt="Create an updated project checkpoint from these notes. Include: objective, current status, completed/verified work, decisions and constraints, blockers, next steps, and files.\n\n"+transcript_or_notes
        state=await self.scheduler.run(self.ollama.generate,prompt,CHECKPOINT_SYSTEM)
        self.store.save_state(project_id,session_id,state)
        self.store.add_memory(project_id,"checkpoint",state,session_id,importance=5,source="llm_checkpoint")
        self.store.add_event(project_id,"checkpoint_saved","Checkpoint updated",session_id,verified=False)
        return state
