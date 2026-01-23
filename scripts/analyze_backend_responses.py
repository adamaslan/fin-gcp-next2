#!/usr/bin/env python3
"""
Backend Response Analyzer
Processes API responses and extracts key insights
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class BackendAnalyzer:
    """Analyzes backend API responses and generates insights."""

    def __init__(self, run_dir: str):
        """Initialize analyzer with run directory."""
        self.run_dir = Path(run_dir)
        self.responses = self._load_responses()
        self.insights = {}

    def _load_responses(self) -> Dict[str, Any]:
        """Load all JSON response files."""
        responses = {}
        for json_file in sorted(self.run_dir.glob("*.json")):
            try:
                with open(json_file, 'r') as f:
                    responses[json_file.stem] = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load {json_file}: {e}")
        return responses

    def analyze_health(self):
        """Analyze health check responses."""
        if '01_health' not in self.responses:
            return None

        health = self.responses['01_health']
        return {
            "service": health.get("service"),
            "version": health.get("version"),
            "status": health.get("status"),
            "gcp_services": health.get("gcp", {})
        }

    def analyze_trade_plans(self) -> Dict[str, Any]:
        """Analyze all trade plan responses."""
        insights = {}

        for key, data in self.responses.items():
            if 'trade_plan' in key and isinstance(data, dict):
                symbol = data.get("symbol", "UNKNOWN")
                has_trades = data.get("has_trades", False)
                trade_plans = data.get("trade_plans", [])

                insights[symbol] = {
                    "symbol": symbol,
                    "has_trades": has_trades,
                    "trade_count": len(trade_plans),
                    "trades": []
                }

                for trade in trade_plans:
                    insights[symbol]["trades"].append({
                        "timeframe": trade.get("timeframe"),
                        "bias": trade.get("bias"),
                        "entry_price": trade.get("entry_price"),
                        "stop_price": trade.get("stop_price"),
                        "target_price": trade.get("target_price"),
                        "risk_reward_ratio": trade.get("risk_reward_ratio"),
                        "risk_quality": trade.get("risk_quality"),
                        "primary_signal": trade.get("primary_signal")
                    })

        return insights

    def analyze_scans(self) -> Dict[str, Any]:
        """Analyze trade scan responses."""
        insights = {}

        for key, data in self.responses.items():
            if 'scan' in key and isinstance(data, dict):
                universe = data.get("universe", "UNKNOWN")
                total_scanned = data.get("total_scanned", 0)
                trades = data.get("qualified_trades", [])

                insights[universe] = {
                    "universe": universe,
                    "total_scanned": total_scanned,
                    "qualified_count": len(trades),
                    "duration_seconds": data.get("duration_seconds"),
                    "conversion_rate": (len(trades) / total_scanned * 100) if total_scanned > 0 else 0,
                    "top_5_trades": []
                }

                # Sort by signal strength if available, else by entry price
                sorted_trades = sorted(
                    trades,
                    key=lambda x: x.get("signal_strength", 0) or 0,
                    reverse=True
                )

                for trade in sorted_trades[:5]:
                    insights[universe]["top_5_trades"].append({
                        "symbol": trade.get("symbol"),
                        "entry_price": trade.get("entry_price"),
                        "stop_price": trade.get("stop_price"),
                        "target_price": trade.get("target_price"),
                        "signal_strength": trade.get("signal_strength"),
                        "timeframe": trade.get("timeframe")
                    })

        return insights

    def analyze_portfolio(self) -> Optional[Dict[str, Any]]:
        """Analyze portfolio risk response."""
        if '08_portfolio_risk' not in self.responses:
            return None

        data = self.responses['08_portfolio_risk']

        return {
            "total_value": data.get("total_value"),
            "total_max_loss": data.get("total_max_loss"),
            "risk_percent_of_portfolio": data.get("risk_percent_of_portfolio"),
            "overall_risk_level": data.get("overall_risk_level"),
            "position_count": len(data.get("positions", [])),
            "sector_concentration": data.get("sector_concentration", {}),
            "hedge_suggestions": data.get("hedge_suggestions", []),
            "positions": [
                {
                    "symbol": p.get("symbol"),
                    "shares": p.get("shares"),
                    "current_value": p.get("current_value")
                }
                for p in data.get("positions", [])
            ]
        }

    def analyze_morning_brief(self) -> Optional[Dict[str, Any]]:
        """Analyze morning brief response."""
        if '09_morning_brief' not in self.responses:
            return None

        data = self.responses['09_morning_brief']

        # Count signals by action
        signal_counts = {"BUY": 0, "HOLD": 0, "SELL": 0}
        for signal in data.get("watchlist_signals", []):
            action = signal.get("action", "").upper()
            if action in signal_counts:
                signal_counts[action] += 1

        return {
            "market_open": data.get("market_status", {}).get("market_open"),
            "vix": data.get("market_status", {}).get("vix"),
            "market_sentiment": data.get("market_status", {}).get("market_sentiment"),
            "economic_events": len(data.get("economic_events", [])),
            "watchlist_symbols": len(data.get("watchlist_signals", [])),
            "signal_distribution": signal_counts,
            "sector_leaders": [
                {
                    "sector": s.get("sector"),
                    "leaders": s.get("leaders", []),
                    "sentiment": s.get("sentiment")
                }
                for s in data.get("sector_leaders", [])
            ],
            "key_themes": data.get("key_themes", [])
        }

    def generate_report(self, output_file: str) -> None:
        """Generate comprehensive analysis report."""

        # Analyze all data
        health = self.analyze_health()
        trade_plans = self.analyze_trade_plans()
        scans = self.analyze_scans()
        portfolio = self.analyze_portfolio()
        morning_brief = self.analyze_morning_brief()

        # Generate report content
        report = []
        report.append("# Backend Response Analysis Report\n\n")
        report.append(f"**Generated**: {datetime.now().isoformat()}\n")
        report.append(f"**Run Directory**: {self.run_dir}\n")
        report.append("---\n\n")

        # Health Section
        if health:
            report.append("## System Health\n\n")
            report.append(f"- **Service**: {health['service']}\n")
            report.append(f"- **Version**: {health['version']}\n")
            report.append(f"- **Status**: {health['status']}\n")
            report.append("- **GCP Services**:\n")
            for service, status in health['gcp_services'].items():
                report.append(f"  - {service}: {status}\n")
            report.append("\n")

        # Trade Plans Section
        if trade_plans:
            report.append("## Trade Planning Analysis\n\n")
            report.append(f"**Securities Analyzed**: {len(trade_plans)}\n\n")

            for symbol, data in trade_plans.items():
                report.append(f"### {symbol}\n\n")
                report.append(f"- **Has Trades**: {data['has_trades']}\n")
                report.append(f"- **Trade Count**: {data['trade_count']}\n")

                if data['trades']:
                    report.append("\n**Trade Details**:\n\n")
                    for i, trade in enumerate(data['trades'], 1):
                        report.append(f"**Trade {i}**: {trade['bias'].upper() if trade['bias'] else 'N/A'}\n")
                        report.append(f"- Timeframe: {trade['timeframe']}\n")
                        report.append(f"- Entry: ${trade['entry_price']}\n")
                        report.append(f"- Stop: ${trade['stop_price']}\n")
                        report.append(f"- Target: ${trade['target_price']}\n")
                        report.append(f"- Risk/Reward: {trade['risk_reward_ratio']}:1\n")
                        report.append(f"- Quality: {trade['risk_quality']}\n")
                        report.append(f"- Signal: {trade['primary_signal']}\n\n")

            report.append("\n")

        # Scans Section
        if scans:
            report.append("## Universe Scanning Analysis\n\n")

            for universe, data in scans.items():
                report.append(f"### {universe.upper()}\n\n")
                report.append(f"- **Total Scanned**: {data['total_scanned']}\n")
                report.append(f"- **Qualified Setups**: {data['qualified_count']}\n")
                report.append(f"- **Conversion Rate**: {data['conversion_rate']:.2f}%\n")
                report.append(f"- **Duration**: {data['duration_seconds']:.2f}s\n")

                if data['top_5_trades']:
                    report.append("\n**Top 5 Qualified Trades**:\n\n")
                    for i, trade in enumerate(data['top_5_trades'], 1):
                        report.append(f"{i}. **{trade['symbol']}**")
                        if trade['signal_strength']:
                            report.append(f" (Strength: {trade['signal_strength']*100:.0f}%)")
                        report.append("\n")
                        report.append(f"   - Entry: ${trade['entry_price']}\n")
                        report.append(f"   - Stop: ${trade['stop_price']}\n")
                        report.append(f"   - Target: ${trade['target_price']}\n")
                        report.append(f"   - Timeframe: {trade['timeframe']}\n\n")

                report.append("\n")

        # Portfolio Section
        if portfolio:
            report.append("## Portfolio Risk Analysis\n\n")
            report.append(f"- **Total Value**: ${portfolio['total_value']:,.2f}\n")
            report.append(f"- **Max Loss**: ${portfolio['total_max_loss']:,.2f}\n")
            report.append(f"- **Risk %**: {portfolio['risk_percent_of_portfolio']:.1f}%\n")
            report.append(f"- **Risk Level**: {portfolio['overall_risk_level']}\n")
            report.append(f"- **Positions**: {portfolio['position_count']}\n\n")

            if portfolio['positions']:
                report.append("**Position Details**:\n\n")
                for pos in portfolio['positions']:
                    report.append(f"- **{pos['symbol']}**: {pos['shares']} shares = ${pos['current_value']:,.2f}\n")
                report.append("\n")

            if portfolio['sector_concentration']:
                report.append("**Sector Concentration**:\n\n")
                for sector, pct in portfolio['sector_concentration'].items():
                    report.append(f"- {sector}: {pct:.1f}%\n")
                report.append("\n")

            if portfolio['hedge_suggestions']:
                report.append("**Hedge Suggestions**:\n\n")
                for suggestion in portfolio['hedge_suggestions'][:3]:
                    report.append(f"- {suggestion}\n")
                report.append("\n")

        # Morning Brief Section
        if morning_brief:
            report.append("## Market Brief Summary\n\n")
            report.append(f"- **Market Open**: {'Yes' if morning_brief['market_open'] else 'No'}\n")
            report.append(f"- **VIX**: {morning_brief['vix']}\n")
            report.append(f"- **Sentiment**: {morning_brief.get('market_sentiment', 'N/A')}\n")
            report.append(f"- **Economic Events**: {morning_brief['economic_events']}\n\n")

            report.append("**Watchlist Signal Distribution**:\n\n")
            for action, count in morning_brief['signal_distribution'].items():
                report.append(f"- {action}: {count}\n")
            report.append("\n")

            if morning_brief['sector_leaders']:
                report.append("**Sector Leaders**:\n\n")
                for sector_info in morning_brief['sector_leaders']:
                    report.append(f"- **{sector_info['sector']}** ({sector_info['sentiment']}):\n")
                    for leader in sector_info['leaders'][:3]:
                        report.append(f"  - {leader}\n")
                report.append("\n")

            if morning_brief['key_themes']:
                report.append("**Key Market Themes**:\n\n")
                for theme in morning_brief['key_themes']:
                    report.append(f"- {theme}\n")
                report.append("\n")

        # Write report
        with open(output_file, 'w') as f:
            f.writelines(report)

        print(f"✓ Analysis report generated: {output_file}")

def main():
    """Main entry point."""
    if len(sys.argv) != 3:
        print("Usage: analyze_backend_responses.py <run_dir> <output_file>")
        sys.exit(1)

    run_dir = sys.argv[1]
    output_file = sys.argv[2]

    # Check run directory exists
    if not Path(run_dir).is_dir():
        print(f"Error: Run directory not found: {run_dir}")
        sys.exit(1)

    # Generate analysis
    analyzer = BackendAnalyzer(run_dir)
    analyzer.generate_report(output_file)

    print(f"✓ Complete analysis available at: {output_file}")

if __name__ == "__main__":
    main()
