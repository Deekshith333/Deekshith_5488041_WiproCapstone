Feature: Goibibo Holidays positive and negative test cases
  As an automation tester
  I want separate positive and negative BDD scenarios
  So that validations and happy paths are reported clearly

  @positive @traveller
  Scenario: TC_POS_001 - Valid traveller data for Hyderabad to Goa
    When I execute the positive or negative Goibibo Holidays journey for case "TC_POS_001"
    Then the positive journey should stop at card details boundary

  @positive @traveller
  Scenario: TC_POS_002 - Valid traveller data for Mumbai to Rajasthan
    When I execute the positive or negative Goibibo Holidays journey for case "TC_POS_002"
    Then the positive journey should stop at card details boundary

  @positive @route @filter
  Scenario: TC_POS_003 - Bengaluru to Kerala with category filter
    When I execute the positive or negative Goibibo Holidays journey for case "TC_POS_003"
    Then the positive journey should stop at card details boundary

  @positive @route @filter
  Scenario: TC_POS_004 - Chennai to Andaman with hotel filter
    When I execute the positive or negative Goibibo Holidays journey for case "TC_POS_004"
    Then the positive journey should stop at card details boundary

  @positive @route @filter
  Scenario: TC_POS_005 - Pune to Himachal Pradesh with duration filter
    When I execute the positive or negative Goibibo Holidays journey for case "TC_POS_005"
    Then the positive journey should stop at card details boundary

  @negative @validation
  Scenario: TC_NEG_001 - Missing first name validation
    When I execute the positive or negative Goibibo Holidays journey for case "TC_NEG_001"
    Then the negative validation should be reported

  @negative @validation
  Scenario: TC_NEG_002 - Invalid mobile validation
    When I execute the positive or negative Goibibo Holidays journey for case "TC_NEG_002"
    Then the negative validation should be reported
