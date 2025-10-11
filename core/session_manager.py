"""
Session Manager for WaveSpeed AI Application

Handles saving and loading complete workspace sessions including:
- Both Seedream V4 tabs (images, prompts, settings)
- UI state (zoom, view mode, splitters)
- Recent Results state
- Window state and positions
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from core.logger import get_logger

logger = get_logger()


class SessionManager:
    """Manages complete workspace session save/load"""
    
    def __init__(self, sessions_folder: str = "data/sessions"):
        """
        Initialize session manager
        
        Args:
            sessions_folder: Folder to store session files
        """
        self.sessions_folder = Path(sessions_folder)
        self.sessions_folder.mkdir(parents=True, exist_ok=True)
        logger.info(f"SessionManager initialized - folder: {self.sessions_folder}")
    
    def save_session(self, session_name: str, session_data: Dict[str, Any]) -> bool:
        """
        Save complete workspace session
        
        Args:
            session_name: Name for the session
            session_data: Complete session state dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Sanitize session name for filename
            safe_name = "".join(c for c in session_name if c.isalnum() or c in (' ', '-', '_')).strip()
            if not safe_name:
                safe_name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Add metadata
            session_data['session_name'] = session_name
            session_data['saved_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            session_data['version'] = "1.0"
            
            # Save to file
            filename = f"{safe_name}.json"
            filepath = self.sessions_folder / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Session saved: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return False
    
    def load_session(self, session_name: str) -> Optional[Dict[str, Any]]:
        """
        Load workspace session
        
        Args:
            session_name: Name of the session to load
            
        Returns:
            Session data dictionary or None if failed
        """
        try:
            # Try exact filename first
            filepath = self.sessions_folder / f"{session_name}.json"
            
            if not filepath.exists():
                # Try finding by session name in metadata
                for file in self.sessions_folder.glob("*.json"):
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if data.get('session_name') == session_name:
                                filepath = file
                                break
                    except:
                        continue
            
            if not filepath.exists():
                logger.error(f"Session not found: {session_name}")
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            logger.info(f"✅ Session loaded: {filepath.name}")
            return session_data
            
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            return None
    
    def list_sessions(self) -> list:
        """
        List all available sessions
        
        Returns:
            List of session info dictionaries
        """
        sessions = []
        
        try:
            for filepath in sorted(self.sessions_folder.glob("*.json"), key=os.path.getmtime, reverse=True):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    sessions.append({
                        'filename': filepath.stem,
                        'name': data.get('session_name', filepath.stem),
                        'saved_at': data.get('saved_at', 'Unknown'),
                        'version': data.get('version', '1.0')
                    })
                except Exception as e:
                    logger.debug(f"Could not read session {filepath.name}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error listing sessions: {e}")
        
        return sessions
    
    def delete_session(self, session_name: str) -> bool:
        """
        Delete a session file
        
        Args:
            session_name: Name of session to delete
            
        Returns:
            True if successful
        """
        try:
            filepath = self.sessions_folder / f"{session_name}.json"
            
            if filepath.exists():
                filepath.unlink()
                logger.info(f"✅ Session deleted: {session_name}")
                return True
            else:
                logger.warning(f"Session not found for deletion: {session_name}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return False
    
    def export_session_data(self, main_app) -> Dict[str, Any]:
        """
        Extract complete session data from main application
        
        Args:
            main_app: Reference to main application instance
            
        Returns:
            Complete session state dictionary
        """
        session_data = {
            'window_state': {},
            'tab_1': {},
            'tab_2': {},
            'ui_state': {},
            'recent_results': {}
        }
        
        try:
            # Window state
            if hasattr(main_app, 'root'):
                session_data['window_state'] = {
                    'geometry': main_app.root.geometry(),
                    'state': main_app.root.state()
                }
            
            # Tab 1 state
            if hasattr(main_app, 'seedream_tab_1'):
                session_data['tab_1'] = self._extract_tab_state(main_app.seedream_tab_1)
            
            # Tab 2 state
            if hasattr(main_app, 'seedream_tab_2'):
                session_data['tab_2'] = self._extract_tab_state(main_app.seedream_tab_2)
            
            # UI state (splitters, zoom, view mode)
            if hasattr(main_app, 'seedream_tab_1') and hasattr(main_app.seedream_tab_1, 'improved_layout'):
                layout = main_app.seedream_tab_1.improved_layout
                session_data['ui_state'] = self._extract_ui_state(layout)
            
            # Recent Results state
            if hasattr(main_app, 'recent_results_panel'):
                session_data['recent_results'] = self._extract_recent_results_state(main_app.recent_results_panel)
            
            logger.debug("Session data extracted successfully")
            return session_data
            
        except Exception as e:
            logger.error(f"Error extracting session data: {e}")
            return session_data
    
    def _extract_tab_state(self, tab) -> Dict[str, Any]:
        """Extract state from a Seedream V4 tab"""
        tab_data = {}
        
        try:
            # Image path
            if hasattr(tab, 'improved_layout'):
                layout = tab.improved_layout
                
                # Input image(s)
                if hasattr(layout, 'image_manager') and hasattr(layout.image_manager, 'selected_image_paths'):
                    paths = layout.image_manager.selected_image_paths
                    tab_data['input_images'] = paths if paths else []
                
                # Result image
                if hasattr(layout, 'results_manager') and hasattr(layout.results_manager, 'result_image_path'):
                    tab_data['result_image'] = layout.results_manager.result_image_path
                
                # Prompt
                if hasattr(layout, 'prompt_manager') and hasattr(layout.prompt_manager, 'prompt_text'):
                    try:
                        tab_data['prompt'] = layout.prompt_manager.prompt_text.get("1.0", "end-1c")
                    except:
                        tab_data['prompt'] = ""
                
                # Settings
                if hasattr(layout, 'settings_manager'):
                    settings = layout.settings_manager
                    tab_data['settings'] = {
                        'width': settings.width_var.get() if hasattr(settings, 'width_var') else 1024,
                        'height': settings.height_var.get() if hasattr(settings, 'height_var') else 1024,
                        'seed': settings.seed_var.get() if hasattr(settings, 'seed_var') else -1,
                        'sync_mode': settings.sync_mode_var.get() if hasattr(settings, 'sync_mode_var') else True,
                        'base64_output': settings.base64_output_var.get() if hasattr(settings, 'base64_output_var') else False
                    }
                
                # Zoom level
                if hasattr(layout, 'zoom_var'):
                    tab_data['zoom'] = layout.zoom_var.get()
        
        except Exception as e:
            logger.error(f"Error extracting tab state: {e}")
        
        return tab_data
    
    def _extract_ui_state(self, layout) -> Dict[str, Any]:
        """Extract UI state (view mode, splitters, etc.)"""
        ui_data = {}
        
        try:
            # View mode
            if hasattr(layout, 'comparison_controller'):
                ui_data['view_mode'] = layout.comparison_controller.current_mode
                ui_data['overlay_opacity'] = layout.comparison_controller.overlay_opacity
            
            # Splitter positions (from ui_preferences)
            if hasattr(layout, 'ui_preferences'):
                prefs = layout.ui_preferences
                ui_data['splitter_position'] = prefs.get('splitter_position')
                ui_data['main_app_splitter_position'] = prefs.get('main_app_splitter_position')
                ui_data['side_panel_position'] = prefs.get('side_panel_position')
            
            # Sync settings
            if hasattr(layout, 'sync_zoom_var'):
                ui_data['sync_zoom'] = layout.sync_zoom_var.get()
            if hasattr(layout, 'sync_drag_var'):
                ui_data['sync_drag'] = layout.sync_drag_var.get()
        
        except Exception as e:
            logger.error(f"Error extracting UI state: {e}")
        
        return ui_data
    
    def _extract_recent_results_state(self, panel) -> Dict[str, Any]:
        """Extract Recent Results panel state"""
        results_data = {}
        
        try:
            if hasattr(panel, 'current_thumbnail_size'):
                results_data['thumbnail_size'] = panel.current_thumbnail_size
            if hasattr(panel, 'current_filter'):
                results_data['filter'] = panel.current_filter
        
        except Exception as e:
            logger.error(f"Error extracting recent results state: {e}")
        
        return results_data
    
    def restore_session(self, main_app, session_data: Dict[str, Any]) -> bool:
        """
        Restore complete session state to application
        
        Args:
            main_app: Main application instance
            session_data: Session data dictionary
            
        Returns:
            True if successful
        """
        try:
            logger.info("🔄 Restoring session...")
            
            # Schedule restoration after UI is ready
            main_app.root.after(100, lambda: self._restore_session_delayed(main_app, session_data))
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore session: {e}")
            return False
    
    def _restore_session_delayed(self, main_app, session_data: Dict[str, Any]):
        """Delayed session restoration after UI is ready"""
        try:
            # Restore Tab 1
            if 'tab_1' in session_data and hasattr(main_app, 'seedream_tab_1'):
                self._restore_tab_state(main_app.seedream_tab_1, session_data['tab_1'])
            
            # Restore Tab 2
            if 'tab_2' in session_data and hasattr(main_app, 'seedream_tab_2'):
                self._restore_tab_state(main_app.seedream_tab_2, session_data['tab_2'])
            
            # Restore UI state (after a short delay for tabs to load)
            if 'ui_state' in session_data:
                main_app.root.after(500, lambda: self._restore_ui_state(main_app, session_data['ui_state']))
            
            # Restore Recent Results state
            if 'recent_results' in session_data and hasattr(main_app, 'recent_results_panel'):
                self._restore_recent_results_state(main_app.recent_results_panel, session_data['recent_results'])
            
            # Restore window state (last, after content is loaded)
            if 'window_state' in session_data:
                main_app.root.after(1000, lambda: self._restore_window_state(main_app, session_data['window_state']))
            
            logger.info("✅ Session restored successfully")
            
        except Exception as e:
            logger.error(f"Error during session restoration: {e}")
    
    def _restore_tab_state(self, tab, tab_data: Dict[str, Any]):
        """Restore state to a Seedream V4 tab"""
        try:
            if not hasattr(tab, 'improved_layout'):
                return
            
            layout = tab.improved_layout
            
            # Restore input image(s)
            if 'input_images' in tab_data and tab_data['input_images']:
                paths = tab_data['input_images']
                if paths and len(paths) > 0:
                    # Verify files exist before loading
                    valid_paths = [p for p in paths if os.path.exists(p)]
                    if valid_paths:
                        if len(valid_paths) == 1:
                            layout.load_image(valid_paths[0])
                        else:
                            layout.load_images(valid_paths)
                        logger.debug(f"Restored {len(valid_paths)} input image(s)")
            
            # Restore prompt (use the proper method if available)
            if 'prompt' in tab_data and tab_data['prompt']:
                if hasattr(layout, 'prompt_manager'):
                    # Use set_prompt_text method if available (handles all the state properly)
                    if hasattr(layout.prompt_manager, 'set_prompt_text'):
                        layout.prompt_manager.set_prompt_text(tab_data['prompt'])
                        logger.debug("Restored prompt using set_prompt_text()")
                    # Fallback to manual setting
                    elif hasattr(layout.prompt_manager, 'prompt_text'):
                        # Clear any placeholder state first
                        if hasattr(layout.prompt_manager, 'prompt_has_placeholder'):
                            layout.prompt_manager.prompt_has_placeholder = False
                        
                        # Set the prompt text
                        layout.prompt_manager.prompt_text.delete("1.0", "end")
                        layout.prompt_manager.prompt_text.insert("1.0", tab_data['prompt'])
                        
                        # Ensure text is visible (not gray placeholder color)
                        try:
                            layout.prompt_manager.prompt_text.config(fg='#333333')
                        except:
                            pass
                        
                        # Trigger any update handlers
                        if hasattr(layout.prompt_manager, '_on_prompt_text_changed'):
                            try:
                                layout.prompt_manager._on_prompt_text_changed(None)
                            except:
                                pass
                        
                        logger.debug("Restored prompt manually")
            
            # Restore settings
            if 'settings' in tab_data:
                settings = tab_data['settings']
                if hasattr(layout, 'settings_manager'):
                    mgr = layout.settings_manager
                    if hasattr(mgr, 'width_var'):
                        mgr.width_var.set(settings.get('width', 1024))
                    if hasattr(mgr, 'height_var'):
                        mgr.height_var.set(settings.get('height', 1024))
                    if hasattr(mgr, 'seed_var'):
                        mgr.seed_var.set(settings.get('seed', -1))
                    if hasattr(mgr, 'sync_mode_var'):
                        mgr.sync_mode_var.set(settings.get('sync_mode', True))
                    if hasattr(mgr, 'base64_output_var'):
                        mgr.base64_output_var.set(settings.get('base64_output', False))
                    logger.debug("Restored settings")
            
            # Restore zoom (after images are loaded)
            if 'zoom' in tab_data:
                tab.improved_layout.parent_frame.after(200, lambda: layout.zoom_var.set(tab_data['zoom']))
        
        except Exception as e:
            logger.error(f"Error restoring tab state: {e}")
    
    def _restore_ui_state(self, main_app, ui_data: Dict[str, Any]):
        """Restore UI state"""
        try:
            if not hasattr(main_app, 'seedream_tab_1') or not hasattr(main_app.seedream_tab_1, 'improved_layout'):
                return
            
            layout = main_app.seedream_tab_1.improved_layout
            
            # Restore view mode
            if 'view_mode' in ui_data and hasattr(layout, 'comparison_controller'):
                layout.comparison_controller.set_mode(ui_data['view_mode'])
                logger.debug(f"Restored view mode: {ui_data['view_mode']}")
            
            # Restore overlay opacity
            if 'overlay_opacity' in ui_data and hasattr(layout, 'comparison_controller'):
                layout.comparison_controller.overlay_opacity = ui_data['overlay_opacity']
                layout.comparison_controller.opacity_var.set(ui_data['overlay_opacity'])
            
            # Restore splitter positions
            if hasattr(layout, 'load_ui_state'):
                # Reconstruct ui_preferences for load_ui_state
                prefs = {}
                if 'splitter_position' in ui_data:
                    prefs['splitter_position'] = ui_data['splitter_position']
                if 'main_app_splitter_position' in ui_data:
                    prefs['main_app_splitter_position'] = ui_data['main_app_splitter_position']
                if 'side_panel_position' in ui_data:
                    prefs['side_panel_position'] = ui_data['side_panel_position']
                
                if prefs:
                    # Temporarily store and restore
                    layout.ui_preferences.update(prefs)
                    layout._try_restore_splitters()
                    logger.debug("Restored splitter positions")
            
            # Restore sync settings
            if 'sync_zoom' in ui_data and hasattr(layout, 'sync_zoom_var'):
                layout.sync_zoom_var.set(ui_data['sync_zoom'])
            if 'sync_drag' in ui_data and hasattr(layout, 'sync_drag_var'):
                layout.sync_drag_var.set(ui_data['sync_drag'])
        
        except Exception as e:
            logger.error(f"Error restoring UI state: {e}")
    
    def _restore_recent_results_state(self, panel, results_data: Dict[str, Any]):
        """Restore Recent Results panel state"""
        try:
            if 'thumbnail_size' in results_data:
                panel.current_thumbnail_size = results_data['thumbnail_size']
            if 'filter' in results_data:
                panel.current_filter = results_data['filter']
            
            # Trigger refresh
            if hasattr(panel, 'render_results_grid'):
                panel.render_results_grid()
        
        except Exception as e:
            logger.error(f"Error restoring recent results state: {e}")
    
    def _restore_window_state(self, main_app, window_data: Dict[str, Any]):
        """Restore window geometry and state"""
        try:
            if 'geometry' in window_data:
                main_app.root.geometry(window_data['geometry'])
            if 'state' in window_data:
                main_app.root.state(window_data['state'])
            
            logger.debug("Restored window state")
        
        except Exception as e:
            logger.error(f"Error restoring window state: {e}")

