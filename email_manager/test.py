from email_reader import extract_meeting_info

def test_email_reader():
    print("\n--- Testing Email Reader Functions ---\n")
    
    # Test Case 1: Normal email with all information
    print("Test Case 1: Normal email with complete information")
    email_1 = """
    Hey Team,
    We need to discuss the upcoming product launch. Let's have a meeting on February 22, 2025, at 3 PM.
    This is extremely urgent and critical for the project.
    Best,
    John
    """
    result_1 = extract_meeting_info(email_1)
    print("Extraction Result 1:", result_1)
    
    # Test Case 2: Email without explicit time
    print("\nTest Case 2: Email without explicit time")
    email_2 = """
    Hi everyone,
    Let's meet next Monday, March 15, 2025, to review the quarterly results.
    Regards,
    Sarah
    """
    result_2 = extract_meeting_info(email_2)
    print("Extraction Result 2:", result_2)
    
    # Test Case 3: Email with minimal information
    print("\nTest Case 3: Email with minimal information")
    email_3 = """
    Quick sync tomorrow?
    -Tom
    """
    result_3 = extract_meeting_info(email_3)
    print("Extraction Result 3:", result_3)

if __name__ == "__main__":
    test_email_reader()
