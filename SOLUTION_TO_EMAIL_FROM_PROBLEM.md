# SOLUTION: Fixing the "Email from:" Display in Dynamics 365

This document details the successful solution to the problem where the Dynamics 365 timeline incorrectly displayed "Email from: Closed" instead of the actual sender's name.

## 1. The Root Cause

The initial investigation into fields like `sender`, `submittedby`, and `_emailsender_value` was a dead end. The core issue was a misunderstanding of how Dynamics 365 handles email participants (From, To, Cc, Bcc).

The "Email from:" display is not controlled by a simple string field. It is determined by a related **Activity Party** record. This relationship must be established **at the moment the email is created** via a `POST` request. Attempting to set or update this relationship after creation via a `PATCH` request will fail.

The correct way to define these participants is by using the navigation property named `email_activity_parties`.

## 2. The Correct API Payload

To solve the problem, the payload for the `POST /api/data/v9.2/emails` request must be structured to include an `email_activity_parties` array.

Within this array, each object represents a participant. The `participationtypemask` field is used to define their role:

*   `participationtypemask: 1` = Sender (From)
*   `participationtypemask: 2` = Recipient (To)
*   `participationtypemask: 3` = CC Recipient
*   `participationtypemask: 4` = BCC Recipient

### Example of a Successful Payload

This payload correctly creates an email from the RingCentral contact to the System User, which solves the display issue.

```json
{
    "subject": "This is a correctly imported email",
    "description": "The body of the email with <br> HTML formatting.",
    "regardingobjectid_contact@odata.bind": "/contacts(6a219814-dc41-f011-b4cb-7c1e52168e20)",
    "directioncode": false,
    "actualstart": "2025-04-01T10:00:00Z",
    "actualend": "2025-04-01T10:00:00Z",
    "senton": "2025-04-01T10:00:00Z",

    "email_activity_parties": [
        {
            "partyid_contact@odata.bind": "/contacts(6a219814-dc41-f011-b4cb-7c1e52168e20)",
            "participationtypemask": 1
        },
        {
            "partyid_systemuser@odata.bind": "/systemusers(5794f83f-9b37-f011-8c4e-000d3a9c4367)",
            "participationtypemask": 2
        }
    ]
}
```

## 3. The Final Two-Step Process

With the correct payload identified, the final, reliable import process for each email is:

1.  **Create the Email:** Send a `POST` request to the `/emails` endpoint with the payload structured as shown above. This correctly creates the email in a default "Open" state with the sender's name properly displayed.

2.  **Update the Status:** After a successful creation, send a `PATCH` request to the `/emails({new_email_id})` endpoint to update the status. The payload for this is:
    ```json
    {
        "statecode": 1,
        "statuscode": 4
    }
    ```
    This changes the email's status to "Closed" with a reason of "Received," which completes the process.

By following this two-step method, all aspects of the email (Sender Display, HTML Formatting, and Status) are set correctly. 