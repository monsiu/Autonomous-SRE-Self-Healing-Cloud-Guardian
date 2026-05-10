"""
Setup script for ML components
Run this to initialize ChromaDB and seed sample data
"""
import logging
from ml.vector_store import vector_store
from ml.llm_engine import llm_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_ml_components():
    logger.info("Setting up ML components...")
    
    # Initialize vector store and seed data
    logger.info("Seeding ChromaDB with sample incidents...")
    vector_store.seed_sample_incidents()
    
    # Initialize LLM engine (placeholder for actual model loading)
    logger.info("Initializing LLM engine...")
    llm_engine.load_model()
    
    logger.info("ML components setup complete!")

if __name__ == "__main__":
    setup_ml_components()
