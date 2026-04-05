import flet as ft
import yfinance as yf
import pandas as pd
import numpy as np
import os

# --- IMPORT THE NEW LOGIC FILES ---
import USD_logic, GBP_logic, EUR_logic, CNY_logic, JPY_logic

# Mapping selection to the imported logic modules
logic_map = {
    "USD": USD_logic,
    "GBP": GBP_logic,
    "EUR": EUR_logic,
    "CNY": CNY_logic,
    "JPY": JPY_logic
}

# --- GLOBAL UI COMPONENTS ---
curr_dropdown = ft.Dropdown(
    label="Currency",
    options=[ft.dropdown.Option("USD"), ft.dropdown.Option("GBP"), ft.dropdown.Option("EUR"), ft.dropdown.Option("CNY"), ft.dropdown.Option("JPY")],
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

    def get_prediction(e):
        user_choice = curr_dropdown.value
        ticker = f"{user_choice}ETB=X"
        
        page.splash = ft.ProgressBar()
        page.update()

        try:
            data = yf.download(ticker, period="40d", interval="1d", progress=False)
            
            if not data.empty:
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = data.columns.get_level_values(0)
                
                prices = data['Close'].dropna()
                cp = float(prices.iloc[-1])
                yp = float(prices.iloc[-2])
                m7 = float(prices.tail(7).mean())
                m30 = float(prices.tail(30).mean())

                rate_display.value = f"{cp:.2f} ETB"

                # --- NEW LOGIC: NO MORE JOBLIB ---
                # We call the .score() function from the converted logic file
                selected_logic = logic_map[user_choice]
                features = [cp, yp, m7, m30] # List format for m2cgen
                
                # The score function returns the [7d, 15d, 30d] list
                results = selected_logic.score(features)

                user_amount = float(amount_input.value) if amount_input.value else 0
                pred_7d.value = f"Next Week: {(results[0] * user_amount):,.2f} ETB"
                pred_15d.value = f"In 2 Weeks: {(results[1] * user_amount):,.2f} ETB"
                pred_30d.value = f"In 1 Month: {(results[2] * user_amount):,.2f} ETB"
            else:
                pred_7d.value = "Data fetch failed."

        except Exception as ex:
            print(f"Error: {ex}")
            pred_7d.value = "Forecast Error"
        
        page.splash = None
        page.update()

    page.add(
        ft.Text("Ethio-Forex AI", size=25, weight="bold", color="amber"),
        curr_dropdown,
        amount_input,
        ft.FilledButton("Generate Forecast", on_click=get_prediction, style=ft.ButtonStyle(bgcolor="amber", color="black")),
        ft.Divider(),
        rate_display,
        ft.Column([pred_7d, pred_15d, pred_30d], spacing=10)
    )

if __name__ == "__main__":
    ft.app(target=main)