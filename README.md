<h1>Expense Splitter</h1>

<p>
  A backend system built to manage shared expenses within groups. 
  It tracks expenses, balances, wallets, and settlements with fully transparent and reliable calculations.
</p>

<hr>

<h2>Goal</h2>
<p>
  To build a reliable backend that automates expense splitting and maintains real-time balances for all group members.
</p>

<h2>Objectives</h2>
<ul>
  <li>Record expenses and split them accurately among group members</li>
  <li>Maintain individual user wallets with deposit and withdrawal support</li>
  <li>Track who owes whom and automate reimbursement logic</li>
  <li>Allow creation of groups and dynamic member management</li>
  <li>Provide clear transaction history for audits and transparency</li>
</ul>

<hr>

<h2>System Overview</h2>
<p>
  The system allows users to form groups, add expenses, split amounts based on members
  and manage balances through an integrated wallet system. Calculations remain accurate 
  even when members join or leave groups
</p>

<h3>Main Components</h3>
<ul>
  <li><strong>Users:</strong> Profiles linked to wallet accounts.</li>
  <li><strong>Groups:</strong> Dedicated spaces for splitting expenses.</li>
  <li><strong>Wallets:</strong> Track real-time user balances.</li>
  <li><strong>Transactions:</strong> Expenses, reimbursements, and settlements.</li>
</ul>

<hr>

<h2>Structure</h2>
<table>
  <tr>
    <th>File</th>
    <th>Description</th>
  </tr>
  <tr>
    <td><code>users.py</code></td>
    <td>Handles user creation and wallet linking.</td>
  </tr>
  <tr>
    <td><code>groups.py</code></td>
    <td>Manages groups and their members.</td>
  </tr>
  <tr>
    <td><code>wallet.py</code></td>
    <td>Manages wallet operations: deposit, withdrawal, and balance checks.</td>
  </tr>
  <tr>
    <td><code>transactions.py</code></td>
    <td>Handles expense entries and reimbursement logic.</td>
  </tr>
  <tr>
    <td><code>analytics.py</code></td>
    <td>Provides summaries and balance analysis.</td>
  </tr>
  <tr>
    <td><code>models.py</code></td>
    <td>Defines core data structures.</td>
  </tr>
  <tr>
    <td><code>db.py</code></td>
    <td>Database configuration and initialization.</td>
  </tr>
  <tr>
    <td><code>main.py</code></td>
    <td>Application entry point.</td>
  </tr>
</table>

<h2>Features</h2>
<ul>
  <li>Automated and accurate expense splitting.</li>
  <li>User wallets for handling deposits and withdrawals.</li>
  <li>Reimbursement and settlement calculation.</li>
  <li>Complete transaction history.</li>
  <li>Group-based expense categorization.</li>
</ul>
