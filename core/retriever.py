from pathlib import Path
import argparse
import pickle
import numpy as np

# SWAP THESE TWO LINES:
from sentence_transformers import SentenceTransformer
import faiss  # Must come AFTER sentence_transformers on Windows!

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
VECTORSTORE_DIR = Path("assets/vectorstores")


class Retriever:
    """
    Retriever for one agent / one bubble.

    Expected files:
        assets/vectorstores/<agent_slug>/index.faiss
        assets/vectorstores/<agent_slug>/index.pkl
    """

    def __init__(self, agent_slug: str):
        self.agent_slug = agent_slug
        self.path = VECTORSTORE_DIR / agent_slug

        index_path = self.path / "index.faiss"
        metadata_path = self.path / "index.pkl"

        # TODO 1 & 2: Check if files exist before loading
        if not index_path.exists():
            raise FileNotFoundError(f"FAISS index not found at: {index_path.resolve()}")

        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found at: {metadata_path.resolve()}")

        # TODO 3: Load the FAISS index
        self.index = faiss.read_index(str(index_path))

        # TODO 4: Load metadata using pickle
        with open(metadata_path, "rb") as f:
            self.metadata = pickle.load(f)

        # TODO 5: Load SentenceTransformer model
        self.model = SentenceTransformer(MODEL_NAME)

    def search(self, query: str, k: int = 5) -> list[dict]:
        """
        Search for the top-k most similar fragments.

        Returns a list of dictionaries.
        Each result should contain:
            - original metadata fields
            - score
            - position
        """

        # TODO 6: Encode the query as a normalized float32 2D array
        query_vector = self.model.encode(
            query, 
            normalize_embeddings=True, 
            convert_to_numpy=True
        ).astype("float32").reshape(1, -1)

        # TODO 7: Search inside the FAISS index
        scores, positions = self.index.search(query_vector, k)

        results = []

        # TODO 8: Process positions and populate results list
        for score, pos in zip(scores[0], positions[0]):
            if pos == -1:
                continue
            
            # Deep/safe copy the original metadata dictionary segment
            chunk_data = dict(self.metadata[pos])
            chunk_data["score"] = float(score)
            chunk_data["position"] = int(pos)
            
            results.append(chunk_data)

        return results

    def format_for_prompt(self, chunks: list[dict]) -> str:
        """
        Format retrieved fragments as context.
        This will be useful in C6.
        """

        if not chunks:
            return "(Nu au fost găsite fragmente relevante.)"

        lines = []

        # TODO 9: Format matching structure style
        for i, chunk in enumerate(chunks, start=1):
            score_formatted = f"{chunk['score']:.3f}"
            lines.append(f"[Fragment {i} | score={score_formatted}]\n{chunk['text']}")

        return "\n\n".join(lines)


def main():
    """
    Terminal test.

    Example:
        python -m core.retriever --agent anti_sistem --query "CCR a decis anularea alegerilor după suspiciuni privind influențe externe." --k 5
    """

    parser = argparse.ArgumentParser(
        description="Test semantic retrieval for one agent bubble."
    )

    parser.add_argument(
        "--agent",
        required=True,
        help="Agent slug, for example: anti_sistem"
    )

    parser.add_argument(
        "--query",
        required=True,
        help="Text used as semantic search query"
    )

    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help="Number of retrieved fragments"
    )

    args = parser.parse_args()

    retriever = Retriever(args.agent)
    chunks = retriever.search(args.query, k=args.k)

    print("Agent:", args.agent)
    print("Interogare:", args.query)
    print("Vectori în index:", retriever.index.ntotal)
    print("Rezultate recuperate:", len(chunks))

    for i, chunk in enumerate(chunks, start=1):
        print(f"\nRezultat {i}")
        print("Poziție:", chunk["position"])
        print("Scor:", round(chunk["score"], 3))

        if "agent" in chunk:
            print("Agent text:", chunk["agent"])

        if "source_channel" in chunk:
            print("Sursă:", chunk["source_channel"])

        if "video_title" in chunk:
            print("Video:", chunk["video_title"])

        print("Text:", chunk["text"][:500])


# CRITICAL: This statement must be fully unindented at the left margin!
if __name__ == "__main__":
    main()