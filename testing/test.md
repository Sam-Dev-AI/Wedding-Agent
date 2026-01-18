# Final System Verification Plan

## 1. Availability Logic (Hybrid)
- **Objective**: Verify that the system correctly identifies free slots based on "Explicit Available Blocks" or "Implicit Gaps".
- **Targets**:
    - **Jan 12**: Expect slots in 10am-1pm and 4pm-8pm. **CRITICAL**: Verify gap 1pm-4pm is BUSY.
    - **Jan 13**: Expect slots in 10am-1pm and 6pm-8pm.

## 2. Tools & Booking
- **Objective**: Verify that booking tools work and return the correct messages.
- **Tests**:
    - `book_tour`: Should return "success" message without links.
    - `book_manager_meeting`: Should return "success" message without links (in chat) but imply link in email.

## 3. RAG / Knowledge
- **Objective**: Verify the agent can answer venue questions.
- **Test**: Ask "What is the capacity?" and check if it uses the knowledge base.

## 4. Agent Tone & Protocols
- **Objective**: Verify the agent follows the new "Direct" and "Professional" guidelines.
- **Checks**:
    - No "Splendid" or "Exquisite".
    - No "Let me check..." filler.
    - No URL links in chat output.
    - Response time (simulated measure).

## 5. Alternative Dates
- **Objective**: Verify the agent suggests alternatives when a date is full.
- **Test**: Simulate a fully busy day and check the response message.
