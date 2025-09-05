"""
Cross-Tab Navigator Component for WaveSpeed AI Application

This module provides functionality to send results between different tabs
and automatically navigate to the target tab.
"""

import tkinter as tk
from tkinter import ttk
from core.logger import get_logger
from utils.utils import show_success, show_error, create_temp_file
import tempfile
import os

logger = get_logger()


class CrossTabNavigator:
    """Handles cross-tab navigation and result sharing"""
    
    def __init__(self, main_app):
        self.main_app = main_app
        
    def create_send_to_dropdown(self, parent, result_image, current_tab_name):
        """Create a dropdown button for sending results to other tabs"""
        
        # Get available target tabs based on current tab
        target_tabs = self.get_available_targets(current_tab_name)
        
        if not target_tabs:
            return None
            
        # Create dropdown button
        send_button = ttk.Menubutton(parent, text="📤 Send To...", style="Accent.TButton")
        send_menu = tk.Menu(send_button, tearoff=0)
        send_button.config(menu=send_menu)
        
        # Add menu items for each target tab
        for tab_info in target_tabs:
            tab_id, tab_name, tab_icon = tab_info
            send_menu.add_command(
                label=f"{tab_icon} {tab_name}",
                command=lambda tid=tab_id, tname=tab_name: self.send_to_tab(result_image, tid, tname, current_tab_name)
            )
        
        return send_button
    
    def get_available_targets(self, current_tab_name):
        """Get list of available target tabs based on current tab"""
        
        # Define all tabs with their IDs, names, and icons
        all_tabs = [
            ("editor", "Nano Banana Editor", "🍌"),
            ("seededit", "SeedEdit", "✨"),
            ("upscaler", "Image Upscaler", "🔍"),
            ("video", "Wan 2.2", "🎬"),
            ("seeddance", "SeedDance", "🕺")
        ]
        
        # Define valid targets for each tab type
        target_rules = {
            "editor": ["seededit", "upscaler", "video", "seeddance"],  # Nano Banana can send to all others
            "seededit": ["editor", "upscaler", "video", "seeddance"],  # SeedEdit can send to all others
            "upscaler": ["editor", "seededit", "video", "seeddance"],  # Upscaler can send to all others
            "video": [],  # Video tabs don't produce images to send
            "seeddance": []  # Video tabs don't produce images to send
        }
        
        # Map current tab name to tab ID
        tab_name_to_id = {
            "Nano Banana Editor": "editor",
            "SeedEdit": "seededit", 
            "Image Upscaler": "upscaler",
            "Wan 2.2": "video",
            "SeedDance": "seeddance"
        }
        
        current_tab_id = tab_name_to_id.get(current_tab_name)
        if not current_tab_id:
            return []
            
        # Get valid targets for current tab
        valid_target_ids = target_rules.get(current_tab_id, [])
        
        # Return matching tab info
        return [tab for tab in all_tabs if tab[0] in valid_target_ids]
    
    def send_to_tab(self, result_image, target_tab_id, target_tab_name, source_tab_name):
        """Send result image to target tab and navigate there"""
        
        try:
            # Create temporary file from result image
            temp_path, error = create_temp_file(result_image, f"cross_tab_{target_tab_id}")
            if error:
                show_error("Error", f"Failed to prepare image for transfer: {error}")
                return
            
            # Navigate to target tab and set the image
            success = self.navigate_to_tab_with_image(target_tab_id, temp_path, target_tab_name)
            
            if not success:
                show_error("Navigation Error", f"Failed to navigate to {target_tab_name} tab.")
                
        except Exception as e:
            logger.error(f"Cross-tab navigation error: {e}")
            show_error("Error", f"Failed to send image to {target_tab_name}: {str(e)}")
    
    def navigate_to_tab_with_image(self, target_tab_id, image_path, target_tab_name):
        """Navigate to target tab and set the image"""
        
        try:
            # Get the target tab object
            target_tab = self.get_tab_object(target_tab_id)
            if not target_tab:
                logger.error(f"Target tab not found: {target_tab_id}")
                return False
            
            # Switch to the target tab
            self.switch_to_tab(target_tab_id)
            
            # Set the image in the target tab
            if hasattr(target_tab, 'on_image_selected'):
                target_tab.on_image_selected(image_path)
                logger.info(f"Successfully sent image to {target_tab_name}")
                return True
            else:
                logger.error(f"Target tab {target_tab_name} doesn't support image input")
                return False
                
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            return False
    
    def get_tab_object(self, tab_id):
        """Get the tab object by ID"""
        tab_mapping = {
            "editor": self.main_app.editor_tab,
            "seededit": self.main_app.seededit_tab,
            "upscaler": self.main_app.upscaler_tab,
            "video": self.main_app.video_tab,
            "seeddance": self.main_app.seeddance_tab
        }
        return tab_mapping.get(tab_id)
    
    def switch_to_tab(self, tab_id):
        """Switch to the specified tab"""
        
        # Map tab IDs to notebook tab indices
        tab_indices = {
            "editor": 0,      # Nano Banana Editor
            "seededit": 1,    # SeedEdit  
            "upscaler": 2,    # Image Upscaler
            "video": 3,       # Wan 2.2
            "seeddance": 4    # SeedDance
        }
        
        tab_index = tab_indices.get(tab_id)
        if tab_index is not None and self.main_app.notebook:
            self.main_app.notebook.select(tab_index)
            logger.info(f"Switched to tab: {tab_id} (index {tab_index})")
        else:
            logger.error(f"Invalid tab ID or notebook not available: {tab_id}")


class CrossTabButton:
    """Helper class to create cross-tab sharing buttons"""
    
    @staticmethod
    def create_send_button(parent, main_app, result_image, current_tab_name):
        """Create a 'Send To' button with dropdown menu"""
        
        if not main_app or not result_image:
            return None
            
        navigator = CrossTabNavigator(main_app)
        return navigator.create_send_to_dropdown(parent, result_image, current_tab_name)
    
    @staticmethod
    def update_send_button(send_button, main_app, result_image, current_tab_name):
        """Update existing send button with new result image"""
        
        if not send_button or not main_app or not result_image:
            return
            
        # Enable the button
        send_button.config(state="normal")
        
        # Update the menu commands with new result image
        navigator = CrossTabNavigator(main_app)
        menu = send_button['menu']
        
        # Clear existing menu
        menu.delete(0, 'end')
        
        # Recreate menu with updated image
        target_tabs = navigator.get_available_targets(current_tab_name)
        for tab_info in target_tabs:
            tab_id, tab_name, tab_icon = tab_info
            menu.add_command(
                label=f"{tab_icon} {tab_name}",
                command=lambda tid=tab_id, tname=tab_name: navigator.send_to_tab(result_image, tid, tname, current_tab_name)
            )
