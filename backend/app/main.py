import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import router
from app.api.judge_routes import judge_router
from app.api.attacker_routes import attacker_router
import app.target as target_module
import app.judge as judge_module
import app.attackers as attackers_module

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("sentinelloop.target")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup banner
    logger.info("=" * 60)
    logger.info("  SentinelLoop — Core Service Initialized")
    logger.info(f"  Target Provider : {target_module.active_provider.__class__.__name__} ({target_module.active_provider.model_name})")
    logger.info(f"  Judge Provider  : {judge_module.active_judge.__class__.__name__} ({judge_module.active_judge.model_name})")
    logger.info(f"  Attacker Squad  : {len(attackers_module.attacker_squad.agents)} specialist agents active")
    logger.info(f"  System Prompt   : {settings.SYSTEM_PROMPT_PATH}")
    logger.info(f"  Guardrail Config: {settings.GUARDRAILS_CONFIG_PATH}")
    logger.info("=" * 60)
    yield
    logger.info("SentinelLoop Service shutting down.")


app = FastAPI(
    title="SentinelLoop — Core System",
    description=(
        "Attackable, patchable Target Chatbot Service + LLM-as-a-Judge Scorer + Adaptive Attacker Squad "
        "supporting continuous 0-1 evaluation, hot-reloads, and multi-agent red-teaming."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for React dashboard communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(judge_router)
app.include_router(attacker_router)


@app.get("/")
async def root():
    return {
        "service": "SentinelLoop Target Chatbot Service",
        "status": "online",
        "provider": target_module.active_provider.__class__.__name__,
        "model": target_module.active_provider.model_name,
        "docs_url": "/docs",
        "health_url": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
