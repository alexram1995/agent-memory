import httpx

class OllamaClient:
    def __init__(self, base_url, model, context_length=8192, keep_alive="30m", timeout=180):
        self.base_url=base_url.rstrip("/"); self.model=model
        self.context_length=context_length; self.keep_alive=keep_alive; self.timeout=timeout

    async def generate(self, prompt, system=None):
        payload={"model":self.model,"prompt":prompt,"stream":False,"keep_alive":self.keep_alive,
                 "options":{"num_ctx":self.context_length,"temperature":0.2}}
        if system: payload["system"]=system
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r=await client.post(self.base_url+"/api/generate",json=payload)
            r.raise_for_status()
            return r.json().get("response","")
