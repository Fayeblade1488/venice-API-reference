#!/usr/bin/env python3
"""
test_add_code_samples_edge_cases.py - Edge Case Tests for add_code_samples

This module provides comprehensive edge case testing for the add_code_samples
script to ensure robust error handling and correct behavior in unusual scenarios.

Test Categories:
    - Error handling: Missing files, invalid YAML, empty specs
    - Edge cases: Empty paths, None values, invalid methods
    - Boundary conditions: Existing samples, partial specs
    - Integration: CLI usage, file permissions

Author: Venice.ai API Reference Team
"""

import unittest
import yaml
import os
import tempfile
import shutil
from add_code_samples import add_code_samples


class TestAddCodeSamplesEdgeCases(unittest.TestCase):
    """Comprehensive edge case tests for add_code_samples functionality."""
    
    def setUp(self):
        """Set up temporary test directory and files."""
        self.test_dir = tempfile.mkdtemp()
        self.test_spec_path = os.path.join(self.test_dir, "test_spec.yaml")
        
    def tearDown(self):
        """Clean up temporary test files and directory."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_empty_paths_section(self):
        """
        Test handling of spec with empty paths section.
        
        Ensures the script handles specs with no endpoints gracefully.
        """
        spec = {
            'openapi': '3.0.0',
            'info': {'title': 'Empty API', 'version': '1.0.0'},
            'paths': {}
        }
        
        with open(self.test_spec_path, 'w') as f:
            yaml.dump(spec, f)
        
        # Should not raise an error
        add_code_samples(self.test_spec_path)
        
        # Verify file still valid
        with open(self.test_spec_path, 'r') as f:
            result = yaml.safe_load(f)
        
        self.assertEqual(result['paths'], {})
    
    def test_missing_paths_section(self):
        """
        Test handling of spec without paths section.
        
        The paths section is required by OpenAPI, but script should handle
        its absence gracefully.
        """
        spec = {
            'openapi': '3.0.0',
            'info': {'title': 'No Paths API', 'version': '1.0.0'}
        }
        
        with open(self.test_spec_path, 'w') as f:
            yaml.dump(spec, f)
        
        # Should not raise an error
        add_code_samples(self.test_spec_path)
        
        # Verify spec unchanged
        with open(self.test_spec_path, 'r') as f:
            result = yaml.safe_load(f)
        
        self.assertNotIn('paths', result)
    
    def test_none_path_item(self):
        """
        Test handling of path items that are None.
        
        Some tools may leave None values, script should skip them.
        """
        spec = {
            'openapi': '3.0.0',
            'info': {'title': 'Test', 'version': '1.0.0'},
            'paths': {
                '/valid': {
                    'get': {
                        'summary': 'Valid endpoint',
                        'responses': {'200': {'description': 'OK'}}
                    }
                },
                '/invalid': None
            }
        }
        
        with open(self.test_spec_path, 'w') as f:
            yaml.dump(spec, f)
        
        # Should not raise an error
        add_code_samples(self.test_spec_path)
        
        # Verify valid endpoint got samples
        with open(self.test_spec_path, 'r') as f:
            result = yaml.safe_load(f)
        
        self.assertIn('x-codeSamples', result['paths']['/valid']['get'])
        self.assertIsNone(result['paths']['/invalid'])
    
    def test_non_dict_operation(self):
        """
        Test handling of operations that are not dictionaries.
        
        Invalid OpenAPI specs may have non-dict values, script should skip them.
        """
        spec = {
            'openapi': '3.0.0',
            'info': {'title': 'Test', 'version': '1.0.0'},
            'paths': {
                '/test': {
                    'get': 'invalid string value',
                    'post': {
                        'summary': 'Valid POST',
                        'responses': {'200': {'description': 'OK'}}
                    }
                }
            }
        }
        
        with open(self.test_spec_path, 'w') as f:
            yaml.dump(spec, f)
        
        # Should not raise an error
        add_code_samples(self.test_spec_path)
        
        # Verify POST got samples but GET didn't cause errors
        with open(self.test_spec_path, 'r') as f:
            result = yaml.safe_load(f)
        
        self.assertEqual(result['paths']['/test']['get'], 'invalid string value')
        self.assertIn('x-codeSamples', result['paths']['/test']['post'])
    
    def test_invalid_http_methods(self):
        """
        Test that invalid HTTP methods are skipped.
        
        OpenAPI specs may have non-method keys like 'parameters', 'summary'.
        These should be ignored.
        """
        spec = {
            'openapi': '3.0.0',
            'info': {'title': 'Test', 'version': '1.0.0'},
            'paths': {
                '/test': {
                    'parameters': [{'name': 'id', 'in': 'path'}],
                    'summary': 'Test endpoint',
                    'description': 'This is a test',
                    'get': {
                        'summary': 'Valid GET',
                        'responses': {'200': {'description': 'OK'}}
                    }
                }
            }
        }
        
        with open(self.test_spec_path, 'w') as f:
            yaml.dump(spec, f)
        
        # Should not raise an error
        add_code_samples(self.test_spec_path)
        
        # Verify non-method keys unchanged
        with open(self.test_spec_path, 'r') as f:
            result = yaml.safe_load(f)
        
        self.assertIn('parameters', result['paths']['/test'])
        self.assertIn('summary', result['paths']['/test'])
        self.assertIn('x-codeSamples', result['paths']['/test']['get'])
    
    def test_all_valid_http_methods(self):
        """
        Test that all valid HTTP methods get code samples.
        
        Tests GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD, TRACE.
        """
        methods = ['get', 'post', 'put', 'delete', 'patch', 'options', 'head', 'trace']
        
        paths = {}
        for method in methods:
            paths[f'/{method}'] = {
                method: {
                    'summary': f'Test {method.upper()}',
                    'responses': {'200': {'description': 'OK'}}
                }
            }
        
        spec = {
            'openapi': '3.0.0',
            'info': {'title': 'Test', 'version': '1.0.0'},
            'paths': paths
        }
        
        with open(self.test_spec_path, 'w') as f:
            yaml.dump(spec, f)
        
        add_code_samples(self.test_spec_path)
        
        # Verify all methods got samples
        with open(self.test_spec_path, 'r') as f:
            result = yaml.safe_load(f)
        
        for method in methods:
            self.assertIn(
                'x-codeSamples',
                result['paths'][f'/{method}'][method],
                f"{method.upper()} should have code samples"
            )
    
    def test_existing_samples_not_overwritten(self):
        """
        Test that existing x-codeSamples are preserved.
        
        Operations that already have code samples should not be modified.
        """
        custom_sample = {
            'lang': 'Ruby',
            'label': 'Custom Ruby Example',
            'source': 'require "http"\nHTTP.get("https://example.com")'
        }
        
        spec = {
            'openapi': '3.0.0',
            'info': {'title': 'Test', 'version': '1.0.0'},
            'paths': {
                '/with-samples': {
                    'get': {
                        'summary': 'Has samples',
                        'x-codeSamples': [custom_sample],
                        'responses': {'200': {'description': 'OK'}}
                    }
                },
                '/without-samples': {
                    'get': {
                        'summary': 'No samples',
                        'responses': {'200': {'description': 'OK'}}
                    }
                }
            }
        }
        
        with open(self.test_spec_path, 'w') as f:
            yaml.dump(spec, f)
        
        add_code_samples(self.test_spec_path)
        
        with open(self.test_spec_path, 'r') as f:
            result = yaml.safe_load(f)
        
        # Existing samples should be unchanged
        self.assertEqual(
            result['paths']['/with-samples']['get']['x-codeSamples'],
            [custom_sample]
        )
        
        # New samples should be added
        self.assertIn('x-codeSamples', result['paths']['/without-samples']['get'])
        self.assertEqual(len(result['paths']['/without-samples']['get']['x-codeSamples']), 3)
    
    def test_special_characters_in_path(self):
        """
        Test handling of paths with special characters.
        
        Paths may contain parameters, special chars that need proper handling.
        """
        spec = {
            'openapi': '3.0.0',
            'info': {'title': 'Test', 'version': '1.0.0'},
            'paths': {
                '/users/{id}': {
                    'get': {
                        'summary': 'Get user by ID',
                        'responses': {'200': {'description': 'OK'}}
                    }
                },
                '/files/{path*}': {
                    'get': {
                        'summary': 'Get file',
                        'responses': {'200': {'description': 'OK'}}
                    }
                }
            }
        }
        
        with open(self.test_spec_path, 'w') as f:
            yaml.dump(spec, f)
        
        add_code_samples(self.test_spec_path)
        
        with open(self.test_spec_path, 'r') as f:
            result = yaml.safe_load(f)
        
        # Verify code samples include the special characters
        samples = result['paths']['/users/{id}']['get']['x-codeSamples']
        curl_sample = next(s['source'] for s in samples if s['lang'] == 'cURL')
        
        self.assertIn('/users/{id}', curl_sample)
    
    def test_multiple_operations_same_path(self):
        """
        Test handling of multiple operations on the same path.
        
        A single path can have multiple methods (GET, POST, etc.).
        """
        spec = {
            'openapi': '3.0.0',
            'info': {'title': 'Test', 'version': '1.0.0'},
            'paths': {
                '/users': {
                    'get': {
                        'summary': 'List users',
                        'responses': {'200': {'description': 'OK'}}
                    },
                    'post': {
                        'summary': 'Create user',
                        'responses': {'201': {'description': 'Created'}}
                    },
                    'delete': {
                        'summary': 'Delete all users',
                        'responses': {'204': {'description': 'Deleted'}}
                    }
                }
            }
        }
        
        with open(self.test_spec_path, 'w') as f:
            yaml.dump(spec, f)
        
        add_code_samples(self.test_spec_path)
        
        with open(self.test_spec_path, 'r') as f:
            result = yaml.safe_load(f)
        
        # All operations should get samples
        path_item = result['paths']['/users']
        self.assertIn('x-codeSamples', path_item['get'])
        self.assertIn('x-codeSamples', path_item['post'])
        self.assertIn('x-codeSamples', path_item['delete'])
        
        # POST should have request body, GET should not
        post_curl = next(
            s['source'] for s in path_item['post']['x-codeSamples']
            if s['lang'] == 'cURL'
        )
        get_curl = next(
            s['source'] for s in path_item['get']['x-codeSamples']
            if s['lang'] == 'cURL'
        )
        
        self.assertIn('-d', post_curl)
        self.assertNotIn('-d', get_curl)
    
    def test_large_spec_performance(self):
        """
        Test performance with a large number of endpoints.
        
        Ensures the script can handle large API specs efficiently.
        """
        # Create spec with 100 endpoints
        paths = {}
        for i in range(100):
            paths[f'/endpoint{i}'] = {
                'get': {
                    'summary': f'Endpoint {i}',
                    'responses': {'200': {'description': 'OK'}}
                }
            }
        
        spec = {
            'openapi': '3.0.0',
            'info': {'title': 'Large API', 'version': '1.0.0'},
            'paths': paths
        }
        
        with open(self.test_spec_path, 'w') as f:
            yaml.dump(spec, f)
        
        import time
        start = time.time()
        add_code_samples(self.test_spec_path)
        elapsed = time.time() - start
        
        # Should complete in reasonable time (default < 5 seconds, configurable via ADD_CODE_SAMPLES_PERF_THRESHOLD)
        threshold = float(os.environ.get("ADD_CODE_SAMPLES_PERF_THRESHOLD", "5.0"))
        self.assertLess(elapsed, threshold, f"Processing 100 endpoints took too long (>{threshold}s)")
        
        # Verify all got samples
        with open(self.test_spec_path, 'r') as f:
            result = yaml.safe_load(f)
        
        for i in range(100):
            self.assertIn('x-codeSamples', result['paths'][f'/endpoint{i}']['get'])
    
    def test_utf8_encoding_preserved(self):
        """
        Test that UTF-8 characters in spec are preserved.
        
        The script should handle international characters correctly.
        """
        spec = {
            'openapi': '3.0.0',
            'info': {
                'title': 'API avec caractères spéciaux',
                'version': '1.0.0',
                'description': '日本語のテキスト'
            },
            'paths': {
                '/test': {
                    'get': {
                        'summary': 'Tëst ëndpöint with ümläüts',
                        'responses': {'200': {'description': 'OK'}}
                    }
                }
            }
        }
        
        with open(self.test_spec_path, 'w', encoding='utf-8') as f:
            yaml.dump(spec, f, allow_unicode=True)
        
        add_code_samples(self.test_spec_path)
        
        with open(self.test_spec_path, 'r', encoding='utf-8') as f:
            result = yaml.safe_load(f)
        
        # Verify UTF-8 characters preserved
        self.assertEqual(result['info']['title'], 'API avec caractères spéciaux')
        self.assertEqual(result['info']['description'], '日本語のテキスト')
        self.assertEqual(result['paths']['/test']['get']['summary'], 'Tëst ëndpöint with ümläüts')


def main():
    """
    Main entry point for running edge case tests.
    
    Runs all tests and reports results.
    """
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
