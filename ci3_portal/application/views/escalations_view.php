<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analyst Escalations | Project Atlas</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0a0e17;
            --bg-secondary: #111827;
            --bg-tertiary: #1f2937;
            --border-color: rgba(255, 255, 255, 0.08);
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --accent-blue: #3b82f6;
            --accent-cyan: #06b6d4;
            --accent-emerald: #10b981;
            --accent-amber: #f59e0b;
            --accent-rose: #f43f5e;
            --font-main: 'Plus Jakarta Sans', sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background-color: var(--bg-primary);
            color: var(--text-main);
            font-family: var(--font-main);
            min-height: 100vh;
            padding: 2rem;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border-color);
        }

        .header h1 { font-size: 1.5rem; font-weight: 700; }
        .back-link {
            color: var(--accent-cyan);
            text-decoration: none;
            font-weight: 600;
            font-size: 0.9rem;
        }

        .card {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }

        th, td {
            padding: 1rem 1.25rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }

        th {
            background: rgba(255, 255, 255, 0.03);
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }

        tr:hover {
            background: rgba(255, 255, 255, 0.02);
        }

        .ticket-id {
            font-family: var(--font-mono);
            color: #93c5fd;
            font-weight: 600;
        }

        .status-badge {
            padding: 0.25rem 0.6rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
        }

        .status-open {
            background: rgba(244, 63, 94, 0.15);
            color: var(--accent-rose);
            border: 1px solid rgba(244, 63, 94, 0.3);
        }

        .status-resolved {
            background: rgba(16, 185, 129, 0.15);
            color: var(--accent-emerald);
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>Senior Analyst Escalation Queue</h1>
            <p style="color: var(--text-muted); font-size: 0.85rem; margin-top: 0.25rem;">
                Client: <strong><?php echo html_escape($active_client_name); ?> (<?php echo html_escape($active_client_id); ?>)</strong>
            </p>
        </div>
        <a href="<?php echo site_url('chat'); ?>" class="back-link">← Return to Research Copilot</a>
    </div>

    <div class="card">
        <table>
            <thead>
                <tr>
                    <th>Ticket ID</th>
                    <th>Question</th>
                    <th>Escalation Reason</th>
                    <th>Confidence</th>
                    <th>Status</th>
                    <th>Created At</th>
                </tr>
            </thead>
            <tbody>
                <?php if (empty($escalations)): ?>
                    <tr>
                        <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 2rem;">
                            No escalation tickets found for this client.
                        </td>
                    </tr>
                <?php else: ?>
                    <?php foreach ($escalations as $ticket): ?>
                        <tr>
                            <td class="ticket-id"><?php echo html_escape($ticket['id']); ?></td>
                            <td style="max-width: 320px; font-weight: 500;"><?php echo html_escape($ticket['question']); ?></td>
                            <td style="color: #fde68a; max-width: 280px;"><?php echo html_escape($ticket['reason']); ?></td>
                            <td>
                                <strong><?php echo round($ticket['confidence'] * 100); ?>%</strong>
                            </td>
                            <td>
                                <span class="status-badge <?php echo $ticket['status'] === 'resolved' ? 'status-resolved' : 'status-open'; ?>">
                                    <?php echo html_escape($ticket['status']); ?>
                                </span>
                            </td>
                            <td style="color: var(--text-muted);"><?php echo html_escape(substr($ticket['created_at'], 0, 19)); ?></td>
                        </tr>
                    <?php endforeach; ?>
                <?php endif; ?>
            </tbody>
        </table>
    </div>
</body>
</html>
