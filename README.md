<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
</head>

<body>

    <h1>Expense Splitter</h1>
    <p>
        A backend system built to manage shared group expenses. 
        It tracks expenses, balances, wallets, and settlements with accurate calculations.
    </p>

    <hr>

    <h2>Goal</h2>
    <p>
        To build a reliable backend system that automatically splits expenses 
        and maintains accurate balances for all members in a group.
    </p>

    <hr>

    <h2>Objectives</h2>
    <ul>
        <li>Record expenses and split the amount among group members.</li>
        <li>Create and manage groups efficiently.</li>
        <li>Maintain individual user wallets for balance tracking.</li>
        <li>Handle reimbursements and settlements automatically.</li>
        <li>Provide a clear transaction history for transparency.</li>
    </ul>

    <hr>

    <h2>System Overview</h2>
    <p>
        The system enables users to form groups, add shared expenses, and let the backend 
        calculate splits. Each user has a wallet, and every debit/credit is updated 
        automatically. All balances remain consistent even as new members join or existing 
        members leave.
    </p>

    <h3>Main Components</h3>
    <ul>
        <li><strong>Users:</strong> Profiles with linked wallets.</li>
        <li><strong>Groups:</strong> Manage members and shared expenses.</li>
        <li><strong>Wallets:</strong> Track user balances.</li>
        <li><strong>Transactions:</strong> Record expenses, splits, and settlements.</li>
    </ul>

    <hr>

    <h2>Project Structure</h2>
    <ul>
        <li><code>users.py</code> – Handles user creation and wallet mapping.</li>
        <li><code>groups.py</code> – Manages groups and member activities.</li>
        <li><code>wallet.py</code> – Controls balance updates, deposits, withdrawals.</li>
        <li><code>transactions.py</code> – Handles expense splits and settlements.</li>
        <li><code>analytics.py</code> – Summary and balance breakdown.</li>
        <li><code>models.py</code> – Core data models.</li>
        <li><code>db.py</code> – Database initialization.</li>
        <li><code>main.py</code> – Entry point of the application.</li>
    </ul>

    <hr>

    <h2>Features</h2>
    <ul>
        <li>Accurate and automated expense splitting.</li>
        <li>User wallets with live balance updates.</li>
        <li>Reimbursing and settlement handling.</li>
        <li>Complete transaction history.</li>
        <li>Group expense management.</li>
    </ul>

</body>
</html>
