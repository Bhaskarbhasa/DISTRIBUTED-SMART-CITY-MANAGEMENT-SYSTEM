import enum
import structlog

logger = structlog.get_logger()

class RaftState(enum.Enum):
    FOLLOWER = "FOLLOWER"
    CANDIDATE = "CANDIDATE"
    LEADER = "LEADER"

class StateMachine:
    def __init__(self):
        self.state = RaftState.FOLLOWER
        self.current_term = 0
        self.voted_for = None
        self.commit_index = 0
        self.last_applied = 0
        
    def transition_to(self, new_state: RaftState, term: int = None):
        old_state = self.state
        self.state = new_state
        if term is not None and term > self.current_term:
            self.current_term = term
            self.voted_for = None
            
        logger.info("Raft state transition", 
                   old_state=old_state.value, 
                   new_state=new_state.value, 
                   term=self.current_term)

    def become_follower(self, term: int):
        self.transition_to(RaftState.FOLLOWER, term)

    def become_candidate(self):
        self.transition_to(RaftState.CANDIDATE, self.current_term + 1)
        self.voted_for = None

    def become_leader(self):
        self.transition_to(RaftState.LEADER, self.current_term)
