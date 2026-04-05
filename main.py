import flet as ft
import yfinance as yf
import pandas as pd
import joblib
import numpy as np
import os
import sys

# --- GLOBAL UI COMPONENTS ---
curr_dropdown = ft.Dropdown(
    label="Currency",
    options=[ft.dropdown.Option("USD"), ft.dropdown.Option("GBP"), ft.dropdown.Option("EUR")],
    value="USD",
)
amount_input = ft.TextField(label="Amount", value="100", keyboard_type=ft.KeyboardType.NUMBER)
rate_display = ft.Text("--- ETB", size=40, weight="bold")

# Three separate labels for your three Kaggle targets
pred_7d = ft.Text("Next Week: --", size=16, color="green", weight="bold")
pred_15d = ft.Text("In 2 Weeks: --", size=16, color="blue")
pred_30d = ft.Text("In 1 Month: --", size=16, color="purple")

def get_resource_path(relative_path):
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main(page: ft.Page):
    page.title = "Ethio-Forex AI Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20

    def get_prediction(e):
        print("Fetching Multi-Output Forecast...")
        user_choice = curr_dropdown.value
        ticker = f"{user_choice}ETB=X"
        model_name = f"{user_choice}_model.pkl"
        model_path = get_resource_path(os.path.join("assets", model_name))

        page.splash = ft.ProgressBar()
        page.update()

        try:
            # 1. Fetch data for feature engineering
            data = yf.download(ticker, period="40d", interval="1d", progress=False)
            
            if not data.empty and os.path.exists(model_path):
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = data.columns.get_level_values(0)
                
                prices = data['Close'].dropna()
                
                # --- MATCH KAGGLE FEATURES ---
                cp = float(prices.iloc[-1])   # 'Close'
                yp = float(prices.iloc[-2])   # 'Yesterday'
                m7 = float(prices.tail(7).mean())   # 'MA_7'
                m30 = float(prices.tail(30).mean()) # 'MA_30'

                rate_display.value = f"{cp:.2f} ETB"

                # 2. Predict all 3 targets in one jump
                model = joblib.load(model_path)
                features = pd.DataFrame([[cp, yp, m7, m30]], 
                                     columns=['Close', 'Yesterday', 'MA_7', 'MA_30'])
                
                # Kaggle model returns [Week, 2-Weeks, 1-Month]
                prediction_raw = model.predict(features)
                results = np.ravel(prediction_raw) 

                user_amount = float(amount_input.value) if amount_input.value else 0
                
                # 3. Update the UI with the Multi-Output results
                pred_7d.value = f"Next Week: {(results[0] * user_amount):,.2f} ETB"
                pred_15d.value = f"In 2 Weeks: {(results[1] * user_amount):,.2f} ETB"
                pred_30d.value = f"In 1 Month: {(results[2] * user_amount):,.2f} ETB"
            else:
                pred_7d.value = "Data or Model error."

        except Exception as ex:
            print(f"Error: {ex}")
            pred_7d.value = "Forecast Failed"
        
        page.splash = None
        page.update()

    # --- UI LAYOUT ---
    page.add(
        ft.Text("Ethio-Forex AI", size=25, weight="bold", color="amber"),
        ft.Container(
            content=ft.Column([
                ft.Text("Live Rate", size=12, color="grey"),
                rate_display
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=10
        ),
        curr_dropdown,
        amount_input,
        ft.FilledButton(
            "Generate Forecast", 
            on_click=get_prediction,
            style=ft.ButtonStyle(bgcolor="amber", color="black")
        ),
        ft.Divider(),
        ft.Column([
            pred_7d,
            pred_15d,
            pred_30d
        ], spacing=10)
    )

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")