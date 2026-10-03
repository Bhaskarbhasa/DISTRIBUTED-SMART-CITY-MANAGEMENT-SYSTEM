import asyncio
import os
import random
import time
import httpx
import structlog
from typing import Dict, Any, List
from config import settings
from raft.state_machine import StateMachine, RaftState
from raft.log import RaftLog
from raft.persistence import RaftPersistence
from metrics import raft_current_term, raft_is_leader, raft_commit_index, raft_log_length, raft_leader_changes_total
from kafka_client import kafka_client

logger = structlog.get_logger()

class RaftNode:
    def __init__(self, node_id: str, peers: List[str]):
        self.node_id = node_id
        self.peers = peers
        self.state_machine = StateMachine()
        
        data_dir = f"/app/data/raft_{self.node_id}" if os.path.exists("/app") else f"./data/raft_{self.node_id}"
        self.log = RaftLog(data_dir)
        self.persistence = RaftPersistence(data_dir)
        
        term, voted_for = self.persistence.load_state()
        self.state_machine.current_term = term
        self.state_machine.voted_for = voted_for
        
        # Leader state
        self.next_index = {}
        self.match_index = {}
        
        self.election_timeout_task = None
        self.heartbeat_task = None
        self.leader_id = None
        
        self.update_metrics()
        
    def update_metrics(self):
        raft_current_term.set(self.state_machine.current_term)
        raft_is_leader.set(1 if self.state_machine.state == RaftState.LEADER else 0)
        raft_commit_index.set(self.state_machine.commit_index)
        raft_log_length.set(self.log.get_last_log_index())

    def reset_election_timeout(self):
        if self.election_timeout_task:
            self.election_timeout_task.cancel()
        
        if self.state_machine.state != RaftState.LEADER:
            timeout_ms = random.randint(settings.ELECTION_TIMEOUT_MIN_MS, settings.ELECTION_TIMEOUT_MAX_MS)
            self.election_timeout_task = asyncio.create_task(self._election_timeout_coro(timeout_ms))
            
    async def _election_timeout_coro(self, timeout_ms: int):
        try:
            await asyncio.sleep(timeout_ms / 1000.0)
            await self.start_election()
        except asyncio.CancelledError:
            pass
            
    async def start_election(self):
        self.state_machine.become_candidate()
        self.state_machine.voted_for = self.node_id
        self.persistence.save_state(self.state_machine.current_term, self.state_machine.voted_for)
        self.update_metrics()
        
        logger.info("Starting election", term=self.state_machine.current_term, node_id=self.node_id)
        
        votes = 1 # Vote for self
        
        # Send RequestVote to all peers
        last_log_index = self.log.get_last_log_index()
        last_log_term = self.log.get_last_log_term()
        
        req_data = {
            "term": self.state_machine.current_term,
            "candidate_id": self.node_id,
            "last_log_index": last_log_index,
            "last_log_term": last_log_term
        }
        
        async with httpx.AsyncClient(timeout=1.0) as client:
            tasks = []
            for peer in self.peers:
                url = f"http://{peer}/raft/request-vote"
                tasks.append(client.post(url, json=req_data))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for res in results:
                if isinstance(res, Exception):
                    continue
                if res.status_code == 200:
                    data = res.json()
                    if data.get("term") > self.state_machine.current_term:
                        self.state_machine.become_follower(data.get("term"))
                        self.persistence.save_state(self.state_machine.current_term, None)
                        self.reset_election_timeout()
                        self.update_metrics()
                        return
                        
                    if data.get("vote_granted"):
                        votes += 1
                        
        if votes > (len(self.peers) + 1) // 2 and self.state_machine.state == RaftState.CANDIDATE:
            logger.info("Won election", term=self.state_machine.current_term, votes=votes)
            self.become_leader()
        else:
            self.reset_election_timeout()
            
    def become_leader(self):
        self.state_machine.become_leader()
        self.leader_id = self.node_id
        raft_leader_changes_total.inc()
        self.update_metrics()
        
        last_index = self.log.get_last_log_index()
        for peer in self.peers:
            self.next_index[peer] = last_index + 1
            self.match_index[peer] = 0
            
        asyncio.create_task(kafka_client.publish_leader_change(self.state_machine.current_term, self.node_id))
        
        if self.election_timeout_task:
            self.election_timeout_task.cancel()
            
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        # Immediate heartbeat
        asyncio.create_task(self.broadcast_append_entries())
        
    async def _heartbeat_loop(self):
        try:
            while self.state_machine.state == RaftState.LEADER:
                await asyncio.sleep(settings.HEARTBEAT_INTERVAL_MS / 1000.0)
                await self.broadcast_append_entries()
        except asyncio.CancelledError:
            pass

    async def broadcast_append_entries(self):
        if self.state_machine.state != RaftState.LEADER:
            return
            
        async with httpx.AsyncClient(timeout=1.0) as client:
            tasks = []
            for peer in self.peers:
                prev_log_index = self.next_index[peer] - 1
                prev_log_term = self.log.get_term_at(prev_log_index)
                entries = self.log.get_entries_after(prev_log_index)
                
                req_data = {
                    "term": self.state_machine.current_term,
                    "leader_id": self.node_id,
                    "prev_log_index": prev_log_index,
                    "prev_log_term": prev_log_term,
                    "entries": entries,
                    "leader_commit": self.state_machine.commit_index
                }
                url = f"http://{peer}/raft/append-entries"
                tasks.append((peer, client.post(url, json=req_data)))
                
            for peer, task in tasks:
                try:
                    res = await task
                    if res.status_code == 200:
                        data = res.json()
                        if data.get("term") > self.state_machine.current_term:
                            self.state_machine.become_follower(data.get("term"))
                            self.persistence.save_state(self.state_machine.current_term, None)
                            self.reset_election_timeout()
                            self.update_metrics()
                            return
                            
                        if data.get("success"):
                            self.next_index[peer] = prev_log_index + len(entries) + 1
                            self.match_index[peer] = self.next_index[peer] - 1
                        else:
                            self.next_index[peer] = max(1, self.next_index[peer] - 1)
                except Exception:
                    pass
                    
        # Update commit index
        match_indices = [self.log.get_last_log_index()] + list(self.match_index.values())
        match_indices.sort(reverse=True)
        majority_index = match_indices[len(match_indices) // 2]
        
        if majority_index > self.state_machine.commit_index and self.log.get_term_at(majority_index) == self.state_machine.current_term:
            self.state_machine.commit_index = majority_index
            self.update_metrics()
            self.apply_logs()
            
    def apply_logs(self):
        while self.state_machine.commit_index > self.state_machine.last_applied:
            self.state_machine.last_applied += 1
            entry = self.log.get_entry(self.state_machine.last_applied)
            # Actually applying to state machine logic goes here
            # In this case, we just increment last_applied

    async def handle_request_vote(self, term: int, candidate_id: str, last_log_index: int, last_log_term: int) -> dict:
        if term > self.state_machine.current_term:
            self.state_machine.become_follower(term)
            self.persistence.save_state(self.state_machine.current_term, None)
            
        vote_granted = False
        
        if term == self.state_machine.current_term:
            if self.state_machine.voted_for in (None, candidate_id):
                my_last_log_term = self.log.get_last_log_term()
                my_last_log_index = self.log.get_last_log_index()
                
                # Check log is up-to-date
                if last_log_term > my_last_log_term or (last_log_term == my_last_log_term and last_log_index >= my_last_log_index):
                    vote_granted = True
                    self.state_machine.voted_for = candidate_id
                    self.persistence.save_state(self.state_machine.current_term, self.state_machine.voted_for)
                    self.reset_election_timeout()
                    
        self.update_metrics()
        return {"term": self.state_machine.current_term, "vote_granted": vote_granted}

    async def handle_append_entries(self, term: int, leader_id: str, prev_log_index: int, prev_log_term: int, entries: List[dict], leader_commit: int) -> dict:
        if term > self.state_machine.current_term:
            self.state_machine.become_follower(term)
            self.persistence.save_state(self.state_machine.current_term, None)
            
        if term < self.state_machine.current_term:
            return {"term": self.state_machine.current_term, "success": False}
            
        self.reset_election_timeout()
        self.leader_id = leader_id
        
        if self.state_machine.state == RaftState.CANDIDATE:
            self.state_machine.become_follower(term)
            
        success = self.log.append_entries(prev_log_index, prev_log_term, entries)
        
        if success:
            if leader_commit > self.state_machine.commit_index:
                self.state_machine.commit_index = min(leader_commit, self.log.get_last_log_index())
                self.apply_logs()
                
        self.update_metrics()
        return {"term": self.state_machine.current_term, "success": success}
        
    async def submit_command(self, command: dict) -> dict:
        if self.state_machine.state != RaftState.LEADER:
            return {"success": False, "leader_hint": self.leader_id}
            
        index = self.log.append_entry(self.state_machine.current_term, command)
        self.update_metrics()
        
        # Broadcast immediately to commit faster
        asyncio.create_task(self.broadcast_append_entries())
        
        # Wait for commit (simplified wait loop)
        for _ in range(20):
            if self.state_machine.commit_index >= index:
                return {"success": True, "index": index}
            await asyncio.sleep(0.05)
            
        return {"success": False, "error": "Timeout waiting for commit"}
