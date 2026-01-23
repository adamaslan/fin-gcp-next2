#!/usr/bin/env python3
"""
Backend Comprehensive Report Generator
Combines all API responses into a single markdown report
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class ReportGenerator:
    """Generates comprehensive backend report from test results."""

    def __init__(self, run_dir: str):
        """Initialize report generator."""
        self.run_dir = Path(run_dir)
        self.responses = self._load_responses()

    def _load_responses(self) -> Dict[str, Any]:
        """Load all JSON response files."""
        responses = {}
        for json_file in sorted(self.run_dir.glob("*.json")):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    responses[json_file.stem] = data
            except Exception as e:
                print(f"Warning: Could not load {json_file}: {e}")
        return responses

    def _format_json(self, obj: Any, indent: int = 2) -> str:
        """Format JSON object for display."""
        return json.dumps(obj, indent=indent)

    def generate_report(self, output_file: str) -> None:
        """Generate comprehensive report."""

        report = []

        # Header
        report.append("# Complete Backend Execution Report\n\n")
        report.append(f"**Generated**: {datetime.now().isoformat()}\n")
        report.append(f"**Environment**: fin-ai1\n")
        report.append(f"**Project**: MCP Finance\n")
        report.append(f"**Run Directory**: {self.run_dir}\n")
        report.append("---\n\n")

        # Executive Summary
        report.append("## Executive Summary\n\n")
        report.append(f"- **Total API Tests**: {len(self.responses)}\n")

        successful = sum(1 for r in self.responses.values() if r and isinstance(r, dict))
        report.append(f"- **Successful Responses**: {successful}\n")
        report.append(f"- **Report Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")

        # Section: Health Checks
        report.append("## API Responses by Endpoint\n\n")

        # Organize responses by category
        categories = {
            "Health & Status": [k for k in self.responses.keys() if 'health' in k],
            "Trade Planning": [k for k in self.responses.keys() if 'trade_plan' in k],
            "Trade Scanning": [k for k in self.responses.keys() if 'scan' in k],
            "Portfolio Analysis": [k for k in self.responses.keys() if 'portfolio' in k],
            "Market Intelligence": [k for k in self.responses.keys() if 'brief' in k or 'morning' in k],
            "Security Analysis": [k for k in self.responses.keys() if 'analyze' in k or 'signals' in k],
            "Comparison": [k for k in self.responses.keys() if 'compare' in k],
            "Statistics": [k for k in self.responses.keys() if 'stats' in k]
        }

        for category, keys in categories.items():
            if not keys:
                continue

            report.append(f"### {category}\n\n")

            for key in keys:
                data = self.responses.get(key)
                if not data:
                    continue

                # Format key name
                endpoint_name = key.replace('_', ' ').title()
                report.append(f"#### {endpoint_name}\n\n")

                # Extract useful info for summary
                if isinstance(data, dict):
                    # Health endpoints
                    if 'status' in data and 'service' in data:
                        report.append(f"**Status**: {data.get('status')}\n")
                        report.append(f"**Service**: {data.get('service')}\n")
                        report.append(f"**Version**: {data.get('version')}\n\n")

                    # Trade plan endpoints
                    elif 'symbol' in data and 'trade_plans' in data:
                        report.append(f"**Symbol**: {data.get('symbol')}\n")
                        report.append(f"**Has Trades**: {data.get('has_trades')}\n")
                        report.append(f"**Trade Count**: {len(data.get('trade_plans', []))}\n")
                        if data.get('trade_plans'):
                            report.append(f"**Primary Signal**: {data['trade_plans'][0].get('primary_signal')}\n")
                        report.append("\n")

                    # Scan endpoints
                    elif 'universe' in data and 'qualified_trades' in data:
                        report.append(f"**Universe**: {data.get('universe')}\n")
                        report.append(f"**Total Scanned**: {data.get('total_scanned')}\n")
                        report.append(f"**Qualified Setups**: {len(data.get('qualified_trades', []))}\n")
                        report.append(f"**Duration**: {data.get('duration_seconds', 'N/A')}s\n")
                        if data.get('qualified_trades'):
                            report.append(f"**Top Setup**: {data['qualified_trades'][0].get('symbol')}\n")
                        report.append("\n")

                    # Portfolio risk
                    elif 'total_value' in data and 'positions' in data:
                        report.append(f"**Total Value**: ${data.get('total_value', 0):,.2f}\n")
                        report.append(f"**Max Loss**: ${data.get('total_max_loss', 0):,.2f}\n")
                        report.append(f"**Risk Level**: {data.get('overall_risk_level')}\n")
                        report.append(f"**Position Count**: {len(data.get('positions', []))}\n")
                        if data.get('sector_concentration'):
                            report.append("**Sectors**: ")
                            report.append(", ".join(data['sector_concentration'].keys()))
                            report.append("\n")
                        report.append("\n")

                    # Morning brief
                    elif 'market_status' in data and 'watchlist_signals' in data:
                        report.append(f"**Market Status**: {data.get('market_status', {}).get('market_status', 'N/A')}\n")
                        report.append(f"**VIX**: {data.get('market_status', {}).get('vix', 'N/A')}\n")
                        report.append(f"**Signals**: {len(data.get('watchlist_signals', []))}\n")
                        report.append(f"**Themes**: {len(data.get('key_themes', []))}\n")
                        report.append("\n")

                # Full JSON response
                report.append("**Full Response**:\n\n")
                report.append("```json\n")
                report.append(self._format_json(data))
                report.append("\n```\n\n")

        # Data Insights Section
        report.append("---\n\n")
        report.append("## Data Insights\n\n")

        # Trade insights
        trade_plans = {k: v for k, v in self.responses.items() if 'trade_plan' in k}
        if trade_plans:
            report.append("### Trade Planning Insights\n\n")
            total_trades = sum(len(v.get('trade_plans', [])) for v in trade_plans.values())
            report.append(f"- **Total Securities Analyzed**: {len(trade_plans)}\n")
            report.append(f"- **Total Trade Plans Generated**: {total_trades}\n")
            report.append(f"- **Average Plans Per Symbol**: {total_trades / len(trade_plans):.1f}\n\n")

        # Scan insights
        scans = {k: v for k, v in self.responses.items() if 'scan' in k}
        if scans:
            report.append("### Universe Scanning Insights\n\n")
            total_scanned = sum(v.get('total_scanned', 0) for v in scans.values())
            total_qualified = sum(len(v.get('qualified_trades', [])) for v in scans.values())
            if total_scanned > 0:
                conversion_rate = (total_qualified / total_scanned * 100) if total_scanned > 0 else 0
                report.append(f"- **Total Securities Scanned**: {total_scanned}\n")
                report.append(f"- **Total Qualified Setups**: {total_qualified}\n")
                report.append(f"- **Overall Conversion Rate**: {conversion_rate:.2f}%\n\n")

        # Portfolio insights
        portfolio = self.responses.get('08_portfolio_risk', {})
        if portfolio:
            report.append("### Portfolio Insights\n\n")
            report.append(f"- **Total Portfolio Value**: ${portfolio.get('total_value', 0):,.2f}\n")
            report.append(f"- **Maximum Loss**: ${portfolio.get('total_max_loss', 0):,.2f}\n")
            report.append(f"- **Risk %**: {portfolio.get('risk_percent_of_portfolio', 0):.1f}%\n")
            report.append(f"- **Risk Level**: {portfolio.get('overall_risk_level')}\n")
            report.append(f"- **Position Count**: {len(portfolio.get('positions', []))}\n\n")

        # Brief insights
        brief = self.responses.get('09_morning_brief', {})
        if brief:
            report.append("### Market Intelligence Insights\n\n")
            report.append(f"- **VIX Level**: {brief.get('market_status', {}).get('vix', 'N/A')}\n")
            report.append(f"- **Economic Events**: {len(brief.get('economic_events', []))}\n")
            report.append(f"- **Watchlist Symbols**: {len(brief.get('watchlist_signals', []))}\n")
            report.append(f"- **Key Themes**: {len(brief.get('key_themes', []))}\n\n")

        # Summary statistics
        report.append("## Response Statistics\n\n")
        report.append("| Endpoint | Size (bytes) | Status |\n")
        report.append("|----------|-------------|--------|\n")

        for key in sorted(self.responses.keys()):
            data = self.responses[key]
            size = len(json.dumps(data))
            status = "✓" if data else "✗"
            endpoint_name = key.replace('_', ' ').title()
            report.append(f"| {endpoint_name} | {size:,} | {status} |\n")

        report.append("\n")

        # Footer
        report.append("---\n\n")
        report.append("## Report Information\n\n")
        report.append(f"- **Report Generated**: {datetime.now().isoformat()}\n")
        report.append(f"- **Environment**: fin-ai1 (Python 3.10)\n")
        report.append(f"- **Project**: MCP Finance Backend\n")
        report.append(f"- **Total Responses**: {len(self.responses)}\n")

        # Write report
        with open(output_file, 'w') as f:
            f.writelines(report)

        print(f"✓ Comprehensive report generated: {output_file}")

def main():
    """Main entry point."""
    if len(sys.argv) != 3:
        print("Usage: generate_backend_report.py <run_dir> <output_file>")
        sys.exit(1)

    run_dir = sys.argv[1]
    output_file = sys.argv[2]

    # Check run directory exists
    if not Path(run_dir).is_dir():
        print(f"Error: Run directory not found: {run_dir}")
        sys.exit(1)

    # Generate report
    generator = ReportGenerator(run_dir)
    generator.generate_report(output_file)

    print(f"✓ Report available at: {output_file}")

if __name__ == "__main__":
    main()
