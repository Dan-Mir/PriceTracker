"""
Script per eseguire tutti i test
"""
import unittest
import sys
import os

# Aggiungi la directory tests al path
sys.path.insert(0, os.path.dirname(__file__))

# Importa i test
from test_db import TestPriceDatabase, TestDatabaseIntegrity
from test_parser_utils import TestParserUtilities, TestParserBlacklist
from test_integration import TestIntegrationWorkflow, TestDataConsistency


def run_all_tests():
    """Esegue tutti i test con report dettagliato"""
    
    # Crea la suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Aggiungi tutti i test
    suite.addTests(loader.loadTestsFromTestCase(TestPriceDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseIntegrity))
    suite.addTests(loader.loadTestsFromTestCase(TestParserUtilities))
    suite.addTests(loader.loadTestsFromTestCase(TestParserBlacklist))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationWorkflow))
    suite.addTests(loader.loadTestsFromTestCase(TestDataConsistency))
    
    # Esegui i test con verbosity=2 per output dettagliato
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Report finale
    print("\n" + "="*70)
    print("REPORT FINALE")
    print("="*70)
    print(f"Test eseguiti: {result.testsRun}")
    print(f"Successi: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Fallimenti: {len(result.failures)}")
    print(f"Errori: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ TUTTI I TEST SONO PASSATI!")
        return 0
    else:
        print("\n❌ ALCUNI TEST SONO FALLITI!")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
