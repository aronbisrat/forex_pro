import flet as ft
import requests  # Stable alternative to yfinance
import joblib
import os

def main(page: ft.Page):
    page.title = "Ethio-Forex AI"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 400
    page.window_height = 800

    rate_display = ft.Text("--- ETB", size=45, weight="bold")
    pred_label = ft.Text("Ready", italic=True, color="grey")

    curr_dropdown = ft.Dropdown(
        label="Currency",
        options=[ft.dropdown.Option("USD"), ft.dropdown.Option("GBP"), ft.dropdown.Option("EUR")],
        value="USD",
    )
    
    amount_input = ft.TextField(label="Amount", value="100")

    def get_prediction(e):
        page.splash = ft.ProgressBar() 
        page.update()

        try:
            # Using a reliable free API instead of Yahoo Finance
            base_url = f"https://open.er-api.com/v6/latest/{curr_dropdown.value}"
            response = requests.get(base_url)
            data = response.json()

            if response.status_code == 200:
                # ETB rate is in the 'rates' dictionary
                current_val = data['rates'].get('ETB')
                rate_display.value = f"{current_val:.2f} ETB"
                
                model_file = f"assets/{choice}_model.pkl"
                if os.path.exists(model_file):
                    # For prediction, we use the live rate as the 'current' feature
                    model = joblib.load(model_file)
                    # Simple dummy features since we can't get history easily without yfinance
                    # Use current value for all inputs just to see the app work
                    features = [[current_val, current_val, current_val, current_val]]
                    prediction = model.predict(features)[0]
                    final_rate = prediction[0] if hasattr(prediction, "__len__") else prediction
                    total = float(amount_input.value) * final_rate
                    pred_label.value = f"Next Week Estimate: {total:,.2f} ETB"
                    pred_label.color = "green"
                else:
                    pred_label.value = "Model file missing. Prediction simulated."
            else:
                pred_label.value = "API Error: Could not fetch rate."
        
        except Exception as ex:
            pred_label.value = f"Error: {str(ex)}"
        
        page.splash = None 
        page.update()

    btn = ft.Container(
        content=ft.Text("Predict Rate", color="black", weight="bold"),
        bgcolor="amber", padding=15, border_radius=10, on_click=get_prediction
    )

    page.add(
        ft.Text("Ethio-Forex AI", size=24, weight="bold"),
        ft.Card(content=ft.Container(content=rate_display, padding=30, alignment=ft.Alignment(0,0))),
        curr_dropdown,
        amount_input,
        ft.Container(height=10),
        btn,
        ft.Container(content=pred_label, padding=20)
    )

if __name__ == "__main__":
    # FIX: Using .run() instead of .app() to clear the warning
    ft.run(main)