"""
Balance Indicator Component for WaveSpeed AI Application

This module provides a balance indicator widget that displays the user's account balance
in the top corner of the application.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from core.logger import get_logger
from utils.utils import show_error

logger = get_logger()


class BalanceIndicator:
    """Balance indicator widget for displaying account balance"""
    
    def __init__(self, parent, api_client):
        self.parent = parent
        self.api_client = api_client
        self.balance = None
        self.update_thread = None
        self.should_update = True
        self.last_update = 0
        self.update_interval = 300  # 5 minutes between updates
        self._updates_started = False
        
        self.setup_ui()
        # Don't start updates immediately - wait for main loop to be ready
        # self.start_balance_updates() will be called after mainloop starts
    
    def setup_ui(self):
        """Setup the balance indicator UI"""
        # Create main frame
        self.frame = ttk.Frame(self.parent)
        
        # Balance display frame with border
        self.balance_frame = ttk.Frame(self.frame, style="Card.TFrame")
        self.balance_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Balance icon and text
        balance_container = ttk.Frame(self.balance_frame)
        balance_container.pack(fill=tk.X, padx=8, pady=4)
        
        # Icon
        self.icon_label = ttk.Label(balance_container, text="💰", font=('Arial', 12))
        self.icon_label.pack(side=tk.LEFT)
        
        # Balance amount
        self.balance_label = ttk.Label(
            balance_container, 
            text="Loading...", 
            font=('Arial', 10, 'bold'),
            foreground='#2E7D32'  # Green color for balance
        )
        self.balance_label.pack(side=tk.LEFT, padx=(4, 0))
        
        # Refresh button (small)
        self.refresh_button = ttk.Button(
            balance_container,
            text="🔄",
            width=3,
            command=self.refresh_balance
        )
        self.refresh_button.pack(side=tk.RIGHT)
        
        # Last updated info (smaller text)
        self.update_info_label = ttk.Label(
            self.balance_frame,
            text="",
            font=('Arial', 8),
            foreground='#666666'
        )
        self.update_info_label.pack(pady=(0, 2))
    
    def start_balance_updates(self):
        """Start automatic balance updates"""
        if not self._updates_started and (self.update_thread is None or not self.update_thread.is_alive()):
            self._updates_started = True
            self.should_update = True
            self.update_thread = threading.Thread(target=self._balance_update_loop, daemon=True)
            self.update_thread.start()
            logger.info("Balance updates started")
    
    def stop_balance_updates(self):
        """Stop automatic balance updates"""
        self.should_update = False
    
    def _balance_update_loop(self):
        """Background loop for updating balance"""
        # Initial update
        self.update_balance()
        
        while self.should_update:
            try:
                time.sleep(10)  # Check every 10 seconds
                current_time = time.time()
                
                # Only update if enough time has passed
                if current_time - self.last_update >= self.update_interval:
                    self.update_balance()
                    
            except Exception as e:
                logger.error(f"Balance update loop error: {e}")
                time.sleep(30)  # Wait longer on error
    
    def update_balance(self):
        """Update balance from API"""
        def _update_in_background():
            try:
                balance, error = self.api_client.get_balance()
                
                # Update UI in main thread - check if parent still exists
                try:
                    self.parent.after(0, lambda: self._update_balance_ui(balance, error))
                except (RuntimeError, tk.TclError) as e:
                    if "main thread is not in main loop" in str(e) or "application has been destroyed" in str(e):
                        logger.debug("Skipping balance UI update - main loop not ready yet")
                    else:
                        raise
                
            except Exception as e:
                logger.error(f"Balance update error: {e}")
                try:
                    self.parent.after(0, lambda: self._update_balance_ui(None, str(e)))
                except (RuntimeError, tk.TclError) as e:
                    if "main thread is not in main loop" in str(e) or "application has been destroyed" in str(e):
                        logger.debug("Skipping balance error UI update - main loop not ready yet")
                    else:
                        raise
        
        # Run in background thread
        threading.Thread(target=_update_in_background, daemon=True).start()
    
    def _update_balance_ui(self, balance, error):
        """Update balance UI (must be called from main thread)"""
        try:
            current_time = time.time()
            self.last_update = current_time
            
            if balance is not None:
                self.balance = balance
                
                # Format balance nicely
                if balance >= 1000:
                    balance_text = f"${balance:,.2f}"
                elif balance >= 1:
                    balance_text = f"${balance:.2f}"
                else:
                    balance_text = f"${balance:.4f}"
                
                self.balance_label.config(text=balance_text, foreground='#2E7D32')
                
                # Update timestamp
                time_str = time.strftime("%H:%M", time.localtime(current_time))
                self.update_info_label.config(text=f"Updated: {time_str}")
                
                # Change icon based on balance level
                if balance > 50:
                    self.icon_label.config(text="💰")  # Full wallet
                elif balance > 10:
                    self.icon_label.config(text="💵")  # Money
                elif balance > 1:
                    self.icon_label.config(text="🪙")  # Coin
                else:
                    self.icon_label.config(text="⚠️")  # Warning - low balance
                    self.balance_label.config(foreground='#D32F2F')  # Red for low balance
                
            else:
                # Error state
                self.balance_label.config(text="Error", foreground='#D32F2F')
                self.icon_label.config(text="❌")
                self.update_info_label.config(text=f"Error: {error[:30]}..." if error and len(error) > 30 else f"Error: {error}")
                
        except Exception as e:
            logger.error(f"Balance UI update error: {e}")
    
    def refresh_balance(self):
        """Manually refresh balance"""
        # Disable button temporarily
        self.refresh_button.config(state="disabled", text="⏳")
        
        def _enable_button():
            try:
                self.refresh_button.config(state="normal", text="🔄")
            except:
                pass  # Widget might be destroyed
        
        # Re-enable button after 2 seconds
        self.parent.after(2000, _enable_button)
        
        # Force update
        self.last_update = 0  # Reset to force immediate update
        self.update_balance()
    
    def get_frame(self):
        """Get the main frame widget"""
        return self.frame
    
    def destroy(self):
        """Clean up resources"""
        self.stop_balance_updates()
        if self.frame:
            self.frame.destroy()


class BalanceIndicatorMixin:
    """Mixin to add balance indicator to any window"""
    
    def setup_balance_indicator(self, api_client, position="top"):
        """Setup balance indicator in the window"""
        if not hasattr(self, 'balance_indicator'):
            if position == "top":
                # Add to top of the window
                self.balance_indicator = BalanceIndicator(self.root, api_client)
                self.balance_indicator.get_frame().pack(side=tk.TOP, fill=tk.X, before=self.notebook if hasattr(self, 'notebook') else None)
            else:
                # Add to specified parent
                self.balance_indicator = BalanceIndicator(position, api_client)
        
        return self.balance_indicator
    
    def cleanup_balance_indicator(self):
        """Clean up balance indicator"""
        if hasattr(self, 'balance_indicator'):
            self.balance_indicator.destroy()
            delattr(self, 'balance_indicator')
