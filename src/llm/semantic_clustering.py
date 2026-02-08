from typing import List, Dict, Tuple, Set
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class SemanticClusterConsolidator:
    """
    Consolidates clusters across multiple LLM runs using semantic similarity.
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', similarity_threshold: float = 0.75):
        """
        Initialize the consolidator.
        
        Args:
            model_name: Sentence transformer model to use for embeddings
            similarity_threshold: Cosine similarity threshold for merging clusters (0-1)
        """
        self.model = SentenceTransformer(model_name)
        self.similarity_threshold = similarity_threshold
    
    def consolidate_clusters(
        self, 
        all_clusters: List[Dict[str, object]]
    ) -> List[Dict[str, object]]:
        """
        Consolidate clusters from multiple runs by merging semantically similar ones.
        
        Args:
            all_clusters: List of cluster dicts with 'cluster' and 'queries' keys
            
        Returns:
            Consolidated list of cluster dicts
        """
        if not all_clusters:
            return []
        
        # Extract unique cluster titles
        cluster_titles = list(set(c['cluster'] for c in all_clusters))
        
        if len(cluster_titles) <= 1:
            return all_clusters
        
        # Generate embeddings for cluster titles
        print(f"Generating embeddings for {len(cluster_titles)} unique cluster titles...")
        embeddings = self.model.encode(cluster_titles)
        
        # Find similar clusters
        similarity_matrix = cosine_similarity(embeddings)
        merged_groups = self._find_merge_groups(cluster_titles, similarity_matrix)
        
        print(f"Consolidated {len(cluster_titles)} clusters into {len(merged_groups)} groups")
        
        # Merge clusters in each group
        consolidated = []
        for group in merged_groups:
            merged_cluster = self._merge_cluster_group(all_clusters, group)
            consolidated.append(merged_cluster)
        
        return consolidated
    
    def _find_merge_groups(
        self, 
        cluster_titles: List[str], 
        similarity_matrix: np.ndarray
    ) -> List[Set[str]]:
        """
        Find groups of cluster titles that should be merged.
        
        Uses a greedy approach: if two clusters are similar enough, merge them.
        """
        n = len(cluster_titles)
        merged_groups = []
        assigned = set()
        
        for i in range(n):
            if cluster_titles[i] in assigned:
                continue
            
            # Start a new group with this cluster
            group = {cluster_titles[i]}
            assigned.add(cluster_titles[i])
            
            # Find all similar clusters
            for j in range(i + 1, n):
                if cluster_titles[j] in assigned:
                    continue
                
                if similarity_matrix[i][j] >= self.similarity_threshold:
                    group.add(cluster_titles[j])
                    assigned.add(cluster_titles[j])
            
            merged_groups.append(group)
        
        return merged_groups
    
    def _merge_cluster_group(
        self, 
        all_clusters: List[Dict[str, object]], 
        group: Set[str]
    ) -> Dict[str, object]:
        """
        Merge all clusters in a group into a single cluster.
        
        Uses the shortest title as the canonical name.
        Deduplicates queries.
        """
        # Find the shortest title as canonical
        canonical_title = min(group, key=len)
        
        # Collect all queries from clusters in this group
        all_queries = []
        for cluster in all_clusters:
            if cluster['cluster'] in group:
                all_queries.extend(cluster['queries'])
        
        # Deduplicate queries (case-insensitive)
        unique_queries = self._deduplicate_queries(all_queries)
        
        return {
            'cluster': canonical_title,
            'queries': unique_queries,
            'merged_from': list(group) if len(group) > 1 else None
        }
    
    def _deduplicate_queries(self, queries: List[str]) -> List[str]:
        """Remove duplicate queries using case-insensitive comparison."""
        seen = set()
        unique = []
        
        for query in queries:
            normalized = query.lower().strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique.append(query)
        
        return unique


def consolidate_with_semantic_clustering(
    all_clusters: List[Dict[str, object]],
    similarity_threshold: float = 0.75
) -> List[Dict[str, object]]:
    """
    Convenience function to consolidate clusters using semantic similarity.
    
    Args:
        all_clusters: List of cluster dicts from multiple LLM runs
        similarity_threshold: Cosine similarity threshold for merging (0-1)
        
    Returns:
        Consolidated list of cluster dicts
    """
    consolidator = SemanticClusterConsolidator(similarity_threshold=similarity_threshold)
    return consolidator.consolidate_clusters(all_clusters)
