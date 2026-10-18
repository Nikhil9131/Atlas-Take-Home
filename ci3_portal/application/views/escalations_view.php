<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Senior Analyst Escalation Queue | Project Atlas</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            /* Vanilla Palette */
            --bg-base: #f6f2ea;
            --bg-surface: #ffffff;
            --bg-card: rgba(255, 255, 255, 0.9);
            --bg-input: #ffffff;
            --bg-tertiary: #ede5d5;
            
            --border-subtle: rgba(160, 130, 95, 0.22);
            --border-medium: rgba(140, 110, 75, 0.35);
            --border-glow: rgba(217, 119, 6, 0.35);
            
            --text-primary: #1f1a16;
            --text-secondary: #52473e;
            --text-muted: #7d7064;
            
            --vanilla-cream: #faf5eb;
            --vanilla-custard: #faeed7;
            --caramel-primary: #b45309;
            --caramel-hover: #92400e;
            --caramel-glow: rgba(180, 83, 9, 0.16);
            --warm-gold: #d97706;
            
            --emerald-primary: #15803d;
            --emerald-bg: #edf8f0;
            --emerald-border: rgba(21, 128, 61, 0.3);
            
            --amber-primary: #b45309;
            --amber-bg: #fef7ea;
            --amber-border: rgba(180, 83, 9, 0.3);
            
            --rose-primary: #b91c1c;
            --rose-bg: #fdf2f2;
            --rose-border: rgba(185, 28, 28, 0.3);

            --font-sans: 'Plus Jakarta Sans', sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
            --radius-md: 10px;
            --radius-lg: 14px;
            --radius-xl: 18px;
            --transition-smooth: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
            --shadow-subtle: 0 4px 18px rgba(120, 90, 60, 0.05);
            --shadow-card: 0 8px 24px rgba(100, 70, 45, 0.07);
            --shadow-elevated: 0 16px 40px rgba(80, 55, 35, 0.12);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            background-color: var(--bg-base);
            background-image: 
                radial-gradient(circle at 12% 10%, rgba(245, 222, 179, 0.5) 0%, transparent 45%),
                radial-gradient(circle at 88% 88%, rgba(235, 205, 160, 0.4) 0%, transparent 50%),
                radial-gradient(circle at 50% 50%, rgba(255, 252, 246, 0.7) 0%, transparent 60%);
            color: var(--text-primary);
            font-family: var(--font-sans);
            min-height: 100vh;
            padding: 2rem 2.5rem;
            -webkit-font-smoothing: antialiased;
        }

        /* Header Navigation */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1.25rem;
            border-bottom: 1px solid var(--border-subtle);
        }

        .header-title-group h1 {
            font-size: 1.6rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            display: flex;
            align-items: center;
            gap: 0.65rem;
            color: var(--text-primary);
        }

        .header-title-group p {
            color: var(--text-muted);
            font-size: 0.85rem;
            margin-top: 0.35rem;
        }

        .back-nav-btn {
            background: #ffffff;
            border: 1px solid var(--border-subtle);
            color: var(--caramel-primary);
            padding: 0.55rem 1.15rem;
            border-radius: var(--radius-md);
            font-size: 0.84rem;
            font-weight: 600;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            transition: var(--transition-smooth);
            box-shadow: var(--shadow-subtle);
        }

        .back-nav-btn:hover {
            background: var(--vanilla-custard);
            border-color: var(--caramel-primary);
            color: var(--caramel-hover);
            transform: translateX(-2px);
            box-shadow: var(--shadow-card);
        }

        /* KPI Metric Cards */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1.25rem;
            margin-bottom: 2rem;
        }

        .metric-card {
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 1.25rem 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
            box-shadow: var(--shadow-card);
            position: relative;
            overflow: hidden;
            transition: var(--transition-smooth);
        }

        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-elevated);
        }

        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4.5px;
            height: 100%;
        }

        .metric-card.card-caramel::before { background: var(--caramel-primary); }
        .metric-card.card-rose::before { background: var(--rose-primary); }
        .metric-card.card-emerald::before { background: var(--emerald-primary); }
        .metric-card.card-amber::before { background: var(--warm-gold); }

        .metric-label {
            font-size: 0.74rem;
            text-transform: uppercase;
            font-weight: 700;
            letter-spacing: 0.05em;
            color: var(--text-muted);
        }

        .metric-value {
            font-size: 1.75rem;
            font-weight: 800;
            font-family: var(--font-mono);
            color: var(--text-primary);
        }

        .metric-sub {
            font-size: 0.72rem;
            color: var(--text-muted);
        }

        /* Search & Filter Toolbar */
        .toolbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            gap: 1rem;
        }

        .search-input-wrap {
            position: relative;
            max-width: 400px;
            width: 100%;
        }

        .search-input {
            width: 100%;
            background: var(--bg-input);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 0.6rem 0.85rem 0.6rem 2.2rem;
            font-size: 0.84rem;
            color: var(--text-primary);
            outline: none;
            font-family: var(--font-sans);
            transition: var(--transition-smooth);
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.02);
        }

        .search-input:focus {
            border-color: var(--caramel-primary);
            box-shadow: 0 0 0 3px var(--caramel-glow);
        }

        .search-svg {
            position: absolute;
            left: 0.75rem;
            top: 50%;
            transform: translateY(-50%);
            width: 14px;
            height: 14px;
            color: var(--text-muted);
        }

        .filter-tabs {
            display: flex;
            gap: 0.4rem;
        }

        .filter-btn {
            background: var(--bg-tertiary);
            border: 1px solid var(--border-subtle);
            color: var(--text-secondary);
            padding: 0.4rem 0.85rem;
            border-radius: var(--radius-md);
            font-size: 0.76rem;
            font-weight: 600;
            cursor: pointer;
            transition: var(--transition-smooth);
        }

        .filter-btn.active, .filter-btn:hover {
            background: var(--vanilla-custard);
            color: var(--caramel-primary);
            border-color: rgba(180, 83, 9, 0.4);
        }

        /* Table Card */
        .table-panel {
            background: #ffffff;
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-xl);
            overflow: hidden;
            box-shadow: var(--shadow-card);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.86rem;
            text-align: left;
        }

        th {
            background: var(--vanilla-cream);
            color: var(--text-muted);
            text-transform: uppercase;
            font-size: 0.72rem;
            letter-spacing: 0.06em;
            font-weight: 700;
            padding: 1.1rem 1.25rem;
            border-bottom: 1px solid var(--border-subtle);
        }

        td {
            padding: 1rem 1.25rem;
            border-bottom: 1px solid var(--border-subtle);
            vertical-align: middle;
        }

        tbody tr {
            cursor: pointer;
            transition: var(--transition-smooth);
        }

        tbody tr:hover {
            background: var(--vanilla-cream);
        }

        tbody tr:last-child td {
            border-bottom: none;
        }

        .ticket-id-chip {
            font-family: var(--font-mono);
            font-size: 0.82rem;
            font-weight: 700;
            color: var(--caramel-primary);
            background: var(--vanilla-custard);
            padding: 0.2rem 0.55rem;
            border-radius: 4px;
            border: 1px solid rgba(180, 83, 9, 0.25);
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
        }

        .status-badge {
            padding: 0.25rem 0.65rem;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            display: inline-block;
        }

        .status-open {
            background: var(--rose-bg);
            color: var(--rose-primary);
            border: 1px solid var(--rose-border);
        }

        .status-resolved {
            background: var(--emerald-bg);
            color: var(--emerald-primary);
            border: 1px solid var(--emerald-border);
        }

        .confidence-pill {
            font-family: var(--font-mono);
            font-weight: 700;
            font-size: 0.82rem;
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
            background: var(--vanilla-custard);
            color: var(--caramel-primary);
            border: 1px solid rgba(180, 83, 9, 0.2);
        }

        /* Ticket Detail Modal */
        .modal-overlay {
            position: fixed;
            inset: 0;
            background: rgba(30, 24, 18, 0.55);
            backdrop-filter: blur(8px);
            z-index: 100;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 1.5rem;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease;
        }

        .modal-overlay.open {
            opacity: 1;
            pointer-events: auto;
        }

        .modal-window {
            background: #ffffff;
            border: 1px solid var(--border-medium);
            border-radius: var(--radius-xl);
            max-width: 650px;
            width: 100%;
            padding: 2rem;
            box-shadow: var(--shadow-elevated);
            transform: translateY(12px);
            transition: var(--transition-smooth);
        }

        .modal-overlay.open .modal-window {
            transform: translateY(0);
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1.5rem;
        }

        .modal-close-btn {
            background: var(--bg-tertiary);
            border: 1px solid var(--border-subtle);
            color: var(--text-secondary);
            width: 32px;
            height: 32px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 1.2rem;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: var(--transition-smooth);
        }

        .modal-close-btn:hover {
            background: var(--vanilla-custard);
            color: var(--caramel-primary);
        }

        .kv-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.85rem;
            margin-bottom: 1.25rem;
        }

        .kv-card {
            background: var(--vanilla-cream);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 0.75rem 1rem;
        }

        .kv-label {
            font-size: 0.68rem;
            text-transform: uppercase;
            font-weight: 700;
            color: var(--text-muted);
        }

        .kv-val {
            font-size: 0.88rem;
            font-weight: 600;
            margin-top: 0.25rem;
            color: var(--text-primary);
        }

        .detail-block {
            background: var(--vanilla-cream);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 1rem;
            margin-bottom: 1rem;
            font-size: 0.86rem;
            line-height: 1.6;
        }

        /* Toast */
        .toast-box {
            position: fixed;
            bottom: 1.5rem;
            right: 1.5rem;
            background: #ffffff;
            border: 1.5px solid var(--caramel-primary);
            color: var(--text-primary);
            padding: 0.75rem 1.25rem;
            border-radius: var(--radius-md);
            font-size: 0.82rem;
            font-weight: 600;
            box-shadow: var(--shadow-elevated);
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
            z-index: 120;
        }
        .toast-box.show { opacity: 1; }

        @media (max-width: 900px) {
            .metrics-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body>

    <!-- Header Navigation -->
    <div class="header">
        <div class="header-title-group">
            <h1>
                <span>🚨 Senior Analyst Escalation Queue</span>
            </h1>
            <p>
                Persisted relational queue for inquiries with low confidence (&lt;70%), boundary ambiguities, or unanswerable requests.
            </p>
        </div>

        <a href="<?php echo site_url('chat'); ?>" class="back-nav-btn">
            <span>← Return to Research Copilot</span>
        </a>
    </div>

    <?php
        $total_tickets = count($escalations);
        $open_tickets = 0;
        $resolved_tickets = 0;
        $total_conf = 0;

        foreach ($escalations as $t) {
            if ($t['status'] === 'open') $open_tickets++;
            if ($t['status'] === 'resolved') $resolved_tickets++;
            $total_conf += (float)$t['confidence'];
        }
        $avg_conf = $total_tickets > 0 ? round(($total_conf / $total_tickets) * 100) : 0;
    ?>

    <!-- KPI Metric Cards Grid -->
    <div class="metrics-grid">
        <div class="metric-card card-caramel">
            <span class="metric-label">Total Escalations</span>
            <span class="metric-value"><?php echo $total_tickets; ?></span>
            <span class="metric-sub">Client: <?php echo html_escape($active_client_name); ?> (<?php echo html_escape($active_client_id); ?>)</span>
        </div>
        <div class="metric-card card-rose">
            <span class="metric-label">Open / Action Required</span>
            <span class="metric-value"><?php echo $open_tickets; ?></span>
            <span class="metric-sub">Pending analyst review & sign-off</span>
        </div>
        <div class="metric-card card-emerald">
            <span class="metric-label">Resolved Tickets</span>
            <span class="metric-value"><?php echo $resolved_tickets; ?></span>
            <span class="metric-sub">Synthesized by senior research team</span>
        </div>
        <div class="metric-card card-amber">
            <span class="metric-label">Average Confidence</span>
            <span class="metric-value"><?php echo $avg_conf; ?>%</span>
            <span class="metric-sub">Trigger threshold: &lt; 70% confidence</span>
        </div>
    </div>

    <!-- Search & Filter Controls -->
    <div class="toolbar">
        <div class="search-input-wrap">
            <svg class="search-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            <input type="text" id="ticketSearch" class="search-input" placeholder="Search by Ticket ID, question, or reason..." oninput="filterTickets()">
        </div>

        <div class="filter-tabs">
            <button class="filter-btn active" onclick="setFilter('all', this)">All (<?php echo $total_tickets; ?>)</button>
            <button class="filter-btn" onclick="setFilter('open', this)">Open (<?php echo $open_tickets; ?>)</button>
            <button class="filter-btn" onclick="setFilter('resolved', this)">Resolved (<?php echo $resolved_tickets; ?>)</button>
        </div>
    </div>

    <!-- Escalations Table Card -->
    <div class="table-panel">
        <table>
            <thead>
                <tr>
                    <th>Ticket ID</th>
                    <th>Inquiry Question</th>
                    <th>Escalation Rationale</th>
                    <th>Confidence</th>
                    <th>Status</th>
                    <th>Timestamp</th>
                </tr>
            </thead>
            <tbody id="ticketsTbody">
                <?php if (empty($escalations)): ?>
                    <tr>
                        <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 3rem 1rem;">
                            No escalation tickets logged for active client <?php echo html_escape($active_client_id); ?>.
                        </td>
                    </tr>
                <?php else: ?>
                    <?php foreach ($escalations as $ticket): ?>
                        <tr class="ticket-row" 
                            data-id="<?php echo html_escape($ticket['id']); ?>" 
                            data-status="<?php echo html_escape($ticket['status']); ?>" 
                            data-question="<?php echo html_escape($ticket['question']); ?>" 
                            data-reason="<?php echo html_escape($ticket['reason']); ?>" 
                            data-confidence="<?php echo round($ticket['confidence'] * 100); ?>%"
                            data-time="<?php echo html_escape(substr($ticket['created_at'], 0, 19)); ?>"
                            onclick="inspectTicket(this)">
                            
                            <td>
                                <span class="ticket-id-chip">
                                    <?php echo html_escape($ticket['id']); ?>
                                </span>
                            </td>
                            <td style="max-width: 340px; font-weight: 500;">
                                <?php echo html_escape($ticket['question']); ?>
                            </td>
                            <td style="color: var(--caramel-primary); max-width: 300px; font-size: 0.82rem; font-weight: 500;">
                                <?php echo html_escape($ticket['reason']); ?>
                            </td>
                            <td>
                                <span class="confidence-pill">
                                    <?php echo round($ticket['confidence'] * 100); ?>%
                                </span>
                            </td>
                            <td>
                                <span class="status-badge <?php echo $ticket['status'] === 'resolved' ? 'status-resolved' : 'status-open'; ?>">
                                    <?php echo html_escape($ticket['status']); ?>
                                </span>
                            </td>
                            <td style="color: var(--text-muted); font-size: 0.78rem; font-family: var(--font-mono);">
                                <?php echo html_escape(substr($ticket['created_at'], 0, 19)); ?>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                <?php endif; ?>
            </tbody>
        </table>
    </div>

    <!-- Ticket Detail Modal -->
    <div class="modal-overlay" id="ticketModal" onclick="closeModalOnOverlay(event)">
        <div class="modal-window">
            <div class="modal-header">
                <div>
                    <h3 id="modalTicketId" style="font-family: var(--font-mono); color: var(--caramel-primary);">ESC-2025-001</h3>
                    <p style="font-size: 0.78rem; color: var(--text-muted); margin-top: 0.2rem;">Relational Database Ticket Record</p>
                </div>
                <button class="modal-close-btn" onclick="closeModal()">×</button>
            </div>

            <div class="kv-grid">
                <div class="kv-card">
                    <div class="kv-label">Assigned Client</div>
                    <div class="kv-val"><?php echo html_escape($active_client_name); ?> (<?php echo html_escape($active_client_id); ?>)</div>
                </div>
                <div class="kv-card">
                    <div class="kv-label">Ticket Status</div>
                    <div class="kv-val" id="modalTicketStatus">OPEN</div>
                </div>
                <div class="kv-card">
                    <div class="kv-label">Copilot Confidence</div>
                    <div class="kv-val" id="modalTicketConf" style="color: var(--warm-gold);">40%</div>
                </div>
                <div class="kv-card">
                    <div class="kv-label">Created At</div>
                    <div class="kv-val" id="modalTicketTime" style="font-family: var(--font-mono); font-size: 0.8rem;">2025-05-10</div>
                </div>
            </div>

            <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; color: var(--text-muted); margin-bottom: 0.4rem;">
                Inquiry Question:
            </div>
            <div class="detail-block" id="modalTicketQuestion" style="font-weight: 500;">
                Question text...
            </div>

            <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; color: var(--text-muted); margin-bottom: 0.4rem;">
                Escalation Rationale:
            </div>
            <div class="detail-block" id="modalTicketReason" style="color: var(--caramel-primary); border-left: 3.5px solid var(--caramel-primary); background: var(--vanilla-custard);">
                Reason text...
            </div>

            <div style="display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 1.5rem;">
                <button class="filter-btn" onclick="copyModalTicketId()">📋 Copy Ticket ID</button>
                <button class="back-nav-btn" onclick="closeModal()" style="border-radius: var(--radius-md);">Close</button>
            </div>
        </div>
    </div>

    <div class="toast-box" id="toast">Copied to clipboard</div>

    <script>
        let currentFilter = 'all';
        let currentTicketId = '';

        function showToast(text) {
            const toast = document.getElementById('toast');
            toast.textContent = text;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 2500);
        }

        function filterTickets() {
            const query = document.getElementById('ticketSearch').value.toLowerCase().trim();
            const rows = document.querySelectorAll('.ticket-row');
            
            rows.forEach(row => {
                const id = row.getAttribute('data-id').toLowerCase();
                const question = row.getAttribute('data-question').toLowerCase();
                const reason = row.getAttribute('data-reason').toLowerCase();
                const status = row.getAttribute('data-status').toLowerCase();

                const matchesSearch = id.includes(query) || question.includes(query) || reason.includes(query);
                const matchesFilter = (currentFilter === 'all') || (status === currentFilter);

                row.style.display = (matchesSearch && matchesFilter) ? '' : 'none';
            });
        }

        function setFilter(status, btn) {
            currentFilter = status;
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterTickets();
        }

        function inspectTicket(row) {
            currentTicketId = row.getAttribute('data-id');
            document.getElementById('modalTicketId').textContent = currentTicketId;
            document.getElementById('modalTicketStatus').textContent = row.getAttribute('data-status').toUpperCase();
            document.getElementById('modalTicketConf').textContent = row.getAttribute('data-confidence');
            document.getElementById('modalTicketTime').textContent = row.getAttribute('data-time');
            document.getElementById('modalTicketQuestion').textContent = row.getAttribute('data-question');
            document.getElementById('modalTicketReason').textContent = row.getAttribute('data-reason');

            document.getElementById('ticketModal').classList.add('open');
        }

        function closeModal() {
            document.getElementById('ticketModal').classList.remove('open');
        }

        function closeModalOnOverlay(e) {
            if (e.target.id === 'ticketModal') closeModal();
        }

        function copyModalTicketId() {
            if (currentTicketId) {
                navigator.clipboard.writeText(currentTicketId);
                showToast(`Copied Ticket ID: ${currentTicketId}`);
            }
        }
    </script>
</body>
</html>
