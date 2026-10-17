"""ChromaDB vector database client with entitlement-filtered querying."""

import os
import shutil
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.ingestion.chunker import DocumentChunk


class VectorStoreService:
    """Manages document vector embeddings and entitlement-aware semantic search."""

    def __init__(self, persist_directory: Optional[str] = None):
        self.persist_dir = persist_directory or settings.CHROMA_PERSIST_DIRECTORY
        os.makedirs(self.persist_dir, exist_ok=True)
        
        # Initialize persistent Chroma client
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        
        # Default local embedding function (MiniLM ONNX)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"ChromaDB initialized at '{self.persist_dir}'. Current chunks: {self.collection.count()}")

    def add_chunks(self, chunks: List[DocumentChunk]) -> int:
        """
        Idempotently add or update chunks in ChromaDB.
        Uses deterministic chunk_id to avoid duplication.
        """
        if not chunks:
            return 0

        ids = [c.chunk_id for c in chunks]
        documents = [c.content for c in chunks]
        metadatas = [
            {
                "report_id": c.report_id,
                "report_title": c.report_title,
                "sector": c.sector,
                "page": int(c.page),
                "access": c.access,
                "is_injection_detected": bool(c.is_injection_detected)
            }
            for c in chunks
        ]

        # Upsert ensures idempotent re-ingestion
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        logger.info(f"Upserted {len(chunks)} chunks into vector store.")
        return len(chunks)

    def query(
        self,
        query_text: str,
        authorized_report_ids: List[str],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search vector store with STRICT entitlement filtering.
        If authorized_report_ids is empty, returns NO chunks.
        """
        if not authorized_report_ids:
            logger.info("Entitlement filter has 0 authorized reports. Returning empty retrieval.")
            return []

        # Construct ChromaDB where clause
        if len(authorized_report_ids) == 1:
            where_clause = {"report_id": authorized_report_ids[0]}
        else:
            where_clause = {"report_id": {"$in": authorized_report_ids}}

        results = self.collection.query(
            query_texts=[query_text],
            n_results=min(top_k, max(1, self.collection.count())),
            where=where_clause,
            include=["documents", "metadatas", "distances"]
        )

        formatted_results: List[Dict[str, Any]] = []
        if not results or not results["documents"] or not results["documents"][0]:
            return formatted_results

        docs = results["documents"][0]
        metas = results["metadatas"][0] if results["metadatas"] else []
        ids = results["ids"][0] if results["ids"] else []
        distances = results["distances"][0] if results["distances"] else []

        for i in range(len(docs)):
            formatted_results.append({
                "chunk_id": ids[i] if i < len(ids) else f"chunk_{i}",
                "content": docs[i],
                "metadata": metas[i] if i < len(metas) else {},
                "score": float(1.0 - distances[i]) if i < len(distances) and distances[i] is not None else 1.0
            })

        logger.info(f"Retrieved {len(formatted_results)} entitlement-filtered chunks for query.")
        return formatted_results

    def count(self) -> int:
        """Return total number of chunks stored."""
        return self.collection.count()

    def reset(self):
        """Reset the collection (for testing)."""
        self.client.delete_collection(settings.CHROMA_COLLECTION_NAME)
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=self.embedding_fn
        )


vector_store = VectorStoreService()
