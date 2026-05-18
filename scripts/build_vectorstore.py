import json
import pickle
from pathlib import Path
import numpy as np

import faiss
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
VECTORSTORE_DIR = Path("assets/vectorstores")
DATA_DIR = Path("data")

def load_data(agent_slug: str) -> list:
    """Helper to safely load chunks from any available project data source."""
    # Option A: Look in data/cleaned/ for a sample file
    cleaned_sample = DATA_DIR / "cleaned" / "corpus_youtube_sample.json"
    if cleaned_sample.exists():
        print(f"📂 Loading data from cleaned sample catalog: {cleaned_sample}")
        with open(cleaned_sample, "r", encoding="utf-8") as f:
            all_chunks = json.load(f)
        # Filter for the agent if specified inside
        agent_chunks = [c for c in all_chunks if c.get("agent") == agent_slug]
        if agent_chunks:
            return agent_chunks
        return all_chunks

    # Option B: Look in data/bubbles/ for an agent-specific file (JSON or JSONL)
    bubble_dir = DATA_DIR / "bubbles"
    
    # Try JSON format
    json_path = bubble_dir / f"{agent_slug}.json"
    if json_path.exists():
        print(f"📂 Loading data from bubble file: {json_path}")
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    # Try JSONL format (JSON Lines)
    jsonl_path = bubble_dir / f"{agent_slug}.jsonl"
    if jsonl_path.exists():
        print(f"📂 Loading data from line-by-line bubble file: {jsonl_path}")
        chunks = []
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    chunks.append(json.loads(line))
        return chunks

    return []

def build_for_agent(agent_slug: str):
    print(f"\n--- Generating Vectorstore for Agent: {agent_slug} ---")
    
    agent_dir = VECTORSTORE_DIR / agent_slug
    agent_dir.mkdir(parents=True, exist_ok=True)
    
    index_path = agent_dir / "index.faiss"
    metadata_path = agent_dir / "index.pkl"

    agent_chunks = load_data(agent_slug)
    
    if not agent_chunks:
        print(f"❌ Error: No source data could be located for '{agent_slug}'. Skipping.")
        return

    # Extract text values safely
    texts = [chunk["text"] for chunk in agent_chunks if "text" in chunk and chunk["text"]]
    
    if not texts:
        print(f"❌ Error: No text found inside datasets for {agent_slug}")
        return

    print(f"Encoding {len(texts)} entries using {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True).astype("float32")

    # Set up FAISS mapping
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    # Write files
    faiss.write_index(index, str(index_path))
    with open(metadata_path, "wb") as f:
        pickle.dump(agent_chunks, f)

    print(f"✅ Success! Vectorstore built with {index.ntotal} items.")

def main():
    agents = ["anti_sistem", "anti_suveranist"]
    for agent in agents:
        build_for_agent(agent)

if __name__ == "__main__":
    main()