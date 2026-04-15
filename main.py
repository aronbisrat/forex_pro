import flet as ft
import yfinance as yf
import pandas as pd
import numpy as np
import os

# --- IMPORT THE CONVERTED LOGIC FILES ---
try:
    import USD_logic, GBP_logic, EUR_logic, CNY_logic, JPY_logic
    logic_map = {
        "USD": USD_logic,
        "GBP": GBP_logic,
        "EUR": EUR_logic,
        "CNY": CNY_logic,
        "JPY": JPY_logic
    }
except ImportError as e:
    print(f"Logic Import Error: {e}")
    logic_map = {}

# --- UI COMPONENTS ---
curr_dropdown = ft.Dropdown(
    label="Currency",
    options=[
        ft.dropdown.Option("USD"), ft.dropdown.Option("GBP"), 
        ft.dropdown.Option("EUR"), ft.dropdown.Option("CNY"), 
        ft.dropdown.Option("JPY")
    ],
    value="USD",
)
amount_input = ft.TextField(label="Amount", value="100", keyboard_type=ft.KeyboardType.NUMBER)
rate_display = ft.Text("--- ETB", size=40, weight="bold")
pred_7d = ft.Text("Next Week: --", size=16, color="green", weight="bold")
pred_15d = ft.Text("In 2 Weeks: --", size=16, color="blue")
pred_30d = ft.Text("In 1 Month: --", size=16, color="purple")

def main(page: ft.Page):
    page.title = "Ethio-Forex AI Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 400
    page.window_height = 750
    page.scroll = "auto"

    def get_prediction(e):
        user_choice = curr_dropdown.value
        ticker_str = f"{user_choice}ETB=X"
        
        page.splash = ft.ProgressBar()
        page.update()

        data = None
        # --- RETRY LOOP (Solves the 'First Click' / NoneType error) ---
        for attempt in range(3):
            try:
                data = yf.download(ticker_str, period="40d", interval="1d", progress=False, auto_adjust=True)
                if data is not None and not data.empty:
                    break
            except Exception:
                continue

        try:
            if data is None or data.empty:
                pred_7d.value = "Market Busy. Click Again."
                page.splash = None
                page.update()
                return

            # Handle MultiIndex Columns
            if isinstance(data.columns, pd.MultiIndex):
                prices = data['Close'][ticker_str].dropna()
            else:
                prices = data['Close'].dropna()
            
            cp = float(prices.iloc[-1])
            yp = float(prices.iloc[-2])
            m7 = float(prices.tail(7).mean())
            m30 = float(prices.tail(30).mean())

            rate_display.value = f"{cp:.2f} ETB"

            if user_choice in logic_map:
                results = logic_map[user_choice].score([cp, yp, m7, m30])
                
                # Safety for float vs list
                if isinstance(results, (list, np.ndarray, tuple)):
                    v7, v15, v30 = results[0], results[1], results[2]
                else:
                    v7 = v15 = v30 = results

                amt = float(amount_input.value) if amount_input.value else 0
                pred_7d.value = f"Next Week: {(v7 * amt):,.2f} ETB"
                pred_15d.value = f"In 2 Weeks: {(v15 * amt):,.2f} ETB"
                pred_30d.value = f"In 1 Month: {(v30 * amt):,.2f} ETB"

        except Exception as ex:
            pred_7d.value = f"Error: {str(ex)}"
        
        page.splash = None
        page.update()

    page.add(
        ft.Text("Ethio-Forex AI", size=25, weight="bold", color="amber"),
        ft.Divider(),
        ft.Column([ft.Text("Live Market Rate", size=12), rate_display], horizontal_alignment="center"),
        curr_dropdown,
        amount_input,
        ft.FilledButton("Generate Forecast", on_click=get_prediction, width=400, style=ft.ButtonStyle(bgcolor="amber", color="black")),
        ft.Divider(),
        ft.Column([pred_7d, pred_15d, pred_30d], spacing=15)
    )

if __name__ == "__main__":
    ft.run(main)