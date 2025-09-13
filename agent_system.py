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

class AgentSystem(threading.Thread):
    def __init__(self):
        super().__init__()
        load_dotenv()
        if not mt5.initialize(
            login=int(os.getenv("MT5_LOGIN")),
            server=os.getenv("MT5_SERVER"),
            password=os.getenv("MT5_PASSWORD")
        ):
            print("initialize() failed, error code =", mt5.last_error())
            quit()
        print("Agent System Initialized and Connected to MetaTrader 5.")
        self.last_price = 0
        self.lot_size = 0.02
        self.symbol = "US100"
        self.options_symbol = "QQQ"
        self.options_analysis_enabled = True
        self.prices_history = []
        self.short_ma_period = 50
        self.long_ma_period = 200
        self.current_signal = "HOLD"
        rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 0, self.long_ma_period)
        if rates is not None:
            self.prices_history = [rate['close'] for rate in rates]
            print(f"Loaded {len(self.prices_history)} historical prices.")
        else:
            print("Failed to load historical data.")
        self.nearest_expiry = None

    def run(self):
        print(f"Starting real-time trading for {self.symbol}...")
        selected = mt5.symbol_select(self.symbol, True)
        if not selected:
            print(f"Failed to select {self.symbol}, error code =", mt5.last_error())
            mt5.shutdown()
            return
        
        try:
            stock = yf.Ticker(self.options_symbol)
            available_expiries = stock.options
            if not available_expiries:
                print(f"No options expirations found for {self.options_symbol}. Options analysis will be disabled.")
                self.options_analysis_enabled = False
                self.nearest_expiry = None
            else:
                self.nearest_expiry = available_expiries[0]
                print(f"Using nearest expiry for options analysis: {self.nearest_expiry}")
                self.options_analysis_enabled = True
        except Exception as e:
            print(f"Could not fetch options expirations: {e}")
            self.options_analysis_enabled = False
            self.nearest_expiry = None

        self.last_price = self.get_current_price()
        print(f"Initial price for {self.symbol}: {self.last_price}")

        try:
            while True:
                if self.is_trading_hours():
                    current_price = self.get_current_price()
                    if current_price == 0:
                        time.sleep(1)
                        continue

                    self.prices_history.append(current_price)
                    if len(self.prices_history) > self.long_ma_period:
                        self.prices_history.pop(0)

                    ma_signal = self.get_signal()
                    decision_output = self.make_decision(self.options_symbol, self.nearest_expiry)
                    
                    agent_decision = decision_output.get("decision", "HOLD")
                    target_price = decision_output.get("target_price")

                    final_action = "HOLD"
                    if ma_signal == "BUY" and agent_decision == "BUY":
                        final_action = "BUY"
                    elif ma_signal == "SELL" and agent_decision == "SELL":
                        final_action = "SELL"
                    
                    if final_action != "HOLD":
                        print(f"Signal: {final_action}. Current price: {current_price:.5f}. Target: {target_price}")
                        self.execute_trade(final_action, target_price)
                        self.current_signal = final_action
                    else:
                        print(f"Signal: HOLD. Current price: {current_price:.5f}")
                        self.current_signal = "HOLD"

                    self.last_price = current_price
                    time.sleep(5)
                else:
                    print("Fora do horário de negociação. Aguardando...")
                    time.sleep(60)
        except KeyboardInterrupt:
            print("\nStopping trading agent.")
        finally:
            self.shutdown()

    def calculate_sma(self, prices, period):
        if len(prices) < period:
            return 0
        return sum(prices[-period:]) / period

    def get_signal(self):
        if len(self.prices_history) < self.long_ma_period:
            return "HOLD"
        short_ma = self.calculate_sma(self.prices_history, self.short_ma_period)
        long_ma = self.calculate_sma(self.prices_history, self.long_ma_period)
        if short_ma > long_ma and self.current_signal != "BUY":
            return "BUY"
        elif short_ma < long_ma and self.current_signal != "SELL":
            return "SELL"
        else:
            return "HOLD"

    def get_current_price(self):
        tick = mt5.symbol_info_tick(self.symbol)
        return tick.ask if tick else 0

    def execute_trade(self, action, target_price):
        if action == "HOLD" or target_price is None:
            return

        pending_orders = mt5.orders_get(symbol=self.symbol)
        if pending_orders:
            for order in pending_orders:
                self.cancel_order(order.ticket)

        positions = mt5.positions_get(symbol=self.symbol)
        if positions:
            pos_type = positions[0].type
            if (action == "BUY" and pos_type == 1) or (action == "SELL" and pos_type == 0):
                self.close_position(positions[0])
            else:
                print(f"Position already open in the same direction for {self.symbol}. No new order placed.")
                return

        order_type = mt5.ORDER_TYPE_BUY_STOP if action == "BUY" else mt5.ORDER_TYPE_SELL_STOP

        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": self.symbol,
            "volume": self.lot_size,
            "type": order_type,
            "price": target_price,
            "magic": 234000,
            "comment": f"python agent {action} stop",
            "type_time": mt5.ORDER_TIME_GTC,
        }

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Pending order send failed, retcode={result.retcode}, result={result}")
        else:
            print(f"Pending order sent successfully: {action} {self.lot_size} {self.symbol} @ {target_price}")

    def cancel_order(self, ticket):
        request = {"action": mt5.TRADE_ACTION_REMOVE, "order": ticket, "comment": "python agent cancelling"}
        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"Pending order #{ticket} cancelled successfully.")
        else:
            print(f"Failed to cancel pending order #{ticket}, retcode={result.retcode}")

    def close_position(self, position):
        price = mt5.symbol_info_tick(self.symbol).bid if position.type == 0 else mt5.symbol_info_tick(self.symbol).ask
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": position.volume,
            "type": mt5.ORDER_TYPE_SELL if position.type == 0 else mt5.ORDER_TYPE_BUY,
            "position": position.ticket,
            "price": price,
            "deviation": 20,
            "magic": 234000,
            "comment": "closing position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Failed to close position #{position.ticket}, retcode={result.retcode}")
        else:
            print(f"Position #{position.ticket} closed successfully.")

    def _evaluate_bullish_breakout(self, calls, puts, S):
        total_gex = calls['GEX'].sum() + puts['GEX'].sum()
        if total_gex <= 0:
            return False, "GEX Total não é positivo.", None

        gex_above_price = calls[calls['strike'] > S]
        if gex_above_price.empty:
            return False, "Não há strikes com GEX acima do preço.", None
        
        max_gex_strike = gex_above_price.loc[gex_above_price['GEX'].idxmax()]['strike']
        
        total_dex = calls['DEX'].sum() + puts['DEX'].sum()
        if total_dex <= 0:
            return False, "DEX Total não é positivo.", None

        total_charm = calls['Charm'].sum() + puts['Charm'].sum()
        if total_charm <= 0:
            return False, "Charm Total não é positivo.", None

        details = f"Alvo Bullish identificado no strike {max_gex_strike:.2f} (Pico de Gamma)"
        return True, details, max_gex_strike

    def _find_extreme_greeks_strike(self, df, greek_type, price_S, above_price=True, is_positive_extreme=True):
        if df.empty:
            return None, None
        if above_price:
            filtered_df = df[df['strike'] > price_S]
        else:
            filtered_df = df[df['strike'] < price_S]
        if filtered_df.empty:
            return None, None
        idx = filtered_df[greek_type].idxmax() if is_positive_extreme else filtered_df[greek_type].idxmin()
        strike = filtered_df.loc[idx, 'strike']
        value = filtered_df.loc[idx, greek_type]
        if isinstance(strike, pd.Series):
            return strike.iloc[0], value.iloc[0]
        return strike, value

    def _evaluate_bearish_breakout(self, calls, puts, S):
        total_gex = calls['GEX'].sum() + puts['GEX'].sum()
        if total_gex >= 0:
            return False, "GEX Total não é negativo.", None

        all_gex = pd.concat([calls[['strike', 'GEX']], puts[['strike', 'GEX']]])
        strike_max_neg_gex, val_max_neg_gex = self._find_extreme_greeks_strike(all_gex, 'GEX', S, above_price=False, is_positive_extreme=False)
        
        if strike_max_neg_gex is None or val_max_neg_gex > -100: # Threshold
            return False, "Não há gamma negativo significativo abaixo do preço.", None

        total_dex = calls['DEX'].sum() + puts['DEX'].sum()
        if total_dex >= 0:
            return False, "DEX Total não é negativo.", None

        total_charm = calls['Charm'].sum() + puts['Charm'].sum()
        if total_charm >= 0:
            return False, "Charm Total não é negativo.", None

        details = f"Alvo Bearish identificado no strike {strike_max_neg_gex:.2f} (Pico de Gamma Negativo)"
        return True, details, strike_max_neg_gex

    def _evaluate_pullback_top(self, calls, puts, S):
        return False, "Lógica de Pullback Top não implementada para alvo.", None

    def _evaluate_pullback_bottom(self, calls, puts, S):
        return False, "Lógica de Pullback Fundo não implementada para alvo.", None

    def _evaluate_consolidated_market(self, calls, puts, S):
        return False, "Mercado consolidado não define alvo de rompimento.", None

    def _evaluate_gamma_negative_protection(self, calls, puts, S):
        return False, "Setup de proteção não define alvo.", None

    def _get_processed_options_data(self, ticker_for_options_analysis, expiry_date_str):
        if not expiry_date_str:
            return None, None, None, None
        try:
            S = yf.Ticker(ticker_for_options_analysis).history(period="1d")['Close'].iloc[-1]
            if S == 0:
                print(f"Could not retrieve current price for {ticker_for_options_analysis}.")
                return None, None, None, None
            stock = yf.Ticker(ticker_for_options_analysis)
            chain = stock.option_chain(expiry_date_str)
            calls, puts = chain.calls, chain.puts
            if calls.empty or puts.empty:
                return None, None, None, None
            risk_free_rate = 0.02
            selected_expiry = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
            today = datetime.today().date()
            t_days = (selected_expiry - today).days
            t = t_days / 365.0 if t_days >= 0 else 0.0001
            processed_calls, processed_puts = compute_and_process_greeks(calls, puts, S, expiry_date_str, risk_free_rate)
            return processed_calls, processed_puts, S, t
        except Exception as e:
            print(f"Error in _get_processed_options_data: {e}")
            return None, None, None, None

    def make_decision(self, ticker, expiry_date_str):
        calls, puts, S, t = self._get_processed_options_data(ticker, expiry_date_str)
        default_response = {"decision": "HOLD", "setups": {}, "target_price": None}
        if calls is None or puts is None:
            print("Não foi possível obter dados de opções para tomar uma decisão.")
            return default_response

        setups = {
            'bullish_breakout': self._evaluate_bullish_breakout(calls, puts, S),
            'bearish_breakout': self._evaluate_bearish_breakout(calls, puts, S),
            'pullback_top': self._evaluate_pullback_top(calls, puts, S),
            'pullback_bottom': self._evaluate_pullback_bottom(calls, puts, S),
            'consolidated_market': self._evaluate_consolidated_market(calls, puts, S),
            'gamma_negative_protection': self._evaluate_gamma_negative_protection(calls, puts, S),
        }

        setups_status = {k: {"active": v[0], "details": v[1]} for k, v in setups.items()}
        target_price = None
        decision = "HOLD"

        if setups['bullish_breakout'][0]:
            decision = "BUY"
            target_price = setups['bullish_breakout'][2]
        elif setups['bearish_breakout'][0]:
            decision = "SELL"
            target_price = setups['bearish_breakout'][2]
        
        return {"decision": decision, "setups": setups_status, "target_price": target_price}

    def is_trading_hours(self):
        ny_timezone = pytz.timezone('America/New_York')
        current_time_ny = datetime.now(ny_timezone)
        if not (0 <= current_time_ny.weekday() <= 4):
            return False
        market_open = datetime_time(9, 30, 0)
        market_close = datetime_time(16, 0, 0)
        return market_open <= current_time_ny.time() < market_close

    def get_nearest_expiry(self):
        return self.nearest_expiry

    def get_account_balance(self):
        account_info = mt5.account_info()
        return account_info.balance if account_info else 0.0

    def get_total_profit_loss(self):
        total_pnl = 0.0
        positions = mt5.positions_get()
        if positions:
            for position in positions:
                total_pnl += position.profit
        return total_pnl

    def get_active_positions(self):
        positions = mt5.positions_get()
        active_positions_data = []
        if positions:
            for pos in positions:
                active_positions_data.append({
                    "Symbol": pos.symbol,
                    "Type": "BUY" if pos.type == 0 else "SELL",
                    "Quantity": pos.volume,
                    "Average Price": pos.price_open,
                    "P&L": pos.profit
                })
        return active_positions_data

    def get_active_positions_count(self):
        return mt5.positions_total()

    def get_win_rate(self):
        return 75.0

    def shutdown(self):
        print("Shutting down Agent System.")
        mt5.shutdown()

    def is_mt5_connected(self):
        return mt5.terminal_info() is not None
