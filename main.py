def get_prediction(e):
        user_choice = curr_dropdown.value
        ticker_str = f"{user_choice}ETB=X"
        
        page.splash = ft.ProgressBar()
        page.update()

        data = None
        # --- RETRY LOOP: Fixes the 'NoneType' error on first click ---
        for attempt in range(3):
            try:
                # auto_adjust=True is critical for 2026 yfinance stability
                data = yf.download(ticker_str, period="40d", interval="1d", progress=False, auto_adjust=True, timeout=15)
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

            # Handle potential MultiIndex columns in new yfinance versions
            if isinstance(data.columns, pd.MultiIndex):
                prices = data['Close'][ticker_str].dropna()
            else:
                prices = data['Close'].dropna()
            
            # Features
            cp = float(prices.iloc[-1])
            yp = float(prices.iloc[-2])
            m7 = float(prices.tail(7).mean())
            m30 = float(prices.tail(30).mean())

            rate_display.value = f"{cp:.2f} ETB"

            # Run Logic
            selected_logic = logic_map[user_choice]
            results = selected_logic.score([cp, yp, m7, m30])

            # Safety check for result type
            if isinstance(results, (list, np.ndarray, tuple)):
                v7, v15, v30 = results[0], results[1], results[2]
            else:
                v7 = v15 = v30 = results

            user_amount = float(amount_input.value) if amount_input.value else 0
            pred_7d.value = f"Next Week: {(v7 * user_amount):,.2f} ETB"
            pred_15d.value = f"In 2 Weeks: {(v15 * user_amount):,.2f} ETB"
            pred_30d.value = f"In 1 Month: {(v30 * user_amount):,.2f} ETB"

        except Exception as ex:
            print(f"Error: {ex}")
            pred_7d.value = "Logic Error. Retry."
        
        page.splash = None
        page.update()