Feature: Goibibo Holidays end to end booking journey
  As an automation tester
  I want one complete BDD flow from Goibibo homepage to card details boundary
  So that the full business journey is proven separately

  @e2e @positive
  Scenario: TC_E2E_001 - End to end holiday booking until card details boundary
    When I execute the complete end to end Goibibo Holidays journey for case "TC_E2E_001"
    Then the end to end journey should stop at card details boundary
