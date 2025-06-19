"""Database configuration for st.connection setup.

This module provides:
- Basic database connection configuration
- Connection management utilities
- Database initialization (without table creation)
- Cache management for Streamlit performance
"""

from contextlib import contextmanager
from pathlib import Path

import streamlit as st


class DatabaseConfig:
    """Database configuration constants and paths."""

    # Project paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    DB_PATH: Path = DATA_DIR / "business_dashboard.db"
    DB_URL: str = f"sqlite:///{DB_PATH}"

    # Connection settings
    CONNECTION_NAME: str = "business_db"
    CONNECTION_TIMEOUT: int = 30

    # Cache TTL settings (seconds)
    TTL_REALTIME: int = 30  # Real-time dashboard data
    TTL_DASHBOARD: int = 300  # Standard dashboard queries
    TTL_REPORTS: int = 1800  # Analytics and reports
    TTL_MASTER: int = 3600  # Master data (retailers, products)

    # Connection configuration for st.connection
    CONNECTION_CONFIG = {
        "url": DB_URL,
        "autocommit": False,  # Use transactions for data integrity
        "connect_args": {
            "check_same_thread": False,
            "timeout": CONNECTION_TIMEOUT,
            # SQLite performance optimizations
            "isolation_level": None,  # Enable autocommit mode control
        },
    }

    # Streamlit connection parameters
    ST_CONNECTION_PARAMS = {
        "ttl": None,  # No automatic cache expiration
        "max_entries": None,  # No limit on cache entries
    }


@st.cache_resource
def get_database_connection():
    """Get cached database connection instance.

    Returns:
        SQLConnection: Streamlit SQL connection instance

    Note:
        Uses st.cache_resource to prevent reconnection on Streamlit rerun.
        Connection is shared across the entire app session.
    """
    # Ensure data directory exists before connection
    DatabaseConfig.DATA_DIR.mkdir(parents=True, exist_ok=True)

    return st.connection(
        DatabaseConfig.CONNECTION_NAME,
        type="sql",
        **DatabaseConfig.CONNECTION_CONFIG,
        **DatabaseConfig.ST_CONNECTION_PARAMS,
    )


def test_database_connection() -> bool:
    """Test database connection health.

    Returns:
        bool: True if connection successful, False otherwise

    Example:
        if test_database_connection():
            st.success("Database connected")
        else:
            st.error("Database connection failed")
    """
    try:
        conn = get_database_connection()
        # Simple test query
        result = conn.query("SELECT 1 as test", ttl=0)
        return len(result) > 0 and result.iloc[0]["test"] == 1
    except Exception as e:
        st.error(f"Database connection test failed: {e}")
        return False


def clear_database_cache() -> None:
    """Clear all database-related cache.

    Use this after database operations that modify data
    to ensure cached queries return fresh data.

    Note:
        Clears st.cache_data but preserves st.cache_resource (connections).
    """
    st.cache_data.clear()
    st.toast("🔄 Database cache cleared", icon="ℹ️")


def get_database_info() -> dict[str, str | bool]:
    """Get database connection information.

    Returns:
        dict: Database connection details for debugging

    Example:
        info = get_database_info()
        st.json(info)
    """
    return {
        "database_path": str(DatabaseConfig.DB_PATH),
        "database_url": DatabaseConfig.DB_URL,
        "connection_name": DatabaseConfig.CONNECTION_NAME,
        "data_directory": str(DatabaseConfig.DATA_DIR),
        "database_exists": DatabaseConfig.DB_PATH.exists(),
        "data_dir_exists": DatabaseConfig.DATA_DIR.exists(),
    }


def execute_query(
    query: str, params: dict | None = None, ttl: int = DatabaseConfig.TTL_DASHBOARD
):
    """Execute cached database query.

    Args:
        query: SQL query string with named parameters
        params: Query parameters dictionary
        ttl: Cache time-to-live in seconds

    Returns:
        DataFrame: Query results as pandas DataFrame

    Example:
        result = execute_query(
            "SELECT COUNT(*) as total FROM retailers WHERE status = :status",
            params={"status": "ACTIVE"},
            ttl=300
        )
    """
    conn = get_database_connection()

    return conn.query(
        query, params=params or {}, ttl=ttl, show_spinner="Loading data..."
    )


# Context manager for database operations


@contextmanager
def get_db_session():
    """Context manager for database transactions.

    Yields:
        Session: SQLAlchemy session for database operations

    Example:
        with get_db_session() as session:
            session.execute("INSERT INTO retailers ...")
            # Auto-commit on success, rollback on error
    """
    conn = get_database_connection()

    with conn.session as session:
        try:
            yield session
            session.commit()
            # Clear cache after successful database modification
            clear_database_cache()
        except Exception:
            session.rollback()
            raise


# Database status utilities
def get_database_status() -> dict[str, bool]:
    """Get comprehensive database status.

    Returns:
        dict: Status information for database health check

    Example:
        status = get_database_status()
        if status["connection_ok"]:
            st.success("Database is healthy")
    """
    status = {
        "data_dir_exists": False,
        "database_file_exists": False,
        "connection_ok": False,
        "writeable": False,
    }

    try:
        # Check data directory
        status["data_dir_exists"] = DatabaseConfig.DATA_DIR.exists()

        # Check database file
        status["database_file_exists"] = DatabaseConfig.DB_PATH.exists()

        # Test connection
        status["connection_ok"] = test_database_connection()

        # Test write access
        if status["connection_ok"]:
            with get_db_session() as session:
                session.execute("CREATE TEMP TABLE test_write (id INTEGER)")
                status["writeable"] = True

    except Exception:
        pass  # Status already set to False

    return status


# Utility function untuk debugging
def debug_database_info() -> None:
    """Display database information for debugging purposes.

    Shows database paths, connection status, and file system info.
    Use this function in Streamlit pages for troubleshooting.
    """
    st.subheader("🔍 Database Debug Information")

    # Basic info
    info = get_database_info()
    st.json(info)

    # Status check
    status = get_database_status()

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "Data Directory", "✅ Exists" if status["data_dir_exists"] else "❌ Missing"
        )
        st.metric(
            "Database File",
            "✅ Exists" if status["database_file_exists"] else "❌ Missing",
        )

    with col2:
        st.metric("Connection", "✅ OK" if status["connection_ok"] else "❌ Failed")
        st.metric("Write Access", "✅ OK" if status["writeable"] else "❌ Failed")

    # File system info
    if DatabaseConfig.DB_PATH.exists():
        file_size = DatabaseConfig.DB_PATH.stat().st_size
        st.metric("Database Size", f"{file_size:,} bytes")


# TODO: Add database backup functionality
# TODO: Add database migration system
# PINNED: Consider connection pooling for concurrent access
# REMINDER: Always use parameterized queries to prevent SQL injection
