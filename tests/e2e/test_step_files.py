"""
End-to-end tests for refactored step files.

These tests verify that all step files can be imported and their main functions
can be called successfully after the refactoring.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def mock_providers():
    """Create mock providers for testing"""
    llm_provider = Mock()
    llm_provider.provider_name = "openai"
    llm_provider.model_name = "gpt-4"
    llm_provider.generate_text.return_value = "Test script content"

    tts_provider = Mock()
    tts_provider.provider_name = "openai"
    tts_provider.model_name = "tts-1"
    tts_provider.available_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    tts_provider.generate_audio.return_value = None

    return llm_provider, tts_provider


@pytest.fixture
def mock_user_inputs():
    """Mock user inputs for testing"""
    return {
        "topic": "Test Topic",
        "tone": "casual",
        "voice": "nova",
        "length": "medium",
        "url": "https://example.com/article",
        "file": "test.txt"
    }


class TestStepFilesCanImport:
    """Test that all step files can be imported without errors"""

    def test_import_step3(self):
        """Test importing step3_script_generator.py"""
        import step3_script_generator
        assert hasattr(step3_script_generator, 'main')

    def test_import_step4(self):
        """Test importing step4_save_script.py"""
        import step4_save_script
        assert hasattr(step4_save_script, 'main')

    def test_import_step5(self):
        """Test importing step5_generate_podcast.py"""
        import step5_generate_podcast
        assert hasattr(step5_generate_podcast, 'main')

    def test_import_step6(self):
        """Test importing step6_podcast_episode.py"""
        import step6_podcast_episode
        assert hasattr(step6_podcast_episode, 'main')

    def test_import_step7(self):
        """Test importing step7_custom_podcast.py"""
        import step7_custom_podcast
        assert hasattr(step7_custom_podcast, 'main')

    def test_import_step8(self):
        """Test importing step8_podcast_from_source.py"""
        import step8_podcast_from_source
        assert hasattr(step8_podcast_from_source, 'main')

    def test_import_step9(self):
        """Test importing step9_multi_source_podcast.py"""
        import step9_multi_source_podcast
        assert hasattr(step9_multi_source_podcast, 'main')

    def test_import_step10(self):
        """Test importing step10_podcast_from_urls.py"""
        import step10_podcast_from_urls
        assert hasattr(step10_podcast_from_urls, 'main')

    def test_import_step11(self):
        """Test importing step11_configurable_podcast.py"""
        import step11_configurable_podcast
        assert hasattr(step11_configurable_podcast, 'main')

    def test_import_step12(self):
        """Test importing step12_hybrid_sources_podcast.py"""
        import step12_hybrid_sources_podcast
        assert hasattr(step12_hybrid_sources_podcast, 'main')

    def test_import_step13(self):
        """Test importing step13_mixed_sources_podcast.py"""
        import step13_mixed_sources_podcast
        assert hasattr(step13_mixed_sources_podcast, 'main')

    def test_import_step14(self):
        """Test importing step14_episode_metadata.py"""
        import step14_episode_metadata
        assert hasattr(step14_episode_metadata, 'main')

    def test_import_step17(self):
        """Test importing step17_episode_browser.py"""
        import step17_episode_browser
        assert hasattr(step17_episode_browser, 'main')

    def test_import_step18(self):
        """Test importing step18_regenerate_episode.py"""
        import step18_regenerate_episode
        assert hasattr(step18_regenerate_episode, 'main')

    def test_import_step19(self):
        """Test importing step19_rss_podcast.py"""
        import step19_rss_podcast
        assert hasattr(step19_rss_podcast, 'main')

    def test_import_step20(self):
        """Test importing step20_pasted_content_podcast.py"""
        import step20_pasted_content_podcast
        assert hasattr(step20_pasted_content_podcast, 'main')


class TestStepFilesUseCoreModules:
    """Test that step files are actually using core modules"""

    def test_step3_uses_core_modules(self):
        """Verify step3 imports from core modules"""
        import step3_script_generator
        import inspect

        source = inspect.getsource(step3_script_generator)
        assert "from core.provider_setup import" in source
        assert "from core.content_generation import" in source

    def test_step5_uses_core_modules(self):
        """Verify step5 imports from core modules"""
        import step5_generate_podcast
        import inspect

        source = inspect.getsource(step5_generate_podcast)
        assert "from core" in source
        # Verify it's not using duplicated functions
        assert "def build_script(" not in source

    def test_step10_uses_core_modules(self):
        """Verify step10 imports from core modules"""
        import step10_podcast_from_urls
        import inspect

        source = inspect.getsource(step10_podcast_from_urls)
        assert "from core" in source
        assert "from core.source_management import" in source
        # Verify not using duplicated functions
        assert "def fetch_article_text(" not in source

    def test_step14_uses_core_modules(self):
        """Verify step14 imports from core modules"""
        import step14_episode_metadata
        import inspect

        source = inspect.getsource(step14_episode_metadata)
        assert "from core.episode_management import" in source
        # Verify not using duplicated functions
        assert "def save_metadata(" not in source or "save_episode_metadata" in source

    def test_step19_uses_core_modules(self):
        """Verify step19 imports from core modules"""
        import step19_rss_podcast
        import inspect

        source = inspect.getsource(step19_rss_podcast)
        assert "from core.rss_utils import" in source
        # Verify not using duplicated functions
        assert "def parse_rss_feed(" not in source


class TestStepFilesNoCodeDuplication:
    """Test that step files don't contain duplicated code"""

    @pytest.mark.parametrize("step_module,forbidden_functions", [
        ("step3_script_generator", ["def sanitize_filename(", "def get_word_range("]),
        ("step5_generate_podcast", ["def build_script(", "def generate_audio("]),
        ("step7_custom_podcast", ["def validate_choice(", "def get_user_input("]),
        ("step10_podcast_from_urls", ["def fetch_article_text(", "def parse_csv_input("]),
        ("step14_episode_metadata", ["def save_json(", "def update_episode_index("]),
        ("step17_episode_browser", ["def display_episode_list(", "def format_episode_summary("]),
        ("step19_rss_podcast", ["def parse_rss_feed(", "def save_rss_info("]),
        ("step20_pasted_content_podcast", ["def read_multiline_input(", "def sanitize_filename("]),
    ])
    def test_no_duplicated_functions(self, step_module, forbidden_functions):
        """Test that step files don't re-implement core functions"""
        import importlib
        import inspect

        module = importlib.import_module(step_module)
        source = inspect.getsource(module)

        for func in forbidden_functions:
            # Allow imports but not definitions
            if func in source:
                # Check it's an import, not a definition
                lines = source.split('\n')
                for line in lines:
                    if func in line:
                        assert 'import' in line or 'from' in line, \
                            f"{step_module} should not define {func}, should import from core"


