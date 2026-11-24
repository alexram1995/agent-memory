from .memory.store import Store

class ContextBuilder:
    def __init__(self, store: Store): self.store=store

    def build(self, project_id, query, max_memories=8):
        sections=[]
        state=self.store.get_state(project_id)
        if state: sections.append("## ACTIVE STATE\n"+state)
        memories=self.store.search(project_id,query,max_memories)
        if memories:
            sections.append("## RELEVANT MEMORY\n"+"\n".join(f"[{m['kind']}] {m['content']}" for m in memories))
        events=self.store.recent_events(project_id,8)
        if events:
            sections.append("## RECENT EVENTS\n"+"\n".join(f"- {e['event_type']}: {e['content']} (verified={bool(e['verified'])})" for e in events))
        return "\n\n".join(sections) or "No stored project memory."
