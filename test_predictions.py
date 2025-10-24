"""
Test script to verify ML model predictions are properly normalized between 0-100%
"""

import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ml_service import get_model

def test_predictions():
    print("=" * 70)
    print("TESTING ML MODEL PREDICTIONS - SCORE NORMALIZATION")
    print("=" * 70)
    
    # Test case: Sample from user's request
    print("\n[TEST] Sample input (N=90, P=42, K=43, temp=21, humidity=82, ph=6.5, rainfall=202)")
    
    try:
        model = get_model()
        predictions = model.predict(N=90, P=42, K=43, temperature=21, humidity=82, ph=6.5, rainfall=202)
        
        print("\n[RESULTS]")
        all_valid = True
        for i, pred in enumerate(predictions, 1):
            score = pred['suitability_score']
            is_valid = 0 <= score <= 100
            status = "VALID" if is_valid else "INVALID"
            
            print("{0}. {1}: {2}% [{3}]".format(i, pred['crop_name'], score, status))
            
            if not is_valid:
                all_valid = False
                print("   ERROR: Score outside valid range!")
        
        if all_valid:
            print("\n" + "=" * 70)
            print("SUCCESS: All scores are between 0-100%")
            print("=" * 70)
        else:
            print("\nFAILED: Some scores are outside valid range!")
            return False
            
    except Exception as e:
        print("\nFAILED with exception: {0}".format(str(e)))
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = test_predictions()
        sys.exit(0 if success else 1)
    except Exception as e:
        print("\nERROR: {0}".format(str(e)))
        sys.exit(1)
