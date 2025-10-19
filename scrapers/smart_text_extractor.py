"""
Smart Text Extractor - Advanced pattern matching for data extraction
Extracts pricing, policies, and operational data from text content
"""

import re
from typing import Dict, List, Optional, Any
from loguru import logger


class SmartTextExtractor:
    """Advanced pattern matching for data extraction"""

    # Comprehensive pattern library
    PATTERNS = {
        'insurance': [
            r'insurance[:\s]+€?\s*(\d+(?:\.\d{2})?)',
            r'coverage[:\s]+€?\s*(\d+(?:\.\d{2})?)',
            r'protection[:\s]+€?\s*(\d+(?:\.\d{2})?)\s*(?:/day|per day|daily)?',
            r'€\s*(\d+(?:\.\d{2})?)\s*(?:per day|daily)?\s*insurance',
            r'comprehensive\s+insurance[:\s]+€?\s*(\d+(?:\.\d{2})?)',
            r'insurance package[:\s]+€?\s*(\d+(?:\.\d{2})?)',
        ],
        'cleaning_fee': [
            r'cleaning[:\s]+€?\s*(\d+(?:\.\d{2})?)',
            r'cleaning fee[:\s]+€?\s*(\d+(?:\.\d{2})?)',
            r'final cleaning[:\s]+€?\s*(\d+(?:\.\d{2})?)',
            r'€\s*(\d+(?:\.\d{2})?)\s*cleaning',
            r'end of rental cleaning[:\s]+€?\s*(\d+(?:\.\d{2})?)',
        ],
        'booking_fee': [
            r'booking fee[:\s]+€?\s*(\d+(?:\.\d{2})?)',
            r'reservation fee[:\s]+€?\s*(\d+(?:\.\d{2})?)',
            r'service fee[:\s]+€?\s*(\d+(?:\.\d{2})?)',
            r'€\s*(\d+(?:\.\d{2})?)\s*booking fee',
        ],
        'min_rental_days': [
            r'minimum[:\s]+(\d+)\s*(?:day|night)s?',
            r'min\.?\s*rental[:\s]+(\d+)\s*(?:day|night)s?',
            r'at least\s+(\d+)\s*(?:day|night)s?',
            r'minimum stay[:\s]+(\d+)',
            r'min\.?\s*(\d+)\s*(?:day|night)s?',
        ],
        'mileage_limit': [
            r'(\d+)\s*km\s*(?:per day|daily|/day)',
            r'mileage[:\s]+(\d+)\s*km',
            r'kilometers included[:\s]+(\d+)',
            r'(\d+)\s*kilometers?\s*(?:per day|daily)',
        ],
        'mileage_cost': [
            r'€?\s*(\d+(?:\.\d{2})?)\s*(?:per|/)?\s*km',
            r'additional\s+km[:\s]+€?\s*(\d+(?:\.\d{2})?)',
            r'extra\s+kilometer[:\s]+€?\s*(\d+(?:\.\d{2})?)',
        ],
        'deposit': [
            r'deposit[:\s]+€?\s*(\d+(?:,?\d{3})*(?:\.\d{2})?)',
            r'security deposit[:\s]+€?\s*(\d+(?:,?\d{3})*(?:\.\d{2})?)',
            r'€\s*(\d+(?:,?\d{3})*(?:\.\d{2})?)\s*deposit',
        ],
        'one_way_fee': [
            r'one[- ]way[:\s]+€?\s*(\d+(?:\.\d{2})?)',
            r'different\s+location[:\s]+€?\s*(\d+(?:\.\d{2})?)',
            r'drop[- ]off\s+fee[:\s]+€?\s*(\d+(?:\.\d{2})?)',
        ],
        'weekend_premium': [
            r'weekend[:\s]+\+?\s*(\d+)%',
            r'saturday\s+\+?\s*(\d+)%',
            r'(\d+)%\s*weekend surcharge',
        ],
        'driver_age_min': [
            r'minimum\s+age[:\s]+(\d+)',
            r'driver.*?(\d+)\s+years',
            r'at least\s+(\d+)\s+years',
            r'(\d+)\+\s*years',
        ],
        'cancellation_policy': [
            r'(free cancellation)',
            r'(non-refundable)',
            r'(flexible cancellation)',
            r'cancel.*?(\d+)\s*days',
        ],
    }

    @classmethod
    def extract_all_fields(cls, text: str) -> Dict[str, Any]:
        """Extract all possible fields from text"""
        results = {}

        # Extract numeric fields
        for field_name, patterns in cls.PATTERNS.items():
            value = cls._extract_numeric_field(text, patterns, field_name)
            if value is not None:
                results[field_name] = value

        # Extract boolean/string fields
        results.update(cls._extract_boolean_fields(text))

        return results

    @classmethod
    def _extract_numeric_field(cls, text: str, patterns: List[str], field_name: str) -> Optional[float]:
        """Extract numeric value using pattern list"""
        for pattern in patterns:
            try:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value_str = match.group(1)
                    # Remove commas from numbers
                    value_str = value_str.replace(',', '')

                    try:
                        value = float(value_str)

                        # Validate based on field type
                        if cls._is_valid_value(field_name, value):
                            logger.debug(f"Extracted {field_name}: {value}")
                            return value
                    except ValueError:
                        continue
            except Exception as e:
                logger.debug(f"Pattern match failed for {field_name}: {e}")
                continue

        return None

    @classmethod
    def _is_valid_value(cls, field_name: str, value: float) -> bool:
        """Validate extracted value is reasonable"""
        ranges = {
            'insurance': (1, 150),  # €1-150 per day
            'cleaning_fee': (10, 500),  # €10-500
            'booking_fee': (0, 200),  # €0-200
            'min_rental_days': (1, 30),  # 1-30 days
            'mileage_limit': (50, 1000),  # 50-1000 km/day
            'mileage_cost': (0.05, 5.0),  # €0.05-5 per km
            'deposit': (100, 5000),  # €100-5000
            'one_way_fee': (0, 500),  # €0-500
            'weekend_premium': (0, 100),  # 0-100%
            'driver_age_min': (18, 30),  # 18-30 years
        }

        if field_name in ranges:
            min_val, max_val = ranges[field_name]
            return min_val <= value <= max_val

        return True

    @classmethod
    def _extract_boolean_fields(cls, text: str) -> Dict[str, Any]:
        """Extract boolean and string fields"""
        results = {}

        # Fuel policy
        if 'full to full' in text.lower() or 'full-to-full' in text.lower():
            results['fuel_policy'] = 'Full to Full'
        elif 'same to same' in text.lower():
            results['fuel_policy'] = 'Same to Same'
        elif 'pre-purchase' in text.lower() or 'prepaid' in text.lower():
            results['fuel_policy'] = 'Pre-purchase'

        # One-way rental
        if any(phrase in text.lower() for phrase in ['one-way', 'one way', 'different location']):
            results['one_way_rental_allowed'] = True

        # Unlimited mileage
        if 'unlimited' in text.lower() and any(word in text.lower() for word in ['mileage', 'km', 'kilometer']):
            results['mileage_unlimited'] = True

        # Cancellation
        if 'free cancellation' in text.lower():
            results['free_cancellation'] = True
        elif 'non-refundable' in text.lower():
            results['free_cancellation'] = False

        # Additional drivers
        if re.search(r'additional driver[:\s]+€?\s*(\d+)', text, re.IGNORECASE):
            match = re.search(r'additional driver[:\s]+€?\s*(\d+)', text, re.IGNORECASE)
            results['additional_driver_fee'] = float(match.group(1))

        return results

    @classmethod
    def extract_features(cls, text: str) -> List[str]:
        """Extract vehicle features from text"""
        features = []

        feature_keywords = {
            'air_conditioning': ['air conditioning', 'a/c', 'climate control'],
            'gps': ['gps', 'navigation', 'sat nav'],
            'wifi': ['wifi', 'wi-fi', 'internet'],
            'solar_panel': ['solar', 'solar panel'],
            'heating': ['heating', 'heater'],
            'shower': ['shower', 'bathroom'],
            'toilet': ['toilet', 'wc'],
            'kitchen': ['kitchen', 'kitchenette'],
            'automatic': ['automatic', 'auto transmission'],
            'manual': ['manual transmission'],
            'cruise_control': ['cruise control'],
            'bike_rack': ['bike rack', 'bicycle rack'],
            'roof_rack': ['roof rack'],
            'awning': ['awning'],
            '4wd': ['4wd', '4x4', 'all-wheel'],
        }

        text_lower = text.lower()
        for feature, keywords in feature_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                features.append(feature)

        return features

    @classmethod
    def extract_pricing_notes(cls, text: str) -> List[str]:
        """Extract pricing notes and conditions"""
        notes = []

        # Common pricing notes patterns
        note_patterns = [
            r'price(?:s)?\s+(?:include|including)[:\s]+([^.]+)',
            r'price(?:s)?\s+(?:exclude|excluding)[:\s]+([^.]+)',
            r'additional\s+costs?[:\s]+([^.]+)',
            r'please note[:\s]+([^.]+)',
            r'important[:\s]+([^.]+)',
        ]

        for pattern in note_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                note = match.group(1).strip()
                if len(note) > 10 and len(note) < 200:
                    notes.append(note)

        return notes[:5]  # Return top 5 notes


if __name__ == "__main__":
    print("Smart Text Extractor")
    print("=" * 50)

    # Example usage
    sample_text = """
    Pricing Information:
    - Base rate: €85 per night
    - Insurance: €15 per day
    - Cleaning fee: €75
    - Minimum rental: 3 days
    - Mileage: 200 km per day included
    - Additional km: €0.25/km
    - One-way rental: €100 fee

    Policies:
    - Full to full fuel policy
    - Free cancellation up to 48 hours
    - Minimum driver age: 25 years
    """

    extractor = SmartTextExtractor()
    results = extractor.extract_all_fields(sample_text)

    print("\nExtracted Data:")
    for key, value in results.items():
        print(f"  {key}: {value}")