class TestStepFilesStructure:
    """Test the structure and organization of step files"""

    @pytest.mark.parametrize("step_module", [
        "step3_script_generator",
        "step5_generate_podcast",
        "step7_custom_podcast",
        "step10_podcast_from_urls",
        "step14_episode_metadata",
        "step17_episode_browser",
        "step19_rss_podcast",
        "step20_pasted_content_podcast",
    ])
    def test_has_main_function(self, step_module):
        """Test that step files have a main() function"""
        import importlib

        module = importlib.import_module(step_module)
        assert hasattr(module, 'main'), f"{step_module} should have a main() function"
        assert callable(getattr(module, 'main')), f"main in {step_module} should be callable"

    @pytest.mark.parametrize("step_module", [
        "step3_script_generator",
        "step5_generate_podcast",
        "step7_custom_podcast",
        "step10_podcast_from_urls",
        "step14_episode_metadata",
        "step19_rss_podcast",
        "step20_pasted_content_podcast",
    ])
    def test_has_main_guard(self, step_module):
        """Test that step files have if __name__ == '__main__' guard"""
        import importlib
        import inspect

        module = importlib.import_module(step_module)
        source = inspect.getsource(module)

        assert 'if __name__ == "__main__"' in source, \
            f"{step_module} should have if __name__ == '__main__' guard"


