import tkinter 
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading

class CryptoConverter:
    
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title("Crypto Converter")
        self.root.geometry("1000x700")
        self.root.resizable(1, 1)
        
        # Cryptocurrencies list
        self.cryptos = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'BNB': 'binancecoin',
            'XRP': 'ripple',
            'ADA': 'cardano',
            'DOGE': 'dogecoin',
            'LTC': 'litecoin',
            'SOL': 'solana',
            'USDT': 'tether',
            'USDC': 'usd-coin'
        }
        
        # Currencies list
        self.currencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'INR', 'UAH', 'RUB']
        
        self.create_widgets()
        self.root.mainloop()
        
    def create_widgets(self):
        # Title
        title_label = ttk.Label(self.root, text="Крипто-Конвертер", font=("Helvetica", 16, "bold"))
        title_label.grid(column=0, row=0, columnspan=2, padx=10, pady=10)
        
        # Left panel for controls
        left_frame = ttk.Frame(self.root)
        left_frame.grid(column=0, row=1, columnspan=1, padx=10, pady=10, sticky="nsew")
        
        # Crypto selection
        ttk.Label(left_frame, text="Вибрати крипто:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.crypto_var = tkinter.StringVar(value="BTC")
        crypto_menu = ttk.Combobox(left_frame, textvariable=self.crypto_var, 
                                    values=list(self.cryptos.keys()), state="readonly", width=20)
        crypto_menu.pack(fill="x", pady=(0, 15))
        crypto_menu.bind("<<ComboboxSelected>>", lambda e: self.on_crypto_change())
        
        # Amount input
        ttk.Label(left_frame, text="Кількість:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.amount_entry = ttk.Entry(left_frame, width=25)
        self.amount_entry.insert(0, "1")
        self.amount_entry.pack(fill="x", pady=(0, 15))
        
        # Target currency
        ttk.Label(left_frame, text="До якої валюти:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.to_var = tkinter.StringVar(value="USD")
        to_menu = ttk.Combobox(left_frame, textvariable=self.to_var, 
                               values=self.currencies, state="readonly", width=20)
        to_menu.pack(fill="x", pady=(0, 15))
        
        # Convert button
        convert_button = ttk.Button(left_frame, text="Конвертувати", command=self.convert)
        convert_button.pack(fill="x", pady=10)
        
        # Info panel
        ttk.Label(left_frame, text="Інформація про курс:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(15, 5))
        self.info_text = scrolledtext.ScrolledText(left_frame, height=15, width=40, state="disabled")
        self.info_text.pack(fill="both", expand=True, pady=(0, 10))
        
        # Right panel for chart
        self.chart_frame = ttk.Frame(self.root)
        self.chart_frame.grid(column=1, row=1, padx=10, pady=10, sticky="nsew")
        
        ttk.Label(self.chart_frame, text="Графік ціни (7 днів)", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 5))
        
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(1, weight=1)
        
        # Load initial data
        self.load_crypto_info()
        
    def on_crypto_change(self):
        """Called when crypto selection changes"""
        self.load_crypto_info()
        self.show_chart()
        
    def load_crypto_info(self):
        """Load crypto information in background thread"""
        thread = threading.Thread(target=self._fetch_crypto_info)
        thread.daemon = True
        thread.start()
        
    def _fetch_crypto_info(self):
        """Fetch cryptocurrency information"""
        try:
            crypto_id = self.cryptos[self.crypto_var.get()]
            # Support all currencies
            all_currencies = ','.join([c.lower() for c in self.currencies])
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies={all_currencies}&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true"
            
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if crypto_id in data:
                crypto_data = data[crypto_id]
                
                # Update info text
                self.info_text.config(state="normal")
                self.info_text.delete(1.0, "end")
                
                crypto_symbol = self.crypto_var.get()
                price_usd = crypto_data.get('usd', 0)
                price_eur = crypto_data.get('eur', 0)
                price_gbp = crypto_data.get('gbp', 0)
                change_24h = crypto_data.get('usd_24h_change', 0)
                market_cap = crypto_data.get('usd_market_cap', 0)
                volume = crypto_data.get('usd_24h_vol', 0)
                
                # Currency symbols
                symbols = {'usd': '$', 'eur': '€', 'gbp': '£', 'jpy': '¥', 'aud': 'A$', 
                          'cad': 'C$', 'chf': 'CHF', 'cny': '¥', 'inr': '₹', 'uah': '₴', 'rub': '₽'}
                
                info = f"{crypto_symbol}\n"
                info += f"{'='*35}\n\n"
                info += f"Ціна за 1 {crypto_symbol}:\n"
                info += f"  USD: ${price_usd:,.2f}\n"
                info += f"  EUR: €{price_eur:,.2f}\n"
                info += f"  GBP: £{price_gbp:,.2f}\n"
                
                # Add prices for all selected currencies
                if price_usd > 0:  # Only show other currencies if we have valid data
                    info += f"  JPY: ¥{crypto_data.get('jpy', 0):,.0f}\n"
                    info += f"  UAH: ₴{crypto_data.get('uah', 0):,.2f}\n\n"
                else:
                    info += "\n"
                info += f"Зміна за 24г: {change_24h:+.2f}%\n\n"
                info += f"Ринкова капіталізація: ${market_cap:,.0f}\n\n"
                info += f"Об'єм торговлі (24г): ${volume:,.0f}\n"
                
                self.info_text.insert(1.0, info)
                self.info_text.config(state="disabled")
                
        except Exception as e:
            self.info_text.config(state="normal")
            self.info_text.delete(1.0, "end")
            self.info_text.insert(1.0, f"Помилка: {str(e)}")
            self.info_text.config(state="disabled")
        
        # Show chart after loading info
        self.show_chart()
        
    def convert(self):
        """Convert cryptocurrency to target currency"""
        try:
            amount = float(self.amount_entry.get())
            crypto_id = self.cryptos[self.crypto_var.get()]
            target_currency = self.to_var.get().lower()
            
            # Fetch current rate for the selected currency
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies={target_currency}"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if crypto_id not in data:
                messagebox.showerror("Помилка", f"Не можу отримати дані для {crypto_id}")
                return
                
            crypto_data = data[crypto_id]
            
            if target_currency not in crypto_data:
                messagebox.showerror("Помилка", f"Валюта {target_currency.upper()} не підтримується або недоступна")
                return
            
            rate = crypto_data.get(target_currency, 0)
            
            if rate == 0:
                messagebox.showerror("Помилка", f"Не можу отримати курс для {target_currency.upper()}")
                return
                
            result = amount * rate
            crypto_symbol = self.crypto_var.get()
            
            # Format the result based on currency
            if target_currency in ['usd']:
                formatted_result = f"${result:,.2f}"
            elif target_currency in ['eur']:
                formatted_result = f"€{result:,.2f}"
            elif target_currency in ['gbp']:
                formatted_result = f"£{result:,.2f}"
            elif target_currency in ['jpy', 'cny']:
                formatted_result = f"{result:,.0f}"
            elif target_currency in ['uah']:
                formatted_result = f"₴{result:,.2f}"
            else:
                formatted_result = f"{result:,.2f}"
            
            message = f"{amount} {crypto_symbol} = {formatted_result} {self.to_var.get()}\n\n"
            message += f"Курс обміну: 1 {crypto_symbol} = {rate:,.2f} {self.to_var.get()}"
            
            messagebox.showinfo("Результат конверсії", message)
            
        except ValueError:
            messagebox.showerror("Помилка", "Будь ласка, введіть коректну кількість")
        except requests.exceptions.Timeout:
            messagebox.showerror("Помилка", "Час очікування на відповідь був перевищений. Спробуйте ще раз.")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Помилка", "Проблема з інтернет-з'єднанням. Перевірте з'єднання.")
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка при конверсії: {str(e)}")
            
    def show_chart(self):
        """Display price chart for the last 7 days"""
        thread = threading.Thread(target=self._fetch_chart_data)
        thread.daemon = True
        thread.start()
        
    def _fetch_chart_data(self):
        """Fetch historical data and display chart"""
        try:
            crypto_id = self.cryptos[self.crypto_var.get()]
            crypto_symbol = self.crypto_var.get()
            
            # Fetch historical data
            url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart?vs_currency=usd&days=7&interval=daily"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if 'prices' not in data:
                print(f"Помилка: Немає даних про ціни для {crypto_symbol}")
                return
                
            prices = data['prices']
            
            if not prices or len(prices) == 0:
                print(f"Помилка: Порожній список цін для {crypto_symbol}")
                return
            
            # Prepare data
            dates = [datetime.fromtimestamp(p[0]/1000).strftime('%d.%m') for p in prices]
            values = [p[1] for p in prices]
            
            # Clear previous chart
            for widget in self.chart_frame.winfo_children()[1:]:
                widget.destroy()
            
            # Create new figure
            fig = Figure(figsize=(5, 5), dpi=100)
            ax = fig.add_subplot(111)
            
            # Plot data with color coding for up and down movements
            x_pos = range(len(values))
            
            # Draw colored segments based on price direction
            for i in range(len(values) - 1):
                if values[i+1] >= values[i]:
                    # Price went up - green
                    color = '#22c55e'  # Green
                    ax.plot([i, i+1], [values[i], values[i+1]], marker='o', 
                           linewidth=3, markersize=7, color=color)
                else:
                    # Price went down - red
                    color = '#ef4444'  # Red
                    ax.plot([i, i+1], [values[i], values[i+1]], marker='o', 
                           linewidth=3, markersize=7, color=color)
            
            # Add the last marker
            if len(values) > 0:
                ax.plot(len(values)-1, values[-1], marker='o', markersize=7, color='#3b82f6')
            
            # Fill areas under the curve with gradient effect
            for i in range(len(values) - 1):
                if values[i+1] >= values[i]:
                    ax.fill_between([i, i+1], 0, [values[i], values[i+1]], 
                                   alpha=0.2, color='#22c55e')
                else:
                    ax.fill_between([i, i+1], 0, [values[i], values[i+1]], 
                                   alpha=0.2, color='#ef4444')
            
            ax.set_xticks(x_pos)
            ax.set_xticklabels(dates, rotation=45)
            ax.set_title(f'Ціна {crypto_symbol} (останні 7 днів)', fontsize=12, fontweight='bold')
            ax.set_xlabel('Дата', fontsize=10)
            ax.set_ylabel('Ціна (USD)', fontsize=10)
            ax.grid(True, alpha=0.3, linestyle='--')
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            print(f"✓ Графік для {crypto_symbol} успішно завантажений")
                
        except requests.exceptions.Timeout:
            print(f"Помилка: Час очікування для {crypto_symbol} перевищений")
        except requests.exceptions.ConnectionError:
            print(f"Помилка: Проблема з з'єднанням для {crypto_symbol}")
        except ValueError as e:
            print(f"Помилка: Помилка обробки даних для {crypto_symbol}: {str(e)}")
        except Exception as e:
            print(f"Помилка при завантаженні графіка для {crypto_symbol}: {str(e)}")
            
if __name__ == "__main__":
    CryptoConverter()
    
    