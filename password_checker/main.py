"""Password checker web app entry point."""

from __future__ import annotations

import secrets
import string
import webbrowser
from threading import Timer

from flask import Flask, render_template_string, request


PASSWORD_LENGTH = 16
APP_HOST = "127.0.0.1"
APP_PORT = 5000

app = Flask(__name__)

PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Password Checker</title>
    <style>
        :root {
            color-scheme: dark;
            --bg: #0b1020;
            --panel: rgba(15, 23, 42, 0.82);
            --panel-border: rgba(148, 163, 184, 0.16);
            --text: #e2e8f0;
            --muted: #94a3b8;
            --accent: #38bdf8;
            --good: #22c55e;
            --warn: #f59e0b;
            --bad: #ef4444;
        }

        * { box-sizing: border-box; }
        body {
            margin: 0;
            min-height: 100vh;
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            color: var(--text);
            background:
                radial-gradient(circle at top left, rgba(56, 189, 248, 0.24), transparent 35%),
                radial-gradient(circle at right 20%, rgba(34, 197, 94, 0.18), transparent 28%),
                linear-gradient(160deg, #050816 0%, #0b1020 55%, #111827 100%);
            display: grid;
            place-items: center;
            padding: 24px;
        }

        .shell {
            width: min(960px, 100%);
            display: grid;
            gap: 20px;
            grid-template-columns: 1.1fr 0.9fr;
            align-items: start;
        }

        .hero, .panel {
            background: var(--panel);
            border: 1px solid var(--panel-border);
            backdrop-filter: blur(18px);
            border-radius: 24px;
            box-shadow: 0 24px 60px rgba(0, 0, 0, 0.28);
        }

        .hero {
            padding: 32px;
        }

        .kicker {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 0.78rem;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            color: var(--accent);
            margin-bottom: 14px;
        }

        h1 {
            margin: 0 0 14px;
            font-size: clamp(2.3rem, 4vw, 4rem);
            line-height: 0.95;
            max-width: 10ch;
        }

        .lead {
            margin: 0;
            max-width: 60ch;
            color: var(--muted);
            font-size: 1.02rem;
            line-height: 1.65;
        }

        .rules {
            margin-top: 24px;
            display: grid;
            gap: 10px;
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }

        .rule {
            padding: 14px 16px;
            border-radius: 16px;
            background: rgba(15, 23, 42, 0.72);
            border: 1px solid rgba(148, 163, 184, 0.12);
            color: var(--muted);
            font-size: 0.95rem;
        }

        .rule strong {
            display: block;
            color: var(--text);
            margin-bottom: 4px;
        }

        .panel {
            padding: 24px;
        }

        .form {
            display: grid;
            gap: 14px;
        }

        .field, .result, .generated {
            border-radius: 18px;
            border: 1px solid rgba(148, 163, 184, 0.14);
            background: rgba(2, 6, 23, 0.38);
        }

        .field {
            padding: 16px;
        }

        label {
            display: block;
            font-size: 0.88rem;
            color: var(--muted);
            margin-bottom: 10px;
        }

        input[type="password"], input[type="text"] {
            width: 100%;
            border: 0;
            outline: none;
            background: transparent;
            color: var(--text);
            font-size: 1.05rem;
            letter-spacing: 0.02em;
        }

        .actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        button, .button-link {
            border: 0;
            border-radius: 999px;
            padding: 12px 16px;
            font-weight: 700;
            font-size: 0.95rem;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.18s ease, box-shadow 0.18s ease, opacity 0.18s ease;
        }

        button:hover, .button-link:hover { transform: translateY(-1px); }

        .primary {
            background: linear-gradient(135deg, #38bdf8, #22c55e);
            color: #04111d;
            box-shadow: 0 12px 30px rgba(56, 189, 248, 0.24);
        }

        .secondary {
            background: rgba(148, 163, 184, 0.12);
            color: var(--text);
        }

        .generated, .result {
            padding: 18px;
        }

        .result {
            display: grid;
            gap: 12px;
            margin-top: 16px;
        }

        .scoreline {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            flex-wrap: wrap;
        }

        .badge {
            padding: 8px 12px;
            border-radius: 999px;
            font-size: 0.85rem;
            font-weight: 700;
        }

        .weak { background: rgba(239, 68, 68, 0.16); color: #fca5a5; }
        .medium { background: rgba(245, 158, 11, 0.16); color: #fbbf24; }
        .strong { background: rgba(34, 197, 94, 0.16); color: #86efac; }
        .very-strong { background: rgba(56, 189, 248, 0.16); color: #7dd3fc; }

        ul {
            list-style: none;
            padding: 0;
            margin: 0;
            display: grid;
            gap: 8px;
        }

        li {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            color: var(--muted);
            padding: 10px 12px;
            border-radius: 14px;
            background: rgba(15, 23, 42, 0.45);
        }

        .pass { color: #86efac; }
        .fail { color: #fca5a5; }

        .generated code {
            word-break: break-all;
            font-size: 1rem;
            color: #dbeafe;
        }

        .hint {
            margin-top: 14px;
            color: var(--muted);
            font-size: 0.9rem;
        }

        @media (max-width: 860px) {
            .shell { grid-template-columns: 1fr; }
            .rules { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <main class="shell">
        <section class="hero">
            <div class="kicker">Password strength checker</div>
            <h1>Check a password in the browser.</h1>
            <p class="lead">Type a password, score it against six rules, and see the result instantly without touching the terminal. You can also generate a strong random password with one click.</p>

            <div class="rules">
                <div class="rule"><strong>Minimum length</strong>At least 8 characters.</div>
                <div class="rule"><strong>Preferred length</strong>At least 12 characters.</div>
                <div class="rule"><strong>Uppercase</strong>Needs one capital letter.</div>
                <div class="rule"><strong>Lowercase</strong>Needs one lowercase letter.</div>
                <div class="rule"><strong>Digit</strong>Needs one numeric character.</div>
                <div class="rule"><strong>Special character</strong>Needs one punctuation mark.</div>
            </div>
        </section>

        <section class="panel">
            <form class="form" method="post">
                <div class="field">
                    <label for="password">Password</label>
                    <input id="password" name="password" type="password" value="{{ password or '' }}" autocomplete="off" placeholder="Enter a password to check">
                </div>

                <div class="actions">
                    <button class="primary" type="submit" name="action" value="check">Check password</button>
                    <button class="secondary" type="submit" name="action" value="generate">Generate strong password</button>
                </div>
            </form>

            {% if generated_password %}
            <div class="generated" style="margin-top: 18px;">
                <label>Generated password</label>
                <code>{{ generated_password }}</code>
            </div>
            {% endif %}

            {% if result %}
            {% set strength_key = result.strength|lower|replace(' ', '-') %}
            <div class="result">
                <div class="scoreline">
                    <div>
                        <div style="color: var(--muted); font-size: 0.9rem;">Strength</div>
                        <div style="font-size: 1.6rem; font-weight: 800;">{{ result.strength }}</div>
                    </div>
                    <div class="badge {{ strength_key }}">Score {{ result.score }}/6</div>
                </div>

                <ul>
                    <li><span>Minimum length</span><span class="{{ 'pass' if result.checks.min_length else 'fail' }}">{{ 'PASS' if result.checks.min_length else 'FAIL' }}</span></li>
                    <li><span>Preferred length</span><span class="{{ 'pass' if result.checks.preferred_length else 'fail' }}">{{ 'PASS' if result.checks.preferred_length else 'FAIL' }}</span></li>
                    <li><span>Uppercase</span><span class="{{ 'pass' if result.checks.uppercase else 'fail' }}">{{ 'PASS' if result.checks.uppercase else 'FAIL' }}</span></li>
                    <li><span>Lowercase</span><span class="{{ 'pass' if result.checks.lowercase else 'fail' }}">{{ 'PASS' if result.checks.lowercase else 'FAIL' }}</span></li>
                    <li><span>Digit</span><span class="{{ 'pass' if result.checks.digit else 'fail' }}">{{ 'PASS' if result.checks.digit else 'FAIL' }}</span></li>
                    <li><span>Special character</span><span class="{{ 'pass' if result.checks.special else 'fail' }}">{{ 'PASS' if result.checks.special else 'FAIL' }}</span></li>
                </ul>
            </div>
            {% endif %}

            <div class="hint">Tip: the generated password already satisfies all six checks.</div>
        </section>
    </main>
</body>
</html>"""

PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Password Strength Checker</title>
    <meta name="theme-color" content="#050816">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {
            color-scheme: dark;
            --bg-1: #050816;
            --bg-2: #0a1020;
            --bg-3: #121a30;
            --panel: rgba(12, 18, 34, 0.68);
            --panel-strong: rgba(12, 18, 34, 0.84);
            --border: rgba(148, 163, 184, 0.16);
            --text: #f5f7fb;
            --muted: #93a2b8;
            --accent: #7dd3fc;
            --accent-2: #8b5cf6;
            --shadow: 0 24px 72px rgba(0, 0, 0, 0.34);
            --radius: 22px;
        }

        :root[data-theme="light"] {
            color-scheme: light;
            --bg-1: #f4f7fb;
            --bg-2: #e8eef9;
            --bg-3: #dbe5f7;
            --panel: rgba(255, 255, 255, 0.62);
            --panel-strong: rgba(255, 255, 255, 0.84);
            --border: rgba(15, 23, 42, 0.08);
            --text: #0f172a;
            --muted: #516077;
            --accent: #2563eb;
            --accent-2: #7c3aed;
            --shadow: 0 24px 72px rgba(15, 23, 42, 0.12);
        }

        * { box-sizing: border-box; }
        body {
            margin: 0;
            min-height: 100vh;
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            color: var(--text);
            background: linear-gradient(145deg, var(--bg-1), var(--bg-2) 50%, var(--bg-3));
            overflow-x: hidden;
        }

        body::before,
        body::after {
            content: "";
            position: fixed;
            width: 30rem;
            height: 30rem;
            border-radius: 999px;
            filter: blur(78px);
            opacity: 0.3;
            pointer-events: none;
            z-index: 0;
            animation: drift 14s ease-in-out infinite;
        }

        body::before {
            top: -8rem;
            left: -8rem;
            background: radial-gradient(circle, rgba(125, 211, 252, 0.82) 0%, rgba(125, 211, 252, 0.12) 44%, transparent 72%);
        }

        body::after {
            right: -9rem;
            bottom: -10rem;
            background: radial-gradient(circle, rgba(139, 92, 246, 0.78) 0%, rgba(139, 92, 246, 0.14) 44%, transparent 72%);
            animation-delay: -6s;
        }

        @keyframes drift {
            0%, 100% { transform: translate3d(0, 0, 0) scale(1); }
            50% { transform: translate3d(18px, 14px, 0) scale(1.04); }
        }

        .page {
            position: relative;
            z-index: 1;
            min-height: 100vh;
            padding: 24px;
            display: grid;
            gap: 22px;
            grid-template-rows: auto 1fr;
        }

        .nav,
        .hero,
        .panel,
        .card {
            background: var(--panel);
            border: 1px solid var(--border);
            backdrop-filter: blur(18px);
            box-shadow: var(--shadow);
        }

        .nav {
            width: min(1220px, 100%);
            margin: 0 auto;
            border-radius: 999px;
            padding: 14px 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 14px;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 10px;
            min-width: 0;
        }

        .brand-mark {
            width: 40px;
            height: 40px;
            border-radius: 14px;
            display: grid;
            place-items: center;
            font-weight: 800;
            background: linear-gradient(135deg, rgba(125, 211, 252, 0.3), rgba(139, 92, 246, 0.3));
            box-shadow: 0 14px 34px rgba(125, 211, 252, 0.12);
        }

        .brand-copy { display: grid; gap: 2px; min-width: 0; }
        .brand-name { font-size: 0.98rem; font-weight: 800; letter-spacing: -0.02em; }
        .brand-subtitle {
            font-size: 0.82rem;
            color: var(--muted);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 24ch;
        }

        .toggle {
            width: 44px;
            height: 44px;
            border: 1px solid var(--border);
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.06);
            color: var(--text);
            cursor: pointer;
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        }
        .toggle:hover { transform: translateY(-1px); box-shadow: 0 0 0 6px rgba(125, 211, 252, 0.08); }

        .shell {
            width: min(1220px, 100%);
            margin: 0 auto;
            display: grid;
            grid-template-columns: minmax(0, 1fr) minmax(0, 0.98fr);
            gap: 24px;
            align-items: stretch;
        }

        .hero,
        .panel {
            position: relative;
            overflow: hidden;
            border-radius: var(--radius);
        }

        .hero::before,
        .panel::before {
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.06), transparent 40%);
            pointer-events: none;
        }

        .hero { padding: 34px; display: grid; gap: 22px; align-content: center; }
        h1 { margin: 0; font-size: clamp(2.4rem, 4vw, 4.4rem); line-height: 0.95; letter-spacing: -0.06em; max-width: 10ch; }
        .subtext { margin: 0; color: var(--muted); font-size: 1rem; line-height: 1.45; max-width: 28ch; }

        .rules-box {
            display: grid;
            gap: 12px;
        }

        .rules-title {
            text-align: center;
            font-size: 0.82rem;
            font-weight: 800;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            color: var(--accent);
        }

        .rules { display: grid; gap: 10px; }
        .rule {
            padding: 14px 15px;
            border-radius: 16px;
            background: rgba(15, 23, 42, 0.34);
            border: 1px solid rgba(148, 163, 184, 0.12);
            display: flex;
            align-items: center;
            gap: 10px;
            transition: transform 0.25s ease, border-color 0.25s ease, background 0.25s ease;
        }
        .rule-copy { display: grid; gap: 2px; }
        .rule-name { font-weight: 700; color: var(--text); }
        .rule-example { font-size: 0.82rem; color: var(--muted); }
        .rule[data-state="true"] { border-color: rgba(74, 222, 128, 0.26); background: rgba(74, 222, 128, 0.08); }
        .rule[data-state="false"] { border-color: rgba(251, 113, 133, 0.2); background: rgba(251, 113, 133, 0.06); }
        .rule-ico {
            width: 26px;
            height: 26px;
            border-radius: 999px;
            display: grid;
            place-items: center;
            flex: 0 0 auto;
            font-size: 0.9rem;
        }
        .rule[data-state="true"] .rule-ico { color: #22c55e; background: rgba(74, 222, 128, 0.14); }
        .rule[data-state="false"] .rule-ico { color: #fb7185; background: rgba(251, 113, 133, 0.12); }

        .panel { padding: 24px; display: grid; gap: 16px; align-content: start; }
        .field,
        .card {
            border-radius: 18px;
            border: 1px solid rgba(148, 163, 184, 0.14);
            background: var(--panel-strong);
        }

        .field { padding: 16px; transition: border-color 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease; }
        .field:focus-within { border-color: rgba(125, 211, 252, 0.4); box-shadow: 0 0 0 6px rgba(125, 211, 252, 0.08); transform: translateY(-1px); }
        label { display: block; margin-bottom: 10px; color: var(--muted); font-size: 0.85rem; }

        .password-wrap { position: relative; }
        input[type="password"], input[type="text"] {
            width: 100%;
            border: 0;
            outline: none;
            background: transparent;
            color: var(--text);
            font: inherit;
            font-size: 1.06rem;
            padding-right: 44px;
        }
        input[type="password"]::-ms-reveal,
        input[type="password"]::-ms-clear {
            display: none;
        }
        .toggle-visibility {
            position: absolute;
            right: 6px;
            top: 50%;
            transform: translateY(-50%);
            width: 32px;
            height: 32px;
            border: 0;
            border-radius: 999px;
            background: transparent;
            color: var(--muted);
            cursor: pointer;
            display: grid;
            place-items: center;
            transition: background 0.2s ease, color 0.2s ease, transform 0.2s ease;
        }
        .toggle-visibility:hover { background: rgba(125, 211, 252, 0.12); color: var(--text); transform: translateY(-50%) scale(1.05); }

        .actions { display: flex; flex-wrap: wrap; gap: 10px; }
        button {
            border: 0;
            border-radius: 999px;
            padding: 12px 16px;
            font: inherit;
            font-weight: 700;
            cursor: pointer;
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        }
        button:hover { transform: translateY(-2px); }
        .primary { background: linear-gradient(135deg, #38bdf8, #22c55e); color: #04111d; box-shadow: 0 14px 28px rgba(56, 189, 248, 0.2); }
        .secondary, .ghost { background: rgba(148, 163, 184, 0.12); color: var(--text); }
        .ghost { border: 1px solid rgba(125, 211, 252, 0.12); }

        .card { padding: 18px; }
        .score-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 12px; }
        .score-label { font-size: 0.82rem; color: var(--muted); margin-bottom: 6px; }
        .score-value { font-size: 1.55rem; font-weight: 900; letter-spacing: -0.05em; }
        .score-badge { border-radius: 999px; padding: 8px 12px; font-size: 0.84rem; font-weight: 800; }
        .weak { background: rgba(239, 68, 68, 0.14); color: #fecaca; }
        .medium { background: rgba(245, 158, 11, 0.14); color: #fde68a; }
        .strong { background: rgba(34, 197, 94, 0.14); color: #bbf7d0; }
        .very-strong { background: rgba(56, 189, 248, 0.14); color: #bae6fd; }
        .meter-head { display: flex; justify-content: space-between; gap: 12px; color: var(--muted); font-size: 0.82rem; margin-bottom: 10px; }
        .meter-track { height: 12px; border-radius: 999px; background: rgba(148, 163, 184, 0.16); overflow: hidden; }
        .meter-fill {
            width: 0;
            height: 100%;
            border-radius: inherit;
            background: linear-gradient(90deg, #fb7185 0%, #fbbf24 50%, #4ade80 100%);
            transition: width 0.45s cubic-bezier(.22, 1, .36, 1);
        }
        .time-row { margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.12); display: flex; align-items: center; justify-content: space-between; gap: 12px; }
        .time-row span:first-child { color: var(--muted); font-size: 0.82rem; }
        .time-value { font-weight: 800; letter-spacing: -0.03em; }

        @media (max-width: 920px) {
            .page { padding: 16px; }
            .shell { grid-template-columns: 1fr; }
            .hero, .panel { padding-left: 18px; padding-right: 18px; }
            .hero { padding-top: 28px; padding-bottom: 28px; }
            h1 { max-width: none; font-size: clamp(2.1rem, 9vw, 3.6rem); }
            .brand-subtitle { max-width: 18ch; }
        }
    </style>
</head>
<body>
    <div class="page">
        <header class="nav">
            <div class="brand">
                <div class="brand-mark">P</div>
                <div class="brand-copy">
                    <div class="brand-name">PulseVault</div>
                    <div class="brand-subtitle">Clean password checks</div>
                </div>
            </div>
            <button class="toggle" type="button" id="themeToggle" aria-label="Toggle theme">◐</button>
        </header>

        <main class="shell">
            <section class="hero">
                <div>
                    <h1>Check strength at a glance.</h1>
                    <p class="subtext">Fast, simple feedback.</p>
                </div>

                <div class="rules-box">
                    <div class="rules-title">Password Check</div>
                    <div class="rules" id="ruleListLeft">
                        <div class="rule" data-rule="min_length" data-state="{{ 'true' if checks.min_length else 'false' }}"><span class="rule-ico">{{ '✔' if checks.min_length else '✖' }}</span><span class="rule-copy"><span class="rule-name">8+ characters</span><span class="rule-example">erenmikas@123A</span></span></div>
                        <div class="rule" data-rule="uppercase" data-state="{{ 'true' if checks.uppercase else 'false' }}"><span class="rule-ico">{{ '✔' if checks.uppercase else '✖' }}</span><span class="rule-copy"><span class="rule-name">Uppercase</span><span class="rule-example">A, B, C</span></span></div>
                        <div class="rule" data-rule="lowercase" data-state="{{ 'true' if checks.lowercase else 'false' }}"><span class="rule-ico">{{ '✔' if checks.lowercase else '✖' }}</span><span class="rule-copy"><span class="rule-name">Lowercase</span><span class="rule-example">a, b, c</span></span></div>
                        <div class="rule" data-rule="digit" data-state="{{ 'true' if checks.digit else 'false' }}"><span class="rule-ico">{{ '✔' if checks.digit else '✖' }}</span><span class="rule-copy"><span class="rule-name">Number</span><span class="rule-example">1, 2, 3</span></span></div>
                        <div class="rule" data-rule="special" data-state="{{ 'true' if checks.special else 'false' }}"><span class="rule-ico">{{ '✔' if checks.special else '✖' }}</span><span class="rule-copy"><span class="rule-name">Symbol</span><span class="rule-example">!, @, #</span></span></div>
                    </div>
                </div>
            </section>

            <section class="panel">
                <form class="form" method="post" id="checkerForm">
                    <div class="field">
                        <label for="password">Password</label>
                        <div class="password-wrap">
                            <input id="password" name="password" type="password" value="{{ password or '' }}" autocomplete="off" placeholder="Enter password" spellcheck="false">
                            <button class="toggle-visibility" type="button" id="visibilityToggle" aria-label="Show password">👁</button>
                        </div>
                    </div>

                    <div class="actions">
                        <button class="primary" type="submit" name="action" value="check">Check Password</button>
                        <button class="secondary" type="submit" name="action" value="generate" id="generateBtn">Generate Strong Password</button>
                        <button class="ghost" type="button" id="copyBtn">Copy Password</button>
                    </div>
                </form>

                <div class="card" id="resultCard">
                    {% set strength_key = (result.strength if result else 'Weak')|lower|replace(' ', '-') %}
                    {% set score_value = result.score if result else 0 %}
                    {% set score_percent = (score_value / 5) * 100 %}

                    <div class="score-row">
                        <div>
                            <div class="score-label">Score</div>
                            <div class="score-value" id="scoreText">{{ score_value }}/5</div>
                        </div>
                        <div class="score-badge {{ strength_key }}" id="scoreBadge">{{ score_value }}/5</div>
                    </div>

                    <div class="meter-head">
                        <span>Strength bar</span>
                        <span id="meterPercent">{{ score_percent|round(0)|int }}%</span>
                    </div>
                    <div class="meter-track"><div class="meter-fill" id="meterFill" style="width: {{ score_percent }}%;"></div></div>

                    <div class="time-row">
                        <span>Time to crack</span>
                        <span class="time-value" id="crackTime">{{ crack_time }}</span>
                    </div>
                </div>
            </section>
        </main>
    </div>

    <script>
        const root = document.documentElement;
        const themeToggle = document.getElementById('themeToggle');
        const liveInput = document.getElementById('password');
        const copyBtn = document.getElementById('copyBtn');
        const generateBtn = document.getElementById('generateBtn');
        const visibilityToggle = document.getElementById('visibilityToggle');
        const scoreText = document.getElementById('scoreText');
        const scoreBadge = document.getElementById('scoreBadge');
        const meterFill = document.getElementById('meterFill');
        const meterPercent = document.getElementById('meterPercent');
        const crackTime = document.getElementById('crackTime');

        const storedTheme = localStorage.getItem('pulsevault-theme');
        if (storedTheme) root.dataset.theme = storedTheme;

        function analyzePassword(password) {
            const checks = {
                min_length: password.length >= 8,
                uppercase: /[A-Z]/.test(password),
                lowercase: /[a-z]/.test(password),
                digit: /[0-9]/.test(password),
                special: /[^A-Za-z0-9]/.test(password),
            };
            const score = Object.values(checks).filter(Boolean).length;
            const strength = score <= 1 ? 'Weak' : score === 2 ? 'Medium' : score <= 4 ? 'Strong' : 'Very Strong';
            return { checks, score, strength };
        }

        function crackEstimate(password, score) {
            if (!password) return '--';
            if (score === 5 && password.length >= 16) return 'Years+';
            if (score >= 4) return 'Months+';
            if (score >= 3) return 'Days';
            if (score >= 2) return 'Hours';
            return 'Minutes';
        }

        function paintRules(checks) {
            document.querySelectorAll('#ruleListLeft [data-rule]').forEach((node) => {
                const key = node.getAttribute('data-rule');
                const passed = Boolean(checks[key]);
                node.setAttribute('data-state', String(passed));
                const icon = node.querySelector('.rule-ico');
                if (icon) icon.textContent = passed ? '✔' : '✖';
            });
        }

        function updatePreview(password) {
            const result = analyzePassword(password);
            const percent = (result.score / 5) * 100;
            scoreText.textContent = `${result.score}/5`;
            scoreBadge.textContent = `${result.score}/5`;
            scoreBadge.className = `score-badge ${result.strength.toLowerCase().replace(/ /g, '-')}`;
            meterFill.style.width = `${percent}%`;
            meterPercent.textContent = `${Math.round(percent)}%`;
            crackTime.textContent = crackEstimate(password, result.score);
            paintRules(result.checks);
        }

        if (liveInput) {
            liveInput.addEventListener('input', () => updatePreview(liveInput.value));
            updatePreview(liveInput.value || '');
        }

        if (visibilityToggle && liveInput) {
            visibilityToggle.addEventListener('click', () => {
                const nextType = liveInput.type === 'password' ? 'text' : 'password';
                liveInput.type = nextType;
                visibilityToggle.textContent = nextType === 'password' ? '👁' : '🙈';
                visibilityToggle.setAttribute('aria-label', nextType === 'password' ? 'Show password' : 'Hide password');
                liveInput.focus();
            });
        }

        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                const nextTheme = root.dataset.theme === 'light' ? 'dark' : 'light';
                root.dataset.theme = nextTheme;
                localStorage.setItem('pulsevault-theme', nextTheme);
            });
        }

        if (copyBtn) {
            copyBtn.addEventListener('click', async () => {
                const value = liveInput?.value || '';
                if (!value) return;
                try {
                    await navigator.clipboard.writeText(value);
                    copyBtn.textContent = 'Copied';
                    setTimeout(() => copyBtn.textContent = 'Copy Password', 1000);
                } catch (error) {
                    copyBtn.textContent = 'Copy Failed';
                    setTimeout(() => copyBtn.textContent = 'Copy Password', 1000);
                }
            });
        }

        if (generateBtn) {
            generateBtn.addEventListener('click', () => {
                generateBtn.textContent = 'Generating...';
                setTimeout(() => { generateBtn.textContent = 'Generate Strong Password'; }, 800);
            });
        }
    </script>
</body>
</html>"""


def generate_password(length: int = PASSWORD_LENGTH) -> str:
    """Generate a strong random password that satisfies all criteria."""

    length = max(length, 12)
    required_groups = [
        string.ascii_uppercase,
        string.ascii_lowercase,
        string.digits,
        string.punctuation,
    ]

    characters = [secrets.choice(group) for group in required_groups]
    pool = string.ascii_letters + string.digits + string.punctuation
    characters.extend(secrets.choice(pool) for _ in range(length - len(characters)))
    secrets.SystemRandom().shuffle(characters)
    return "".join(characters)


def evaluate_password(password: str) -> dict[str, object]:
    """Evaluate the five visible password rules for the web UI."""

    checks = {
        "min_length": len(password) >= 8,
        "uppercase": any(character.isupper() for character in password),
        "lowercase": any(character.islower() for character in password),
        "digit": any(character.isdigit() for character in password),
        "special": any(character in string.punctuation for character in password),
    }

    score_value = sum(checks.values())
    if score_value <= 1:
        strength = "Weak"
    elif score_value == 2:
        strength = "Medium"
    elif score_value <= 4:
        strength = "Strong"
    else:
        strength = "Very Strong"

    return {
        "checks": checks,
        "score": score_value,
        "strength": strength,
    }


def estimate_time_to_crack(password: str, result: dict[str, object]) -> str:
    """Return a short time-to-crack label."""

    if not password:
        return "--"

    score_value = int(result["score"])
    if score_value == 5 and len(password) >= 16:
        return "Years+"
    if score_value >= 4:
        return "Months+"
    if score_value >= 3:
        return "Days"
    if score_value >= 2:
        return "Hours"
    return "Minutes"


def open_browser() -> None:
    """Open the app in the default browser after the server starts."""

    webbrowser.open(f"http://{APP_HOST}:{APP_PORT}")


@app.route("/", methods=["GET", "POST"])
def index() -> str:
    """Render the password checker page."""

    password = ""
    result = None
    generated_password = ""
    crack_time = "--"
    checks = {
        "min_length": False,
        "uppercase": False,
        "lowercase": False,
        "digit": False,
        "special": False,
    }

    if request.method == "POST":
        action = request.form.get("action", "check")
        if action == "generate":
            generated_password = generate_password()
            password = generated_password
            result = evaluate_password(generated_password)
        else:
            password = request.form.get("password", "")
            result = evaluate_password(password) if password else None

        if result is not None:
            checks = result["checks"]
            crack_time = estimate_time_to_crack(password, result)

    if result is not None:
        checks = result["checks"]

    return render_template_string(
        PAGE_TEMPLATE,
        password=password,
        result=result,
        generated_password=generated_password,
        crack_time=crack_time,
        checks=checks,
    )


def main() -> None:
    """Start the web server and open the browser."""

    Timer(0.8, open_browser).start()
    app.run(host=APP_HOST, port=APP_PORT, debug=False)


if __name__ == "__main__":
    main()