import pytest

class RaftNode:
    def __init__(self):
        self.state = "FOLLOWER"
        self.term = 0
        self.voted_for = None
    
    def start_election(self):
        self.state = "CANDIDATE"
        self.term += 1
        self.voted_for = self
    
    def receive_vote(self, votes, cluster_size):
        if votes > cluster_size // 2:
            self.state = "LEADER"

def test_leader_election_logic():
    node = RaftNode()
    assert node.state == "FOLLOWER"
    node.start_election()
    assert node.state == "CANDIDATE"
    assert node.term == 1
    node.receive_vote(3, 5)
    assert node.state == "LEADER"

def test_vote_granting():
    node = RaftNode()
    # node votes if it hasn't voted in this term
    pass

def test_term_increment():
    node = RaftNode()
    node.start_election()
    assert node.term == 1

def test_log_consistency_check():
    pass
