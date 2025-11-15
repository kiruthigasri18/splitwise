<h1>Expense Splitter</h1>

<p>
  A backend system built to manage shared expenses within groups. 
  It tracks expenses, balances, wallets and settlements with fully transparent and reliable calculations.
</p>



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


<h2>Structure</h2>


<ul>
  <li><code>users.py</code> — Handles user creation, user details, and wallet linking.</li>
  <li><code>groups.py</code> — Manages group creation, members, and group-level operations.</li>
  <li><code>wallet.py</code> — Controls wallet functions such as deposits, withdrawals, and balance updates.</li>
  <li><code>transactions.py</code> — Stores expenses, splits amounts, and calculates reimbursements.</li>
  <li><code>analytics.py</code> — Generates summaries and overall balance reports.</li>
  <li><code>models.py</code> — Contains the core data models used across the system.</li>
  <li><code>db.py</code> — Database configuration and setup.</li>
  <li><code>main.py</code> — The entry point to run the application.</li>
</ul>



<h2>Features</h2>
<ul>
  <li>Automated and accurate expense splitting.</li>
  <li>User wallets for handling deposits and withdrawals.</li>
  <li>Reimbursement and settlement calculation.</li>
  <li>Complete transaction history.</li>
  <li>Group-based expense categorization.</li>
</ul>
