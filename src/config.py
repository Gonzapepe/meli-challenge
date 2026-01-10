import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.1-70b-versatile")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "voyage-3-large")
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    REGULATIONS_DIR: Path = DATA_DIR / "regulations"
    TEST_TEXTS_DIR: Path = DATA_DIR / "test_texts"
    VECTOR_DB_PATH: Path = Path(os.getenv("VECTOR_DB_PATH", str(DATA_DIR / "vector_db")))
    OUTPUTS_DIR: Path = PROJECT_ROOT / "outputs"
    
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 4000
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY environment variable is required")


config = Config()