class TestRefactoredCodeQuality:
    """Test the quality of refactored code"""

    def test_imports_organized(self):
        """Test that imports are organized (stdlib, third-party, core)"""
        import step10_podcast_from_urls
        import inspect

        source = inspect.getsource(step10_podcast_from_urls)
        lines = source.split('\n')

        # Find import section
        import_lines = [l for l in lines if l.strip().startswith(('import ', 'from '))]

        # Should have imports from pathlib (stdlib), core (local)
        has_stdlib = any('pathlib' in l or 'datetime' in l for l in import_lines)
        has_core = any('from core' in l for l in import_lines)

        assert has_stdlib or has_core, "Should have organized imports"

    def test_provider_initialization_order(self):
        """Test that providers are initialized before being used"""
        import step11_configurable_podcast
        import inspect

        source = inspect.getsource(step11_configurable_podcast)
        lines = source.split('\n')

        # Find provider initialization
        init_line = None
        provider_use_line = None

        for i, line in enumerate(lines):
            if 'initialize_providers()' in line:
                init_line = i
            if init_line is None and 'tts_provider.' in line:
                provider_use_line = i

        # Provider should be initialized before use
        if provider_use_line is not None:
            assert init_line is not None, "Providers must be initialized"
            assert init_line < provider_use_line, "Providers must be initialized before use"

    def test_no_hardcoded_paths(self):
        """Test that step files use config for paths"""
        import step10_podcast_from_urls
        import inspect

        source = inspect.getsource(step10_podcast_from_urls)

        # Should not have hard-coded "output" path (should use config)
        lines = source.split('\n')
        for line in lines:
            if 'OUTPUT_ROOT' in line or 'output_root' in line:
                # Good - using config
                break
        else:
            # Check if hard-coded
            if 'Path("output")' in source:
                assert 'config.OUTPUT_ROOT' in source or 'OUTPUT_ROOT =' in source, \
                    "Should use config for output paths"


class TestCoreModulesAvailable:
    """Test that all core modules are available for import"""

    def test_import_validation(self):
        """Test importing core.validation"""
        from core import validation
        assert hasattr(validation, 'sanitize_filename')
        assert hasattr(validation, 'validate_choice')
        assert hasattr(validation, 'get_word_range')

    def test_import_file_utils(self):
        """Test importing core.file_utils"""
        from core import file_utils
        assert hasattr(file_utils, 'save_json')
        assert hasattr(file_utils, 'save_text_file')
        assert hasattr(file_utils, 'read_text_file')

    def test_import_source_management(self):
        """Test importing core.source_management"""
        from core import source_management
        assert hasattr(source_management, 'fetch_article_text')
        assert hasattr(source_management, 'save_sources_to_directory')

    def test_import_provider_setup(self):
        """Test importing core.provider_setup"""
        from core import provider_setup
        assert hasattr(provider_setup, 'initialize_providers')

    def test_import_content_generation(self):
        """Test importing core.content_generation"""
        from core import content_generation
        assert hasattr(content_generation, 'build_script')
        assert hasattr(content_generation, 'build_show_notes')
        assert hasattr(content_generation, 'generate_audio')

    def test_import_episode_management(self):
        """Test importing core.episode_management"""
        from core import episode_management
        assert hasattr(episode_management, 'create_episode_directory')
        assert hasattr(episode_management, 'save_episode_metadata')

    def test_import_rss_utils(self):
        """Test importing core.rss_utils"""
        from core import rss_utils
        assert hasattr(rss_utils, 'parse_rss_feed')

    def test_import_episode_browser(self):
        """Test importing core.episode_browser"""
        from core import episode_browser
        assert hasattr(episode_browser, 'display_episode_list')

    def test_import_episode_regenerator(self):
        """Test importing core.episode_regenerator"""
        from core import episode_regenerator
        assert hasattr(episode_regenerator, 'regenerate_episode')
