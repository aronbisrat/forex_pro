import flet as ft
import yfinance as yf
import pandas as pd
import numpy as np
import os
import sys

# --- IMPORT THE CONVERTED LOGIC FILES ---
# Ensure USD_logic.py, GBP_logic.py, etc., are in the same folder as this script
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
    print(f"Error: Missing logic files! {e}")
    logic_map = {}

# --- GLOBAL UI COMPONENTS ---
curr_dropdown = ft.Dropdown(
    label="Currency",
    options=[
        ft.dropdown.Option("USD"), 
        ft.dropdown.Option("GBP"), 
        ft.dropdown.Option("EUR"), 
        ft.dropdown.Option("CNY"), 
        ft.dropdown.Option("JPY")
    ],
    value="USD",
)
amount_input = ft.TextField(label="Amount", value="100", keyboard_type=ft.KeyboardType.NUMBER)
rate_display = ft.Text("--- ETB", size=40, weight="bold")

# Prediction Labels
pred_7d = ft.Text("Next Week: --", size=16, color="green", weight="bold")
pred_15d = ft.Text("In 2 Weeks: --", size=16, color="blue")
pred_30d = ft.Text("In 1 Month: --", size=16, color="purple")

def main(page: ft.Page):
    page.title = "Ethio-Forex AI Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.window_width = 400
    page.window_height = 700

    def get_prediction(e):
        user_choice = curr_dropdown.value
        ticker = f"{user_choice}ETB=X"
        
        # UI Feedback
        page.splash = ft.ProgressBar()
        page.update()

        try:
            # 1. Fetch live data for features
            data = yf.download(ticker, period="40d", interval="1d", progress=False)
            
            if not data.empty and user_choice in logic_map:
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = data.columns.get_level_values(0)
                
                prices = data['Close'].dropna()
                
                # Features: [Close, Yesterday, MA_7, MA_30]
                cp = float(prices.iloc[-1])
                yp = float(prices.iloc[-2])
                m7 = float(prices.tail(7).mean())
                m30 = float(prices.tail(30).mean())

                rate_display.value = f"{cp:.2f} ETB"

                # 2. Run the logic
                selected_logic = logic_map[user_choice]
                features = [cp, yp, m7, m30]
                results = selected_logic.score(features)

                # --- SAFETY CHECK: HANDLE FLOAT VS LIST ---
                if isinstance(results, (list, np.ndarray, tuple)):
                    val_7d, val_15d, val_30d = results[0], results[1], results[2]
                else:
                    # If model only predicted 1 day, use it as base
                    val_7d = results
                    val_15d = results
                    val_30d = results

                user_amount = float(amount_input.value) if amount_input.value else 0
                
                # Update UI
                pred_7d.value = f"Next Week: {(val_7d * user_amount):,.2f} ETB"
                pred_15d.value = f"In 2 Weeks: {(val_15d * user_amount):,.2f} ETB"
                pred_30d.value = f"In 1 Month: {(val_30d * user_amount):,.2f} ETB"
            else:
                pred_7d.value = "Data/Logic Missing"

        except Exception as ex:
            print(f"Error: {ex}")
            pred_7d.value = f"Error: {str(ex)}"
        
        page.splash = None
        page.update()

    # --- UI LAYOUT ---
    page.add(
        ft.Text("Ethio-Forex AI", size=25, weight="bold", color="amber"),
        ft.Divider(),
        ft.Container(
            content=ft.Column([
                ft.Text("Current Market Rate", size=12, color="grey"),
                rate_display
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=10
        ),
        curr_dropdown,
        amount_input,
        ft.FilledButton(
            "Generate Forecast", 
            on_click=get_prediction,
            width=page.window_width,
            style=ft.ButtonStyle(bgcolor="amber", color="black")
        ),
        ft.Divider(),
        ft.Column([
            pred_7d,
            pred_15d,
            pred_30d
        ], spacing=15)
    )

if __name__ == "__main__":
    # Updated from ft.app to ft.run as per version 0.84.0+
    ft.run(main)