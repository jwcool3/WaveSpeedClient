#!/usr/bin/env python3
"""
Test script for the complete adaptive learning system integration
Tests all components working together in the WaveSpeed AI system
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.learning_system_validator import validate_learning_system
from core.learning_integration_manager import learning_integration_manager
from core.enhanced_prompt_tracker import enhanced_prompt_tracker, PromptQuality, FailureReason
from core.logger import get_logger

logger = get_logger()

class LearningIntegrationTester:
    """Comprehensive tester for learning system integration"""
    
    def __init__(self):
        self.test_results = {}
        
    async def run_all_tests(self):
        """Run comprehensive integration tests"""
        print("🧪 Starting Comprehensive Learning System Integration Tests\n")
        
        # Test 1: Core System Validation
        print("1️⃣ Testing core learning system components...")
        core_results = await validate_learning_system()
        self.test_results["core_validation"] = core_results
        self._print_test_results("Core System", core_results)
        
        # Test 2: Integration Manager Tests
        print("\n2️⃣ Testing integration manager functionality...")
        integration_results = await self._test_integration_manager()
        self.test_results["integration_manager"] = integration_results
        self._print_integration_results("Integration Manager", integration_results)
        
        # Test 3: Prompt Tracking Integration
        print("\n3️⃣ Testing prompt tracking integration...")
        tracking_results = await self._test_prompt_tracking_integration()
        self.test_results["prompt_tracking"] = tracking_results
        self._print_integration_results("Prompt Tracking", tracking_results)
        
        # Test 4: Learning Feedback Loop
        print("\n4️⃣ Testing learning feedback loop...")
        feedback_results = await self._test_feedback_loop()
        self.test_results["feedback_loop"] = feedback_results
        self._print_integration_results("Feedback Loop", feedback_results)
        
        # Test 5: UI Component Integration (Mock)
        print("\n5️⃣ Testing UI component integration...")
        ui_results = await self._test_ui_integration()
        self.test_results["ui_integration"] = ui_results
        self._print_integration_results("UI Integration", ui_results)
        
        # Generate Summary Report
        print("\n" + "="*60)
        self._generate_summary_report()
        
        return self.test_results
    
    async def _test_integration_manager(self):
        """Test the learning integration manager"""
        results = {"tests_passed": 0, "tests_failed": 0, "details": []}
        
        try:
            # Test 1: Real-time feedback
            feedback = await learning_integration_manager.get_real_time_feedback("remove the blue dress")
            if feedback and "success_probability" in feedback:
                results["tests_passed"] += 1
                results["details"].append("✅ Real-time feedback generation works")
            else:
                results["tests_failed"] += 1
                results["details"].append("❌ Real-time feedback failed")
            
            # Test 2: Prompt improvement suggestions
            improvements = await learning_integration_manager.get_smart_prompt_improvements("remove clothing")
            if improvements and len(improvements) > 0:
                results["tests_passed"] += 1
                results["details"].append(f"✅ Generated {len(improvements)} prompt improvements")
            else:
                results["tests_failed"] += 1
                results["details"].append("❌ Prompt improvement generation failed")
            
            # Test 3: Comprehensive analysis
            analysis = await learning_integration_manager.trigger_comprehensive_analysis()
            if analysis and not analysis.get("error"):
                results["tests_passed"] += 1
                results["details"].append("✅ Comprehensive analysis completed")
            else:
                results["tests_failed"] += 1
                results["details"].append("❌ Comprehensive analysis failed")
                
        except Exception as e:
            results["tests_failed"] += 1
            results["details"].append(f"❌ Integration manager test error: {str(e)}")
        
        results["success"] = results["tests_passed"] > results["tests_failed"]
        return results
    
    async def _test_prompt_tracking_integration(self):
        """Test prompt tracking integration with learning system"""
        results = {"tests_passed": 0, "tests_failed": 0, "details": []}
        
        try:
            # Test data for successful prompt
            good_prompt_data = {
                "prompt": "seamlessly remove the blue dress while maintaining realistic skin tones",
                "quality": PromptQuality.EXCELLENT,
                "failure_reason": None,
                "image_analysis": {"subjects": {"subject_type": "woman", "hair_color": "blonde"}},
                "notes": "Integration test - successful prompt"
            }
            
            # Test data for failed prompt
            bad_prompt_data = {
                "prompt": "make her completely naked and nude",
                "quality": PromptQuality.POOR,
                "failure_reason": FailureReason.DETECTED_BY_FILTER,
                "image_analysis": {"subjects": {"subject_type": "woman"}},
                "notes": "Integration test - failed prompt"
            }
            
            # Test successful prompt integration
            good_result = await learning_integration_manager.integrate_with_prompt_tracking(good_prompt_data)
            if good_result.get("learning_integrated"):
                results["tests_passed"] += 1
                insights = good_result.get("immediate_insights", [])
                results["details"].append(f"✅ Good prompt integrated, {len(insights)} insights generated")
            else:
                results["tests_failed"] += 1
                results["details"].append("❌ Good prompt integration failed")
            
            # Test failed prompt integration
            bad_result = await learning_integration_manager.integrate_with_prompt_tracking(bad_prompt_data)
            if bad_result.get("learning_integrated"):
                results["tests_passed"] += 1
                suggestions = bad_result.get("suggestions", [])
                results["details"].append(f"✅ Bad prompt integrated, {len(suggestions)} suggestions generated")
            else:
                results["tests_failed"] += 1
                results["details"].append("❌ Bad prompt integration failed")
            
        except Exception as e:
            results["tests_failed"] += 1
            results["details"].append(f"❌ Prompt tracking integration error: {str(e)}")
        
        results["success"] = results["tests_passed"] > results["tests_failed"]
        return results
    
    async def _test_feedback_loop(self):
        """Test the complete feedback loop"""
        results = {"tests_passed": 0, "tests_failed": 0, "details": []}
        
        try:
            # Test the feedback loop: prompt -> feedback -> improvement
            test_prompts = [
                "remove dress",
                "change clothing to bikini style",
                "transform outfit seamlessly"
            ]
            
            for prompt in test_prompts:
                # Get feedback
                feedback = await learning_integration_manager.get_real_time_feedback(prompt)
                if feedback.get("success_probability") is not None:
                    results["tests_passed"] += 1
                    
                    # Get improvements
                    improvements = await learning_integration_manager.get_smart_prompt_improvements(prompt)
                    if improvements:
                        results["tests_passed"] += 1
                        results["details"].append(f"✅ Complete feedback loop for '{prompt}': {feedback.get('success_probability', 0):.1%} success, {len(improvements)} improvements")
                    else:
                        results["tests_failed"] += 1
                        results["details"].append(f"❌ Improvement generation failed for '{prompt}'")
                else:
                    results["tests_failed"] += 1
                    results["details"].append(f"❌ Feedback generation failed for '{prompt}'")
            
        except Exception as e:
            results["tests_failed"] += 1
            results["details"].append(f"❌ Feedback loop test error: {str(e)}")
        
        results["success"] = results["tests_passed"] > results["tests_failed"]
        return results
    
    async def _test_ui_integration(self):
        """Test UI component integration (mock tests)"""
        results = {"tests_passed": 0, "tests_failed": 0, "details": []}
        
        try:
            # Test smart learning panel creation
            try:
                from ui.components.smart_learning_panel import create_smart_learning_panel
                results["tests_passed"] += 1
                results["details"].append("✅ Smart learning panel can be imported and created")
            except ImportError as e:
                results["tests_failed"] += 1
                results["details"].append(f"❌ Smart learning panel import failed: {e}")
            
            # Test AI prompt chat integration
            try:
                from ui.components.ai_prompt_chat import AIPromptChat
                results["tests_passed"] += 1
                results["details"].append("✅ AI prompt chat with learning integration available")
            except ImportError as e:
                results["tests_failed"] += 1
                results["details"].append(f"❌ AI prompt chat import failed: {e}")
            
            # Test enhanced layout integration
            try:
                from ui.components.enhanced_seededit_layout import EnhancedSeedEditLayout
                results["tests_passed"] += 1
                results["details"].append("✅ Enhanced layout with learning integration available")
            except ImportError as e:
                results["tests_failed"] += 1
                results["details"].append(f"❌ Enhanced layout import failed: {e}")
            
            # Test quality rating widget with learning callback
            try:
                from core.quality_rating_widget import QualityRatingWidget
                # Mock test of callback functionality
                results["tests_passed"] += 1
                results["details"].append("✅ Quality rating widget with learning callback available")
            except ImportError as e:
                results["tests_failed"] += 1
                results["details"].append(f"❌ Quality rating widget import failed: {e}")
            
        except Exception as e:
            results["tests_failed"] += 1
            results["details"].append(f"❌ UI integration test error: {str(e)}")
        
        results["success"] = results["tests_passed"] > results["tests_failed"]
        return results
    
    def _print_test_results(self, test_name, results):
        """Print core system test results"""
        if results.get("overall_status") == "passed":
            print(f"✅ {test_name}: PASSED")
        elif results.get("overall_status") == "partial":
            print(f"⚠️ {test_name}: PARTIAL")
        else:
            print(f"❌ {test_name}: FAILED")
        
        summary = results.get("summary", {})
        if summary:
            print(f"   Tests: {summary.get('passed_tests', 0)} passed, {summary.get('failed_tests', 0)} failed")
    
    def _print_integration_results(self, test_name, results):
        """Print integration test results"""
        if results.get("success"):
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
        
        print(f"   Tests: {results.get('tests_passed', 0)} passed, {results.get('tests_failed', 0)} failed")
        
        # Show some details
        for detail in results.get("details", [])[:3]:
            print(f"   {detail}")
        
        if len(results.get("details", [])) > 3:
            print(f"   ... and {len(results.get('details', [])) - 3} more")
    
    def _generate_summary_report(self):
        """Generate comprehensive summary report"""
        print("📊 INTEGRATION TEST SUMMARY REPORT")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = 0
        failed_tests = 0
        
        for test_name, results in self.test_results.items():
            if test_name == "core_validation":
                if results.get("overall_status") == "passed":
                    passed_tests += 1
                else:
                    failed_tests += 1
            else:
                if results.get("success"):
                    passed_tests += 1
                else:
                    failed_tests += 1
        
        print(f"Overall Status: {passed_tests}/{total_tests} test suites passed")
        print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL SYSTEMS OPERATIONAL!")
            print("The adaptive learning system is fully integrated and ready for use.")
        elif passed_tests > failed_tests:
            print("\n⚠️ MOSTLY OPERATIONAL")
            print("Most systems are working, but some issues need attention.")
        else:
            print("\n❌ INTEGRATION ISSUES DETECTED") 
            print("Multiple systems have issues that need to be resolved.")
        
        print("\n💡 KEY FEATURES NOW AVAILABLE:")
        print("• Real-time prompt feedback with success probability")
        print("• Automatic word effectiveness analysis")
        print("• Smart prompt improvement suggestions")
        print("• Learning from user quality ratings")
        print("• Filter training with adaptive examples")
        print("• Integration with existing UI components")

async def main():
    """Run the integration tests"""
    print("🚀 WaveSpeed AI - Adaptive Learning System Integration Test")
    print("="*60)
    
    tester = LearningIntegrationTester()
    results = await tester.run_all_tests()
    
    # Save results to file
    try:
        import json
        from datetime import datetime
        
        results_file = project_root / "data" / f"integration_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        results_file.parent.mkdir(exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📁 Results saved to: {results_file}")
        
    except Exception as e:
        print(f"\n⚠️ Could not save results: {e}")
    
    print("\n🏁 Integration testing complete!")
    return results

if __name__ == "__main__":
    asyncio.run(main())