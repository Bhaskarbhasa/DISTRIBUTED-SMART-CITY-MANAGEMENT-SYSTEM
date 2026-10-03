from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any

router = APIRouter(prefix="/raft")

class RequestVoteRequest(BaseModel):
    term: int
    candidate_id: str
    last_log_index: int
    last_log_term: int
    
class AppendEntriesRequest(BaseModel):
    term: int
    leader_id: str
    prev_log_index: int
    prev_log_term: int
    entries: List[dict]
    leader_commit: int

@router.post("/request-vote")
async def request_vote(req: RequestVoteRequest, request: Request):
    node = request.app.state.raft_node
    return await node.handle_request_vote(req.term, req.candidate_id, req.last_log_index, req.last_log_term)

@router.post("/append-entries")
async def append_entries(req: AppendEntriesRequest, request: Request):
    node = request.app.state.raft_node
    return await node.handle_append_entries(req.term, req.leader_id, req.prev_log_index, req.prev_log_term, req.entries, req.leader_commit)

@router.get("/status")
async def get_status(request: Request):
    node = request.app.state.raft_node
    return {
        "node_id": node.node_id,
        "state": node.state_machine.state.value,
        "term": node.state_machine.current_term,
        "leader_id": node.leader_id,
        "commit_index": node.state_machine.commit_index,
        "last_applied": node.state_machine.last_applied,
        "log_length": node.log.get_last_log_index()
    }
    
@router.post("/command")
async def submit_command(command: dict, request: Request):
    node = request.app.state.raft_node
    res = await node.submit_command(command)
    if not res.get("success") and "leader_hint" in res:
        raise HTTPException(status_code=400, detail={"error": "Not leader", "leader_hint": res["leader_hint"]})
    return res
