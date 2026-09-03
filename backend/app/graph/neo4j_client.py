import os
from typing import Optional, List, Dict, Any
try:
    from neo4j import GraphDatabase, Driver
    HAS_NEO4J = True
except ImportError:
    GraphDatabase = None
    Driver = Any
    HAS_NEO4J = False
from app.utils.logger import logger

class Neo4jClient:
    """Client wrapper for Neo4j graph operations with fault-tolerant local fallback."""

    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "forensics_neo4j_password")
        self._driver: Optional[Driver] = None
        self._is_available: Optional[bool] = None

    def connect(self) -> bool:
        if not self.uri:
            self._is_available = False
            return False
        if not HAS_NEO4J:
            self._is_available = False
            return False
        if self._driver is not None and self._is_available:
            return True
        try:
            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password),
                connection_timeout=5,
            )
            with self._driver.session() as session:
                session.run("RETURN 1 AS test")
            self._is_available = True
            logger.info(f"Connected to Neo4j at {self.uri}")
            return True
        except Exception as e:
            self._is_available = False
            logger.warning(f"Neo4j is not reachable at {self.uri} ({e}). Graph operations will operate in resilient in-memory mode.")
            return False

    @property
    def is_available(self) -> bool:
        if self._is_available is None:
            self.connect()
        return bool(self._is_available)

    def close(self):
        if self._driver:
            self._driver.close()

    def run_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Run Cypher query and return list of record dicts."""
        if not self.is_available or not self._driver:
            return []
        try:
            with self._driver.session() as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Neo4j query error: {e}")
            return []

neo4j_client = Neo4jClient()
