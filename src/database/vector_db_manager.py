from pathlib import Path
from typing import List, Dict, Any, Optional
from langchain_chroma import Chroma
from langchain_voyageai import VoyageAIEmbeddings
from ..config import config

class VectorDBManager:
    """Manages ChromaDB for semantic search of regulations and policies using LangChain"""
    
    def __init__(self, persist_directory: Optional[Path] = None):
        """Initialize ChromaDB manager with LangChain integration
        
        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.persist_directory = persist_directory or config.VECTOR_DB_PATH
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        self.embedding_model = VoyageAIEmbeddings(
            model=config.EMBEDDING_MODEL
        )
        
        self.collections: Dict[str, Chroma] = {}
    
    def get_or_create_collection(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Chroma:
        """Get or create a collection
        
        Args:
            name: Collection name (e.g., 'gdpr', 'hipaa', 'pci_dss')
            metadata: Optional metadata for the collection
        
        Returns:
            Chroma vectorstore instance
        """
        if name in self.collections:
            return self.collections[name]
        
        collection = Chroma(
            collection_name=name,
            embedding_function=self.embedding_model,
            persist_directory=str(self.persist_directory)
        )
        
        self.collections[name] = collection
        return collection
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> int:
        """Add documents to a collection.
        
        Args:
            collection_name: Name of the collection
            documents: List of document texts
            metadatas: Optional list of metadata dicts for each document
            ids: Optional list of unique IDs for each document
        
        Returns:
            Number of documents added
        """
        collection = self.get_or_create_collection(collection_name)
        
        if ids is None:
            try:
                existing_count = len(collection.get()['ids'])
            except:
                existing_count = 0
            ids = [
                f"{collection_name}_{i + existing_count}"
                for i in range(len(documents))
            ]
        
        collection.add_texts(
            texts=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        return len(documents)
    
    def query(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = 3,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query a collection for similar documents.
        
        Args:
            collection_name: Name of the collection to query
            query_text: Query text
            n_results: Number of results to return
            where: Optional metadata filter
        
        Returns:
            Query results with documents, distances, and metadatas
        """
        collection = self.get_or_create_collection(collection_name)
        
        results_with_scores = collection.similarity_search_with_score(
            query=query_text,
            k=n_results,
            filter=where
        )
        
        documents = []
        distances = []
        metadatas = []
        ids = []
        
        for doc, score in results_with_scores:
            documents.append(doc.page_content)
            distances.append(score)
            metadatas.append(doc.metadata)
            ids.append(doc.metadata.get('id', ''))
        
        return {
            'documents': [documents],
            'distances': [distances],
            'metadatas': [metadatas],
            'ids': [ids]
        }
    
    def query_regulations(
        self,
        entity_type: str,
        regulation: Optional[str] = None,
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """Query regulation documents for a specific entity type.
        
        Args:
            entity_type: Type of entity (e.g., 'email', 'credit_card')
            regulation: Specific regulation to search (GDPR, HIPAA, PCI DSS)
            n_results: Number of results to return
        
        Returns:
            List of relevant regulation excerpts
        """
        query_text = f"Requirements and rules for {entity_type} protection and anonymization"
        
        if regulation:
            collection_name = regulation.lower().replace(' ', '_')
            results = self.query(collection_name, query_text, n_results)
        else:
            all_results = []
            for reg in ['gdpr', 'hipaa', 'pci_dss']:
                try:
                    results = self.query(reg, query_text, n_results)
                    for i, doc in enumerate(results.get('documents', [[]])[0]):
                        all_results.append({
                            'regulation': reg.upper().replace('_', ' '),
                            'document': doc,
                            'distance': results['distances'][0][i],
                            'metadata': results.get('metadatas', [[]])[0][i] if results.get('metadatas') else {}
                        })
                except:
                    continue
            
            all_results.sort(key=lambda x: x['distance'])
            return all_results[:n_results]
        
        formatted_results = []
        if results.get('documents'):
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    'regulation': regulation or 'UNKNOWN',
                    'document': doc,
                    'distance': results['distances'][0][i],
                    'metadata': results.get('metadatas', [[]])[0][i] if results.get('metadatas') else {}
                })
        
        return formatted_results
    
    def delete_collection(self, collection_name: str):
        """Delete a collection.
        
        Args:
            collection_name: Name of collection to delete
        """
        try:
            if collection_name in self.collections:
                collection = self.collections[collection_name]
                collection.delete_collection()
                del self.collections[collection_name]
        except:
            pass
    
    def list_collections(self) -> List[str]:
        """List all collections.
        
        Returns:
            List of collection names
        """
        return list(self.collections.keys())
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get statistics for a collection.
        
        Args:
            collection_name: Name of the collection
        
        Returns:
            Dictionary with statistics
        """
        collection = self.get_or_create_collection(collection_name)
        
        try:
            data = collection.get()
            count = len(data['ids'])
        except:
            count = 0
        
        return {
            'name': collection_name,
            'count': count,
            'metadata': {}
        }
    
    def persist(self):
        """Persist all collections to disk.
        
        Note: With LangChain's Chroma, persistence is automatic when persist_directory is set.
        """
        for collection in self.collections.values():
            try:
                collection.persist()
            except:
                pass
    
    def reset_database(self):
        """Reset entire database (delete all collections)."""
        for collection_name in list(self.collections.keys()):
            self.delete_collection(collection_name)
