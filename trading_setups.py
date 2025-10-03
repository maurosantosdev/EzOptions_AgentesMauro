from enum import Enum
import pandas as pd

class SetupType(Enum):
    BULLISH_BREAKOUT = "bullish_breakout"
    BEARISH_BREAKOUT = "bearish_breakout"
    PULLBACK_TOP = "pullback_top"
    PULLBACK_BOTTOM = "pullback_bottom"
    CONSOLIDATED_MARKET = "consolidated_market"
    GAMMA_NEGATIVE_PROTECTION = "gamma_negative_protection"
    BUY_STOP_STRONG_MARKET = "buy_stop_strong_market"
    BUY_LIMIT_STRONG_MARKET = "buy_limit_strong_market"
    SELL_STOP_STRONG_MARKET = "sell_stop_strong_market"
    SELL_LIMIT_STRONG_MARKET = "sell_limit_strong_market"

class SetupResult:
    def __init__(self, setup_type, active, confidence, details, target_price, risk_level):
        self.setup_type = setup_type
        self.active = active
        self.confidence = confidence
        self.details = details
        self.target_price = target_price
        self.risk_level = risk_level

class TradingSetupAnalyzer:
    def __init__(self):
        self.GEX_THRESHOLD = 10000

    def analyze_all_setups(self, calls_df, puts_df, current_price, vwap_data):
        """Analyze all possible setups and return results"""
        results = {}

        # Analyze Bullish Breakout Setup
        results['bullish_breakout'] = self._analyze_bullish_breakout(calls_df, puts_df, current_price, vwap_data)

        # Analyze Bearish Breakout Setup
        results['bearish_breakout'] = self._analyze_bearish_breakout(calls_df, puts_df, current_price, vwap_data)

        # Analyze Pullback to Top Setup
        results['pullback_top'] = self._analyze_pullback_top(calls_df, puts_df, current_price, vwap_data)

        # Analyze Pullback to Bottom Setup
        results['pullback_bottom'] = self._analyze_pullback_bottom(calls_df, puts_df, current_price, vwap_data)

        # Analyze Consolidated Market Setup
        results['consolidated_market'] = self._analyze_consolidated_market(calls_df, puts_df, current_price, vwap_data)

        # Analyze Gamma Negative Protection Setup
        results['gamma_negative_protection'] = self._analyze_gamma_negative_protection(calls_df, puts_df, current_price, vwap_data)

        return results

    def _analyze_bullish_breakout(self, calls_df, puts_df, current_price, vwap_data):
        """Analyze bullish breakout setup"""
        try:
            # Look for high gamma exposure above current price (potential resistance)
            gex_above_price = calls_df[calls_df['strike'] > current_price] if not calls_df.empty else pd.DataFrame()
            
            if gex_above_price.empty or gex_above_price.empty:
                return SetupResult(
                    SetupType.BULLISH_BREAKOUT,
                    False,
                    0,
                    "No options strikes above current price",
                    None,
                    "LOW"
                )
            
            max_gex_strike = gex_above_price.loc[gex_above_price['GEX'].idxmax(), 'strike']
            max_gex_value = gex_above_price['GEX'].max()
            
            # Calculate confidence based on GEX value and distance from price
            distance_from_price = (max_gex_strike - current_price) / current_price
            gex_confidence = min(100, max(0, (max_gex_value / self.GEX_THRESHOLD) * 30))
            distance_confidence = max(0, 30 - (distance_from_price * 1000))
            
            # VWAP alignment
            vwap_confidence = 0
            if 'vwap' in vwap_data and current_price > vwap_data['vwap']:
                vwap_confidence = 25  # Higher confidence when price above VWAP
            
            # Overall confidence
            total_confidence = min(100, gex_confidence + distance_confidence + vwap_confidence)
            
            active = total_confidence >= 30
            
            return SetupResult(
                SetupType.BULLISH_BREAKOUT,
                active,
                total_confidence,
                f"Bullish breakout potential at {max_gex_strike:.2f}",
                max_gex_strike if active else None,
                "HIGH" if total_confidence > 70 else "MEDIUM" if total_confidence > 40 else "LOW"
            )
        except Exception as e:
            return SetupResult(
                SetupType.BULLISH_BREAKOUT,
                False,
                0,
                f"Error analyzing setup: {str(e)}",
                None,
                "LOW"
            )

    def _analyze_bearish_breakout(self, calls_df, puts_df, current_price, vwap_data):
        """Analyze bearish breakout setup"""
        try:
            # Look for high gamma exposure below current price (potential support that could break)
            all_gex = pd.concat([calls_df[['strike', 'GEX']], puts_df[['strike', 'GEX']]]) if not calls_df.empty and not puts_df.empty else pd.DataFrame()
            gex_below_price = all_gex[all_gex['strike'] < current_price] if not all_gex.empty else pd.DataFrame()
            
            if gex_below_price.empty:
                return SetupResult(
                    SetupType.BEARISH_BREAKOUT,
                    False,
                    0,
                    "No options strikes below current price",
                    None,
                    "LOW"
                )
            
            # Find the strike with the highest negative GEX (highest put gamma)
            if not gex_below_price.empty:
                min_gex_strike = gex_below_price.loc[gex_below_price['GEX'].idxmin(), 'strike']
                min_gex_value = gex_below_price['GEX'].min()
                
                # Calculate confidence
                distance_from_price = (current_price - min_gex_strike) / current_price
                gex_confidence = min(100, max(0, (abs(min_gex_value) / self.GEX_THRESHOLD) * 30))
                distance_confidence = max(0, 30 - (distance_from_price * 1000))
                
                # VWAP alignment (lower when below VWAP)
                vwap_confidence = 0
                if 'vwap' in vwap_data and current_price < vwap_data['vwap']:
                    vwap_confidence = 25  # Higher confidence when price below VWAP
                
                total_confidence = min(100, gex_confidence + distance_confidence + vwap_confidence)
                active = total_confidence >= 30
                
                return SetupResult(
                    SetupType.BEARISH_BREAKOUT,
                    active,
                    total_confidence,
                    f"Bearish breakout potential at {min_gex_strike:.2f}",
                    min_gex_strike if active else None,
                    "HIGH" if total_confidence > 70 else "MEDIUM" if total_confidence > 40 else "LOW"
                )
            else:
                return SetupResult(
                    SetupType.BEARISH_BREAKOUT,
                    False,
                    0,
                    "No significant GEX below current price",
                    None,
                    "LOW"
                )
        except Exception as e:
            return SetupResult(
                SetupType.BEARISH_BREAKOUT,
                False,
                0,
                f"Error analyzing setup: {str(e)}",
                None,
                "LOW"
            )

    def _analyze_pullback_top(self, calls_df, puts_df, current_price, vwap_data):
        """Analyze pullback to top (resistance) setup"""
        try:
            # Look for resistance levels above price with high option gamma
            gex_above_price = calls_df[calls_df['strike'] > current_price] if not calls_df.empty else pd.DataFrame()
            if gex_above_price.empty:
                return SetupResult(
                    SetupType.PULLBACK_TOP,
                    False,
                    0,
                    "No resistance levels above current price",
                    None,
                    "LOW"
                )
            
            max_gex_strike = gex_above_price.loc[gex_above_price['GEX'].idxmax(), 'strike']
            
            # Check if price is approaching this level (pullback)
            distance_from_price = (max_gex_strike - current_price) / current_price
            if distance_from_price > 0.02:  # Too far, not a pullback
                return SetupResult(
                    SetupType.PULLBACK_TOP,
                    False,
                    0,
                    "Price too far from resistance level",
                    None,
                    "LOW"
                )
            
            # Confidence based on proximity and GEX value
            gex_value = gex_above_price['GEX'].max()
            gex_confidence = min(40, (gex_value / self.GEX_THRESHOLD) * 40)
            proximity_confidence = max(10, 50 - (distance_from_price * 1000))
            
            total_confidence = min(100, gex_confidence + proximity_confidence)
            active = total_confidence >= 30
            
            return SetupResult(
                SetupType.PULLBACK_TOP,
                active,
                total_confidence,
                f"Pullback to resistance at {max_gex_strike:.2f}",
                max_gex_strike if active else None,
                "MEDIUM" if total_confidence > 50 else "LOW"
            )
        except Exception as e:
            return SetupResult(
                SetupType.PULLBACK_TOP,
                False,
                0,
                f"Error analyzing setup: {str(e)}",
                None,
                "LOW"
            )

    def _analyze_pullback_bottom(self, calls_df, puts_df, current_price, vwap_data):
        """Analyze pullback to bottom (support) setup"""
        try:
            # Look for support levels below price with high option gamma
            all_gex = pd.concat([calls_df[['strike', 'GEX']], puts_df[['strike', 'GEX']]]) if not calls_df.empty and not puts_df.empty else pd.DataFrame()
            gex_below_price = all_gex[all_gex['strike'] < current_price] if not all_gex.empty else pd.DataFrame()
            if gex_below_price.empty:
                return SetupResult(
                    SetupType.PULLBACK_BOTTOM,
                    False,
                    0,
                    "No support levels below current price",
                    None,
                    "LOW"
                )
            
            max_gex_strike = gex_below_price.loc[gex_below_price['GEX'].idxmax(), 'strike'] if not gex_below_price.empty else 0
            
            if max_gex_strike == 0:
                return SetupResult(
                    SetupType.PULLBACK_BOTTOM,
                    False,
                    0,
                    "No significant GEX below current price",
                    None,
                    "LOW"
                )
            
            # Check if price is approaching this level (pullback)
            distance_from_price = (current_price - max_gex_strike) / current_price
            if distance_from_price > 0.02:  # Too far, not a pullback
                return SetupResult(
                    SetupType.PULLBACK_BOTTOM,
                    False,
                    0,
                    "Price too far from support level",
                    None,
                    "LOW"
                )
            
            # Confidence based on proximity and GEX value
            gex_value = gex_below_price['GEX'].max()
            gex_confidence = min(40, (gex_value / self.GEX_THRESHOLD) * 40)
            proximity_confidence = max(10, 50 - (distance_from_price * 1000))
            
            total_confidence = min(100, gex_confidence + proximity_confidence)
            active = total_confidence >= 30
            
            return SetupResult(
                SetupType.PULLBACK_BOTTOM,
                active,
                total_confidence,
                f"Pullback to support at {max_gex_strike:.2f}",
                max_gex_strike if active else None,
                "MEDIUM" if total_confidence > 50 else "LOW"
            )
        except Exception as e:
            return SetupResult(
                SetupType.PULLBACK_BOTTOM,
                False,
                0,
                f"Error analyzing setup: {str(e)}",
                None,
                "LOW"
            )

    def _analyze_consolidated_market(self, calls_df, puts_df, current_price, vwap_data):
        """Analyze consolidated/ranging market setup"""
        try:
            # Look for balanced GEX above and below price, indicating possible range
            gex_above = calls_df[calls_df['strike'] > current_price] if not calls_df.empty else pd.DataFrame()
            gex_below = pd.concat([calls_df[calls_df['strike'] < current_price], puts_df[puts_df['strike'] < current_price]]) if (not calls_df.empty or not puts_df.empty) else pd.DataFrame()
            
            avg_gex_above = gex_above['GEX'].mean() if not gex_above.empty else 0
            avg_gex_below = gex_below['GEX'].mean() if not gex_below.empty else 0
            
            # Check if GEX is relatively balanced (indicating possible consolidation)
            gex_balance = abs(avg_gex_above - avg_gex_below) / max(avg_gex_above + avg_gex_below, 1)
            
            # Check proximity to VWAP for range confirmation
            vwap_proximity = 0
            if 'vwap' in vwap_data:
                vwap_proximity = 1 - min(1, abs(current_price - vwap_data['vwap']) / current_price)
            
            balance_confidence = max(0, (1 - gex_balance) * 50)
            vwap_confidence = vwap_proximity * 30
            
            total_confidence = min(100, balance_confidence + vwap_confidence)
            active = total_confidence >= 40
            
            # For ranging market, target could be mean reversion to VWAP
            target_price = None
            if active and 'vwap' in vwap_data:
                target_price = vwap_data['vwap']
            
            return SetupResult(
                SetupType.CONSOLIDATED_MARKET,
                active,
                total_confidence,
                f"Market showing consolidation signs, targeting VWAP at {target_price:.2f}" if target_price else "Market showing consolidation signs",
                target_price,
                "LOW" if total_confidence < 60 else "MEDIUM"
            )
        except Exception as e:
            return SetupResult(
                SetupType.CONSOLIDATED_MARKET,
                False,
                0,
                f"Error analyzing setup: {str(e)}",
                None,
                "LOW"
            )

    def _analyze_gamma_negative_protection(self, calls_df, puts_df, current_price, vwap_data):
        """Analyze gamma negative protection setup"""
        try:
            # Look for high put gamma (negative GEX) that could provide protection
            puts_gex = puts_df[puts_df['strike'] < current_price] if not puts_df.empty else pd.DataFrame()  # Puts below price
            if puts_gex.empty:
                return SetupResult(
                    SetupType.GAMMA_NEGATIVE_PROTECTION,
                    False,
                    0,
                    "No puts below current price",
                    None,
                    "LOW"
                )
            
            # Find the strike with highest put gamma (most negative GEX)
            if not puts_gex.empty:
                min_gex_strike = puts_gex.loc[puts_gex['GEX'].idxmin(), 'strike']
                min_gex_value = puts_gex['GEX'].min()
                
                # Calculate confidence based on gamma value and distance from price
                distance_from_price = (current_price - min_gex_strike) / current_price
                gamma_confidence = min(50, (abs(min_gex_value) / self.GEX_THRESHOLD) * 50)
                distance_confidence = max(0, 30 - (distance_from_price * 1000))
                
                total_confidence = min(100, gamma_confidence + distance_confidence)
                active = total_confidence >= 25
                
                return SetupResult(
                    SetupType.GAMMA_NEGATIVE_PROTECTION,
                    active,
                    total_confidence,
                    f"Gamma negative protection at {min_gex_strike:.2f}",
                    min_gex_strike if active else None,
                    "LOW" if total_confidence < 50 else "MEDIUM"
                )
            else:
                return SetupResult(
                    SetupType.GAMMA_NEGATIVE_PROTECTION,
                    False,
                    0,
                    "No significant put gamma below current price",
                    None,
                    "LOW"
                )
        except Exception as e:
            return SetupResult(
                SetupType.GAMMA_NEGATIVE_PROTECTION,
                False,
                0,
                f"Error analyzing setup: {str(e)}",
                None,
                "LOW"
            )