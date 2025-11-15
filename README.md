<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
</head>

<body>

    <h1>Expense Splitter</h1>
    <p>
        A backend system built to manage shared expenses within groups.
        It tracks expenses, balances, wallets and settlements with clear and reliable calculations.
    </p>


    <h2>Goal</h2>
    <p>
        To build a dependable backend that automates expense splitting and maintains accurate real-time balances for all group members.
    </p>


    <h2>Objectives</h2>
    <ul>
        <li>Record expenses and split them accurately among group members</li>
        <li>Maintain individual user wallets with deposit and withdrawal support</li>
        <li>Track who owes whom and automate reimbursement logic</li>
        <li>Allow creation of groups and flexible member management</li>
        <li>Provide clear transaction history for audits and transparency</li>
    </ul>


    <h2>System Overview</h2>
    <p>
        The system allows users to form groups, add shared expenses, and let the backend handle the splitting logic.
        Each user has a linked wallet, and all credit/debit movements are updated automatically.
        Calculations remain consistent even when new members join or existing members leave.
    </p>

    <h3>Main Components</h3>
    <ul>
        <li><strong>Users:</strong> Profiles linked to individual wallets.</li>
        <li><strong>Groups:</strong> Separate spaces for managing shared expenses.</li>
        <li><strong>Wallets:</strong> Maintain real-time balances for each user.</li>
        <li><strong>Transactions:</strong> Expense entries, reimbursements, and settlements.</li>
    </ul>


    <h2>Structure</h2>
    <ul>
        <li><code>users.py</code> — Manages user creation, details and wallet association.</li>
        <li><code>groups.py</code> — Handles group creation, membership and operations.</li>
        <li><code>wallet.py</code> — Controls deposits, withdrawals and balance updates.</li>
        <li><code>transactions.py</code> — Stores expenses, splits amounts and manages reimbursements.</li>
        <li><code>analytics.py</code> — Generates summaries and balance breakdowns.</li>
        <li><code>models.py</code> — Defines core data models used across the project.</li>
        <li><code>db.py</code> — Database configuration and initialization.</li>
        <li><code>main.py</code> — Application entry point.</li>
    </ul>


    <h2>Features</h2>
    <ul>
        <li>Automated and accurate expense splitting</li>
        <li>Wallet-based balance management</li>
        <li>Reimbursement and settlement tracking</li>
        <li>Organized and complete transaction history</li>
        <li>Group-level expense management</li>
    </ul>

</body>
</html>
