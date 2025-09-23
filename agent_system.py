import MetaTrader5 as mt5
import time
import os
from dotenv import load_dotenv
import threading
from datetime import datetime, time as datetime_time
import pytz
import yfinance as yf
import pandas as pd
from greeks_calculator import compute_and_process_greeks
from trading_setups import TradingSetupAnalyzer, SetupType

# Lock global para sincronizar o acesso à API do MT5
mt5_lock = threading.Lock()

class AgentSystem(threading.Thread):
    def __init__(self, config):
        super().__init__()
        load_dotenv()

        # --- Configuration ---
        self.name = config.get('name', 'DefaultAgent')
        self.symbol = config.get('symbol', 'US100')
        self.magic_number = config.get('magic_number', 234000)
        self.lot_size = config.get('lot_size', 0.01)
        self.options_symbol = config.get('options_symbol', "QQQ")

        # --- Cached State ---
        self.account_info = None
        self.total_pnl = 0
        self.active_positions_count = 0
        self.latest_decision = {}
        self.is_connected = False

        # --- MT5 Initialization ---
        with mt5_lock:
            if not mt5.initialize(
                login=int(os.getenv("MT5_LOGIN")),
                server=os.getenv("MT5_SERVER"),
                password=os.getenv("MT5_PASSWORD")
            ):
                print(f"[{self.name}] initialize() failed, error code =", mt5.last_error())
                self.is_connected = False
            else:
                self.is_connected = True
                print(f"[{self.name}] Agent System Initialized and Connected to MetaTrader 5.")

        # --- Strategy Parameters ---
        self.options_analysis_enabled = True
        self.nearest_expiry = None
        self.GEX_THRESHOLD = 10000
        self.buy_limit_sl_percent = 0.001
        self.buy_limit_tp_percent = 0.0001
        self.sell_limit_sl_percent = 0.0001
        self.sell_limit_tp_percent = 0.0001
        self.buy_stop_sl_percent = 0.001
        self.buy_stop_tp_percent = 0.0001
        self.sell_stop_sl_percent = 0.0001
        self.sell_stop_tp_percent = 0.0001
        self.positions_closed_today = False

        # --- Trading Setups System ---
        self.setup_analyzer = TradingSetupAnalyzer()
        self.current_setups = {}
        self.vwap_data = {}

    def _update_account_state(self):
        """Fetches all account and position data from MT5 and caches it."""
        if not self.is_connected: return
        with mt5_lock:
            self.account_info = mt5.account_info()
            positions = mt5.positions_get(magic=self.magic_number)
            self.is_connected = mt5.terminal_info() is not None

        if positions:
            self.active_positions_count = len(positions)
            self.total_pnl = sum(p.profit for p in positions)
        else:
            self.active_positions_count = 0
            self.total_pnl = 0

    def run(self):
        if not self.is_connected: return
        print(f"[{self.name}] Starting real-time trading for {self.symbol}...")
        with mt5_lock:
            selected = mt5.symbol_select(self.symbol, True)
        if not selected:
            with mt5_lock:
                print(f"[{self.name}] Failed to select {self.symbol}, error code =", mt5.last_error())
            self.shutdown()
            return
        
        try:
            stock = yf.Ticker(self.options_symbol)
            self.nearest_expiry = stock.options[0]
            print(f"[{self.name}] Using nearest expiry for options analysis: {self.nearest_expiry}")
        except Exception as e:
            print(f"[{self.name}] Could not fetch options expirations: {e}")
            self.options_analysis_enabled = False

        try:
            while self.is_connected:
                self._update_account_state()

                if self.is_trading_hours():
                    decision_output = self.make_decision(self.options_symbol, self.nearest_expiry)
                    self.latest_decision = decision_output
                    
                    orders_to_place = decision_output.get("orders", [])
                    if orders_to_place:
                        self.execute_volatility_trade(orders_to_place)
                    
                    self.monitor_and_manage_positions()
                    time.sleep(5)
                else:
                    ny_timezone = pytz.timezone('America/New_York')
                    current_time_ny = datetime.now(ny_timezone).time()
                    market_close_time = datetime_time(16, 0, 0)
                    market_open_time = datetime_time(9, 0, 0)

                    if current_time_ny >= market_close_time and not self.positions_closed_today:
                        print(f"[{self.name}] Market close time. Closing all open positions.")
                        self.close_all_positions()
                        self.positions_closed_today = True
                    elif current_time_ny < market_open_time:
                        self.positions_closed_today = False
                    
                    time.sleep(60)
        except KeyboardInterrupt:
            print(f"\n[{self.name}] Stopping trading agent.")
        finally:
            self.shutdown()

    def make_decision(self, ticker, expiry_date_str):
        calls, puts, S, t = self._get_processed_options_data(ticker, expiry_date_str)
        default_response = {"orders": [], "setups": {}, "calls": None, "puts": None, "S": None}
        if calls is None or puts is None: return default_response

        # Update VWAP data (simulação - em produção viria de um feed de dados)
        self._update_vwap_data(S)

        # Analyze all 6 setups using the new system
        setups_results = self.setup_analyzer.analyze_all_setups(calls, puts, S, self.vwap_data)
        self.current_setups = setups_results

        # Convert to legacy format for compatibility while transitioning
        legacy_setups = {}
        orders_to_place = []

        for setup_key, setup_result in setups_results.items():
            # Convert to legacy tuple format (active, details, target_price, order_kind)
            order_kind = self._get_order_kind_from_setup(setup_result.setup_type, setup_result.active)
            legacy_setups[setup_key] = (
                setup_result.active,
                setup_result.details,
                setup_result.target_price,
                order_kind
            )

            # Only place orders for setups with sufficient confidence
            if setup_result.active and setup_result.target_price is not None and order_kind is not None:
                action = self._get_action_from_setup(setup_result.setup_type)
                orders_to_place.append((action, setup_result.target_price, order_kind))

        return {
            "orders": orders_to_place,
            "setups": legacy_setups,
            "setups_detailed": setups_results,  # New detailed format
            "calls": calls,
            "puts": puts,
            "S": S
        }

    def execute_volatility_trade(self, orders_to_place):
        with mt5_lock:
            pending_orders = mt5.orders_get(symbol=self.symbol, magic=self.magic_number)
        if pending_orders:
            for order in pending_orders:
                self.cancel_order(order.ticket)

        num_orders = 5
        spacing = 0.001
        for action, target_price, order_kind in orders_to_place:
            grid_volume = self.lot_size / num_orders
            with mt5_lock:
                symbol_info = mt5.symbol_info(self.symbol)
            if symbol_info and grid_volume < symbol_info.volume_min:
                grid_volume = symbol_info.volume_min

            for i in range(num_orders):
                price_multiplier = 1 + (i * spacing) if order_kind in ["BUY_STOP", "SELL_LIMIT"] else 1 - (i * spacing)
                grid_price = target_price * price_multiplier
                self.place_pending_order(action, grid_price, order_kind, volume=grid_volume)

    def place_pending_order(self, action, target_price, order_kind, from_greeks=True, volume=None):
        with mt5_lock:
            symbol_info = mt5.symbol_info(self.symbol)
        if not symbol_info: return

        order_volume = volume if volume is not None else self.lot_size
        if order_volume < symbol_info.volume_min:
            order_volume = symbol_info.volume_min

        converted_target_price = self._convert_price_if_needed(target_price, from_greeks)
        if converted_target_price is None: return

        order_type = self._get_order_type(order_kind)
        if order_type is None: return

        stop_loss_price, take_profit_price = self._calculate_sl_tp(order_kind, converted_target_price)
        
        if not self._validate_order_price(order_type, converted_target_price):
            return

        request = self._build_order_request(action, order_volume, order_type, converted_target_price, stop_loss_price, take_profit_price)
        
        with mt5_lock:
            result = mt5.order_send(request)

        self._handle_order_result(result, action, order_volume, converted_target_price, order_kind)

    def cancel_order(self, ticket):
        request = {"action": mt5.TRADE_ACTION_REMOVE, "order": ticket}
        with mt5_lock:
            result = mt5.order_send(request)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"[{self.name}] Failed to cancel pending order #{ticket}.")

    def close_position(self, position):
        with mt5_lock:
            price = mt5.symbol_info_tick(self.symbol).bid if position.type == 0 else mt5.symbol_info_tick(self.symbol).ask
        request = {
            "action": mt5.TRADE_ACTION_DEAL, "symbol": self.symbol, "volume": position.volume,
            "type": mt5.ORDER_TYPE_SELL if position.type == 0 else mt5.ORDER_TYPE_BUY,
            "position": position.ticket, "price": price, "deviation": 20, "magic": self.magic_number,
            "type_time": mt5.ORDER_TIME_GTC, "type_filling": mt5.ORDER_FILLING_IOC,
        }
        with mt5_lock:
            result = mt5.order_send(request)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"[{self.name}] Failed to close position #{position.ticket}.")

    def close_all_positions(self):
        with mt5_lock:
            open_positions = mt5.positions_get(symbol=self.symbol, magic=self.magic_number)
        if open_positions:
            for position in open_positions:
                self.close_position(position)

    def monitor_and_manage_positions(self):
        with mt5_lock:
            positions = mt5.positions_get(symbol=self.symbol, magic=self.magic_number)
        if positions:
            for position in positions:
                if position.profit <= -0.50:
                    self.execute_loss_recovery(position)

    def execute_loss_recovery(self, position):
        self.close_position(position)
        with mt5_lock:
            tick = mt5.symbol_info_tick(self.symbol)
        if not tick: return

        if position.type == mt5.ORDER_TYPE_BUY:
            self.place_pending_order("SELL", tick.bid * (1 - 0.002), "SELL_STOP", from_greeks=False)
        elif position.type == mt5.ORDER_TYPE_SELL:
            self.place_pending_order("BUY", tick.ask * (1 + 0.002), "BUY_STOP", from_greeks=False)

    # --- Setup Helper Methods ---
    def _update_vwap_data(self, current_price):
        """Simulates VWAP data - in production this would come from market data feed"""
        # Simplified VWAP simulation (in real implementation, calculate from volume-weighted average)
        self.vwap_data = {
            'vwap': current_price * 0.999,  # Simulate VWAP slightly below current price
            'std1_upper': current_price * 1.005,
            'std1_lower': current_price * 0.995,
            'std2_upper': current_price * 1.01,
            'std2_lower': current_price * 0.99
        }

    def _get_order_kind_from_setup(self, setup_type, is_active):
        """Convert setup type to order kind"""
        if not is_active:
            return None

        order_map = {
            SetupType.BULLISH_BREAKOUT: "BUY_STOP",
            SetupType.BEARISH_BREAKOUT: "SELL_STOP",
            SetupType.PULLBACK_TOP: "SELL_LIMIT",
            SetupType.PULLBACK_BOTTOM: "BUY_LIMIT",
            SetupType.CONSOLIDATED_MARKET: "BUY_LIMIT",  # Range trading
            SetupType.GAMMA_NEGATIVE_PROTECTION: "BUY_STOP"
        }
        return order_map.get(setup_type)

    def _get_action_from_setup(self, setup_type):
        """Convert setup type to trading action"""
        action_map = {
            SetupType.BULLISH_BREAKOUT: "BUY",
            SetupType.BEARISH_BREAKOUT: "SELL",
            SetupType.PULLBACK_TOP: "SELL",
            SetupType.PULLBACK_BOTTOM: "BUY",
            SetupType.CONSOLIDATED_MARKET: "BUY",  # Neutral/range trading
            SetupType.GAMMA_NEGATIVE_PROTECTION: "BUY"
        }
        return action_map.get(setup_type, "BUY")

    def get_setup_confidence_summary(self):
        """Return summary of all setup confidences"""
        if not self.current_setups:
            return {}

        summary = {}
        for setup_key, setup_result in self.current_setups.items():
            summary[setup_key] = {
                'confidence': setup_result.confidence,
                'active': setup_result.active,
                'can_analyze': setup_result.confidence >= 90.0,
                'can_operate': setup_result.confidence >= 60.0,
                'risk_level': setup_result.risk_level
            }
        return summary

    # --- Legacy Strategy Evaluation Methods (kept for backward compatibility) ---
    def _evaluate_bullish_breakout(self, calls, puts, S):
        gex_above_price = calls[calls['strike'] > S]
        if gex_above_price.empty or gex_above_price['GEX'].max() <= 0: return False, "", None, None
        max_gex_strike, _ = self._find_extreme_greeks_strike(gex_above_price, 'GEX', S, "BUY_STOP")
        if max_gex_strike is None: return False, "", None, None
        return True, f"Target at {max_gex_strike:.2f}", max_gex_strike, "BUY_STOP"

    def _evaluate_bearish_breakout(self, calls, puts, S):
        all_gex = pd.concat([calls[['strike', 'GEX']], puts[['strike', 'GEX']]])
        strike_max_neg_gex, _ = self._find_extreme_greeks_strike(all_gex, 'GEX', S, "SELL_STOP", is_positive_extreme=False)
        if strike_max_neg_gex is None: return False, "", None, None
        return True, f"Target at {strike_max_neg_gex:.2f}", strike_max_neg_gex, "SELL_STOP"

    def _evaluate_pullback_top(self, calls, puts, S):
        all_gex = pd.concat([calls[['strike', 'GEX']], puts[['strike', 'GEX']]])
        strike_gex, val_gex = self._find_extreme_greeks_strike(all_gex, 'GEX', S, "SELL_LIMIT")
        if strike_gex is None or val_gex < self.GEX_THRESHOLD: return False, "", None, None
        return True, f"Target at {strike_gex:.2f}", strike_gex, "SELL_LIMIT"

    def _evaluate_pullback_bottom(self, calls, puts, S):
        all_gex = pd.concat([calls[['strike', 'GEX']], puts[['strike', 'GEX']]])
        strike_gex, val_gex = self._find_extreme_greeks_strike(all_gex, 'GEX', S, "BUY_LIMIT", is_positive_extreme=False)
        if strike_gex is None or abs(val_gex) < self.GEX_THRESHOLD: return False, "", None, None
        return True, f"Target at {strike_gex:.2f}", strike_gex, "BUY_LIMIT"

    def _find_extreme_greeks_strike(self, df, greek_type, price_S, order_kind, is_positive_extreme=True):
        above_price = order_kind in ["SELL_LIMIT", "BUY_STOP"]
        if above_price:
            filtered_df = df[df['strike'] > price_S]
        else:
            filtered_df = df[df['strike'] < price_S]
        if filtered_df.empty: return None, None
        
        idx = filtered_df[greek_type].idxmax() if is_positive_extreme else filtered_df[greek_type].idxmin()
        strike = filtered_df.loc[idx, 'strike']
        value = filtered_df.loc[idx, greek_type]

        if isinstance(strike, pd.Series):
            return strike.iloc[0], value.iloc[0]
        
        return (strike, value)

    # --- Data Processing and Helper Methods ---
    def _get_processed_options_data(self, ticker, expiry_date_str):
        if not expiry_date_str: return None, None, None, None
        try:
            stock = yf.Ticker(ticker)
            S = stock.history(period="1d")['Close'].iloc[-1]
            if S == 0: return None, None, None, None
            chain = stock.option_chain(expiry_date_str)
            calls, puts = chain.calls, chain.puts
            if calls.empty or puts.empty: return None, None, None, None
            t = (datetime.strptime(expiry_date_str, "%Y-%m-%d").date() - datetime.today().date()).days / 365.0
            processed_calls, processed_puts = compute_and_process_greeks(calls, puts, S, expiry_date_str, 0.02)
            return processed_calls, processed_puts, S, max(t, 0.0001)
        except Exception as e:
            print(f"[{self.name}] Error in _get_processed_options_data: {e}")
            return None, None, None, None

    def _convert_price_if_needed(self, target_price, from_greeks):
        if not from_greeks: return target_price
        with mt5_lock:
            current_price_us100 = mt5.symbol_info_tick(self.symbol).ask
        try:
            current_price_qqq = yf.Ticker(self.options_symbol).history(period="1d")['Close'].iloc[-1]
            if current_price_qqq == 0: return None
            price_ratio = current_price_us100 / current_price_qqq
            return target_price * price_ratio
        except Exception: return None

    def _get_order_type(self, order_kind):
        return {"BUY_LIMIT": mt5.ORDER_TYPE_BUY_LIMIT, "SELL_LIMIT": mt5.ORDER_TYPE_SELL_LIMIT, 
                "BUY_STOP": mt5.ORDER_TYPE_BUY_STOP, "SELL_STOP": mt5.ORDER_TYPE_SELL_STOP}.get(order_kind)

    def _calculate_sl_tp(self, order_kind, price):
        sl_pct = getattr(self, f"{order_kind.lower()}_sl_percent")
        tp_pct = getattr(self, f"{order_kind.lower()}_tp_percent")
        sl_price = price * (1 - sl_pct) if "BUY" in order_kind else price * (1 + sl_pct)
        tp_price = price * (1 + tp_pct) if "BUY" in order_kind else price * (1 - tp_pct)
        return sl_price, tp_price

    def _validate_order_price(self, order_type, price):
        with mt5_lock:
            tick = mt5.symbol_info_tick(self.symbol)
        if not tick: return False
        if order_type == mt5.ORDER_TYPE_BUY_LIMIT and price >= tick.bid: return False
        if order_type == mt5.ORDER_TYPE_SELL_LIMIT and price <= tick.ask: return False
        if order_type == mt5.ORDER_TYPE_BUY_STOP and price <= tick.ask: return False
        if order_type == mt5.ORDER_TYPE_SELL_STOP and price >= tick.bid: return False
        return True

    def _build_order_request(self, action, volume, order_type, price, sl, tp):
        with mt5_lock:
            digits = mt5.symbol_info(self.symbol).digits
        return {
            "action": mt5.TRADE_ACTION_PENDING, "symbol": self.symbol, "volume": volume, "type": order_type,
            "price": round(price, digits), "sl": round(sl, digits), "tp": round(tp, digits), "magic": self.magic_number,
            "comment": f"{self.name} {action}", "type_time": mt5.ORDER_TIME_GTC,
        }

    def _handle_order_result(self, result, action, volume, price, kind):
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"[{self.name}] Order send failed. Code: {result.retcode if result else 'None'}")
        else:
            print(f"[{self.name}] Order sent: {action} {volume} {self.symbol} @ {price:.2f} ({kind})")

    def shutdown(self):
        print(f"[{self.name}] Shutting down Agent System.")
        with mt5_lock:
            if self.is_connected:
                mt5.shutdown()

    # --- Public Data Accessors ---
    def get_account_balance(self): return self.account_info.balance if self.account_info else 0
    def get_account_equity(self): return self.account_info.equity if self.account_info else 0
    def get_free_margin(self): return self.account_info.margin_free if self.account_info else 0
    def get_total_profit_loss(self): return self.total_pnl
    def get_active_positions_count(self): return self.active_positions_count
    def is_mt5_connected(self): return self.is_connected
    def get_nearest_expiry(self): return self.nearest_expiry
    def is_trading_hours(self):
        ny_timezone = pytz.timezone('America/New_York')
        current_time_ny = datetime.now(ny_timezone)
        if not (0 <= current_time_ny.weekday() <= 4):
            return False
        market_open = datetime_time(9, 0, 0)
        market_close = datetime_time(16, 0, 0)
        return market_open <= current_time_ny.time() < market_close
