import asyncio
import uvicorn
from fastapi import FastAPI, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import structlog
from config import settings
from raft.node import RaftNode
from raft.rpc import router as raft_router
from grpc_server import start_grpc_server
from kafka_client import kafka_client

logger = structlog.get_logger()

app = FastAPI(title="Fog Node")
app.include_router(raft_router)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Fog Node", node_id=settings.FOG_NODE_ID, peers=settings.peer_list)
    
    app.state.raft_node = RaftNode(settings.FOG_NODE_ID, settings.peer_list)
    app.state.raft_node.reset_election_timeout()
    
    await kafka_client.start()
    asyncio.create_task(start_grpc_server(app.state.raft_node))

@app.on_event("shutdown")
async def shutdown_event():
    await kafka_client.stop()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    return {"status": "ready"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/status")
def status():
    node = app.state.raft_node
    return {
        "node_id": settings.FOG_NODE_ID,
        "raft_state": node.state_machine.state.value,
        "term": node.state_machine.current_term,
        "leader_id": node.leader_id,
        "log_length": node.log.get_last_log_index()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.FOG_PORT)
