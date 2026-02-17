#!/usr/bin/env python3
"""
TEST CONFIGURATION FILE - Single Source of Truth

Change parameters here to modify ALL tests (MCP and E2E).
This is the ONLY file you need to edit to change test behavior.

Usage:
  1. Modify CONFIG below
  2. Run: python unified_mcp_test.py
  3. All tests will use these settings
"""

# =============================================================================
# PRIMARY TEST CONFIGURATION - EDIT THIS TO CHANGE ALL TESTS
# =============================================================================

CONFIG = {
    # PRIMARY STOCK (main test target)
    "primary_stock": "MU",

    # COMPARISON STOCK (for compare_securities)
    "comparison_stock": "NVDA",

    # PERIOD for all analysis (1mo, 3mo, 6mo, 1y)
    "period": "3mo",

    # USE AI (requires GEMINI_API_KEY)
    "use_ai": False,

    # FIBONACCI settings
    "fibonacci_window": 150,

    # OPTIONS settings (options_risk_analysis parameters)
    "options_expiration_date": None,  # None = use nearest expiration
    "options_type": "both",  # "calls", "puts", or "both"
    "options_min_volume": 75,  # Minimum volume threshold for liquid options

    # PORTFOLIO positions (for portfolio_risk)
    "portfolio_positions": [
        {"symbol": "MU", "shares": 100, "entry_price": 90},
        {"symbol": "NVDA", "shares": 50, "entry_price": 120},
    ],

    # WATCHLIST for morning_brief
    "watchlist": ["MU", "NVDA"],

    # SCREENING settings (screen_securities parameters)
    # universe must be: "sp500", "nasdaq100", "etf_large_cap", etc.
    "screen_universe": "nasdaq100",  # Use nasdaq100 (smaller than sp500)
    "screen_criteria": {"min_score": 50},
    "screen_limit": 5,  # Limit results for testing

    # TRADE SCANNING settings (scan_trades parameters)
    # universe must be: "sp500", "nasdaq100", "etf_large_cap", "crypto"
    "scan_universe": "nasdaq100",  # Use nasdaq100 (smaller than sp500)
    "scan_max_results": 5,  # Maximum results to return

    # API SETTINGS
    "max_api_retries": 1,  # Minimize API calls
    "cache_enabled": True,  # Cache data to avoid re-fetching

    # OUTPUT settings
    "output_dir": "nu-logs",
    "save_baselines": True,
    "verbose": True,
}

# =============================================================================
# DERIVED VALUES (automatically computed from CONFIG)
# =============================================================================

def get_test_symbols():
    """Get all symbols used in tests"""
    symbols = {CONFIG["primary_stock"], CONFIG["comparison_stock"]}
    for pos in CONFIG["portfolio_positions"]:
        symbols.add(pos["symbol"])
    for sym in CONFIG["watchlist"]:
        symbols.add(sym)
    return list(symbols)

def get_comparison_symbols():
    """Get symbols for compare_securities test"""
    return [CONFIG["primary_stock"], CONFIG["comparison_stock"]]

def get_screen_universe():
    """Get universe string for screen_securities"""
    return CONFIG["screen_universe"]

def get_scan_universe():
    """Get universe string for scan_trades"""
    return CONFIG["scan_universe"]

# =============================================================================
# E2E TEST CONFIGURATION
# =============================================================================

E2E_CONFIG = {
    # Base URL for frontend
    "base_url": "http://localhost:3000",

    # Test user credentials (for authenticated tests)
    "test_user_email": "test@example.com",

    # Performance targets
    "landing_page_load_ms": 2000,
    "control_page_load_ms": 3000,
    "tool_execution_ms": 5000,

    # Mobile viewport
    "mobile_width": 375,
    "mobile_height": 667,

    # Desktop viewport
    "desktop_width": 1280,
    "desktop_height": 720,
}

# =============================================================================
# PRINT CONFIG (for debugging)
# =============================================================================

def print_config():
    """Print current test configuration"""
    print("=" * 60)
    print("TEST CONFIGURATION")
    print("=" * 60)
    print(f"Primary Stock:     {CONFIG['primary_stock']}")
    print(f"Comparison Stock:  {CONFIG['comparison_stock']}")
    print(f"Period:            {CONFIG['period']}")
    print(f"Use AI:            {CONFIG['use_ai']}")
    print(f"Fibonacci Window:  {CONFIG['fibonacci_window']}")
    print(f"All Test Symbols:  {get_test_symbols()}")
    print(f"API Retries:       {CONFIG['max_api_retries']}")
    print(f"Cache Enabled:     {CONFIG['cache_enabled']}")
    print("=" * 60)

if __name__ == "__main__":
    print_config()
